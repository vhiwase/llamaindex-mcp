#!/usr/bin/env python3
"""
Local MCP Client with LlamaIndex

This script demonstrates how to create a local MCP (Model Context Protocol) client
that can chat with a database through tools exposed by an MCP server—completely
on your machine.

The script sets up Azure OpenAI GPT-4, initializes an MCP client, and creates
an agent that can interact with the database using natural language.
"""

import os
import pathlib
import sys

try:
    FILE = pathlib.Path(__file__)
except NameError:
    FILE = pathlib.Path("azure_client.py")
BASE = FILE.parent

BASE_ABSOLUTE = BASE.absolute()
if BASE_ABSOLUTE.absolute().as_posix() not in sys.path:
    sys.path.append(BASE_ABSOLUTE.absolute().as_posix())

import importlib

import_path = os.getenv("APP_SETTINGS", "config.LocalConfig")

from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

# Load config modules
module_name, class_name = import_path.rsplit(".", 1)
module = importlib.import_module(module_name)
baseconfig = getattr(module, class_name)

import nest_asyncio
import asyncio
import os


# Apply nest_asyncio to allow nested event loops (required for Jupyter compatibility)
nest_asyncio.apply()

# Import required LlamaIndex components
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core import Settings
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
from llama_index.core.agent.workflow import (
    FunctionAgent,
    ToolCallResult,
    ToolCall
)

from llama_index.core.workflow import Context

# System prompt to guide the LLM's behavior
SYSTEM_PROMPT = """\
You are an AI assistant for Tool Calling.

Before you help a user, you need to work with tools to interact with Our Database
"""

def setup_llm() -> AzureOpenAI:
    """
    Set up Azure OpenAI GPT-4 (Chat Mode).

    # Define your chat message
    messages = [ChatMessage(role=MessageRole.USER, content="Hello, how are you?")]

    # Send the message to the chat model
    response = gpt4o_azure_chat_open_ai_llm.chat(messages)

    # Print the response
    print(response)

    Returns:
        AzureOpenAI: Configured LLM instance
    """
    # Get Azure OpenAI credentials from environment variables
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

    if not all([api_key, endpoint]):
        raise ValueError(
            "Missing required environment variables. Please set:\n"
            "- AZURE_OPENAI_API_KEY\n"
            "- AZURE_OPENAI_ENDPOINT\n"
            "Optional: AZURE_OPENAI_API_VERSION (defaults to 2024-02-15-preview)"
        )

    gpt4o_azure_chat_open_ai_llm= AzureOpenAI(
        model='gpt-4o',
        deployment_name=baseconfig.AZURE_GPT4o_OPENAI_DEPLOYMENT,
        api_key=baseconfig.AZURE_GPT4o_OPENAI_API_KEY,
        azure_endpoint=baseconfig.AZURE_GPT4o_OPENAI_ENDPOINT,
        api_version=baseconfig.AZURE_GPT4o_OPENAI_API_VERSION,
    )
        
    Settings.llm = gpt4o_azure_chat_open_ai_llm
    return gpt4o_azure_chat_open_ai_llm

async def get_agent(tools: McpToolSpec, llm: AzureOpenAI) -> FunctionAgent:
    """
    Create a FunctionAgent with the specified tools and LLM.

    Args:
        tools (McpToolSpec): MCP tools specification
        llm (AzureOpenAI): Configured LLM instance

    Returns:
        FunctionAgent: Configured agent instance
    """
    tools_list = await tools.to_tool_list_async()
    agent = FunctionAgent(
        name="Agent",
        description="An agent that can work with Our Database software.",
        tools=tools_list,
        llm=llm,
        system_prompt=SYSTEM_PROMPT,
    )
    return agent

async def handle_user_message(
    message_content: str,
    agent: FunctionAgent,
    agent_context: Context,
    verbose: bool = False,
) -> str:
    """
    Process a user message and return the agent's response.

    Args:
        message_content (str): User's input message
        agent (FunctionAgent): Configured agent instance
        agent_context (Context): Agent's context
        verbose (bool): Whether to print detailed tool call information

    Returns:
        str: Agent's response
    """
    handler = agent.run(message_content, ctx=agent_context)
    async for event in handler.stream_events():
        if verbose and isinstance(event, ToolCall):
            print(f"Calling tool {event.tool_name} with kwargs {event.tool_kwargs}")
        elif verbose and isinstance(event, ToolCallResult):
            print(f"Tool {event.tool_name} returned {event.tool_output}")

    response = await handler
    return str(response)

async def main():
    """
    Main function to run the MCP client.
    """
    try:
        # Set up the LLM
        llm = setup_llm()

        # Initialize MCP client and tools
        mcp_client = BasicMCPClient("http://127.0.0.1:8000/sse")
        mcp_tool = McpToolSpec(client=mcp_client)

        # Get the agent and create context
        agent = await get_agent(mcp_tool, llm)
        agent_context = Context(agent)

        # Print available tools
        tools = await mcp_tool.to_tool_list_async()
        print("\nAvailable tools:")
        for tool in tools:
            print(f"- {tool.metadata.name}: {tool.metadata.description}")

        # Main interaction loop
        print("\nStarting interaction loop (type 'exit' to quit)")
        while True:
            try:
                user_input = input("\nEnter your message: ")
                if user_input.lower() == "exit":
                    break
                
                print("User:", user_input)
                response = await handle_user_message(
                    user_input, agent, agent_context, verbose=True
                )
                print("Agent:", response)
                
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")

    except ValueError as e:
        print(f"Configuration Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")

if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())
    
    
    # Example interactions with the MCP client:
    # 1. Add a record: "Add this to Record: My name is Vaibhav Hiwase, DOB 9 May 1993, working as a team lead in AI/ML at TechnoMile."
    # 2. Read the latest record: "Read the latest record."
    # 3. Add another record: "Add Data: My name is Jon Doe, I am a bus driver."
    # 4. Read all records: "Read all records."
    # 5. Add a third record: "Add Data: My name is Khan, I am a math teacher and I have a YouTube channel, and I am 30 years older than my son who was born in 2000."
    # 6. Read the last record: "Read the last record."