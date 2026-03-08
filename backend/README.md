# Bibulous Backend

This is the FastAPI backend serving the Bibulous smart book discovery engine. It includes a User-Based Collaborative Filtering algorithm utilizing Pandas to deliver highly personalized book recommendations.

## Requirements

Before starting, ensure you have Python 3.8+ installed. 

This project uses:
- `FastAPI` 
- `Uvicorn` for ASGI server hosting
- `SQLAlchemy` for handling SQLite User and Ratings Data
- `Pandas` and `Numpy` for recommendation dataset generation and filtering
- `Scikit-learn` for similarity scores

## Installation

We strictly recommend using a virtual environment.

1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
2. Activate it:
   - **Windows PowerShell**: `.\venv\Scripts\Activate.ps1`
   - **Windows CMD**: `.\venv\Scripts\activate.bat`
   - **macOS / Linux**: `source venv/bin/activate`

3. Install the specific backend requirements:
   ```bash
   # If a requirements.txt exists:
   pip install -r requirements.txt
   
   # Or install packages directly if no file exists:
   pip install fastapi uvicorn sqlalchemy pandas numpy scikit-learn
   ```

## Starting the Server

The application server uses Uvicorn. To spin it up locally with auto-reloading:

```bash
uvicorn main:app --port 8000 --reload
```

## Structure Overview

- `main.py`: Bootstraps the application, CORS config, and triggers the `oneri.py` Collaborative Filtering train sequence on startup.
- `oneri.py`: Pre-loads book statings and coordinates User-Based Collaborative filtering arrays against the `BX-Books` underlying data. 
- `routers/`: Directory containing endpoints for specific resources like `books.py` mapped to Next.js components.
- `database.py`: Handles persistent connectivity to the local `bibulous.db` SQL file.
- `models.py`: Defines database schemas mapping for reading history, users, comments.
