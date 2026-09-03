import asyncio

from ollama import chat

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


MODEL = "qwen3:8b"


async def main():

    # Start MCP server
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"],
    )

    async with stdio_client(server_params) as (read, write):

        async with ClientSession(read, write) as session:

            # Initialize MCP
            await session.initialize()

            # Discover MCP tools
            mcp_tools = await session.list_tools()

            print("MCP tools:")

            for tool in mcp_tools.tools:
                print(f"- {tool.name}: {tool.description}")

            print()

            # Convert MCP tools to Ollama format
            ollama_tools = []

            for tool in mcp_tools.tools:
                ollama_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.input_schema,
                    },
                })

            # Conversation
            messages = [
                {
                    "role": "user",
                    "content": "What is 123 + 456?",
                }
            ]

            # Ask LLM
            response = chat(
                model=MODEL,
                messages=messages,
                tools=ollama_tools,
            )

            # Add LLM response to conversation
            messages.append(response.message)

            # Check for tool calls
            if response.message.tool_calls:

                for call in response.message.tool_calls:

                    tool_name = call.function.name
                    arguments = call.function.arguments

                    print(f"Calling MCP tool: {tool_name}")
                    print(f"Arguments: {arguments}")

                    # Execute MCP tool
                    result = await session.call_tool(
                        tool_name,
                        arguments=arguments,
                    )

                    print(f"Tool result: {result.structured_content}")

                    # Send result back to LLM
                    messages.append({
                        "role": "tool",
                        "tool_name": tool_name,
                        "content": str(result.structured_content),
                    })

                # Ask LLM for final answer
                final_response = chat(
                    model=MODEL,
                    messages=messages,
                    tools=ollama_tools,
                )

                print()
                print("Final answer:")
                print(final_response.message.content)

            else:

                print("Final answer:")
                print(response.message.content)


if __name__ == "__main__":
    asyncio.run(main())