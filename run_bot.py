#!/usr/bin/env python3
"""
Simple bot runner without Docker.
Runs only the client_bot for testing.
"""

import asyncio
from src.bots.client_bot import main as client_main

if __name__ == "__main__":
    # Create event loop and run the bot
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        client_main()
    except KeyboardInterrupt:
        print("\nБот зупинено користувачем")
    finally:
        loop.close()
