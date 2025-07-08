import asyncio
from dotenv import load_dotenv

from browser_use.llm.azure.chat import ChatAzureOpenAI

load_dotenv()
from browser_use import Agent

async def main():
    agent = Agent(
        task="Goto Yahoo.com and find the most important news",
        llm=ChatAzureOpenAI(
            model="gpt-4.1",
            temperature=1.0,
            api_version="2024-12-01-preview",
        ),
        tool_calling_method="function_calling",
    )
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())