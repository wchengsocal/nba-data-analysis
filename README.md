# 🏀 NBA Analytics Dashboard

A full-stack NBA data analysis platform featuring player performance tracking, team standings, shot chart efficiency, and historical comparisons — powered by a Python/FastAPI backend and React frontend.

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green?style=flat-square&logo=fastapi)
![React](https://img.shields.io/badge/React-18+-61DAFB?style=flat-square&logo=react)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

---

## Features

- **Player Stats & Performance** — career trends, per-game/per-36/advanced metrics, season-over-season comparisons
- **Team Standings & Trends** — conference tables, win streaks, offensive/defensive ratings over time
- **Shot Chart Efficiency** — hexbin shot maps with FG% by zone, hot/cold zone overlays
- **Historical Comparisons** — compare any two players or seasons side-by-side with radar charts and percentile ranks

## Project Structure

```
nba-analytics/
├── backend/             # FastAPI Python backend
│   ├── api/             # Route handlers
│   ├── analysis/        # Core analytics logic
│   ├── data/            # Data fetching & caching (nba_api)
│   └── utils/           # Shared helpers
├── frontend/            # React + Recharts dashboard
│   └── src/
│       ├── components/  # Reusable UI components
│       ├── pages/       # Route-level pages
│       ├── hooks/       # Custom React hooks
│       └── utils/       # API client, formatters
├── notebooks/           # Jupyter EDA notebooks
└── .github/workflows/   # CI pipeline
```

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API docs available at `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Dashboard available at `http://localhost:5173`

### Jupyter Notebooks

```bash
pip install -r backend/requirements.txt jupyter
jupyter notebook notebooks/
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/players/search?q={name}` | Search players |
| GET | `/api/players/{id}/stats` | Career stats |
| GET | `/api/players/{id}/shotchart?season={season}` | Shot chart data |
| GET | `/api/teams/standings?season={season}` | League standings |
| GET | `/api/teams/{id}/trends` | Win/loss trends + ratings |
| GET | `/api/compare?player1={id}&player2={id}` | Head-to-head comparison |

## Data Source

All data is fetched via [`nba_api`](https://github.com/swar/nba_api), the unofficial NBA stats API wrapper. Data is cached locally with `diskcache` to avoid rate-limiting.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, pandas, numpy, nba_api |
| Visualization | matplotlib, seaborn (notebooks) |
| Frontend | React 18, Vite, Recharts, Tailwind CSS |
| Caching | diskcache (backend), React Query (frontend) |
| Testing | pytest (backend), Vitest (frontend) |
| CI | GitHub Actions |

## Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/shot-quality-model`)
3. Commit changes (`git commit -m 'Add expected FG% model'`)
4. Push and open a PR

## License

MIT
