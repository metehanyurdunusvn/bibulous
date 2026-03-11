# Bibulous — Akıllı Kitap Keşif Platformu

Bibulous, Next.js ve FastAPI ile geliştirilmiş yapay zeka destekli bir sosyal kitap öneri platformudur. Kullanıcıların kitap keşfetmesini, puanlamasını ve kişiselleştirilmiş öneriler almasını sağlar.

## Proje Yapısı

```
bibulous/
├── backend/          # FastAPI REST API + Öneri Motoru
├── frontend/         # Next.js kullanıcı arayüzü
├── archives/         # BX-Books veri seti (Books.csv, Ratings.csv, Users.csv)
└── datas/            # Goodreads veri seti (books.csv, tags.csv, book_tags.csv)
```

## Özellikler

- **Kişiselleştirilmiş Onboarding**: Kullanıcı 5+ kitap seçerek profilini oluşturur.
- **Top Picks**: Kullanıcı tabanlı işbirlikçi filtreleme (Collaborative Filtering) ile kişiye özel öneri carousel'ları.
- **Yazar Bazlı Öneriler**: Beğenilen yazarların diğer kitapları.
- **Benzer Temalar**: Başlık benzerliğine dayalı seri/tema önerileri.
- **Öneri Metrikleri**: CF skoru, popülerlik skoru ve tag benzerlik skoru görselleştirmesi.
- **Forum**: Kitaplar üzerine yorum ve tartışma platformu.
- **Kitap Detay**: Her kitap için yorum, benzer kitaplar ve kapak görseli.
- **Carousel Navigasyon**: Sol/sağ ok butonları ve özel yatay scroll bar.
- **Dark Mode UI**: Glassmorphism tasarım, indigo/mor gradient, Outfit font.

## Gereksinimler

| Teknoloji | Minimum Versiyon |
|-----------|-----------------|
| Node.js   | 18+             |
| Python    | 3.8+            |
| npm       | 9+              |

## Hızlı Başlangıç

### 1. Backend (FastAPI + Öneri Motoru)

```bash
cd backend

# Sanal ortam oluştur ve aktif et
python -m venv venv

# Windows PowerShell
.\venv\Scripts\Activate.ps1

# macOS / Linux
source venv/bin/activate

# Bağımlılıkları kur
pip install -r requirements.txt

# Sunucuyu başlat
uvicorn main:app --port 8000 --reload
```

Backend API: `http://localhost:8000`  
Swagger dokümantasyon: `http://localhost:8000/docs`

### 2. Frontend (Next.js)

Yeni bir terminal penceresinde:

```bash
cd frontend
npm install
npm run dev
```

Uygulama: `http://localhost:3000`

## Teknoloji Yığını

### Backend
- **FastAPI** — REST API framework
- **Uvicorn** — ASGI sunucu
- **SQLAlchemy** — SQLite ORM (kullanıcılar, yorumlar)
- **Pandas / NumPy** — veri filtreleme ve işbirlikçi filtreleme
- **Pydantic** — veri doğrulama ve şemalar

### Frontend
- **Next.js 16** (App Router, TypeScript)
- **React 19**
- **Vanilla CSS** — özel tasarım sistemi (`globals.css`)
- **Outfit** — Google Fonts tipografi
