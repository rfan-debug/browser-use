from pathlib import Path

from playwright.sync_api import sync_playwright

PROFILE_DIR = Path.home() / ".cache" / "my_playwright_profile"

def run():
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        try:
            # launch a Chromium *context* that persists to disk
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(PROFILE_DIR),
                headless=False
            )
            page = context.new_page()
            page.goto("https://beta.typeface.ai/?accountId=6195aaed-f8f5-491b-b351-f51e4e5a60df")
            # … log in once, then close; state is saved in PROFILE_DIR …
            input("Press Enter to exit…")
        except Exception as e:
            raise e
        finally:
            context.close()

if __name__ == "__main__":
    run()