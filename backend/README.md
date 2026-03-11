# Bibulous Backend

FastAPI tabanlı REST API ve akıllı kitap öneri motoru.

## Bağımlılıklar

```bash
pip install -r requirements.txt
```

| Paket | Kullanım |
|-------|----------|
| `fastapi` | REST API framework |
| `uvicorn` | ASGI sunucu |
| `sqlalchemy` | SQLite ORM |
| `pandas` / `numpy` | Veri işleme, Collaborative Filtering |
| `pydantic` | Şema ve veri doğrulama |
| `python-dotenv` | Ortam değişkenleri |

## Kurulum

```bash
# 1. Sanal ortam oluştur
python -m venv venv

# 2. Aktif et
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# macOS / Linux:
source venv/bin/activate

# 3. Bağımlılıkları kur
pip install -r requirements.txt

# 4. Sunucuyu başlat
uvicorn main:app --port 8000 --reload
```

API: `http://localhost:8000`  
Swagger: `http://localhost:8000/docs`

## Dosya Yapısı

```
backend/
├── main.py           # Uygulama başlatma, CORS, startup eventi
├── oneri.py          # RecommendationEngine sınıfı (CF + popülerlik + tag bazlı)
├── database.py       # SQLite bağlantısı (SQLAlchemy engine)
├── models.py         # ORM modelleri (User, LikedBook, Comment)
├── schemas.py        # Pydantic şemaları
├── requirements.txt  # Python bağımlılıkları
└── routers/
    ├── books.py      # /api/books — öneri, detay, arama, yorum endpoint'leri
    ├── users.py      # /api/users — kayıt, beğeni endpoint'leri
    └── forum.py      # /api/forum — forum gönderi endpoint'leri
```

## Öneri Motoru (`oneri.py`)

`RecommendationEngine` sınıfı startup'ta otomatik yüklenir ve şu yöntemleri sağlar:

- **`get_recommendations_cf`** — Kullanıcı tabanlı işbirlikçi filtreleme
- **`get_recommendations_with_metrics`** — CF + popülerlik + tag benzerlik skorları ile metrikli öneri
- **`get_recommendations_same_author`** — Aynı yazarın diğer kitapları
- **`get_recommendations_similar_title`** — Başlık benzerliğine göre öneriler
- **`search_books`** — Başlık/yazar tam metin arama

## Veri Setleri

```
archives/       # BX-Books (Book-Crossing)
├── Books.csv
├── Ratings.csv
└── Users.csv

datas/          # Goodreads (tag verisi)
├── books.csv
├── tags.csv
└── book_tags.csv
```
