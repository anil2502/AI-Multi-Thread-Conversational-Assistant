
# executing first it self b/c to avoid to late imports
import asyncio, sys
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI
import json
import uuid
from datetime import datetime, timezone


from fastapi import Request, Depends

from fastapi.responses import StreamingResponse, PlainTextResponse
from langchain_core.messages import HumanMessage, BaseMessage, ToolMessage, AIMessage


from src.db.schema import ChatState



from src.core.lifespan import lifespan

app = FastAPI(lifespan=lifespan)


from src.db.session import get_async_db
from src.db.models import table_structure_config
from src.db.schema import table_fields_validation

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

@app.get('/')
async def home():
    return {"message": "Hi Wellcome Project  Before Apply", 'id': str(uuid.uuid4())}





# @app.post('/predict', response_class=PlainTextResponse) #NOTE :- response_class=PlainTextResponse it will responsible to extract the plain text Other wise it is giving the Quoted Answers "Heloo i am ANIL" like that
@app.post('/predict') #NOTE :- response_class=PlainTextResponse it will responsible to extract the plain text Other wise it is giving the Quoted Answers "Heloo i am ANIL" like that
async def predict(data: ChatState, request: Request, db: AsyncSession = Depends(get_async_db)):
    
    MSG_Obj = [
        HumanMessage(content=data.text) # NOTE Here data.text b/c data is an ChatState Object So we need to extract the text from it
    ]

    CONFIG = {"configurable":{"thread_id": data.thread_id}}

    compiled_graph = (
        request.app.state.compiled_graph
    )
    
    
        
    async def generate():
        
        complete_bot_answer = ""
        is_tool = False
        tool_name = None
        
        async for event in compiled_graph.astream_events({"messages": MSG_Obj}, CONFIG, version="v2"):

            if event['event'] == "on_tool_start":
                tool_name = event["name"]
                is_tool = True
                yield f"{json.dumps({'type': 'tool', 'name': tool_name})}\n"
            elif event["event"] == "on_chat_model_stream":
                chunk_content = event["data"]["chunk"].content
                
                if chunk_content:
                    complete_bot_answer += chunk_content
                    yield f"{json.dumps({'type': 'token', 'content': chunk_content})}\n"
            else:
                continue
        if complete_bot_answer:
            
            if is_tool:
                insert_new_recoard : table_fields_validation = table_structure_config(
                    user_id = "6cafe168-545e-4695-87ba-18ecf8c5eac6",
                    thread_id = data.thread_id,
                    user_question = data.text,
                    bot_answer = complete_bot_answer,
                    is_tool_executed = is_tool,
                    tool_name = tool_name,
                    timestamp = datetime.now(timezone.utc).isoformat()
                )
            else:
                insert_new_recoard : table_fields_validation = table_structure_config(
                    user_id = "6cafe168-545e-4695-87ba-18ecf8c5eac6",
                    thread_id = data.thread_id,
                    user_question = data.text,
                    bot_answer = complete_bot_answer,
                    is_tool_executed = is_tool,
                    tool_name = tool_name,
                    timestamp = datetime.now(timezone.utc).isoformat()
                )
                
            db.add(insert_new_recoard)
            await db.commit()
            print("✅ Full conversation saved asynchronously via SQLAlchemy!")
                
    return StreamingResponse(
        generate(),
        media_type = "application/x-ndjson"
        # media_type="text/event-stream"
    )
    


@app.get('/all_threads')
async def get_all_threads(request: Request, db: AsyncSession = Depends(get_async_db)):

    specific_thread_history = []
    sorted_unique_thread_ids = []
    specific_thread_history_object = await db.execute(select(table_structure_config))
    for i in specific_thread_history_object:
               
        specific_thread_history.append({
            "thread_id" : i[0].thread_id,
            "timestamp" : i[0].timestamp
        })
        
    sorted_history = sorted(specific_thread_history, key= lambda x: x["timestamp"])
    sorted_thread_ids = [i["thread_id"] for i in sorted_history]
    
    for thread_id in sorted_thread_ids:
        if thread_id not in sorted_unique_thread_ids:
            sorted_unique_thread_ids.append(thread_id)           
    
    return sorted_unique_thread_ids



@app.get('/thread_history/{id}')
async def get_Specific_thread_history(id: str, request: Request, db:AsyncSession = Depends(get_async_db)):
    compiled_graph = (
        request.app.state.compiled_graph
    )

    config = {"configurable":{"thread_id": id}}
    specific_thread_history = []
    specific_thread_history_object = await db.execute(select(table_structure_config).where(table_structure_config.thread_id == id))

    
    for i in specific_thread_history_object:
               
        specific_thread_history.append({
            "user_id" : i[0].user_id,
            "thread_id" : i[0].thread_id,
            "user_question" : i[0].user_question,
            "bot_answer" : i[0].bot_answer,
            "is_tool_executed" : i[0].is_tool_executed,
            "tool_name" : i[0].tool_name,
            "timestamp" : i[0].timestamp
        })
    sorted_history = sorted(specific_thread_history, key= lambda x: x["timestamp"])
    return sorted_history


if __name__ == "__main__":
    app.run()


