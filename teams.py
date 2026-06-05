from fastapi import APIRouter, Query, HTTPException
from data.nba_client import get_standings, get_team_trends, search_teams

router = APIRouter()


@router.get("/search")
def team_search(q: str = Query(..., min_length=2)):
    return {"teams": search_teams(q)}


@router.get("/standings")
def standings(season: str = Query("2023-24", regex=r"^\d{4}-\d{2}$")):
    try:
        data = get_standings(season)
        east = [t for t in data if t.get("Conference") == "East"]
        west = [t for t in data if t.get("Conference") == "West"]
        east.sort(key=lambda t: float(t.get("WinPCT", 0)), reverse=True)
        west.sort(key=lambda t: float(t.get("WinPCT", 0)), reverse=True)
        return {"season": season, "east": east, "west": west}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{team_id}/trends")
def team_trends(team_id: int):
    try:
        data = get_team_trends(team_id)
        return {"team_id": team_id, "seasons": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
