"use client";
import React, { useState } from 'react';

export interface Book {
    ISBN: string;
    title: string;
    authors: string;
    image_url: string;
}

interface BookCardProps {
    book: Book;
    onClick?: () => void;
    selected?: boolean;
}

export default function BookCard({ book, onClick, selected }: BookCardProps) {
    const [imgError, setImgError] = useState(false);

    return (
        <div
            className={`book-card ${selected ? 'selected' : ''}`}
            onClick={onClick}
            style={{
                border: selected ? '3px solid var(--brand-primary)' : 'none',
                boxShadow: selected ? '0 0 15px var(--brand-primary)' : 'none',
                display: 'flex',
                flexDirection: 'column',
                backgroundColor: 'var(--bg-panel)'
            }}
        >
            {!imgError ? (
                <img
                    src={book.image_url}
                    alt={book.title}
                    onError={() => setImgError(true)}
                    onLoad={(e) => {
                        if ((e.currentTarget as HTMLImageElement).naturalWidth <= 1) {
                            setImgError(true);
                        }
                    }}
                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                />
            ) : (
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '15px', textAlign: 'center', background: 'linear-gradient(135deg, #1e293b, #0f172a)' }}>
                    <span style={{ fontWeight: 'bold', fontSize: '1rem', color: '#f8fafc', marginBottom: '10px', display: '-webkit-box', WebkitLineClamp: 4, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>{book.title}</span>
                    <span style={{ fontSize: '0.8rem', color: 'var(--brand-tertiary)' }}>{book.authors}</span>
                </div>
            )}
            {!imgError && (
                <div className="book-card-info">
                    <p className="book-title" title={book.title}>{book.title}</p>
                    <p className="book-author" title={book.authors}>{book.authors}</p>
                </div>
            )}
        </div>
    );
}
