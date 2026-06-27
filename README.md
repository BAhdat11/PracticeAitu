# 🎮 Esports Federation KZ — Tournament Registration System

**Developed by:** Bagdat Ayagan | SE-2407 | AITU | Industrial Practice 2026

---

## Project Structure

```
esports_project/
├── backend/              # Node.js + Express REST API
│   ├── models/
│   │   ├── Tournament.js # MongoDB tournament schema
│   │   └── Team.js       # MongoDB team schema
│   ├── routes/
│   │   ├── tournaments.js # /api/tournaments endpoints
│   │   └── teams.js       # /api/teams endpoints
│   ├── server.js          # Express app entry point
│   ├── Dockerfile         # Backend container
│   └── .env               # Environment variables
├── bot/                  # Python Telegram Bot
│   ├── bot.py             # Bot logic (connects to same MongoDB)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/             # HTML/CSS/JS frontend
│   └── index.html
├── docker-compose.yml    # Runs everything together
└── .env                  # BOT_TOKEN
```

---

## Tech Stack

| Layer    | Technology                        |
|----------|-----------------------------------|
| Backend  | Node.js 18, Express.js            |
| Database | MongoDB 6 (via Mongoose ODM)      |
| Frontend | HTML5, CSS3, Vanilla JavaScript   |
| Bot      | Python 3.11, python-telegram-bot  |
| DevOps   | Docker, Docker Compose            |

---

## REST API Endpoints

| Method | Endpoint                        | Description                  |
|--------|---------------------------------|------------------------------|
| GET    | /api/tournaments                | Get all tournaments           |
| GET    | /api/tournaments/:id            | Get tournament with team count|
| POST   | /api/tournaments                | Create tournament             |
| DELETE | /api/tournaments/:id            | Delete tournament + its teams |
| GET    | /api/tournaments/stats/summary  | Dashboard statistics          |
| GET    | /api/teams                      | Get all teams (filter by tour)|
| POST   | /api/teams                      | Register a team               |
| DELETE | /api/teams/:id                  | Remove a team                 |
| GET    | /api/health                     | Server health check           |

---

## How to Run

### Option 1: Docker (recommended)

```bash
# 1. Add your Telegram bot token to .env
echo "BOT_TOKEN=your_token_here" > .env

# 2. Start everything
docker-compose up --build

# 3. Open the website
# http://localhost:3000
```

### Option 2: Manual

```bash
# Terminal 1 — start MongoDB
mongod

# Terminal 2 — start backend
cd backend
npm install
npm start

# Terminal 3 — start Telegram bot
cd bot
pip install -r requirements.txt
# Edit .env: set MONGO_URI=mongodb://localhost:27017/esports
python bot.py

# Open frontend/index.html in browser
```

---

## Telegram Bot Commands

- `/start` — main menu
- `🏆 Register Team` — multi-step team registration
- `📋 View Tournaments` — see all open tournaments
- `📊 My Registrations` — see your registered teams

**Bot and website share the same MongoDB database.**  
Teams registered via Telegram appear in the web dashboard with source "🤖 Telegram".

---

## Getting a Telegram Bot Token

1. Open [@BotFather](https://t.me/BotFather) in Telegram
2. Send `/newbot`
3. Follow instructions, copy the token
4. Paste it in `.env` as `BOT_TOKEN=...`
