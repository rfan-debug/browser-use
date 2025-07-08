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
            generate_gif=True,
        )
        await agent.run()
    except Exception as e:
        raise e


if __name__ == "__main__":

    LOCAL_TEXT = "http://localhost:3000/canvas/625275?accountId=692cafa4-6947-4d4f-b0c5-dfbdd6ab73f6&chatId=f4218945-88ed-431e-9c97-d1622514b43e"
    ALPHA_TEXT = "https://beta.typeface.ai/?accountId=692cafa4-6947-4d4f-b0c5-dfbdd6ab73f6"
    task_1 = f"""
    Go to {ALPHA_TEXT}.
    Go to `Cool project` project and create an image with `strawberry` inside.
    
    ALWAYS REMEMBER the following: 
    Waiting on the loading page and never take actions there. 
    """
    #     Then start chatting in the text box like a professional designer, with a goal of
    #     "creating an image of with a can of soda on the beach" in a professional ads setting.
    #
    #     Press Enter when each chat message is sent.
    #     You might experience multiple rounds of conversations in that box.
    #     with "right-direction arrow" on it.
    #     NEVER click the BUGREPORT button.
    #     NEVER try to identify anything on a loading page. You should simply wait on the Loading page.

    asyncio.run(main(task_1))
