"""
Fastino integration utilities for LangChain.

This module provides FastinoRetriever, FastinoMemory, and FastinoSearchTool
for integrating Fastino Personalization API with LangChain chains and agents.
"""

import os
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from pydantic import Field
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.tools import BaseTool
from dotenv import load_dotenv
from personalization_client import PersonalizationClient

# Load environment variables
load_dotenv()

# Fastino API configuration
FASTINO_API = os.getenv("FASTINO_API", "https://api.fastino.ai").rstrip("/")
# Support both FASTINO_API_KEY and PIONEER_API_KEY for compatibility
FASTINO_KEY = os.getenv("FASTINO_API_KEY") or os.getenv("PIONEER_API_KEY", "")


def _get_client() -> PersonalizationClient:
    """Get or create a Fastino PersonalizationClient instance."""
    api_key = os.getenv("FASTINO_API_KEY") or os.getenv("PIONEER_API_KEY")
    if not api_key:
        raise ValueError(
            "FASTINO_API_KEY or PIONEER_API_KEY environment variable is required. "
            "Set it in your .env file or environment."
        )
    return PersonalizationClient(api_key=api_key, base_url=FASTINO_API)


class FastinoError(Exception):
    """Custom exception for Fastino API errors."""
    pass


class FastinoRetriever(BaseRetriever):
    """
    Retrieve personalized memory snippets for a given user from Fastino.
    
    This retriever queries Fastino's /chunks endpoint for top-k memory snippets
    relevant to a user query, making it suitable for RAG applications.
    
    Example:
        retriever = FastinoRetriever(user_id="usr_42af7c", top_k=3)
        docs = retriever.get_relevant_documents("When does Ash prefer meetings?")
    """
    
    def __init__(self, user_id: str, top_k: int = 5, system_message: Optional[str] = None):
        """
        Initialize the Fastino retriever.
        
        Args:
            user_id: The Fastino user ID to retrieve memories for
            top_k: Number of top memory snippets to retrieve
            system_message: Optional system message for the conversation context
        """
        super().__init__()
        self.user_id = user_id
        self.top_k = top_k
        self.system_message = system_message or "You are a helpful assistant."
    
    def _get_relevant_documents(self, query: str) -> List[Document]:
        """
        Retrieve relevant documents from Fastino.
        
        Args:
            query: The search query
            
        Returns:
            List of Document objects containing memory excerpts
        """
        try:
            client = _get_client()
            conversation_history = [
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": query}
            ]
            
            chunks_response = client.get_chunks(
                user_id=self.user_id,
                conversation_history=conversation_history,
                k=self.top_k
            )
            
            # Extract excerpts from chunks response
            results = chunks_response.results if hasattr(chunks_response, 'results') else chunks_response
            
            return [
                Document(page_content=res.excerpt if hasattr(res, 'excerpt') else str(res))
                for res in results
            ]
        except Exception as e:
            raise FastinoError(f"Failed to retrieve documents: {str(e)}")
    
    async def _aget_relevant_documents(self, query: str) -> List[Document]:
        """Async version of _get_relevant_documents."""
        # For now, use sync version. Can be enhanced with aiohttp if needed.
        return self._get_relevant_documents(query)


class BaseMemory(ABC):
    """Base class for memory in LangChain v1.0+ compatibility."""
    
    @property
    @abstractmethod
    def memory_variables(self) -> List[str]:
        """Return the list of memory variable names."""
        pass
    
    @abstractmethod
    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Load memory variables."""
        pass
    
    @abstractmethod
    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, Any]) -> None:
        """Save context."""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear memory."""
        pass


class FastinoMemory(BaseMemory):
    """
    Persistent memory that stores and retrieves user context from Fastino.
    
    This memory module automatically saves conversation history to Fastino
    and loads user preferences and context when needed.
    
    Example:
        memory = FastinoMemory(user_id="usr_42af7c")
        chain = ConversationChain(llm=llm, memory=memory, verbose=True)
        chain.run("When should I schedule meetings tomorrow?")
    """
    
    def __init__(self, user_id: str, source: str = "langchain"):
        """
        Initialize Fastino memory.
        
        Args:
            user_id: The Fastino user ID
            source: Source identifier for ingested documents
        """
        super().__init__()
        self.user_id = user_id
        self.source = source
    
    @property
    def memory_variables(self) -> List[str]:
        """Return the list of memory variable names."""
        return ["history"]
    
    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Load user preferences and context from Fastino.
        
        Args:
            inputs: Input dictionary from the chain
            
        Returns:
            Dictionary containing memory variables
        """
        try:
            client = _get_client()
            summary_response = client.get_summary(user_id=self.user_id)
            
            # Extract summary text from response
            summary = summary_response.summary if hasattr(summary_response, 'summary') else str(summary_response)
            
            return {"history": summary}
        except Exception as e:
            raise FastinoError(f"Failed to load memory variables: {str(e)}")
    
    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, Any]) -> None:
        """
        Save conversation context to Fastino.
        
        Args:
            inputs: Input dictionary from the chain
            outputs: Output dictionary from the chain
        """
        user_input = inputs.get("input", "")
        assistant_output = outputs.get("output", "")
        
        # Format as message history for ingestion
        message_history = []
        if user_input:
            message_history.append({
                "role": "user",
                "content": user_input
            })
        if assistant_output:
            message_history.append({
                "role": "assistant",
                "content": assistant_output
            })
        
        try:
            client = _get_client()
            client.ingest_data(
                user_id=self.user_id,
                source=self.source,
                message_history=message_history
            )
        except Exception as e:
            # Log error but don't fail the chain
            print(f"Warning: Failed to save context to Fastino: {str(e)}")
    
    def clear(self) -> None:
        """
        Clear memory (optional deletion if needed).
        
        Note: This is a no-op by default. Implement deletion logic if needed.
        """
        pass


class FastinoSearchTool(BaseTool):
    """
    LangChain tool for querying Fastino's personalization API.
    
    This tool allows agents to dynamically query user data during conversations,
    enabling personalized responses based on user history and preferences.
    
    Example:
        tools = [FastinoSearchTool(user_id="usr_42af7c")]
        agent = initialize_agent(tools, llm, agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION)
        agent.run("Who does Ash collaborate with most often?")
    """
    
    name: str = "fastino_search"
    description: str = "Ask personalized questions about a user's preferences, history, and behavior."
    user_id: str = Field(..., description="The Fastino user ID to query")
    
    def __init__(self, user_id: str, **kwargs):
        """
        Initialize the Fastino search tool.
        
        Args:
            user_id: The Fastino user ID to query
            **kwargs: Additional arguments passed to BaseTool
        """
        super().__init__(user_id=user_id, **kwargs)
    
    def _run(self, query: str) -> str:
        """
        Execute the tool synchronously.
        
        Args:
            query: The question to ask about the user
            
        Returns:
            Answer from Fastino API
        """
        try:
            client = _get_client()
            query_response = client.query(
                user_id=self.user_id,
                question=query
            )
            
            # Extract answer from response
            answer = query_response.answer if hasattr(query_response, 'answer') else str(query_response)
            return answer if answer else "No answer available."
        except Exception as e:
            return f"Error querying Fastino: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        """Execute the tool asynchronously."""
        return self._run(query)

