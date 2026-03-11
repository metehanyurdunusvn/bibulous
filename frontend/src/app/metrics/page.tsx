"use client";

import { useState, useEffect } from 'react';
import Navbar from '@/components/Navbar';

interface MetricData {
    total_score: number;
    cf_score: number;
    pop_score: number;
    tag_score: number;
    shared_tags: string[];
}

interface MetricBook {
    ISBN: string;
    title: string;
    authors: string;
    image_url: string;
    metrics: MetricData;
}

export default function MetricsPage() {
    const [books, setBooks] = useState<MetricBook[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const uid = localStorage.getItem('userId');
        if (!uid) return;

        fetch(`http://localhost:8000/api/books/metrics/${uid}`)
            .then(res => res.json())
            .then(data => {
                setBooks(data || []);
                setLoading(false);
            })
            .catch(err => {
                console.error(err);
                setLoading(false);
            });
    }, []);

    return (
        <div>
            <Navbar />
            <h1 style={{ marginBottom: '1rem', fontSize: '2rem' }} className="heading-hero">Öneri Metrikleri</h1>
            <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>Detailed breakdown of your personalized book recommendations.</p>

            {loading ? (
                <p>Loading metrics...</p>
            ) : books.length === 0 ? (
                <p>No metrics available. Please select some books first.</p>
            ) : (
                <div style={{ overflowX: 'auto', background: 'rgba(255,255,255,0.05)', borderRadius: '15px', padding: '1rem' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                        <thead>
                            <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', color: 'var(--accent-color)' }}>
                                <th style={{ padding: '1rem' }}>Book Cover</th>
                                <th style={{ padding: '1rem' }}>Title & Author</th>
                                <th style={{ padding: '1rem' }}>SKOR</th>
                                <th style={{ padding: '1rem' }}>CF/SVD</th>
                                <th style={{ padding: '1rem' }}>POP</th>
                                <th style={{ padding: '1rem' }}>TAG</th>
                                <th style={{ padding: '1rem' }}>ORTAK TAG&apos;LER</th>
                            </tr>
                        </thead>
                        <tbody>
                            {books.map((book, idx) => (
                                <tr key={book.ISBN} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)', background: idx % 2 === 0 ? 'rgba(255,255,255,0.02)' : 'transparent' }}>
                                    <td style={{ padding: '1rem' }}>
                                        <img src={book.image_url} alt={book.title} style={{ width: '50px', height: '75px', objectFit: 'cover', borderRadius: '5px' }} />
                                    </td>
                                    <td style={{ padding: '1rem' }}>
                                        <div style={{ fontWeight: 'bold', marginBottom: '0.2rem' }}>{book.title}</div>
                                        <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{book.authors}</div>
                                    </td>
                                    <td style={{ padding: '1rem', fontWeight: 'bold', color: 'var(--accent-hover)' }}>{book.metrics.total_score.toFixed(2)}</td>
                                    <td style={{ padding: '1rem' }}>{book.metrics.cf_score.toFixed(2)}</td>
                                    <td style={{ padding: '1rem' }}>{book.metrics.pop_score.toFixed(2)}</td>
                                    <td style={{ padding: '1rem' }}>{book.metrics.tag_score.toFixed(2)}</td>
                                    <td style={{ padding: '1rem', fontSize: '0.85rem', maxWidth: '200px' }}>
                                        {book.metrics.shared_tags.length > 0 ? book.metrics.shared_tags.join(', ') : '-'}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}
