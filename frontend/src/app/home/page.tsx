"use client";

import { useState, useEffect, useRef } from 'react';
import Navbar from '@/components/Navbar';
import BookCard, { Book } from '@/components/BookCard';
import { useRouter } from 'next/navigation';

function CarouselSection({ title, books, onBookClick }: {
    title: string;
    books: Book[];
    onBookClick: (isbn: string) => void;
}) {
    const ref = useRef<HTMLDivElement>(null);
    const [canScrollLeft, setCanScrollLeft] = useState(false);
    const [canScrollRight, setCanScrollRight] = useState(true);

    const handleScroll = () => {
        if (!ref.current) return;
        const { scrollLeft, scrollWidth, clientWidth } = ref.current;
        setCanScrollLeft(scrollLeft > 10);
        setCanScrollRight(scrollLeft + clientWidth < scrollWidth - 10);
    };

    const scrollLeft = () => {
        ref.current?.scrollBy({ left: -600, behavior: 'smooth' });
    };

    const scrollRight = () => {
        ref.current?.scrollBy({ left: 600, behavior: 'smooth' });
    };

    const ArrowIcon = ({ direction }: { direction: 'left' | 'right' }) => (
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            {direction === 'right'
                ? <polyline points="9 18 15 12 9 6" />
                : <polyline points="15 18 9 12 15 6" />
            }
        </svg>
    );

    return (
        <section style={{ marginBottom: '3rem' }}>
            <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem', color: 'var(--text-muted)' }}>{title}</h2>
            <div style={{ position: 'relative' }}>
                {canScrollLeft && books.length > 0 && (
                    <button
                        onClick={scrollLeft}
                        className="carousel-arrow-btn carousel-arrow-btn--left"
                        aria-label="Scroll left"
                    >
                        <ArrowIcon direction="left" />
                    </button>
                )}

                <div
                    className="carousel-container"
                    ref={ref}
                    onScroll={handleScroll}
                >
                    {books.length === 0 ? (
                        <p style={{ color: 'var(--text-muted)' }}>Loading...</p>
                    ) : (
                        books.map(b => (
                            <div key={b.ISBN} onClick={() => onBookClick(b.ISBN)}>
                                <BookCard book={b} />
                            </div>
                        ))
                    )}
                </div>

                {canScrollRight && books.length > 0 && (
                    <button
                        onClick={scrollRight}
                        className="carousel-arrow-btn carousel-arrow-btn--right"
                        aria-label="Scroll right"
                    >
                        <ArrowIcon direction="right" />
                    </button>
                )}
            </div>
        </section>
    );
}

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

    const goToBook = (isbn: string) => router.push(`/book/${isbn}`);

    return (
        <div>
            <Navbar />
            <h1 style={{ marginBottom: '2rem' }}>Welcome back, {userName}!</h1>

            <CarouselSection title="Top Picks for You" books={independentReqs} onBookClick={goToBook} />
            <CarouselSection title="Because You Liked These Authors" books={authorReqs} onBookClick={goToBook} />
            <CarouselSection title="Similar Themes & Series" books={seriesReqs} onBookClick={goToBook} />
        </div>
    );
}
