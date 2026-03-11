import os
import pandas as pd
import numpy as np
import time
import warnings

warnings.filterwarnings('ignore')

class RecommendationEngine:
    def __init__(self, data_dir='../archives', datas_dir='../datas'):
        self.data_dir = data_dir
        self.datas_dir = datas_dir
        self.books_df = None
        self.ratings_df = None
        self.books_dict = {}
        
        self.tags_dict = {}
        self.book_tags_dict = {}
        self.isbn_to_goodreads = {}
        
        self.is_trained = False
        
        # User-item matrix equivalents for fast query
        self.user_item_matrix = None
        self.book_stats = None

    def load_data(self):
        print("Loading data...")
        books_path = os.path.join(self.data_dir, 'Books.csv')
        ratings_path = os.path.join(self.data_dir, 'Ratings.csv')
        
        tags_path = os.path.join(self.datas_dir, 'tags.csv')
        book_tags_path = os.path.join(self.datas_dir, 'book_tags.csv')
        books_datas_path = os.path.join(self.datas_dir, 'books.csv')
        
        # Load Books
        self.books_df = pd.read_csv(books_path, sep=',', dtype=str, on_bad_lines='skip')
        self.books_df.rename(columns={
            'Book-Title': 'title',
            'Book-Author': 'authors',
            'Image-URL-M': 'image_url'
        }, inplace=True)
        
        # Load Ratings
        self.ratings_df = pd.read_csv(ratings_path, sep=',', dtype={'User-ID': int, 'Book-Rating': int}, on_bad_lines='skip')
        self.ratings_df.rename(columns={'User-ID': 'user_id', 'Book-Rating': 'rating'}, inplace=True)
        self.ratings_df = self.ratings_df[self.ratings_df['rating'] > 0]
        
        self.books_df['ISBN'] = self.books_df['ISBN'].astype(str)
        self.books_dict = self.books_df.set_index('ISBN')[['title', 'authors', 'image_url']].to_dict('index')

        # Load Tags data
        try:
            if os.path.exists(tags_path):
                tags_df = pd.read_csv(tags_path, on_bad_lines='skip')
                self.tags_dict = tags_df.set_index('tag_id')['tag_name'].to_dict()
                print(f"Loaded {len(self.tags_dict)} tags.")
                
            if os.path.exists(book_tags_path):
                book_tags_df = pd.read_csv(book_tags_path, on_bad_lines='skip')
                # Group tags by goodreads_book_id
                grouped_tags = book_tags_df.groupby('goodreads_book_id')['tag_id'].apply(list).to_dict()
                self.book_tags_dict = grouped_tags
                print(f"Loaded tags for {len(self.book_tags_dict)} books.")
                
            if os.path.exists(books_datas_path):
                books_datas_df = pd.read_csv(books_datas_path, dtype=str, on_bad_lines='skip')
                # Map standard ISBN to goodreads_book_id
                valid_mappings = books_datas_df.dropna(subset=['isbn', 'goodreads_book_id'])
                # Fill missing leading zeros for isbn-10
                isbns_padded = valid_mappings['isbn'].apply(lambda x: str(x).zfill(10)[:10])
                self.isbn_to_goodreads = dict(zip(isbns_padded, valid_mappings['goodreads_book_id'].astype(int)))
                
                # Also try to map by isbn13 or title if we want, but isbn is good for now
                # Add isbn13 mapping as well to be safe
                # Note: archives/Books.csv typically uses isbn10
                print(f"Loaded {len(self.isbn_to_goodreads)} ISBN to Goodreads ID mappings.")
        except Exception as e:
            print(f"Error loading tag data: {e}")

        # Filter dataset to ensure users have rated enough books and books have been rated enough
        min_book_ratings = 50
        min_user_ratings = 20

        counts_b = self.ratings_df['ISBN'].value_counts()
        self.ratings_df = self.ratings_df[self.ratings_df['ISBN'].isin(counts_b[counts_b > min_book_ratings].index)]

        counts_u = self.ratings_df['user_id'].value_counts()
        self.ratings_df = self.ratings_df[self.ratings_df['user_id'].isin(counts_u[counts_u > min_user_ratings].index)]

        valid_books = set(self.books_df['ISBN'])
        self.ratings_df = self.ratings_df[self.ratings_df['ISBN'].isin(valid_books)]

        print(f"Data loading complete. {len(self.ratings_df)} valid ratings remaining.")

    def train_model(self):
        if self.ratings_df is None:
            self.load_data()

        print("Computing average book stats for fallback recommendations...")
        self.book_stats = self.ratings_df.groupby('ISBN').agg(
            avg_rating=('rating', 'mean'),
            count=('rating', 'count')
        ).reset_index()
        
        C = self.book_stats['count'].mean()
        m = self.book_stats['avg_rating'].mean()
        
        self.book_stats['weighted_score'] = (self.book_stats['count'] / (self.book_stats['count'] + C) * self.book_stats['avg_rating']) + (C / (self.book_stats['count'] + C) * m)
        self.book_stats = self.book_stats.sort_values('weighted_score', ascending=False)
        
        self.book_stats['title'] = self.book_stats['ISBN'].map(lambda x: self.books_dict.get(x, {}).get('title'))
        self.book_stats = self.book_stats.dropna(subset=['title']).drop_duplicates(subset=['title'], keep='first').drop('title', axis=1)

        self.is_trained = True
        print("Simple model training complete.")

    def get_recommendations_cf(self, user_id, n=10, liked_isbns=None):
        if not self.is_trained:
            return []
            
        liked_isbns = set(liked_isbns or [])
        user_history = self.ratings_df[self.ratings_df['user_id'] == user_id]
        read_isbns = set(user_history['ISBN']) | liked_isbns
        
        read_authors = set()
        for isbn in read_isbns:
            info = self.books_dict.get(isbn)
            if info and pd.notna(info['authors']):
                read_authors.add(str(info['authors']).lower().strip())
        
        candidates = None

        if liked_isbns:
            similar_users = self.ratings_df[self.ratings_df['ISBN'].isin(liked_isbns)]['user_id'].unique()
            
            if len(similar_users) > 0:
                similar_users_ratings = self.ratings_df[self.ratings_df['user_id'].isin(similar_users)]
                similar_users_ratings = similar_users_ratings[~similar_users_ratings['ISBN'].isin(read_isbns)]
                
                valid_cand_isbns = set()
                for isbn in similar_users_ratings['ISBN'].unique():
                    info = self.books_dict.get(isbn)
                    if info:
                        author = str(info['authors']).lower().strip()
                        if author not in read_authors:
                            valid_cand_isbns.add(isbn)
                            
                similar_users_ratings = similar_users_ratings[similar_users_ratings['ISBN'].isin(valid_cand_isbns)]
                
                if not similar_users_ratings.empty:
                    book_scores = similar_users_ratings.groupby('ISBN').agg(
                        count=('rating', 'count'),
                        avg_rating=('rating', 'mean')
                    ).reset_index()
                    
                    C = book_scores['count'].mean()
                    m = book_scores['avg_rating'].mean()
                    book_scores['score'] = (book_scores['count'] / (book_scores['count'] + C) * book_scores['avg_rating']) + (C / (book_scores['count'] + C) * m)
                    
                    candidates = book_scores.sort_values('score', ascending=False)
        
        if candidates is None or candidates.empty or len(candidates) < n:
            fallback_candidates = self.book_stats[~self.book_stats['ISBN'].isin(read_isbns)]
            fallback_isbns = fallback_candidates['ISBN'].tolist()
            filtered_fallback = []
            for isbn in fallback_isbns:
                info = self.books_dict.get(isbn)
                if info and str(info['authors']).lower().strip() not in read_authors:
                    filtered_fallback.append(isbn)
            fallback_candidates = fallback_candidates[fallback_candidates['ISBN'].isin(filtered_fallback)]
            
            if candidates is not None and not candidates.empty:
                candidates = pd.concat([candidates, fallback_candidates]).drop_duplicates(subset=['ISBN'])
            else:
                candidates = fallback_candidates
        
        results = []
        seen_titles = set()
        
        for idx, row in candidates.iterrows():
            if len(results) >= n:
                break
            isbn = row['ISBN']
            info = self.books_dict.get(isbn)
            if not info:
                continue
                
            author = str(info['authors']).lower().strip()
            
            if author in read_authors:
                continue
                
            title = str(info['title']).lower()
            if title in seen_titles: 
                continue
                
            results.append({
                "ISBN": isbn,
                "title": info['title'],
                "authors": info['authors'],
                "image_url": info['image_url']
            })
            seen_titles.add(title)
            
        return results

    def get_recommendations_with_metrics(self, user_id, liked_isbns=None, n=10):
        if not self.is_trained:
            return []
            
        liked_isbns = set(liked_isbns or [])
        user_history = self.ratings_df[self.ratings_df['user_id'] == user_id] if user_id else pd.DataFrame(columns=['ISBN'])
        read_isbns = set(user_history['ISBN']) | liked_isbns
        
        # Build user tag profile
        user_tags = set()
        for isbn in read_isbns:
            gr_id = self.isbn_to_goodreads.get(isbn)
            if gr_id and gr_id in self.book_tags_dict:
                user_tags.update(self.book_tags_dict[gr_id])
                
        read_authors = set()
        for isbn in read_isbns:
            info = self.books_dict.get(isbn)
            if info and pd.notna(info['authors']):
                read_authors.add(str(info['authors']).lower().strip())
        
        # Get Candidates (CF + Popularity)
        candidates_cf = None
        if liked_isbns:
            similar_users = self.ratings_df[self.ratings_df['ISBN'].isin(liked_isbns)]['user_id'].unique()
            if len(similar_users) > 0:
                similar_users_ratings = self.ratings_df[self.ratings_df['user_id'].isin(similar_users)]
                similar_users_ratings = similar_users_ratings[~similar_users_ratings['ISBN'].isin(read_isbns)]
                
                valid_cand_isbns = set()
                for isbn in similar_users_ratings['ISBN'].unique():
                    info = self.books_dict.get(isbn)
                    if info:
                        author = str(info['authors']).lower().strip()
                        if author not in read_authors:
                            valid_cand_isbns.add(isbn)
                            
                similar_users_ratings = similar_users_ratings[similar_users_ratings['ISBN'].isin(valid_cand_isbns)]
                
                if not similar_users_ratings.empty:
                    book_scores = similar_users_ratings.groupby('ISBN').agg(
                        count=('rating', 'count'),
                        avg_rating=('rating', 'mean')
                    ).reset_index()
                    C = book_scores['count'].mean()
                    m = book_scores['avg_rating'].mean()
                    book_scores['cf_score'] = (book_scores['count'] / (book_scores['count'] + C) * book_scores['avg_rating']) + (C / (book_scores['count'] + C) * m)
                    candidates_cf = book_scores[['ISBN', 'cf_score']]
        
        # Base candidates from popularity
        fallback_candidates = self.book_stats[~self.book_stats['ISBN'].isin(read_isbns)].copy()
        
        # Filter author
        fallback_isbns = fallback_candidates['ISBN'].tolist()
        filtered_fallback = []
        for isbn in fallback_isbns:
            info = self.books_dict.get(isbn)
            if info and str(info['authors']).lower().strip() not in read_authors:
                filtered_fallback.append(isbn)
                
        fallback_candidates = fallback_candidates[fallback_candidates['ISBN'].isin(filtered_fallback)]
        fallback_candidates.rename(columns={'weighted_score': 'pop_score'}, inplace=True)
        
        # Merge CF and Pop scores
        if candidates_cf is not None and not candidates_cf.empty:
            merged = pd.merge(fallback_candidates, candidates_cf, on='ISBN', how='left')
            merged['cf_score'].fillna(0, inplace=True)
        else:
            merged = fallback_candidates.copy()
            merged['cf_score'] = 0.0
            
        # Calculate metrics for each candidate
        metrics_results = []
        seen_titles = set()
        
        # Take a top subset to calculate tag similarities (it can be slow for all)
        merged['combined_base_score'] = merged['cf_score'] * 0.7 + merged['pop_score'] * 0.3
        merged = merged.sort_values('combined_base_score', ascending=False).head(min(100, len(merged)))
        
        for idx, row in merged.iterrows():
            isbn = row['ISBN']
            info = self.books_dict.get(isbn)
            if not info: continue
            
            title = str(info['title'])
            title_lower = title.lower()
            if title_lower in seen_titles: continue
            
            # Tag similarity
            tag_score = 0.0
            shared_tags_data = []
            gr_id = self.isbn_to_goodreads.get(isbn)
            if gr_id and gr_id in self.book_tags_dict:
                book_tags = set(self.book_tags_dict[gr_id])
                overlap = user_tags.intersection(book_tags)
                tag_score = len(overlap) / (len(book_tags) + 1e-5) * 10.0 # scale 0-10 roughly
                
                # Get names of top 3 shared tags
                shared_tag_ids = list(overlap)[:3]
                for tid in shared_tag_ids:
                    if tid in self.tags_dict:
                        shared_tags_data.append(self.tags_dict[tid])
            
            cf_val = float(row['cf_score'])
            pop_val = float(row['pop_score'])
            
            # Combine into a final score
            final_score = (cf_val * 0.5) + (pop_val * 2.0) + (tag_score * 0.5)
            
            metrics_results.append({
                "ISBN": isbn,
                "title": title,
                "authors": info['authors'],
                "image_url": info['image_url'],
                "metrics": {
                    "total_score": round(final_score, 2),
                    "cf_score": round(cf_val, 2),
                    "pop_score": round(pop_val, 2),
                    "tag_score": round(tag_score, 2),
                    "shared_tags": shared_tags_data
                }
            })
            seen_titles.add(title_lower)
            
        metrics_results.sort(key=lambda x: x['metrics']['total_score'], reverse=True)
        return metrics_results[:n]

    def get_recommendations_same_author(self, user_liked_isbns, n=5):
        if not user_liked_isbns:
            return []
            
        target_authors = set()
        for isbn in user_liked_isbns:
            info = self.books_dict.get(isbn)
            if info and pd.notna(info['authors']):
                target_authors.add(str(info['authors']).lower())
                
        if not target_authors:
            return []
            
        mask = self.books_df['authors'].str.lower().isin(target_authors)
        candidates = self.books_df[mask & ~self.books_df['ISBN'].isin(user_liked_isbns)]
        candidates = candidates.drop_duplicates(subset=['title'], keep='first')
        
        if len(candidates) > n:
            candidates = candidates.sample(n)
            
        return [
            {
                "ISBN": row['ISBN'],
                "title": row['title'],
                "authors": row['authors'],
                "image_url": row['image_url']
            } for _, row in candidates.iterrows()
        ]

    def get_recommendations_similar_title(self, user_liked_isbns, n=5, exclude_authors=None):
        if not user_liked_isbns:
            return []
            
        exclude_authors = exclude_authors or set()
            
        keywords = set()
        for isbn in user_liked_isbns:
            info = self.books_dict.get(isbn)
            if info and pd.notna(info['title']):
                words = str(info['title']).lower().split()
                words = [w for w in words if len(w) > 4]
                keywords.update(words)
                
        if not keywords:
            return []
            
        def score_title(title):
            if pd.isna(title): return 0
            t_words = set(str(title).lower().split())
            return len(keywords.intersection(t_words))
            
        self.books_df['temp_score'] = self.books_df['title'].apply(score_title)
        
        mask = ~self.books_df['ISBN'].isin(user_liked_isbns)
        if exclude_authors:
            author_mask = ~self.books_df['authors'].str.lower().isin(exclude_authors)
            mask = mask & author_mask
            
        candidates = self.books_df[(self.books_df['temp_score'] > 0) & mask]
        candidates = candidates.drop_duplicates(subset=['title'], keep='first').sort_values('temp_score', ascending=False).head(n)
        
        self.books_df.drop('temp_score', axis=1, inplace=True)
        
        return [
            {
                "ISBN": row['ISBN'],
                "title": row['title'],
                "authors": row['authors'],
                "image_url": row['image_url']
            } for _, row in candidates.iterrows()
        ]

    def get_top_books(self, skip=0, limit=50):
        if not self.is_trained:
            return []
        
        top_stats = self.book_stats.iloc[skip:skip+limit]
        
        results = []
        for _, row in top_stats.iterrows():
            isbn = row['ISBN']
            info = self.books_dict.get(isbn)
            if info:
                results.append({
                    "ISBN": isbn,
                    "title": info['title'],
                    "authors": info['authors'],
                    "image_url": info['image_url']
                })
        return results

    def get_random_books(self, n=50):
        valid = self.books_df.dropna(subset=['image_url', 'authors', 'title'])
        rated_isbns = set(self.ratings_df['ISBN'].unique())
        valid = valid[valid['ISBN'].isin(rated_isbns)]
        valid = valid.drop_duplicates(subset=['title'], keep='first')
        
        if len(valid) > n:
            sampled = valid.sample(n=n)
        else:
            sampled = valid
            
        return [
            {
                "ISBN": row['ISBN'],
                "title": row['title'],
                "authors": row['authors'],
                "image_url": row['image_url']
            } for _, row in sampled.iterrows()
        ]

    def search_books(self, query, n=10):
        q = str(query).lower()
        mask = self.books_df['title'].str.lower().str.contains(q, na=False) | self.books_df['authors'].str.lower().str.contains(q, na=False)
        matched = self.books_df[mask].drop_duplicates(subset=['title'], keep='first').head(n)
        return [
            {
                "ISBN": row['ISBN'],
                "title": row['title'],
                "authors": row['authors'],
                "image_url": row['image_url']
            } for _, row in matched.iterrows()
        ]

# Global instance to be used by the FastAPI app
recommender = RecommendationEngine(
    data_dir=os.path.join(os.path.dirname(__file__), '..', 'archives'),
    datas_dir=os.path.join(os.path.dirname(__file__), '..', 'datas')
)

