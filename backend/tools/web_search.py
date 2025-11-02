"""
Web Search Tool using Tavily API (with DuckDuckGo fallback)
Optimized for medical and research queries
"""
from tavily import TavilyClient
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

def web_search_tool(query: str, max_results: int = 3) -> str:
    """
    Search the web using Tavily API for medical information
    Falls back to DuckDuckGo if Tavily fails
    
    Args:
        query: Search query
        max_results: Maximum number of results (default: 3)
        
    Returns:
        Formatted search results or error message
    """
    # Try Tavily first (preferred)
    tavily_result = _tavily_search(query, max_results)
    if tavily_result and "ERROR" not in tavily_result:
        return tavily_result
    
    # Fallback to DuckDuckGo
    print("⚠️  Tavily search failed, falling back to DuckDuckGo...")
    ddg_result = _duckduckgo_search(query, max_results)
    
    if ddg_result:
        return ddg_result + "\n\n(Using fallback search engine)"
    
    return "ERROR: Both Tavily and DuckDuckGo searches failed."


def _tavily_search(query: str, max_results: int) -> Optional[str]:
    """
    Primary search using Tavily API
    """
    try:
        api_key = os.getenv("TAVILY_API_KEY")
        
        if not api_key:
            return None
        
        # Initialize Tavily client
        client = TavilyClient(api_key=api_key)
        
        # Perform search with medical context
        response = client.search(
            query=f"medical research {query}",
            max_results=max_results,
            search_depth="advanced",  # More thorough search
            include_answer=True  # Get AI-generated summary
        )
        
        if not response.get("results"):
            return "No web search results found."
        
        # Format results
        formatted_results = []
        
        # Add AI summary if available
        if response.get("answer"):
            formatted_results.append(f"📊 AI Summary: {response['answer']}\n")
        
        # Add individual results
        formatted_results.append("\n🔍 Detailed Sources:\n")
        for i, result in enumerate(response["results"], 1):
            score = result.get('score', 0)
            relevance = "⭐⭐⭐" if score > 0.8 else "⭐⭐" if score > 0.5 else "⭐"
            
            formatted_results.append(
                f"\n{i}. **{result.get('title', 'No title')}**\n"
                f"   📎 URL: {result.get('url', 'No URL')}\n"
                f"   {relevance} Relevance: {score:.2f}\n"
                f"   📄 {result.get('content', 'No description')}\n"
            )
        
        return "".join(formatted_results)
        
    except Exception as e:
        print(f"Tavily search error: {str(e)}")
        return None


def _duckduckgo_search(query: str, max_results: int) -> Optional[str]:
    """
    Fallback search using DuckDuckGo (free, no API key)
    """
    try:
        from duckduckgo_search import DDGS
        
        with DDGS() as ddgs:
            results = list(ddgs.text(
                keywords=f"medical {query}",
                max_results=max_results
            ))
        
        if not results:
            return None
        
        # Format results
        formatted_results = ["🔍 Web Search Results:\n"]
        for i, result in enumerate(results, 1):
            formatted_results.append(
                f"\n{i}. **{result.get('title', 'No title')}**\n"
                f"   📎 URL: {result.get('href', 'No URL')}\n"
                f"   📄 {result.get('body', 'No description')}\n"
            )
        
        return "".join(formatted_results)
        
    except Exception as e:
        print(f"DuckDuckGo search error: {str(e)}")
        return None


# Test function
if __name__ == "__main__":
    print("Testing Web Search Tool...\n")
    print("="*60)
    
    # Test 1: Medical query
    test_query = "chronic kidney disease symptoms treatment"
    print(f"Query: {test_query}\n")
    
    result = web_search_tool(test_query, max_results=2)
    print(result)
    
    print("\n" + "="*60)
    
    # Test 2: Recent research
    test_query2 = "SGLT2 inhibitors kidney disease 2024"
    print(f"\nQuery: {test_query2}\n")
    
    result2 = web_search_tool(test_query2, max_results=2)
    print(result2)