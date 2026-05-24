
import os
import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy.types import Text, DateTime
from datetime import datetime, timezone
from pydantic import BaseModel
from sqlalchemy import Boolean
from dotenv import load_dotenv
load_dotenv()



DATABASE_URL = os.getenv("DB_URL")

async_engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True if you want to see raw SQL logs in your terminal
)


AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False  # Crucial for async: stops objects from expiring after commit
)

Base = declarative_base()

# 4. Async function to create tables if they don't exist 
async def init_models():
    async with async_engine.begin() as conn:
        # This executes the table creation asynchronously
        await conn.run_sync(Base.metadata.create_all)

# 5. FastAPI Dependency helper for Async Sessions
async def get_async_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
            


