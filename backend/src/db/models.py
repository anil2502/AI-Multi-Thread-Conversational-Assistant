

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


from src.db.session import Base



# Example Table Model (Using updated SQLAlchemy 2.0 Syntax)
class table_structure_config(Base):
    
    __tablename__ = "bot_chat_logs"

    user_id: Mapped[str] = mapped_column(default="6cafe168-545e-4695-87ba-18ecf8c5eac6")
    thread_id: Mapped[str] = mapped_column(index=True)
    user_question: Mapped[str] = mapped_column(Text)
    bot_answer: Mapped[str] = mapped_column(Text)
    is_tool_executed : Mapped[bool] = mapped_column(default=False)
    tool_name: Mapped[str | None] = mapped_column(Text, default=None)
    timestamp: Mapped[str] = mapped_column(Text, primary_key=True, index=True)
    
    
    
    
