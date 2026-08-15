import asyncio

# One process-wide cap shared by image extraction, PDF parsing, and chat.
AI_REQUEST_LIMITER = asyncio.Semaphore(2)
