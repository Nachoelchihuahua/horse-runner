# Horse Runner 🐴

An infinite side-scrolling runner game featuring a pixel-art horse. Jump over ground obstacles and duck under aerial ones — how long can you survive?

**Play it now:** https://nachoelchihuahua.github.io/horse-runner/

---

## Gameplay

- The horse runs automatically. Speed increases as your score climbs.
- **Jump** over red ground obstacles.
- **Duck** under blue aerial obstacles.
- Your best score is saved locally between sessions.

### Controls

| Action | Keyboard | Mobile |
|--------|----------|--------|
| Jump | `Space` or `↑` | Tap upper screen |
| Duck | `↓` (hold) | Tap & hold lower screen |
| Restart | `Space` or `Enter` | Tap anywhere |

---

## Versions

### Browser (HTML5)
Open `index.html` directly in any modern browser — no install needed. Also deployed on GitHub Pages.

### Desktop (Python / Pygame)

**Requirements:** Python 3.11+, [uv](https://github.com/astral-sh/uv)

```bash
uv sync
uv run python main.py
```

### API (FastAPI)

A minimal REST API for score tracking:

```bash
uv run uvicorn api:app --reload
```

Endpoints:
- `GET /` — health check
- `GET /score` — returns the best score

### Docker

```bash
docker build -t horse-runner .
docker run -p 8000:8000 horse-runner
```

---

## Tech

- **Browser version:** vanilla HTML5 Canvas + Web Audio API (no dependencies)
- **Desktop version:** Python + Pygame
- **API:** FastAPI + Uvicorn
- **Deploy:** GitHub Pages (browser version)
