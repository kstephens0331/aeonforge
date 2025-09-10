import requests
from bs4 import BeautifulSoup
import os
import json
from typing import Optional, List, Dict
from .api_key_manager import api_key_manager

def web_search(query: str, num_results: int = 5, api_key: Optional[str] = None) -> str:
    """
    Performs a web search using SerpAPI and returns formatted results.
    Accepts an API key directly or falls back to the human-in-the-loop system.

    Args:
        query (str): The search query.
        num_results (int): Number of results to return (default 5).
        api_key (str, optional): The SerpAPI key to use. If not provided, it will be requested.
    """
    print(f"Performing web search for: '{query}'")
    
    # If no API key is passed directly, try to get it from the manager
    if not api_key:
        api_key = api_key_manager.get_api_key(
            service_name="SerpAPI (Google Search)",
            key_name="SERPAPI_KEY",
            description="Provides access to Google Search results for web research"
        )
    
    if not api_key:
        return f"Web search skipped - no API key provided. Query was: '{query}'"
    
    try:
        # Use SerpAPI for Google search results via google-search-results package
        from serpapi import GoogleSearch
        
        search = GoogleSearch({
            "q": query,
            "api_key": api_key,
            "num": num_results
        })
        
        data = search.get_dict()
        
        # Format the results
        return _format_search_results(data, query)
        
    except requests.exceptions.RequestException as e:
        return f"Error performing web search: {e}"
    except json.JSONDecodeError as e:
        return f"Error parsing search results: {e}"
    except Exception as e:
        return f"Unexpected error during web search: {e}"

def _format_search_results(data: dict, query: str) -> str:
    """
    Formats SerpAPI results into a readable string.
    
    Args:
        data: SerpAPI response data
        query: Original search query
        
    Returns:
        Formatted search results string
    """
    results = []
    results.append(f"Web Search Results for: '{query}'")
    results.append("=" * 50)
    
    # Get organic search results
    organic_results = data.get("organic_results", [])
    
    if not organic_results:
        return f"No search results found for: '{query}'"
    
    for i, result in enumerate(organic_results, 1):
        title = result.get("title", "No Title")
        link = result.get("link", "No Link")
        snippet = result.get("snippet", "No description available")
        
        results.append(f"\n{i}. {title}")
        results.append(f"   URL: {link}")
        results.append(f"   Summary: {snippet}")
    
    # Add any featured snippet if available
    featured_snippet = data.get("featured_snippet")
    if featured_snippet:
        results.insert(2, f"\nFeatured Snippet:")
        results.insert(3, f"   {featured_snippet.get('snippet_highlighted_words', [''])[0]}")
        results.insert(4, f"   Source: {featured_snippet.get('link', 'Unknown')}")
    
    # Add search metadata
    search_metadata = data.get("search_metadata", {})
    total_results = search_metadata.get("total_results", "Unknown")
    search_time = search_metadata.get("processing_time_ms", "Unknown")
    
    results.append(f"\nSearch completed in {search_time}ms")
    results.append(f"   Total results available: {total_results}")
    
    return "\n".join(results)

def fetch_webpage_content(url: str) -> str:
    """
    Fetches and extracts text content from a webpage.
    
    Args:
        url (str): The URL to fetch content from.
        
    Returns:
        Extracted text content from the webpage.
    """
    print(f"Fetching content from: {url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract text content
        text = soup.get_text()
        
        # Clean up the text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Limit content length
        max_length = 2000
        if len(text) > max_length:
            text = text[:max_length] + "...\n[Content truncated]"
        
        return f"Content from {url}:\n\n{text}"
        
    except requests.exceptions.RequestException as e:
        return f"Error fetching webpage content: {e}"
    except Exception as e:
        return f"Unexpected error processing webpage: {e}"