import asyncio
import hashlib
from pathlib import Path

from dotenv import load_dotenv

from browser_use.browser import BrowserProfile
from browser_use.llm.azure.chat import ChatAzureOpenAI

load_dotenv()
from browser_use import Agent

PROFILE_DIR = Path.home() / '.cache' / 'my_playwright_profile'
PROFILE_DIR.mkdir(parents=True, exist_ok=True)


def six_digit_hash(input_str: str) -> str:
	digest = hashlib.sha256(input_str.encode('utf-8')).hexdigest()
	digest_int = int(digest, 16)
	hash_val = digest_int % (10**6)
	return f'{hash_val:06d}'


async def main(task: str):
	try:
		hash_str = six_digit_hash(task)
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
				window_size={'width': 1024, 'height': 888},
				maximum_wait_page_load_time=20.0,
				minimum_wait_page_load_time=2.0,
			),
			tool_calling_method='function_calling',
			generate_gif=f'agent_history_{hash_str}.gif',
		)
		await agent.run()
	except Exception as e:
		raise e


if __name__ == '__main__':
	BETA_TEXT = 'https://beta.typeface.ai'

	task_1 = f""" Following these instructions step by step:
    1. Go to the url: {BETA_TEXT}.
    2. click the `Assets` Tab.
    3. click `Add` on the top right.
    4. In the window popped up, click Next button. 
    5. Select upload from device and upload videos <= 3 minutes long for sizzle.
    
    ALWAYS REMEMBER the following: 
    1. Waiting on the loading page and never take actions there. 
    """

	asyncio.run(main(task_1))
