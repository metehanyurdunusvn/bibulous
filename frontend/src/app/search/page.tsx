"use client";

import { useState } from 'react';
import Navbar from '@/components/Navbar';
import BookCard, { Book } from '@/components/BookCard';
import { useRouter } from 'next/navigation';

export default function Search() {
    const router = useRouter();
    const [query, setQuery] = useState('');
    const [results, setResults] = useState<Book[]>([]);

    const doSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!query) return;
        try {
            const res = await fetch(`http://localhost:8000/api/books/search?q=${query}&n=20`);
            const data = await res.json();
            setResults(data);
        } catch (err) {
            console.error(err);
        }
    };

    return (
        <div>
            <Navbar />
            <div style={{ maxWidth: '800px', margin: '0 auto' }}>
                <h1 style={{ marginBottom: '20px' }}>Search Books</h1>
                <form onSubmit={doSearch} style={{ display: 'flex', gap: '10px', marginBottom: '40px' }}>
                    <input
                        type="text"
                        className="input-glass"
                        placeholder="Search by title or author..."
                        value={query}
                        onChange={e => setQuery(e.target.value)}
                    />
                    <button type="submit" className="btn-primary">Search</button>
                </form>

                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '20px', justifyContent: 'center' }}>
                    {results.map(b => (
                        <div key={b.ISBN} onClick={() => router.push(`/book/${b.ISBN}`)}>
                            <BookCard book={b} />
                        </div>
                    ))}
                    {results.length === 0 && <p style={{ color: 'var(--text-muted)' }}>No books found.</p>}
                </div>
            </div>
        </div>
    );
}
