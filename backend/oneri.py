import os
import pandas as pd
import numpy as np
import time
import warnings

warnings.filterwarnings('ignore')

class RecommendationEngine:
    def __init__(self, data_dir='../archives'):
        self.data_dir = data_dir
        self.books_df = None
        self.ratings_df = None
        self.books_dict = {}
        self.is_trained = False
        
        # User-item matrix equivalents for fast query
        self.user_item_matrix = None
        self.book_stats = None

    def load_data(self):
        print("📂 Loading data...")
        books_path = os.path.join(self.data_dir, 'Books.csv')
        ratings_path = os.path.join(self.data_dir, 'Ratings.csv')
        
        # Load Books
        # Handle bad lines just in case
        self.books_df = pd.read_csv(books_path, sep=',', dtype=str, on_bad_lines='skip')
        self.books_df.rename(columns={
            'Book-Title': 'title',
            'Book-Author': 'authors',
            'Image-URL-M': 'image_url'
        }, inplace=True)
        
        # Load Ratings
        self.ratings_df = pd.read_csv(ratings_path, sep=',', dtype={'User-ID': int, 'Book-Rating': int}, on_bad_lines='skip')
        self.ratings_df.rename(columns={'User-ID': 'user_id', 'Book-Rating': 'rating'}, inplace=True)
        # Filter explicitly 0 ratings which means implicit feedback in some datasets, keep > 0
        self.ratings_df = self.ratings_df[self.ratings_df['rating'] > 0]
        
        # Create books dictionary for fast access
        # Ensure ISBNs are string
        self.books_df['ISBN'] = self.books_df['ISBN'].astype(str)
        self.books_dict = self.books_df.set_index('ISBN')[['title', 'authors', 'image_url']].to_dict('index')

        # Filter dataset to ensure users have rated enough books and books have been rated enough (reduce memory)
        min_book_ratings = 50
        min_user_ratings = 20

        counts_b = self.ratings_df['ISBN'].value_counts()
        self.ratings_df = self.ratings_df[self.ratings_df['ISBN'].isin(counts_b[counts_b > min_book_ratings].index)]

        counts_u = self.ratings_df['user_id'].value_counts()
        self.ratings_df = self.ratings_df[self.ratings_df['user_id'].isin(counts_u[counts_u > min_user_ratings].index)]

        # Also ensure books are in books_df
        valid_books = set(self.books_df['ISBN'])
        self.ratings_df = self.ratings_df[self.ratings_df['ISBN'].isin(valid_books)]

        print(f"✅ Data loading complete. {len(self.ratings_df)} valid ratings remaining.")

    def train_model(self):
        if self.ratings_df is None:
            self.load_data()

        print("🚀 Computing average book stats for fallback recommendations...")
        # Pure pandas content-based / popularity-based model as fallback to keep it fast
        self.book_stats = self.ratings_df.groupby('ISBN').agg(
            avg_rating=('rating', 'mean'),
            count=('rating', 'count')
        ).reset_index()
        
        # Bayesian average to smooth out the popular ones
        C = self.book_stats['count'].mean()
        m = self.book_stats['avg_rating'].mean()
        
        self.book_stats['weighted_score'] = (self.book_stats['count'] / (self.book_stats['count'] + C) * self.book_stats['avg_rating']) + (C / (self.book_stats['count'] + C) * m)
        self.book_stats = self.book_stats.sort_values('weighted_score', ascending=False)
        
        # Deduplicate by title to prevent showing multiple editions
        self.book_stats['title'] = self.book_stats['ISBN'].map(lambda x: self.books_dict.get(x, {}).get('title'))
        self.book_stats = self.book_stats.dropna(subset=['title']).drop_duplicates(subset=['title'], keep='first').drop('title', axis=1)

        self.is_trained = True
        print("✅ Simple model training complete.")

    def get_recommendations_cf(self, user_id, n=10, exclude_isbns=None):
        if not self.is_trained:
            return []
            
        exclude_isbns = set(exclude_isbns or [])
        user_history = self.ratings_df[self.ratings_df['user_id'] == user_id]
        read_isbns = set(user_history['ISBN']) | exclude_isbns
        
        # Simplified memory-based logic: return top-rated books that user hasn't read
        candidates = self.book_stats[~self.book_stats['ISBN'].isin(read_isbns)]
        top_candidates = candidates.head(n * 5)
        
        results = []
        seen_authors = set()
        for idx, row in top_candidates.iterrows():
            if len(results) >= n:
                break
            isbn = row['ISBN']
            info = self.books_dict.get(isbn)
            if not info:
                continue
            author = str(info['authors']).lower()
            if author in seen_authors: 
                continue
                
            results.append({
                "ISBN": isbn,
                "title": info['title'],
                "authors": info['authors'],
                "image_url": info['image_url']
            })
            seen_authors.add(author)
            
        return results

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
            
        # Search books with same author
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

    def get_recommendations_similar_title(self, user_liked_isbns, n=5):
        if not user_liked_isbns:
            return []
            
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
        
        candidates = self.books_df[(self.books_df['temp_score'] > 0) & (~self.books_df['ISBN'].isin(user_liked_isbns))]
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
recommender = RecommendationEngine(data_dir=os.path.join(os.path.dirname(__file__), '..', 'archives'))
