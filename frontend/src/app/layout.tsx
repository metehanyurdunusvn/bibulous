import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Bibulous - Smart Book Discovery',
  description: 'Yeni Nesil Sosyal Kitap Platformu ve Akıllı Keşif Rehberi',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <main className="app-container" style={{ padding: '2rem 5%', maxWidth: '1400px', margin: '0 auto' }}>
          {children}
        </main>
      </body>
    </html>
  );
}
