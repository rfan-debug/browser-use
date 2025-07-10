import asyncio
from pathlib import Path

from dotenv import load_dotenv

from browser_use.browser import BrowserProfile
from browser_use.llm.azure.chat import ChatAzureOpenAI

load_dotenv()
from browser_use import Agent

PROFILE_DIR = Path.home() / '.cache' / 'my_playwright_profile'
PROFILE_DIR.mkdir(parents=True, exist_ok=True)


async def main(task: str):
	try:
		# launch a Chromium *context* that persists to disk
		agent = Agent(
			task=task,
			llm=ChatAzureOpenAI(
				model='gpt-4.1',
				temperature=0.2,
				api_version='2024-12-01-preview',
			),
			browser_profile=BrowserProfile(
				user_data_dir=str(PROFILE_DIR),
				headless=False,
				window_size={'width': 999, 'height': 888},
				maximum_wait_page_load_time=20.0,
				minimum_wait_page_load_time=2.0,
			),
			tool_calling_method='function_calling',
			generate_gif=True,
		)
		await agent.run()
	except Exception as e:
		raise e


if __name__ == '__main__':
	LOCAL_TEXT = 'http://localhost:3000/canvas/625275?accountId=692cafa4-6947-4d4f-b0c5-dfbdd6ab73f6&chatId=fea74f70-d0c7-4b8c-b1d2-8206ad168033'
	PREVIEW_TEXT = 'https://kind-pond-08f7fc10f-preview.eastus2.3.azurestaticapps.net/canvas/661623?accountId=692cafa4-6947-4d4f-b0c5-dfbdd6ab73f6'
	BETA_TEXT = 'https://beta.typeface.ai/canvas/661623?accountId=692cafa4-6947-4d4f-b0c5-dfbdd6ab73f6&chatId=0215b5b6-460c-4ff1-8c44-4959213a1e75'
	BETA_TEXT2 = 'https://beta.typeface.ai'

	task_1 = f"""
    First, Go to the url: {BETA_TEXT}.
    Second, type in `create an image with a running rabbit` in the chat box on the left-bottom side.
    Third, press the `right-arrowed` button to send it to the chat.
    ALWAYS REMEMBER the following: 
    1. Waiting on the loading page and never take actions there. 
   	2. NEVER touch anything on the cavas, focus on the chat message itself.
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
