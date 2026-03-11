# Bibulous Frontend

Next.js 16 ile geliştirilmiş, dark-mode glassmorphism tasarımlı kitap keşif arayüzü.

## Kurulum

```bash
npm install
npm run dev
```

Uygulama: `http://localhost:3000`

> Backend'in `http://localhost:8000` adresinde çalışıyor olması gerekir.

## Teknoloji

- **Next.js 16** — App Router, TypeScript
- **React 19**
- **Vanilla CSS** — `src/app/globals.css` içinde özel tasarım sistemi
- **Outfit** — Google Fonts

## Sayfa Yapısı

```
src/app/
├── page.tsx          # Onboarding — kayıt + kitap seçimi
├── layout.tsx        # Global layout ve metadata
├── globals.css       # Tasarım sistemi (renk değişkenleri, glassmorphism, carousel)
├── home/             # Ana sayfa — kişiselleştirilmiş öneri carousel'ları
├── book/[isbn]/      # Kitap detay sayfası
├── search/           # Kitap arama
├── forum/            # Forum gönderileri
└── metrics/          # Öneri metrikleri görselleştirmesi

src/components/
├── BookCard.tsx      # Kitap kartı bileşeni
└── Navbar.tsx        # Navigasyon çubuğu
```

## Tasarım Sistemi

`globals.css` içinde tanımlı CSS değişkenleri:

| Değişken | Değer | Kullanım |
|----------|-------|----------|
| `--bg-base` | `#0a0f1c` | Sayfa arka planı |
| `--brand-primary` | `#6366f1` | İndigo — buton, vurgu |
| `--brand-secondary` | `#a855f7` | Mor — gradient |
| `--brand-tertiary` | `#0ea5e9` | Gökyüzü mavisi — hover |

## Build

```bash
npm run build
npm run start
```
