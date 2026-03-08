"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import BookCard, { Book } from '@/components/BookCard';

export default function Onboarding() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [userId, setUserId] = useState<number | null>(null);
  const [books, setBooks] = useState<Book[]>([]);
  const [selectedIsbns, setSelectedIsbns] = useState<Set<string>>(new Set());
  const [page, setPage] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);

  // Form state
  const [name, setName] = useState('');
  const [surname, setSurname] = useState('');
  const [country, setCountry] = useState('');
  const [language, setLanguage] = useState('');

  const registerUser = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch('http://localhost:8000/api/users/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, surname, country, language })
      });
      const data = await res.json();
      if (data.id) {
        setUserId(data.id);
        localStorage.setItem('userId', data.id.toString());
        localStorage.setItem('userName', data.name);
        setStep(2);
        fetchBooks(0);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const fetchBooks = async (pageNum: number = 0) => {
    try {
      const res = await fetch(`http://localhost:8000/api/books/top?skip=${pageNum * 50}&limit=50`);
      const data = await res.json();
      if (pageNum === 0) {
        setBooks(data);
      } else {
        setBooks(prev => [...prev, ...data]);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const loadMore = () => {
    const nextPage = page + 1;
    setPage(nextPage);
    fetchBooks(nextPage);
  };

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!searchQuery.trim()) {
      setIsSearching(false);
      setPage(0);
      fetchBooks(0);
      return;
    }
    setIsSearching(true);
    try {
      const res = await fetch(`http://localhost:8000/api/books/search?q=${encodeURIComponent(searchQuery)}&n=50`);
      const data = await res.json();
      setBooks(data);
    } catch (err) {
      console.error(err);
    }
  };

  const toggleBook = (isbn: string) => {
    const next = new Set(selectedIsbns);
    if (next.has(isbn)) next.delete(isbn);
    else next.add(isbn);
    setSelectedIsbns(next);
  };

  const finishOnboarding = async () => {
    if (selectedIsbns.size < 5) {
      alert("Lütfen en az 5 kitap seçin (Please select at least 5 books).");
      return;
    }

    // Save selections
    for (const isbn of Array.from(selectedIsbns)) {
      await fetch(`http://localhost:8000/api/users/${userId}/liked_books`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ isbn })
      });
    }

    router.push('/home');
  };

  return (
    <div style={{ padding: '2rem 0', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <h1 className="heading-hero" style={{ marginBottom: '1rem', textAlign: 'center' }}>BIBULOUS</h1>
      <p style={{ color: 'var(--text-muted)', marginBottom: '3rem', fontSize: '1.2rem' }}>
        Yeni Nesil Sosyal Kitap Platformu ve Akıllı Keşif Rehberi
      </p>

      {step === 1 && (
        <form onSubmit={registerUser} className="glass" style={{ padding: '2rem', width: '100%', maxWidth: '400px', display: 'flex', flexDirection: 'column', gap: '15px' }}>
          <h2>Kayıt Ol (Register)</h2>
          <input className="input-glass" placeholder="İsim (Name)" value={name} onChange={e => setName(e.target.value)} required />
          <input className="input-glass" placeholder="Soyisim (Surname)" value={surname} onChange={e => setSurname(e.target.value)} required />
          <input className="input-glass" placeholder="Ülke (Country)" value={country} onChange={e => setCountry(e.target.value)} required />
          <input className="input-glass" placeholder="Tercih Edilen Dil (Language)" value={language} onChange={e => setLanguage(e.target.value)} required />
          <button type="submit" className="btn-primary" style={{ marginTop: '10px' }}>Devam Et</button>
        </form>
      )}

      {step === 2 && (
        <div style={{ width: '100%' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '20px' }}>
            <h2>Beğendiğin Türleri Anlamamız İçin Seç: ({selectedIsbns.size}/5)</h2>

            <form onSubmit={handleSearch} style={{ display: 'flex', gap: '10px' }}>
              <input
                type="text"
                className="input-glass"
                placeholder="Kitap veya Yazar Ara..."
                value={searchQuery}
                onChange={e => {
                  setSearchQuery(e.target.value);
                  if (e.target.value === '') {
                    setIsSearching(false);
                    setPage(0);
                    fetchBooks(0);
                  }
                }}
                style={{ width: '300px', padding: '10px' }}
              />
              <button type="submit" className="btn-primary" style={{ padding: '10px 20px' }}>Ara (Search)</button>
            </form>

            <button onClick={finishOnboarding} className="btn-primary" disabled={selectedIsbns.size < 5} style={{ opacity: selectedIsbns.size < 5 ? 0.5 : 1 }}>
              Bibulous'a Katıl
            </button>
          </div>

          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '20px', justifyContent: 'center', marginBottom: '40px' }}>
            {books.map(b => (
              <BookCard
                key={b.ISBN}
                book={b}
                selected={selectedIsbns.has(b.ISBN)}
                onClick={() => toggleBook(b.ISBN)}
              />
            ))}
          </div>

          {!isSearching && (
            <div style={{ display: 'flex', justifyContent: 'center', paddingBottom: '40px' }}>
              <button onClick={loadMore} className="btn-primary" style={{ padding: '12px 40px', fontSize: '1.1rem' }}>
                Daha Fazla Kitap Yükle (Load More)
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
