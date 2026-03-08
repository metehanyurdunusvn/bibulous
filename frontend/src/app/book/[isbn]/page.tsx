"use client";

import { useState, useEffect } from 'react';
import Navbar from '@/components/Navbar';
import BookCard, { Book } from '@/components/BookCard';
import { useRouter } from 'next/navigation';
import { use } from 'react';

export default function BookDetail({ params }: { params: Promise<{ isbn: string }> }) {
    const router = useRouter();

    // Next 15 requires unwrapping params with React.use()
    const resolvedParams = use(params);
    const isbn = resolvedParams.isbn;

    const [book, setBook] = useState<Book | null>(null);
    const [comments, setComments] = useState<any[]>([]);
    const [newComment, setNewComment] = useState('');
    const [rating, setRating] = useState(5);
    const [userId, setUserId] = useState<number | null>(null);
    const [similarBooks, setSimilarBooks] = useState<Book[]>([]);

    useEffect(() => {
        const uid = localStorage.getItem('userId');
        if (!uid) {
            router.push('/');
            return;
        }
        setUserId(parseInt(uid));

        // Fetch book details
        fetch(`http://localhost:8000/api/books/detail/${isbn}`)
            .then(res => {
                if (!res.ok) throw new Error("Book not found");
                return res.json();
            })
            .then(data => setBook(data))
            .catch(console.error);

        // Fetch similar books
        fetch(`http://localhost:8000/api/books/${isbn}/similar`)
            .then(res => res.json())
            .then(data => setSimilarBooks(data || []))
            .catch(console.error);

        fetchComments();
    }, [isbn, router]);

    const fetchComments = () => {
        fetch(`http://localhost:8000/api/books/${isbn}/comments`)
            .then(res => res.json())
            .then(data => setComments(data))
            .catch(console.error);
    };

    const submitComment = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!userId || !newComment) return;

        await fetch(`http://localhost:8000/api/books/${isbn}/comments?user_id=${userId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ comment: newComment, rating })
        });
        setNewComment('');
        fetchComments();
    };

    if (!book) return <div style={{ padding: '2rem' }}>Loading...</div>;

    return (
        <div>
            <Navbar />
            <div style={{ display: 'flex', gap: '40px', flexWrap: 'wrap' }}>
                <img
                    src={book.image_url}
                    alt={book.title}
                    onError={(e) => { e.currentTarget.src = 'https://via.placeholder.com/300x450?text=No+Cover' }}
                    style={{ width: '300px', borderRadius: '12px', boxShadow: '0 10px 25px rgba(0,0,0,0.5)' }}
                />
                <div style={{ flex: 1, minWidth: '300px' }}>
                    <h1 className="heading-hero" style={{ fontSize: '3rem', marginBottom: '10px' }}>{book.title}</h1>
                    <p style={{ fontSize: '1.5rem', color: 'var(--text-muted)' }}>{book.authors}</p>
                    <p style={{ marginTop: '20px' }}><strong>ISBN:</strong> {book.ISBN}</p>

                    <div className="glass" style={{ padding: '20px', marginTop: '40px' }}>
                        <h3 style={{ marginBottom: '20px' }}>Reviews & Ratings ({comments.length})</h3>

                        <form onSubmit={submitComment} style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '30px' }}>
                            <select
                                value={rating}
                                onChange={e => setRating(parseInt(e.target.value))}
                                className="input-glass"
                                style={{ width: '150px' }}
                            >
                                {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(r => <option key={r} value={r} style={{ color: "black" }}>{r} / 10</option>)}
                            </select>
                            <textarea
                                className="input-glass"
                                placeholder="Share your thoughts on this book..."
                                value={newComment}
                                onChange={e => setNewComment(e.target.value)}
                                rows={3}
                                required
                            />
                            <button className="btn-primary" type="submit" style={{ alignSelf: 'flex-start' }}>Post Review</button>
                        </form>

                        <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                            {comments.map(c => (
                                <div key={c.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '10px' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
                                        <strong>{c.user_name}</strong>
                                        <span style={{ color: 'gold' }}>⭐ {c.rating}/10</span>
                                    </div>
                                    <p style={{ color: 'var(--text-muted)' }}>{c.comment}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            {/* You might also like section */}
            {similarBooks.length > 0 && (
                <div style={{ marginTop: '50px' }}>
                    <h2 className="heading-section" style={{ marginBottom: '20px' }}>Bunları da beğenebilirsin</h2>
                    <div style={{ 
                        display: 'flex', 
                        gap: '20px', 
                        overflowX: 'auto', 
                        padding: '10px 0 20px 0',
                        scrollBehavior: 'smooth' 
                    }}>
                        {similarBooks.map(b => (
                            <div key={b.ISBN} style={{ minWidth: '200px', maxWidth: '200px', flexShrink: 0 }}>
                                <BookCard 
                                    book={b} 
                                    onClick={() => router.push(`/book/${b.ISBN}`)} 
                                />
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
