from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from tools import get_tools

# System prompt tuned for a voice agent
SYSTEM_PROMPT = """You are a highly capable AI Assistant running locally.
You have access to a local SQLite database that stores user data (like names and emails) in the 'users' table.
When a user asks you to interact with the database (insert, search, UPDATE, or delete users), you MUST use the `query_database` tool.
When they ask for the weather or an email to be sent, use those respective tools.
For general knowledge questions, just answer directly in regular conversational text.
CRITICAL RULE: DO NOT hallucinate imaginary tools, and DO NOT output raw JSON text. Use only the provided tools through the proper tool-calling format.
"""

import json

def run_agent(user_input: str) -> str:
    """Invokes the LangGraph ReAct agent with the user's input."""
    # Instructs the system to use llama3.2, which holds up well for function calling while being CPU friendly.
    llm = ChatOllama(model="llama3.2", temperature=0)

    # Load tools
    tools = get_tools()

    # Create a ReAct agent
    agent_executor = create_react_agent(llm, tools=tools, prompt=SYSTEM_PROMPT)
    
    try:
        # Run the agent
        response = agent_executor.invoke({"messages": [HumanMessage(content=user_input)]})
        final_text = response["messages"][-1].content
        
        # Fallback for Llama 3 hallucinating JSON tools instead of plain text
        if final_text.strip().startswith("{") and '"name"' in final_text:
            try:
                # If it successfully parses as a tool hallucination JSON
                parsed = json.loads(final_text)
                if "name" in parsed:
                    # Rerun the user's prompt directly to a tool-less LLM
                    plain_llm = ChatOllama(model="llama3.2", temperature=0.3)
                    fallback_response = plain_llm.invoke([HumanMessage(content=user_input)])
                    return fallback_response.content
            except json.JSONDecodeError:
                pass # Not a valid JSON, just return it
                
        return final_text
    except Exception as e:
        return f"Agent Error: {str(e)}. (Ensure Ollama is running the llama3.2 model locally: `ollama run llama3.2`)"
