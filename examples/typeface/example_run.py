import asyncio
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel

from browser_use.browser import BrowserProfile
from browser_use.llm.azure.chat import ChatAzureOpenAI

load_dotenv()
from browser_use import ActionResult, Agent, BrowserSession, Controller

PROFILE_DIR = Path.home() / '.cache' / 'my_playwright_profile'
PROFILE_DIR.mkdir(parents=True, exist_ok=True)

# Create controller for custom actions
controller = Controller()


# Custom action model for enabling disabled buttons
class EnableButtonModel(BaseModel):
	selector: str | None = None  # CSS selector, if None enables all disabled buttons


# Custom action model for force clicking buttons
class ForceClickModel(BaseModel):
	selector: str  # CSS selector for the button to force click


# Register custom action to enable disabled buttons
@controller.registry.action('Enable disabled buttons on the page to make them interactive', param_model=EnableButtonModel)
async def enable_disabled_buttons(params: EnableButtonModel, browser_session: BrowserSession):
	"""Enable disabled buttons by removing disabled attributes and triggering proper state changes"""
	if params.selector:
		script = f"""
			const button = document.querySelector('{params.selector}');
			if (button) {{
				// Store original state
				button.setAttribute('data-original-disabled', button.disabled.toString());
				
				// Remove disabled state
				button.removeAttribute('disabled');
				button.disabled = false;
				button.style.cursor = 'pointer';
				button.style.opacity = '1';
				button.style.pointerEvents = 'auto';
				
				// Remove disabled classes
				button.classList.remove('disabled', 'btn-disabled', 'button-disabled');
				
				// Trigger events to notify React/Vue components
				button.dispatchEvent(new Event('change', {{ bubbles: true }}));
				button.dispatchEvent(new Event('input', {{ bubbles: true }}));
				button.dispatchEvent(new CustomEvent('enabledByAutomation', {{ bubbles: true }}));
				
				// Try to find and update React component state
				const reactKey = Object.keys(button).find(key => key.startsWith('__reactInternalInstance') || key.startsWith('__reactFiber'));
				if (reactKey && button[reactKey]) {{
					try {{
						const fiber = button[reactKey];
						if (fiber.memoizedProps) {{
							fiber.memoizedProps.disabled = false;
						}}
					}} catch (e) {{
						console.log('Could not update React props:', e);
					}}
				}}
			}}
		"""
	else:
		script = """
			document.querySelectorAll('button[disabled], input[disabled], button[aria-disabled="true"], input[aria-disabled="true"]').forEach(element => {
				// Store original state
				element.setAttribute('data-original-disabled', element.disabled.toString());
				
				// Remove disabled state
				element.removeAttribute('disabled');
				element.removeAttribute('aria-disabled');
				element.disabled = false;
				element.style.cursor = 'pointer';
				element.style.opacity = '1';
				element.style.pointerEvents = 'auto';
				
				// Remove disabled classes
				element.classList.remove('disabled', 'btn-disabled', 'button-disabled');
				
				// Trigger events to notify React/Vue components
				element.dispatchEvent(new Event('change', { bubbles: true }));
				element.dispatchEvent(new Event('input', { bubbles: true }));
				element.dispatchEvent(new CustomEvent('enabledByAutomation', { bubbles: true }));
				
				// Try to find and update React component state
				const reactKey = Object.keys(element).find(key => key.startsWith('__reactInternalInstance') || key.startsWith('__reactFiber'));
				if (reactKey && element[reactKey]) {
					try {
						const fiber = element[reactKey];
						if (fiber.memoizedProps) {
							fiber.memoizedProps.disabled = false;
						}
					} catch (e) {
						console.log('Could not update React props:', e);
					}
				}
			});
		"""

	await browser_session.execute_javascript(script)
	return ActionResult(extracted_content='Successfully enabled disabled buttons and triggered state changes')


# Register custom action to force click buttons that may be disabled
@controller.registry.action('Force click a button even if it appears disabled', param_model=ForceClickModel)
async def force_click_button(params: ForceClickModel, browser_session: BrowserSession):
	"""Force click a button by bypassing normal disabled state checks"""
	script = f"""
		const button = document.querySelector('{params.selector}');
		if (button) {{
			// Store original state
			const originalDisabled = button.disabled;
			const originalPointerEvents = button.style.pointerEvents;
			
			// Temporarily enable the button
			button.disabled = false;
			button.style.pointerEvents = 'auto';
			
			// Try multiple click methods
			try {{
				// Method 1: Direct click
				button.click();
				
				// Method 2: Dispatch mouse events
				button.dispatchEvent(new MouseEvent('mousedown', {{ bubbles: true, cancelable: true }}));
				button.dispatchEvent(new MouseEvent('mouseup', {{ bubbles: true, cancelable: true }}));
				button.dispatchEvent(new MouseEvent('click', {{ bubbles: true, cancelable: true }}));
				
				// Method 3: Dispatch touch events for mobile
				button.dispatchEvent(new TouchEvent('touchstart', {{ bubbles: true, cancelable: true }}));
				button.dispatchEvent(new TouchEvent('touchend', {{ bubbles: true, cancelable: true }}));
				
				// Method 4: Focus and trigger Enter key
				button.focus();
				button.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', bubbles: true }}));
				button.dispatchEvent(new KeyboardEvent('keyup', {{ key: 'Enter', bubbles: true }}));
				
				console.log('Force clicked button:', button);
				return 'success';
			}} catch (e) {{
				console.error('Error force clicking button:', e);
				return 'error: ' + e.message;
			}} finally {{
				// Restore original state
				button.disabled = originalDisabled;
				button.style.pointerEvents = originalPointerEvents;
			}}
		}} else {{
			return 'error: button not found';
		}}
	"""

	result = await browser_session.execute_javascript(script)
	return ActionResult(extracted_content=f'Force click attempt completed: {result}')


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
			controller=controller,  # Use our custom controller with the enable buttons action
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
    Second, if you encounter any disabled buttons that prevent interaction, use the "Enable disabled buttons on the page to make them interactive" action to enable them.
    Third, type in `create an image with a running rabbit` in the chat box on the left-bottom side.
    Fourth, enable disabled buttons on the page to make them interactive
    Finally, press the `right-arrowed` button to send it to the chat. If normal clicking doesn't work, use the "Force click a button even if it appears disabled" action with the appropriate CSS selector.
    ALWAYS REMEMBER the following: 
    1. Waiting on the loading page and never take actions there. 
   	2. NEVER touch anything on the canvas, focus on the chat message itself.
    3. If buttons appear disabled or un-clickable, try these actions in order:
       a) First use "Enable disabled buttons on the page to make them interactive"
       b) If that doesn't work, use "Force click a button even if it appears disabled" with the button's CSS selector
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
