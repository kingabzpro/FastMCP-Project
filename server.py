import os
from typing import List, Dict
from fastmcp import FastMCP
from tavily import TavilyClient

# --- Configuration ---
# Load your Tavily API key from an environment variable
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
if not TAVILY_API_KEY:
    raise ValueError("Please set the TAVILY_API_KEY environment variable.")

# Initialize the Tavily client [[1]]
tavily = TavilyClient(api_key=TAVILY_API_KEY)

# Initialize the FastMCP server instance
mcp = FastMCP(name="AIResearchAssistant")

print(f"✅ AI Research Assistant server initialized.")


@mcp.resource("resource://research/daily_topics")
def get_daily_research_topics() -> List[str]:
    """Provides a dynamic list of suggested topics for daily research."""
    return [
        "Latest breakthroughs in quantum computing",
        "Economic impact of renewable energy adoption",
        "Key takeaways from the most recent G7 summit",
        "Advancements in mRNA vaccine technology",
    ]


print("✅ Resource 'resource://research/daily_topics' registered.")

@mcp.tool(annotations={"title": "Perform Web Search"})
def web_search(query: str, max_results: int = 3) -> List[Dict]:
    """
    Performs a general web search for a given query and returns a list of results.

    Args:
        query: The search query.
        max_results: The maximum number of results to return.
    """
    try:
        response = tavily.search(query=query, max_results=max_results)
        return [
            {"title": r["title"], "url": r["url"], "content": r["content"]}
            for r in response.get("results", [])
        ]
    except Exception as e:
        return [{"error": f"An error occurred: {e}"}]


@mcp.tool(annotations={"title": "Get Latest News"})
def get_latest_news(topic: str) -> List[Dict]:
    """
    Finds the most recent news articles on a specific topic from the last week.

    Args:
        topic: The news topic to search for.
    """
    try:
        response = tavily.search(query=topic, topic="news", time_range="week")
        return [
            {"title": r["title"], "url": r["url"], "content": r["content"]}
            for r in response.get("results", [])
        ]
    except Exception as e:
        return [{"error": f"An error occurred: {e}"}]


@mcp.tool(annotations={"title": "Get Quick Answer"})
def get_quick_answer(question: str) -> str:
    """
    Provides a direct, concise answer to a specific question.

    Args:
        question: The question you want a direct answer for.
    """
    try:
        response = tavily.qna_search(query=question)
        return response
    except Exception as e:
        return f"An error occurred: {e}"


print("✅ Tools 'web_search', 'get_latest_news', and 'get_quick_answer' registered.")

@mcp.prompt
def generate_comprehensive_report_request(topic: str) -> str:
    """Generates a prompt to create a comprehensive report on a topic."""
    return (
        f"Please compile a report on '{topic}'. Follow these steps:\n"
        f"1. First, use the 'get_quick_answer' tool to get a concise summary.\n"
        f"2. Next, use the 'get_latest_news' tool to find recent developments.\n"
        f"3. Finally, use the 'web_search' tool to gather broader context.\n"
        f"Synthesize all this information into a final report."
    )


print("✅ Prompt 'generate_comprehensive_report_request' registered.")


if __name__ == "__main__":
    print("\n🚀 Starting AI Research Assistant Server...")
    print("   Waiting for a client to connect via STDIO.")
    mcp.run(transport="http")