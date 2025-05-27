# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Criar aplicação FastAPI
app = FastAPI(
    title="Ohara - Manga Reader API",
    description="API para leitor de mangás local (Projeto ES2)",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "🏴‍☠️ Ohara - Manga Reader API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/api/test")
async def test_endpoint():
    return {
        "message": "🎉 API Ohara funcionando!",
        "backend": "FastAPI ✅",
        "status": "OK"
    }

@app.get("/api/library")
async def get_library():
    return {
        "mangas": [
            {"id": "one-piece", "title": "One Piece", "chapter_count": 1095},
            {"id": "naruto", "title": "Naruto", "chapter_count": 700},
            {"id": "attack-on-titan", "title": "Attack on Titan", "chapter_count": 139}
        ],
        "total_mangas": 3
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)