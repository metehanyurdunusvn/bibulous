"use client";

import { useState, useEffect } from 'react';
import Navbar from '@/components/Navbar';
import BookCard, { Book } from '@/components/BookCard';
import { useRouter } from 'next/navigation';

export default function Home() {
    const router = useRouter();
    const [userId, setUserId] = useState<number | null>(null);
    const [userName, setUserName] = useState('');

    const [independentReqs, setIndependentReqs] = useState<Book[]>([]);
    const [authorReqs, setAuthorReqs] = useState<Book[]>([]);
    const [seriesReqs, setSeriesReqs] = useState<Book[]>([]);

    useEffect(() => {
        const uid = localStorage.getItem('userId');
        const uname = localStorage.getItem('userName');
        if (!uid) {
            router.push('/');
            return;
        }
        setUserId(parseInt(uid));
        setUserName(uname || '');

        fetch(`http://localhost:8000/api/books/recommend/${uid}`)
            .then(res => res.json())
            .then(data => {
                setIndependentReqs(data.independent || []);
                setAuthorReqs(data.same_author || []);
                setSeriesReqs(data.same_series || []);
            })
            .catch(err => console.error(err));
    }, [router]);

    return (
        <div>
            <Navbar />
            <h1 style={{ marginBottom: '2rem' }}>Welcome back, {userName}!</h1>

            <section style={{ marginBottom: '3rem' }}>
                <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem', color: 'var(--text-muted)' }}>Top Picks for You</h2>
                <div className="carousel-container">
                    {independentReqs.length === 0 ? <p>Loading recommendations...</p> : independentReqs.map(b => (
                        <div key={b.ISBN} onClick={() => router.push(`/book/${b.ISBN}`)}>
                            <BookCard book={b} />
                        </div>
                    ))}
                </div>
            </section>

            <section style={{ marginBottom: '3rem' }}>
                <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem', color: 'var(--text-muted)' }}>Because You Liked These Authors</h2>
                <div className="carousel-container">
                    {authorReqs.length === 0 ? <p style={{ color: 'var(--text-muted)' }}>Not enough data to recommend by author</p> : authorReqs.map(b => (
                        <div key={b.ISBN} onClick={() => router.push(`/book/${b.ISBN}`)}>
                            <BookCard book={b} />
                        </div>
                    ))}
                </div>
            </section>

            <section style={{ marginBottom: '3rem' }}>
                <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem', color: 'var(--text-muted)' }}>Similar Themes & Series</h2>
                <div className="carousel-container">
                    {seriesReqs.length === 0 ? <p style={{ color: 'var(--text-muted)' }}>Not enough data to find similar titles</p> : seriesReqs.map(b => (
                        <div key={b.ISBN} onClick={() => router.push(`/book/${b.ISBN}`)}>
                            <BookCard book={b} />
                        </div>
                    ))}
                </div>
            </section>
        </div>
    );
}
