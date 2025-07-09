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
				'https://kind-pond-08f7fc10f-preview.eastus2.3.azurestaticapps.net/canvas/625275?'
				'accountId=692cafa4-6947-4d4f-b0c5-dfbdd6ab73f6&'
				'chatId=fea74f70-d0c7-4b8c-b1d2-8206ad168033'
			)
			input('Press Enter to exit…')
		except Exception as e:
			raise e
		finally:
			await context.close()


if __name__ == '__main__':
	asyncio.run(run())
