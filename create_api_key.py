"""
create_api_key.py — run this by hand to mint a new API key.

Usage:
    python create_api_key.py alice

This prints the raw key ONCE. Copy it somewhere safe immediately —
the database only ever stores its hash, so if you lose the raw key,
there is no way to recover it. You'd just create a new one.
"""

import sys
from utils.db import init_db, create_api_key

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python create_api_key.py <owner_name>")
        sys.exit(1)

    owner = sys.argv[1]
    init_db()  # make sure the tables exist before we try to insert
    raw_key = create_api_key(owner)

    print(f"Created a new API key for owner: {owner}")
    print(f"Key (copy this now, it will not be shown again):\n{raw_key}")