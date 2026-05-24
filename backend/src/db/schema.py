

from pydantic import BaseModel
from datetime import datetime

class table_fields_validation(BaseModel):
    user_id: str
    thread_id: str
    user_question: str
    bot_answer: str
    is_tool_executed: bool
    tool_name : str | None
    timestamp: str



class ChatState(BaseModel):
    text : str
    thread_id : str
    
    
    