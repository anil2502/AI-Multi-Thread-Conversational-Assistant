import streamlit as st
import uuid
import requests
import json
from mcp.types import TextContent, CallToolResult
import time
################################# General Functions ##################################################

def generate_thread_id():
    thread_id = str(uuid.uuid4())
    return thread_id

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state["thread_id"] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state["message_history"] = []
    

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_conversation_history(thread_id):
    specific_thread_history = requests.get(F"http://127.0.0.1:8000/thread_history/{thread_id}",params=None, headers=None)
    
    if len(specific_thread_history.json()) == 0:
        specific_thread_history = []

    else:
        specific_thread_history = specific_thread_history.json()  #NOTE:- .json() b/c .get() returning response Object to conver it to json using the .json()

    return specific_thread_history 

def get_all_stored_threads():
    all_threads_data = requests.get(F"http://127.0.0.1:8000/all_threads")
    
    if len(all_threads_data.json()) == 0:
        all_threads_data = [generate_thread_id()]
    else:
        all_threads_data = all_threads_data.json()
    
    return all_threads_data

################################# Session setup ##################################################

if 'message_history' not in st.session_state:
    st.session_state["message_history"] = []

if 'chat_threads' not in st.session_state:
    st.session_state["chat_threads"] = get_all_stored_threads()
    
    # 'http://127.0.0.1:8000/all_conversations'
    

if 'thread_id' not in st.session_state:
    st.session_state['thread_id']= st.session_state["chat_threads"][-1]

    specific_thread_history = load_conversation_history(st.session_state['thread_id'])
            
    current_thread_history = []
    is_tool_executed = False
    tool_name = None

            
    for message in specific_thread_history:        

        if message:
            current_thread_history.append({'role': "user", 'content': message["user_question"], "is_tool_exesist": False, "tool_name": None})
            
            if message["is_tool_executed"]:
                tool_name = message["tool_name"]
                current_thread_history.append({'role': "assistant", 'content': message["bot_answer"], "is_tool_exesist": message["is_tool_executed"], "tool_name": tool_name})                
            else:
                current_thread_history.append({'role': "assistant", 'content': message["bot_answer"], "is_tool_exesist": False, "tool_name": None})
          
    st.session_state["message_history"] = current_thread_history



############################ Sidebar UI #########################################################

st.sidebar.title('Lexi Agentic AI')

if st.sidebar.button('New Chat'):
    reset_chat()
    

st.sidebar.header('My Conversations')

for thread_id in st.session_state['chat_threads'][::-1]:

    if thread_id == st.session_state['thread_id']:
        st.sidebar.info(f"▶ {thread_id}") 

    else:
        if st.sidebar.button(thread_id, key=thread_id):
            st.session_state['thread_id'] = thread_id
            
            specific_thread_history = load_conversation_history(thread_id)
            
            current_thread_history = []
            is_tool_executed = False
            tool_name = None
            
            for message in specific_thread_history:

                if message:
                    current_thread_history.append({'role': "user", 'content': message["user_question"], "is_tool_exesist": False, "tool_name": None})            
                    if message["is_tool_executed"]:
                        tool_name = message["tool_name"]
                        current_thread_history.append({'role': "assistant", 'content': message["bot_answer"], "is_tool_exesist": message["is_tool_executed"], "tool_name": tool_name})                
                    else:
                        current_thread_history.append({'role': "assistant", 'content': message["bot_answer"], "is_tool_exesist": False, "tool_name": None})
            st.session_state["message_history"] = current_thread_history

            st.rerun()



############################ Chat Window UI #########################################################

for i in st.session_state['message_history']:

    if i['role'] == 'user':
        st.chat_message('user').write(i["content"])
    else:

        tool = i.get("is_tool_exesist", "tool Not exesist")
        name = i.get("tool_name", "tool_name not exesist")
        if tool != "tool Not exesist" and name != "tool_name not exesist":
            if i["is_tool_exesist"] and i["tool_name"]:
                st.status(f"✅ Used {name} …", state = 'complete')
            
        st.chat_message('assistant').write(i["content"])
        

user_input = st.chat_input('Type here')

if user_input:
    st.chat_message("user").write(user_input)
    st.session_state["message_history"].append({'role': 'user', 'content': user_input})

    # first add the message to message_history
    with st.chat_message("assistant"):

        # With Fast-APIs
        payload = {
            "text": user_input,
            "thread_id": st.session_state["thread_id"]
        }

         # Call FastAPI stream endpoint
        ai_message = requests.post(
            "http://127.0.0.1:8000/predict",
            json = payload, 
            stream = True
        )
        status_box = {"box":None}
        tool_name = None
        
        def ai_only_stream():            
            global status_box, tool_name
            #NOTE:- With StreamingResponse
            for line in ai_message.iter_lines():

                if line:

                    data = json.loads(line)                   

                    # safely get type
                    event_type = data.get("type")

                    # skip if no type
                    if not event_type:
                        continue
                    else:
                        if event_type == "tool":
                            tool_name = data.get("name", "tool_name Not Found")
                            
                            if status_box["box"] is None:
                                status_box["box"] = st.status(f"🔧 Using `{tool_name}` …", expanded=True, state = "running")

                        else:
                            yield data.get("content", "No Content")



        ai_message = st.write_stream(ai_only_stream())
        if tool_name:
            status_box["box"].update(label=f"✅ Used {tool_name} …", state = "complete")    

    st.session_state["message_history"].append({'role': 'assistant', 'content': ai_message})
        
