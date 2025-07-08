import asyncio
from pathlib import Path

from dotenv import load_dotenv
from playwright.async_api import async_playwright, ViewportSize

from browser_use.llm.azure.chat import ChatAzureOpenAI
from browser_use.browser import BrowserProfile

load_dotenv()
from browser_use import Agent

PROFILE_DIR = Path.home() / ".cache" / "my_playwright_profile"
PROFILE_DIR.mkdir(parents=True, exist_ok=True)


async def main(task: str):
    try:
        # launch a Chromium *context* that persists to disk
        agent = Agent(
            task=task,
            llm=ChatAzureOpenAI(
                model="gpt-4.1",
                temperature=0.2,
                api_version="2024-12-01-preview",
            ),
            browser_profile=BrowserProfile(
                user_data_dir=str(PROFILE_DIR),
                headless=False,
                window_size={'width': 999, 'height': 888},
                maximum_wait_page_load_time=20.0,
                minimum_wait_page_load_time=2.0,
            ),
            tool_calling_method="function_calling",
        )
        await agent.run()
    except Exception as e:
        raise e


if __name__ == "__main__":
    task_1 = """
    Go to https://beta.typeface.ai/projects/625275/canvas/9559021?accountId=692cafa4-6947-4d4f-b0c5-dfbdd6ab73f6&chatId=98bc1cb8-37ec-42a7-aae8-70f12587953b
    Then start chatting in the text box like a professional designer, with a goal of 
    "creating an image of with a can of soda on the beach" in a professional ads setting. 
    
    Press Enter when each chat message is sent. 
    You might experience multiple rounds of conversations in that box.
    NEVER click the BUGREPORT button. 
    NEVER try to identify anything on a loading page. You should simply wait on the Loading page. 
    """

    asyncio.run(main(task_1))
