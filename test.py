# from client_url_v2 import (
#     MCPServerManager,
#     # MCPServerConfig,
#     # RemoteLangGraphAgent,
#     # create_mcp_client_and_tools,
#     initialize_agent
# )
# import asyncio

# async def main(query):
#     try:
#         server_manager = MCPServerManager()
#         agent = await initialize_agent(server_manager, ['github_server', 'jira_server'])
#         result = await agent.process_query(query)
#         print(f"Result: {result}")
#     finally:
#         # Cleanup
#         try:
#             if 'agent' in locals() and agent.mcp_client:
#                 await agent.mcp_client.aclose()
#         except:
#             pass


# asyncio.run(main("list all repos"))

import asyncio
import json
import os
from client_url_v2 import MCPServerManager, initialize_agent
from dotenv import load_dotenv

# Load .env at the very start
load_dotenv()

# Set up proper environment variables
# GitHub token for GitHub operations
github_token = os.getenv("GITHUB_PAT")
if not github_token:
    print("❌ Error: GITHUB_TOKEN not found in environment variables")
    print("Please add your GitHub Personal Access Token to your .env file:")
    print("GITHUB_TOKEN=your_github_token_here")
    exit(1)

os.environ["GITHUB_TOKEN"] = github_token

# Fireworks API key (if needed for LLM operations)
fireworks_key = os.getenv("FIREWORKS_API_KEY")
if fireworks_key:
    os.environ["FIREWORKS_API_KEY"] = fireworks_key

async def run_single_query(query: str):
    server_manager = MCPServerManager()
    selected_servers = ['github_server']  # Select all servers for this example

    agent = None
    try:
        print("🔍 Initializing agent with GitHub authentication...")
        
        # Initialize agent with selected servers
        agent = await initialize_agent(server_manager, selected_servers)
        print("✅ Agent ready")

        print(f"🔍 Processing query: {query}")
        
        # Process the query
        result = await agent.process_query(query)
        print("\n📋 Final Result:\n", result.response)
        print("\n🔧 Tool Calls:", json.dumps(
            [f"{tc.name} ({tc.server})" for tc in result.tool_calls], indent=2
        ))
        print(f"\n⏱️ Processing Time: {result.processing_time:.2f}s")

    except Exception as e:
        print(f"❌ Error during execution: {str(e)}")
        
    finally:
        # Safely close MCP client session if supported
        if agent and hasattr(agent.mcp_client, "aclose"):
            try:
                await agent.mcp_client.aclose()
                print("✅ MCP client closed successfully")
            except Exception as e:
                print(f"⚠️ Error closing MCP client: {e}")
        else:
            print("⚠️ MCP client does not support aclose(), skipping cleanup")

async def test_github_connection():
    """Test if GitHub authentication is working"""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return False
        
    try:
        import aiohttp
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.github.com/user", headers=headers) as response:
                if response.status == 200:
                    user_data = await response.json()
                    print(f"✅ GitHub authentication successful for user: {user_data.get('login')}")
                    return True
                else:
                    print(f"❌ GitHub authentication failed: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Error testing GitHub connection: {e}")
        return False

if __name__ == "__main__":
    async def main():
        # Test GitHub connection first
        print("🔍 Testing GitHub authentication...")
        if not await test_github_connection():
            print("Please check your GITHUB_TOKEN in the .env file")
            return
            
        # Run the query
        await run_single_query("list all repos")
    
    asyncio.run(main())