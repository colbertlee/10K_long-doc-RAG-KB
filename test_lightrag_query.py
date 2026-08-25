"""Test LightRAG query directly."""

import asyncio
from rag_kb.lightrag.adapter import LightRAGAdapter

async def test():
    rag = LightRAGAdapter()
    await rag.ensure_initialized()
    result = await rag.query('supervised learning', mode='hybrid')
    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(test())