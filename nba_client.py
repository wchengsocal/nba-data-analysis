"""
Data fetching layer — wraps nba_api with diskcache to avoid rate limits.
All public functions return plain dicts or pandas DataFrames.
"""
import time
import diskcache
import pandas as pd
from nba_api.stats.endpoints import (
    playercareerstats,
    playershotchartdetail,
    leaguestandingsv3,
    teamdashboardbyyearoveryear,
    commonplayerinfo,
    commonteamroster,
    leaguedashteamstats,
)
from nba_api.stats.static import players, teams

CACHE = diskcache.Cache("./.cache")
RATE_LIMIT_DELAY = 0.6  # seconds between API calls


def _cached(key: str, fn, ttl: int = 3600):
    if key in CACHE:
        return CACHE[key]
    time.sleep(RATE_LIMIT_DELAY)
    result = fn()
    CACHE.set(key, result, expire=ttl)
    return result


# ---------------------------------------------------------------------------
# Players
# ---------------------------------------------------------------------------

def search_players(query: str) -> list[dict]:
    all_players = players.get_players()
    q = query.lower()
    return [p for p in all_players if q in p["full_name"].lower()][:20]


def get_player_info(player_id: int) -> dict:
    key = f"player_info_{player_id}"
    def fetch():
        info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
        df = info.get_data_frames()[0]
        row = df.iloc[0]
        return {
            "id": player_id,
            "name": row["DISPLAY_FIRST_LAST"],
            "team": row["TEAM_NAME"],
            "position": row["POSITION"],
            "height": row["HEIGHT"],
            "weight": row["WEIGHT"],
            "birthdate": row["BIRTHDATE"],
            "draft_year": row["DRAFT_YEAR"],
            "country": row["COUNTRY"],
        }
    return _cached(key, fetch, ttl=86400)


def get_player_career_stats(player_id: int) -> list[dict]:
    key = f"career_stats_{player_id}"
    def fetch():
        career = playercareerstats.PlayerCareerStats(player_id=player_id)
        df = career.get_data_frames()[0]
        cols = [
            "SEASON_ID", "TEAM_ABBREVIATION", "GP", "GS", "MIN",
            "PTS", "REB", "AST", "STL", "BLK", "TOV", "FG_PCT",
            "FG3_PCT", "FT_PCT", "PLUS_MINUS",
        ]
        df = df[cols].copy()
        df["PTS_PER_G"] = (df["PTS"] / df["GP"]).round(1)
        df["REB_PER_G"] = (df["REB"] / df["GP"]).round(1)
        df["AST_PER_G"] = (df["AST"] / df["GP"]).round(1)
        return df.to_dict(orient="records")
    return _cached(key, fetch, ttl=3600)


def get_shot_chart(player_id: int, season: str = "2023-24") -> list[dict]:
    key = f"shotchart_{player_id}_{season}"
    def fetch():
        sc = playershotchartdetail.PlayerShotChartDetail(
            player_id=player_id,
            team_id=0,
            season_nullable=season,
            season_type_all_star="Regular Season",
        )
        df = sc.get_data_frames()[0]
        cols = ["LOC_X", "LOC_Y", "SHOT_MADE_FLAG", "SHOT_TYPE",
                "SHOT_ZONE_BASIC", "SHOT_ZONE_AREA", "SHOT_DISTANCE"]
        return df[cols].to_dict(orient="records")
    return _cached(key, fetch, ttl=3600)


# ---------------------------------------------------------------------------
# Teams
# ---------------------------------------------------------------------------

def get_standings(season: str = "2023-24") -> list[dict]:
    key = f"standings_{season}"
    def fetch():
        st = leaguestandingsv3.LeagueStandingsV3(season=season)
        df = st.get_data_frames()[0]
        cols = [
            "TeamID", "TeamName", "Conference", "Division",
            "WINS", "LOSSES", "WinPCT", "HOME", "ROAD",
            "L10", "strCurrentStreak", "PointsPG", "OppPointsPG",
        ]
        available = [c for c in cols if c in df.columns]
        return df[available].to_dict(orient="records")
    return _cached(key, fetch, ttl=1800)


def get_team_trends(team_id: int) -> list[dict]:
    key = f"team_trends_{team_id}"
    def fetch():
        dash = teamdashboardbyyearoveryear.TeamDashboardByYearOverYear(
            team_id=team_id,
            per_mode_simple="PerGame",
        )
        df = dash.get_data_frames()[1]
        cols = [
            "GROUP_VALUE", "GP", "W", "L", "W_PCT",
            "PTS", "OPP_PTS", "PLUS_MINUS",
        ]
        available = [c for c in cols if c in df.columns]
        return df[available].to_dict(orient="records")
    return _cached(key, fetch, ttl=3600)


def search_teams(query: str) -> list[dict]:
    all_teams = teams.get_teams()
    q = query.lower()
    return [t for t in all_teams if q in t["full_name"].lower() or q in t["abbreviation"].lower()]
