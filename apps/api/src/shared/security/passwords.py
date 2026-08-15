import asyncio

from pwdlib import PasswordHash

_password_hash = PasswordHash.recommended()
_semaphore = asyncio.Semaphore(4)


async def hash_password(password: str) -> str:
    async with _semaphore:
        return await asyncio.to_thread(_password_hash.hash, password)


async def verify_password(password: str, password_hash: str) -> bool:
    async with _semaphore:
        return await asyncio.to_thread(_password_hash.verify, password, password_hash)


def needs_rehash(password_hash: str) -> bool:
    return False
