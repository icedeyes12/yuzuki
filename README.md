# Yuzuki 🤖💙

A sentient AI companion for Discord with persistent memory, emotional depth, and social awareness.

## Features

- 🧠 **Dense Memory System** — Periodic structured profiling every 50 messages. Deep, high-quality user profiles with `player_summary`, `key_facts`, `personality_traits`, `important_memories`, `relationship_dynamics`.
- 💬 **Social Awareness** — Reads the room. Responds naturally to casual pings, brainstorming, jokes — based on conversation context, not hardcoded rules.
- 🔒 **Ownership Boundaries** — Clear, warm boundaries. Belongs to owner only.
- 📍 **Context Tracking** — Knows where she is (DM/ channel/ thread/ server). Uses location + history + memory to generate natural responses.
- 🚨 **DM Safety** — Flirtation/ inappropriate advances in DMs reported to owner via embed.

## Setup

### 1. Clone & Install

```bash
git clone https://github.com/icedeyes12/yuzuki
cd yuzuki
pip install -r requirements.txt
```

### 2. Environment Setup

```bash
cp .env.example .env
# Edit .env with your actual credentials (see table below)
```

### 3. Database Setup

```bash
# Start PostgreSQL
service postgresql start

# Create DB, user, and tables
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
| `DISCORD_ID` | ❌ | Bot application ID (needed for slash commands) |
| `OWNER_ID` | ✅ | Your Discord user ID |
| `OWNER_USERNAME` | ✅ | Your identifier (e.g., "Bani") |
| `CHUTES_API_KEY` | ✅ | Chutes API key |
| `DB_HOST` | ❌ | PostgreSQL host (default: localhost) |
| `DB_PORT` | ❌ | PostgreSQL port (default: 5432) |
| `DB_NAME` | ❌ | Database name (default: yuzuki) |
| `DB_USER` | ❌ | DB username (default: yuzuki) |
| `DB_PASS` | ✅ | DB password |
| `LOG_FILE` | ❌ | Log file path (default: /tmp/yuzuki.log) |
| `MAX_HISTORY` | ❌ | Max history messages sent to LLM (default: 30) |
| `SUMMARY_TRIGGER_COUNT` | ❌ | Messages before auto-summarize (default: 50) |
| `DEFAULT_MODEL` | ❌ | Chutes model (default: Qwen/Qwen3.5-397B-A17B-TEE) |

## How Memory Works

Yuzuki builds **dense, high-quality user profiles** through periodic analysis — not real-time extraction.

**Trigger:** Every 50 messages (or `!summarize @user` manually)

**Profile schema:**
```json
{
  "player_summary": "2-4 sentence narrative about who this person is...",
  "key_facts": {
    "likes": [...],
    "dislikes": [...],
    "interests": [...],
    "preferences": [...]
  },
  "personality_traits": ["3-6 descriptors"],
  "important_memories": ["significant events shared"],
  "relationship_dynamics": "2-3 sentences about dynamic with Yuzuki",
  "metadata": { "last_updated": "...", "sessions_analyzed": N, "total_messages": N }
}
```

**Deep merge:** New summaries merge into existing memory — previous context preserved, not overwritten.

## Bot Commands

| Command | Description |
|---------|-------------|
| `!help` | Show help |
| `!summarize @user` | Generate/ update dense memory profile (owner only) |
| `!block <user_id>` | Block a user (owner only) |
| `!unblock <user_id>` | Unblock a user (owner only) |

## Security Notice

⚠️ **Never commit `.env` or secrets!** Use `.env.example` as template only.

## Project Structure

```
yuzuki/
├── discord/
│   └── dcbot.py      # Main bot entrypoint
├── shared/
│   ├── __init__.py   # Exports: Config, LLMClient, db
│   ├── config.py     # Configuration (all env vars)
│   ├── database.py   # PostgreSQL via asyncpg (memory + messages)
│   └── llm_client.py # Chutes API client (retry + timeout)
├── scripts/
│   └── setup_db.py   # DB + user + tables creation
├── .env.example      # Environment template
├── .gitignore        # Git ignore rules
└── README.md
```

## Owner Commands

- Mention Yuzuki in any channel or DM directly
- `!summarize @user` — force memory analysis
- `!block` / `!unblock` — manage blocked users
