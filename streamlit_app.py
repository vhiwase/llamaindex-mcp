# streamlit_app.py

import os
import pathlib
import sys
import asyncio
import nest_asyncio
import tracemalloc
from contextlib import asynccontextmanager

import streamlit as st

# Enable tracemalloc for better debugging
tracemalloc.start()

# Allow nested event loops in Jupyter/Streamlit
nest_asyncio.apply()

# Make sure project root is on sys.path so that azure_client.py can import correctly
FILE = pathlib.Path(__file__).resolve()
BASE = FILE.parent
if BASE.as_posix() not in sys.path:
    sys.path.append(BASE.as_posix())

# Import your existing LLM setup & handler from azure_client.py
from azure_client import setup_llm, get_agent, handle_user_message, Context

# Get server URL from environment variable or use default
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://fastmcp-server:8000/sse")

@asynccontextmanager
async def get_workflow_context():
    """Context manager for workflow operations."""
    try:
        yield
    finally:
        # Clean up any pending tasks
        for task in asyncio.all_tasks():
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

async def initialize_agent():
    """Initialize the agent asynchronously."""
    # 1) Setup LLM
    llm = setup_llm()

    # 2) Initialize the MCP client & tool spec
    from llama_index.tools.mcp import BasicMCPClient, McpToolSpec

    # Use environment variable for server URL
    mcp_client = BasicMCPClient(MCP_SERVER_URL)
    mcp_tool = McpToolSpec(client=mcp_client)

    # 3) Create the agent
    agent = await get_agent(mcp_tool, llm)
    return agent, Context(agent)

# Ensure a single event loop is used throughout the app
if "event_loop" not in st.session_state:
    st.session_state.event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(st.session_state.event_loop)

# Initialize session state for agent & context
if "agent" not in st.session_state:
    try:
        loop = st.session_state.event_loop
        asyncio.set_event_loop(loop)
        agent, context = loop.run_until_complete(initialize_agent())
        st.session_state.agent = agent
        st.session_state.agent_context = context
    except Exception as e:
        st.error(f"Failed to initialize agent: {str(e)}")
        st.stop()

# Page layout
st.set_page_config(page_title="🔧 MCP Agent Chat", layout="wide")
st.title("🔧 MCP‐Powered Chat (Streamlit UI)")
st.write("Type something below and the agent will try to use tools & reply.")

# Chat history in session state
if "history" not in st.session_state:
    st.session_state.history = []  # list of (user_msg, agent_resp) tuples

# Input form
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("You:", "")
    submit = st.form_submit_button("Send")

if submit and user_input.strip() != "":
    st.session_state.history.append((user_input.strip(), None))  # placeholder for response

    async def process_message(message, agent, context):
        """Process a message with proper workflow context."""
        async with get_workflow_context():
            try:
                return await handle_user_message(message, agent, context, verbose=False)
            except Exception as e:
                return f"Error: {str(e)}"

    loop = st.session_state.event_loop
    asyncio.set_event_loop(loop)
    try:
        agent_resp = loop.run_until_complete(
            process_message(
                user_input.strip(),
                st.session_state.agent,
                st.session_state.agent_context
            )
        )
        st.session_state.history[-1] = (user_input.strip(), agent_resp)
    except Exception as e:
        st.error(f"Error processing request: {str(e)}")
        st.session_state.history[-1] = (user_input.strip(), f"Error: {str(e)}")

# Display chat history
for user_msg, resp_msg in st.session_state.history:
    st.markdown(f"**You:** {user_msg}")
    if resp_msg is None:
        st.markdown("**Agent:** _Thinking…_")
    else:
        st.markdown(f"**Agent:** {resp_msg}")

st.markdown("---")
st.caption("Powered by LlamaIndex + FastMCP + Streamlit")
