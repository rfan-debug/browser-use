import asyncio
from pathlib import Path

from playwright.async_api import async_playwright

PROFILE_DIR = Path.home() / '.cache' / 'my_playwright_profile'


async def run():
	PROFILE_DIR.mkdir(parents=True, exist_ok=True)
	async with async_playwright() as p:
		try:
			# launch a Chromium *context* that persists to disk
			context = await p.chromium.launch_persistent_context(user_data_dir=str(PROFILE_DIR), headless=False)
			page = await context.new_page()
			await page.goto(
				'https://beta.typeface.ai/canvas/674657?accountId=5802277a-d2a5-4f21-b927-d577577c3a17&chatId=1b47a9b7-d68e-4764-8b91-45d17b726fcd'
			)
			input('Press Enter to exit…')
		except Exception as e:
			raise e
		finally:
			await context.close()


if __name__ == '__main__':
	asyncio.run(run())
