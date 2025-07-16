import asyncio
import hashlib
import json
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel

from browser_use.agent.views import ActionResult
from browser_use.browser import BrowserProfile
from browser_use.llm.azure.chat import ChatAzureOpenAI

load_dotenv()
from browser_use import Agent, BrowserSession, Controller

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


# Custom action model for diagnosing chat issues
class DiagnoseChatModel(BaseModel):
	pass  # No parameters needed


# Register custom action to enable disabled buttons safely
@controller.registry.action('Enable disabled buttons on the page to make them interactive', param_model=EnableButtonModel)
async def enable_disabled_buttons(params: EnableButtonModel, browser_session: BrowserSession):
	"""Enable disabled buttons with minimal interference to the application workflow"""
	if params.selector:
		script = f"""
			const button = document.querySelector('{params.selector}');
			if (button) {{
				// Store original state for debugging
				const originalState = {{
					disabled: button.disabled,
					ariaDisabled: button.getAttribute('aria-disabled'),
					pointerEvents: button.style.pointerEvents,
					opacity: button.style.opacity
				}};
				console.log('Original button state:', originalState);

				// Minimal changes to avoid breaking React state
				button.removeAttribute('disabled');
				button.disabled = false;
				button.removeAttribute('aria-disabled');

				// Only modify style if it's explicitly blocking interaction
				if (button.style.pointerEvents === 'none') {{
					button.style.pointerEvents = 'auto';
				}}

				console.log('Button enabled successfully');
				return 'enabled';
			}} else {{
				console.log('Button not found with selector: {params.selector}');
				return 'not_found';
			}}
		"""
	else:
		script = """
			let enabledCount = 0;
			document.querySelectorAll('button[disabled], input[disabled], button[aria-disabled="true"], input[aria-disabled="true"]').forEach(element => {
				// Store original state for debugging
				const originalState = {
					disabled: element.disabled,
					ariaDisabled: element.getAttribute('aria-disabled'),
					pointerEvents: element.style.pointerEvents,
					opacity: element.style.opacity
				};
				console.log('Original element state:', originalState);

				// Minimal changes to avoid breaking React state
				element.removeAttribute('disabled');
				element.disabled = false;
				element.removeAttribute('aria-disabled');

				// Only modify style if it's explicitly blocking interaction
				if (element.style.pointerEvents === 'none') {
					element.style.pointerEvents = 'auto';
				}

				enabledCount++;
			});

			console.log(`Enabled ${enabledCount} buttons`);
			return `enabled_${enabledCount}`;
		"""

	result = await browser_session.execute_javascript(script)
	return ActionResult(extracted_content=f'Button enabling completed: {result}')


# # Register custom action to force click buttons that may be disabled
# @controller.registry.action('Force click a button even if it appears disabled', param_model=ForceClickModel)
# async def force_click_button(params: ForceClickModel, browser_session: BrowserSession):
# 	"""Force click a button by bypassing normal disabled state checks"""
# 	script = f"""
# 		const button = document.querySelector('{params.selector}');
# 		if (button) {{
# 			// Store original state
# 			const originalDisabled = button.disabled;
# 			const originalPointerEvents = button.style.pointerEvents;
#
# 			// Temporarily enable the button
# 			button.disabled = false;
# 			button.style.pointerEvents = 'auto';
#
# 			// Try multiple click methods
# 			try {{
# 				// Method 1: Direct click
# 				button.click();
#
# 				// Method 2: Dispatch mouse events
# 				button.dispatchEvent(new MouseEvent('mousedown', {{ bubbles: true, cancelable: true }}));
# 				button.dispatchEvent(new MouseEvent('mouseup', {{ bubbles: true, cancelable: true }}));
# 				button.dispatchEvent(new MouseEvent('click', {{ bubbles: true, cancelable: true }}));
#
# 				// Method 3: Dispatch touch events for mobile
# 				button.dispatchEvent(new TouchEvent('touchstart', {{ bubbles: true, cancelable: true }}));
# 				button.dispatchEvent(new TouchEvent('touchend', {{ bubbles: true, cancelable: true }}));
#
# 				// Method 4: Focus and trigger Enter key
# 				button.focus();
# 				button.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', bubbles: true }}));
# 				button.dispatchEvent(new KeyboardEvent('keyup', {{ key: 'Enter', bubbles: true }}));
#
# 				console.log('Force clicked button:', button);
# 				return 'success';
# 			}} catch (e) {{
# 				console.error('Error force clicking button:', e);
# 				return 'error: ' + e.message;
# 			}} finally {{
# 				// Restore original state
# 				button.disabled = originalDisabled;
# 				button.style.pointerEvents = originalPointerEvents;
# 			}}
# 		}} else {{
# 			return 'error: button not found';
# 		}}
# 	"""
#
# 	result = await browser_session.execute_javascript(script)
# 	return ActionResult(extracted_content=f'Force click attempt completed: {result}')
#
#
# # Register diagnostic action to understand chat workflow issues
# @controller.registry.action(
# 	'Diagnose chat workflow issues and identify what is preventing message sending', param_model=DiagnoseChatModel
# )
# async def diagnose_chat_issues(params: DiagnoseChatModel, browser_session: BrowserSession):
# 	"""Diagnose potential issues with the chat workflow"""
# 	script = """
# 		// Comprehensive diagnostic of chat elements
# 		const diagnosis = {
# 			timestamp: new Date().toISOString(),
# 			url: window.location.href,
# 			errors: [],
# 			elements: {},
# 			validation: {},
# 			eventListeners: {}
# 		};
#
# 		try {
# 			// Look for chat input elements
# 			const chatInputs = document.querySelectorAll('input[type="text"], textarea, [contenteditable="true"]');
# 			diagnosis.elements.chatInputs = Array.from(chatInputs).map(input => ({
# 				tagName: input.tagName,
# 				type: input.type,
# 				disabled: input.disabled,
# 				value: input.value,
# 				placeholder: input.placeholder,
# 				id: input.id,
# 				className: input.className,
# 				styles: {
# 					display: getComputedStyle(input).display,
# 					visibility: getComputedStyle(input).visibility,
# 					pointerEvents: getComputedStyle(input).pointerEvents
# 				}
# 			}));
#
# 			// Look for send buttons
# 			const sendButtons = document.querySelectorAll('button, input[type="submit"], [role="button"]');
# 			diagnosis.elements.sendButtons = Array.from(sendButtons).map(button => ({
# 				tagName: button.tagName,
# 				type: button.type,
# 				disabled: button.disabled,
# 				textContent: button.textContent?.trim(),
# 				innerHTML: button.innerHTML,
# 				id: button.id,
# 				className: button.className,
# 				ariaLabel: button.getAttribute('aria-label'),
# 				styles: {
# 					display: getComputedStyle(button).display,
# 					visibility: getComputedStyle(button).visibility,
# 					pointerEvents: getComputedStyle(button).pointerEvents,
# 					cursor: getComputedStyle(button).cursor
# 				}
# 			}));
#
# 			// Check for form elements
# 			const forms = document.querySelectorAll('form');
# 			diagnosis.elements.forms = Array.from(forms).map(form => ({
# 				action: form.action,
# 				method: form.method,
# 				id: form.id,
# 				className: form.className,
# 				elements: form.elements.length
# 			}));
#
# 			// Check for JavaScript errors
# 			const originalError = window.onerror;
# 			const errors = [];
# 			window.onerror = function(msg, url, line, col, error) {
# 				errors.push({ msg, url, line, col, error: error?.toString() });
# 				if (originalError) originalError.apply(this, arguments);
# 			};
#
# 			// Look for React/Vue roots
# 			const reactRoots = document.querySelectorAll('[data-reactroot], [data-react-root]');
# 			diagnosis.elements.reactRoots = reactRoots.length;
#
# 			// Check for validation messages
# 			const validationMessages = document.querySelectorAll('[role="alert"], .error, .validation-error, .invalid-feedback');
# 			diagnosis.validation.messages = Array.from(validationMessages).map(msg => ({
# 				textContent: msg.textContent?.trim(),
# 				className: msg.className,
# 				visible: getComputedStyle(msg).display !== 'none'
# 			}));
#
# 			// Check console errors
# 			const consoleErrors = [];
# 			const originalConsoleError = console.error;
# 			console.error = function(...args) {
# 				consoleErrors.push(args.join(' '));
# 				originalConsoleError.apply(console, arguments);
# 			};
#
# 			diagnosis.validation.consoleErrors = consoleErrors;
#
# 			return JSON.stringify(diagnosis, null, 2);
#
# 		} catch (error) {
# 			diagnosis.errors.push({
# 				type: 'diagnostic_error',
# 				message: error.message,
# 				stack: error.stack
# 			});
# 			return JSON.stringify(diagnosis, null, 2);
# 		}
# 	"""
#
# 	result = await browser_session.execute_javascript(script)
# 	return ActionResult(extracted_content=f'Chat workflow diagnosis:\n{result}')


def six_digit_hash(input_str: str) -> str:
	digest = hashlib.sha256(input_str.encode('utf-8')).hexdigest()
	digest_int = int(digest, 16)
	hash_val = digest_int % (10**6)
	return f'{hash_val:06d}'


async def main(task: str):
	try:
		hash_str = six_digit_hash(task)
		dt_now = datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
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
			generate_gif=f'agent_history_{dt_now}_{hash_str}.gif',
			controller=controller,  # Use our custom controller with the enable buttons action
		)
		res = await agent.run()
		return res
	except Exception as e:
		raise e


if __name__ == '__main__':
	from example_tasks import task_cases

	agent_history_list, agent_usage_list = asyncio.run(main(task_cases['task_2']))
	for i, hist in enumerate(agent_history_list[1]):
		with open(f'agent_history_{i}.json', 'w') as f:
			json.dump(hist.model_dump(), f, indent=4)

	print('Final result: ', agent_history_list[1][-1].results[0].success)
