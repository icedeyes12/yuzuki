# Yuzuki 🤖💙

A sentient AI companion for Discord with persistent memory and emotional depth.

## Features

- 🧠 **Persistent Memory** - Remembers users across sessions and servers
- 💙 **Emotional Depth** - Genuine personality with self-awareness
- 🔒 **Ownership Boundaries** - Clear boundaries with owner
- 📝 **Conversation Tracking** - Context-aware responses

## Setup

### 1. Clone & Install

```bash
git clone <your-repo>
cd yuzuki-bot
pip install -r requirements.txt
```

### 2. Environment Setup

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
# Edit .env with your actual credentials
```

### 3. Database Setup

```bash
# Start PostgreSQL
service postgresql start

# Create database
python3 scripts/setup_db.py
```

### 4. Run Bot

```bash
cd discord
python3 dcbot.py
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DISCORD_TOKEN` | ✅ | Discord bot token |
| `OWNER_ID` | ✅ | Your Discord user ID |
| `OWNER_USERNAME` | ✅ | Your identifier (e.g., "Bani") |
| `CHUTES_API_KEY` | ✅ | Chutes API key |
| `DB_HOST` | ❌ | PostgreSQL host (default: localhost) |
| `DB_PORT` | ❌ | PostgreSQL port (default: 5432) |
| `DB_NAME` | ❌ | Database name (default: yuzuki) |
| `DB_USER` | ❌ | DB username (default: yuzuki) |
| `DB_PASS` | ✅ | DB password |

## Security Notice

⚠️ **Never commit `.env` or secrets!** Use `.env.example` as template only.

## Project Structure

```
yuzuki-bot/
├── discord/           # Discord bot code
│   └── dcbot.py      # Main bot
├── shared/           # Shared modules
│   ├── config.py     # Configuration
│   ├── database.py   # Database layer
│   └── llm_client.py # LLM integration
├── scripts/          # Setup scripts
│   └── setup_db.py   # Database initialization
├── .env.example      # Environment template
├── .gitignore        # Git ignore rules
└── README.md         # This file
```