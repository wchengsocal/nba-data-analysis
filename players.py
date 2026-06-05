from fastapi import APIRouter, Query, HTTPException
from data.nba_client import (
    search_players,
    get_player_info,
    get_player_career_stats,
    get_shot_chart,
)
from analysis.shot_chart import compute_zone_efficiency, compute_hexbins

router = APIRouter()


@router.get("/search")
def player_search(q: str = Query(..., min_length=2)):
    results = search_players(q)
    if not results:
        return {"players": []}
    return {"players": results}


@router.get("/{player_id}")
def player_info(player_id: int):
    try:
        return get_player_info(player_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{player_id}/stats")
def player_stats(player_id: int):
    try:
        stats = get_player_career_stats(player_id)
        return {"player_id": player_id, "seasons": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{player_id}/shotchart")
def shot_chart(
    player_id: int,
    season: str = Query("2023-24", regex=r"^\d{4}-\d{2}$"),
):
    try:
        shots = get_shot_chart(player_id, season)
        zones = compute_zone_efficiency(shots)
        hexbins = compute_hexbins(shots)
        return {
            "player_id": player_id,
            "season": season,
            "total_shots": len(shots),
            "zones": zones,
            "hexbins": hexbins,
            "raw": shots,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
