from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.players import router as players_router
from api.teams import router as teams_router
from api.compare import router as compare_router

app = FastAPI(
    title="NBA Analytics API",
    description="Player stats, shot charts, team trends, and historical comparisons",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(players_router, prefix="/api/players", tags=["Players"])
app.include_router(teams_router, prefix="/api/teams", tags=["Teams"])
app.include_router(compare_router, prefix="/api/compare", tags=["Compare"])


@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}
