import Link from 'next/link';

export default function Navbar() {
    return (
        <nav style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem 0', marginBottom: '2rem', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
            <Link href="/home" className="heading-hero" style={{ fontSize: '2rem' }}>BIBULOUS</Link>
            <div style={{ display: 'flex', gap: '20px', fontWeight: '500' }}>
                <Link href="/home" style={{ color: 'var(--text-main)', transition: 'color 0.3s' }}>Home</Link>
                <Link href="/search" style={{ color: 'var(--text-main)', transition: 'color 0.3s' }}>Search</Link>
                <Link href="/forum" style={{ color: 'var(--text-main)', transition: 'color 0.3s' }}>Forum</Link>
            </div>
        </nav>
    );
}
