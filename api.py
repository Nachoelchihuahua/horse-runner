from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {
        "game": "Horse Runner",
        "status": "ready",
        "message": "API du jeu disponible"
    }

@app.get("/score")
def score():
    return {
        "best_score": 0
    }