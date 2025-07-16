BETA_URL = 'https://beta.typeface.ai/canvas/674657?accountId=5802277a-d2a5-4f21-b927-d577577c3a17'
task_cases = {
	'task_1': f"""
	1. Go to the url: {BETA_URL}.
	2. Click the `Start a new chat` button on the top to start a new chat.
    3. Click the "Ask anything" input box to gain the editing access of this box and immediately type in `create a sizzle video` in the left bottom "Ask anything" input box.
    4. Press the `right-arrowed` button to send it to the chat.
    5. Wait until the agent's "Thinking" process is done. 
    6. Once the chat bot returns the message, click the "Ask anything" input box to gain the editing access of this box and immediately type in `proceed` in the textbox. 
    7. Press the `right-arrowed` button to send it to the chat.
    8. Wait in the chat window until the content is generated.
    9. If a content is generated, mark it as SUCCESS, otherwise, mark it as FAILED.
    ---
    ALWAYS REMEMBER the following: 
    1. Waiting on the loading page and never take actions there. 
   	2. NEVER touch anything on the canvas, focus on the chat message itself.
    3. Use the diagnostic action whenever something isn't working as expected to understand why.
    """,
	###
	'task_2': f"""
	FOLLOW the these instructions step by step:
	1. Go to the url: {BETA_URL}.
	2. Click the `Start a new chat` button on the top to start a new chat.
    3. Click the "Ask anything" input box to gain the editing access of this box and immediately type in `create a video of dancing penguins` in the left bottom "Ask anything" input box.
    4. Press the `right-arrowed` button to send it to the chat.
    5. Wait for 10 seconds.
    6. Click the "Ask anything" input box to gain the editing access of this box and immediately type in `proceed`,  
    7. Click the input text box to gain focus, and then press the `right-arrowed` button to send it to the chat.
    8. Wait for 60 seconds until the video generation process is done.
    9. If a video content, or even a placeholder, is generated as we expected, mark it as SUCCESS, otherwise, mark it as FAILED. 
    ---
    ALWAYS REMEMBER the following: 
    1. Waiting on the loading page and never take actions there. 
   	2. NEVER touch anything on the canvas, focus on the chat message itself.
    """,
}
