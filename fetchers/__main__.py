# fetchers/__main__.py

from .fetchers import fetchers
import asyncio

if __name__ == "__main__":
    asyncio.run(fetchers())
