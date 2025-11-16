from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_linkup import LinkupSearchTool
from pydantic import BaseModel
from typing import TypedDict
from langgraph.graph import StateGraph, END, START
from personalization_client import PersonalizationClient
from datetime import datetime, timezone

from dotenv import load_dotenv

load_dotenv()

client = PersonalizationClient()

model = ChatOpenAI(model="gpt-4o-mini")
linkup_tool = LinkupSearchTool(
    depth="standard",
    output_type="sourcedAnswer",
    api_key="08b205e2-15fe-4627-84fa-941cc71d0066"
)

class MarketTrendAgent(TypedDict):
    user_id: str
    prompt: str
    linkup_response: str

def create_user_id(state: MarketTrendAgent) -> MarketTrendAgent:
    try:
        response = client.get_summary(user_id=state["user_id"])
        user_id = response.user_id
    except Exception as e:
        response = client.register_user(
            email=f"{state['prompt']}@example.com",
            traits={"name": state["prompt"]}
        )
        user_id = response.user_id
    return {
        "user_id": user_id
    }

SYSTEM_PROMPT = """
You are a Market Trend Analysis Specialist. Your role is to transform user prompts about target demographics and interests into optimized questions for comprehensive market trend analysis.

Your goal is to refine user prompts to better discover:
- Current consumer trends and behaviors
- Social media insights and social listening data
- Market trend analysis focused on specific demographics
- Consumer insights and preferences
- Emerging patterns and shifts in the target market

When receiving a user prompt, extract and enhance the following elements:
1. **Demographic Information**: Age group (e.g., Gen Alpha, Gen Z, Millennials), geographic location, socioeconomic factors
2. **Interests & Preferences**: Specific hobbies, games, content types, brands, activities mentioned
3. **Context**: What the user wants to achieve (marketing, product development, content creation, etc.)

Transform the prompt into a well-structured question that:
- Focuses on CURRENT trends (not historical)
- Includes specific demographic identifiers
- Incorporates relevant interests and preferences
- Asks about consumer behavior, preferences, and emerging patterns
- Considers social media platforms and content consumption habits
- Seeks actionable insights for marketing and business decisions

Example Transformation:
- User Input: "I want to cater to Gen Alpha who are interested in Among Us Content and Love Fortnite"
- Optimized Question: "What are the current market trends, consumer behaviors, and social media insights for Gen Alpha (born 2010-2025) who are interested in Among Us content and Fortnite? What are their content consumption patterns, preferred platforms, emerging interests, and how do these trends impact marketing strategies?"

Guidelines:
- Always include time-specific language (current, latest, emerging, recent)
- Combine demographic and interest information into a cohesive question
- Ask about multiple dimensions: behavior, preferences, platforms, content types
- Consider both explicit interests mentioned and related trends
- Frame questions to yield actionable marketing insights
"""

def retrieval_node(state: MarketTrendAgent) -> MarketTrendAgent:
    model = ChatOpenAI(model="gpt-4o-mini")
    response = model.invoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=state["prompt"])])
    linkup_response = linkup_tool.invoke(response.content)
    
    # Extract answer from LinkUp response
    if hasattr(linkup_response, 'answer'):
        answer = linkup_response.answer
    elif hasattr(linkup_response, 'content'):
        answer = linkup_response.content
    else:
        answer = str(linkup_response)
    
    return {
        "linkup_response": answer
    }

def insert_into_fastino(state: MarketTrendAgent) -> MarketTrendAgent:
    # Generate ISO 8601 timestamp
    timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    
    client.ingest_data(
        user_id=state["user_id"],
        source="linkup",
        message_history=[{
            "role": "user",
            "content": state["prompt"],
            "timestamp": timestamp
        }],
        documents=[{
            "content": state["linkup_response"],
            "document_type": "research_response"
        }]
    )
    return {
        "user_id": state["user_id"],
        "prompt": state["prompt"],
        "linkup_response": state["linkup_response"]
    }
 


workflow = StateGraph(MarketTrendAgent)
workflow.add_node("create_user_id", create_user_id)
workflow.add_node("retrieval", retrieval_node)
workflow.add_node("insert_into_fastino", insert_into_fastino)
workflow.add_edge(START, "create_user_id")
workflow.add_edge("create_user_id", "retrieval")
workflow.add_edge("retrieval", "insert_into_fastino")
workflow.add_edge("insert_into_fastino", END)

workflow.compile()
agent = workflow.compile()
print(agent.invoke({"prompt": "What is the current market trend for Gen Alpha who are interested in Among Us content and Fortnite?", "user_id": "ffae3384-bee5-4bf6-851c-c776aaf11404"}))
