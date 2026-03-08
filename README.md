# Bibulous - Smart Book Discovery Platform

Bibulous is an AI-powered book recommendation platform built with Next.js and FastAPI. It offers a modern, sleek interface for users to discover books, rate them, and receive highly personalized "Top Picks" based on Collaborative Filtering algorithm using their onboarding selections.

## Project Structure

This repository is structured as a monorepo consisting of two main parts:

- **/frontend**: A Next.js application built with React and Tailwind CSS featuring a global dark-mode theme, glassmorphism UI principles, and dynamic recommendation carousels.
- **/backend**: A fast, asynchronous Python API built with FastAPI that handles user data, SQLite database operations, and houses the Pandas-driven Collaborative Filtering recommendation engine.

## Prerequisites

To run this project locally, ensure you have the following installed on your machine:
- **Node.js** (v18 or higher)
- **npm** or **yarn**
- **Python** (3.8 or higher)
- **Git**

## Quick Start Guide

### 1. Launching the Backend (API & Recommendation Engine)

The backend must be running for the frontend to fetch books and user recommendations.

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install the required Python dependencies:
   ```bash
   pip install fastapi uvicorn sqlalchemy pandas scikit-learn
   ```
   *(Note: For more details, refer to `backend/README.md`)*
4. Start the Uvicorn server:
   ```bash
   uvicorn main:app --port 8000 --reload
   ```
   The backend API will now be running at `http://localhost:8000`.

### 2. Launching the Frontend (User Interface)

Open a new terminal window to keep the backend running, then:

1. Navigate to the frontend directory from the project root:
   ```bash
   cd frontend
   ```
2. Install the Node dependencies:
   ```bash
   npm install
   ```
3. Run the Next.js development server:
   ```bash
   npm run dev
   ```
4. Open your browser and visit: `http://localhost:3000`

## Features

- **Onboarding Personalization**: Select 5 starter books and the underlying engine uses User-Based Collaborative Filtering to map your tastes to other readers and curate your feed.
- **Dynamic "Top Picks"**: Real-time horizontally scrolling catalogs of recommendations catered to your user profile.
- **Similar Authors & Titles**: Browse contextually accurate "You might also like" recommendations directly inside a book's detail page.
- **Dark Mode UI**: Vibrant aesthetic featuring custom scrolling and smooth gradient layouts.

For more detailed information, please see the specific README files in the `backend/` and `frontend/` directories.
