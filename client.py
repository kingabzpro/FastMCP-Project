import ast
import asyncio
import pprint

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

# Adjust the URL if your server runs elsewhere
SERVER_URL = "http://localhost:8000/mcp"

pp = pprint.PrettyPrinter(indent=2, width=100)


async def main():
    transport = StreamableHttpTransport(url=SERVER_URL)
    client = Client(transport)
    print("\n🚀 Connecting to FastMCP server at:", SERVER_URL)
    async with client:
        # Ping
        print("\n🔗 Testing server connectivity...")
        await client.ping()
        print("✅ Server is reachable!\n")

        # List tools
        print("🛠️  Available tools:")
        tools = await client.list_tools()
        pp.pprint(tools)
        print()

        # List resources
        print("📚 Available resources:")
        resources = await client.list_resources()
        pp.pprint(resources)
        print()

        # List prompts
        print("💬 Available prompts:")
        prompts = await client.list_prompts()
        pp.pprint(prompts)
        print()

        # Test resource: research/daily_topics
        print("\n📖 Fetching resource: resource://research/daily_topics")
        try:
            daily_topics = await client.read_resource(
                "resource://research/daily_topics"
            )
            # For text/plain, the .text attribute contains the data
            text = daily_topics[0].text
            # Try to parse as list if possible
            try:
                topics = ast.literal_eval(text)
                if isinstance(topics, list):
                    print("Topics for today:")
                    for idx, topic in enumerate(topics, 1):
                        print(f"  {idx}. {topic}")
                else:
                    print("(Not a list, printing as text)")
            except Exception:
                print("(Could not parse as list, printing as text)")
        except Exception as e:
            print(f"❌ Error fetching resource: {e}")
        print()

        # Test tool: web_search
        print("\U0001f50d Testing tool: web_search")
        try:
            ws_result = await client.call_tool(
                "web_search", {"query": "AI research", "max_results": 2}
            )
            print("Results:")
            # Print the structured content if available, else fallback
            if (
                hasattr(ws_result, "structured_content")
                and ws_result.structured_content
            ):
                for idx, item in enumerate(
                    ws_result.structured_content.get("result", []), 1
                ):
                    print(
                        f"  {idx}. {item.get('title', '')}\n     URL: {item.get('url', '')}\n     Content: {item.get('content', '')}\n"
                    )
            elif hasattr(ws_result, "content") and ws_result.content:
                print(ws_result.content)
            else:
                print(ws_result)
        except Exception as e:
            print(f"\u274c Error calling web_search: {e}")
        print()

        # Test tool: get_latest_news
        print("\U0001f4f0 Testing tool: get_latest_news")
        try:
            news_result = await client.call_tool("get_latest_news", {"topic": "AI"})
            print("Results:")
            # Print the structured content if available, else fallback
            if (
                hasattr(news_result, "structured_content")
                and news_result.structured_content
            ):
                for idx, item in enumerate(
                    news_result.structured_content.get("result", []), 1
                ):
                    print(
                        f"  {idx}. {item.get('title', '')}\n     URL: {item.get('url', '')}\n     Content: {item.get('content', '')}\n"
                    )
            elif hasattr(news_result, "content") and news_result.content:
                print(news_result.content)
            else:
                print(news_result)
        except Exception as e:
            print(f"\u274c Error calling get_latest_news: {e}")
        print()

        # Test tool: get_quick_answer
        print("\u26a1 Testing tool: get_quick_answer")
        try:
            answer_result = await client.call_tool(
                "get_quick_answer", {"question": "What is quantum computing?"}
            )
            print("Answer:")
            # Print the result attribute if available
            if (
                hasattr(answer_result, "structured_content")
                and answer_result.structured_content
            ):
                print(answer_result.structured_content.get("result", answer_result))
            elif hasattr(answer_result, "content") and answer_result.content:
                print(answer_result.content)
            else:
                print(answer_result)
        except Exception as e:
            print(f"\u274c Error calling get_quick_answer: {e}")
        print()

        # Test prompt: generate_comprehensive_report_request
        print("📝 Testing prompt: generate_comprehensive_report_request")
        try:
            prompt_result = await client.get_prompt(
                "generate_comprehensive_report_request", {"topic": "AI in healthcare"}
            )
            print("Prompt output:")
            pp.pprint(prompt_result.messages)
        except Exception as e:
            print(f"❌ Error calling prompt: {e}")
        print()


if __name__ == "__main__":
    asyncio.run(main())
