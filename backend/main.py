from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import users, books, forum
from oneri import recommender

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bibulous API")

# Ensure recommendation engine loads data on startup
@app.on_event("startup")
def startup_event():
    print("Initializing recommendataion engine...")
    recommender.load_data()
    recommender.train_model()
    print("Server ready.")

# Setup CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Since it's a dev project
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users, prefix="/api/users", tags=["Users"])
app.include_router(books, prefix="/api/books", tags=["Books"])
app.include_router(forum, prefix="/api/forum", tags=["Forum"])

@app.get("/")
def root():
    return {"message": "Bibulous Recommendation API"}
