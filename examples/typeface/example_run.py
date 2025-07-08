import asyncio
from pathlib import Path

from dotenv import load_dotenv
from playwright.async_api import async_playwright

from browser_use.llm.azure.chat import ChatAzureOpenAI

load_dotenv()
from browser_use import Agent

PROFILE_DIR = Path.home() / ".cache" / "my_playwright_profile"
PROFILE_DIR.mkdir(parents=True, exist_ok=True)


async def main():
    async with async_playwright() as p:
        try:
            # launch a Chromium *context* that persists to disk
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(PROFILE_DIR),
                headless=False
            )
            agent = Agent(
                task="Goto https://beta.typeface.ai/?accountId=6195aaed-f8f5-491b-b351-f51e4e5a60df and go the project page.",
                llm=ChatAzureOpenAI(
                    model="gpt-4.1",
                    temperature=0.2,
                    api_version="2024-12-01-preview",
                ),
                context=context,
                tool_calling_method="function_calling",
            )
            await agent.run()
        except Exception as e:
            raise e
        finally:
            await context.close()


if __name__ == "__main__":
    asyncio.run(main())