import asyncio
from pathlib import Path

from dotenv import load_dotenv
from playwright.async_api import async_playwright, ViewportSize

from browser_use.llm.azure.chat import ChatAzureOpenAI

load_dotenv()
from browser_use import Agent

PROFILE_DIR = Path.home() / ".cache" / "my_playwright_profile"
PROFILE_DIR.mkdir(parents=True, exist_ok=True)


async def main(task: str):
    async with async_playwright() as p:
        browser_context = await p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            viewport=ViewportSize(
                width=1080,
                height=1080
            ),
        )
        try:
            # launch a Chromium *context* that persists to disk
            agent = Agent(
                task=task,
                llm=ChatAzureOpenAI(
                    model="gpt-4.1",
                    temperature=0.2,
                    api_version="2024-12-01-preview",
                ),
                browser_context=browser_context,
                tool_calling_method="function_calling",
            )
            await agent.run()
        except Exception as e:
            raise e
        finally:
            await browser_context.close()


if __name__ == "__main__":
    task_1 = """
    Go to https://beta.typeface.ai/canvas/661623?accountId=692cafa4-6947-4d4f-b0c5-dfbdd6ab73f6&chatId=17bd1b2d-248e-42ea-9bb5-2491e26dccd9
    Then start chatting in the text box like a professional designer, with a goal of 
    "creating an image of with a can of soda on the beach" in a professional ads setting. 
    
    Press Enter when each chat message is sent. 
    You might experience multiple rounds of conversations in that box.
    """

    asyncio.run(main(task_1))