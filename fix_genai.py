import re

with open("update_data.py", "r") as f:
    content = f.read()

old_block = """    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f\"\"\"You are a swing trading assistant. Analyze {ticker} currently at ${price:.2f}.
Recent price history (last 5 days): {history_summary}
The user does NOT do day trading and does NOT do options. 
Based on this simple data, provide a strict recommendation of BUY, SELL, or HOLD for a multi-week swing trade, and a 1-2 sentence justification.
Format your response exactly like this:
ACTION: [BUY/SELL/HOLD]
REASON: [Your 1-2 sentence reason]\"\"\"

    try:
        response = model.generate_content(prompt)
        content = response.text"""

new_block = """    from google import genai
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f\"\"\"You are a swing trading assistant. Analyze {ticker} currently at ${price:.2f}.
Recent price history (last 5 days): {history_summary}
The user does NOT do day trading and does NOT do options. 
Based on this simple data, provide a strict recommendation of BUY, SELL, or HOLD for a multi-week swing trade, and a 1-2 sentence justification.
Format your response exactly like this:
ACTION: [BUY/SELL/HOLD]
REASON: [Your 1-2 sentence reason]\"\"\"

    try:
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
        )
        content = response.text"""

if old_block in content:
    content = content.replace(old_block, new_block)
    with open("update_data.py", "w") as f:
        f.write(content)
    print("Successfully replaced block")
else:
    print("Block not found!")
