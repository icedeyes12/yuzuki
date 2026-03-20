#!/usr/bin/env python3
"""Setup PostgreSQL database for Yuzuki."""

import asyncio
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.database import db

async def setup():
    print("🗄️  Setting up Yuzuki database...")
    
    await db.connect()
    await db.create_tables()  # <-- FIX: Create tables!
    
    print("✅ Database tables created!")
    print("\nTables:")
    print("  - users: User profiles and facts")
    print("  - messages: All message history (partitioned by month)")
    print("  - conversations: Thread contexts")
    print("  - memories: Extracted facts about users")
    
    await db.close()
    print("\n🎉 Setup complete!")

if __name__ == "__main__":
    asyncio.run(setup())