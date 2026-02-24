#!/usr/bin/env python3
"""
Gov.de - Telegram Bots Legal Analyzer
Run all bots for testing.
"""

import threading
from .bots.client_bot import main as client_main
from .bots.core_bot import main as core_main
from .bots.de_bot import main as de_main

def run_client():
    client_main()

def run_core():
    core_main()

def run_de():
    de_main()

if __name__ == "__main__":
    # Run in threads for test
    threading.Thread(target=run_client).start()
    threading.Thread(target=run_core).start()
    threading.Thread(target=run_de).start()