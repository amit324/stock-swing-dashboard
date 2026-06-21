import re

with open("update_data.py", "r") as f:
    content = f.read()

old_block = """    try:
        response = client.models.generate_content(
            model='gemini-flash',
            contents=prompt,
        )
        content = response.text"""

new_block = """    try:
        models_to_try = ['gemini-3.1-flash', 'gemini-3.0-flash', 'gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-flash-latest', 'gemini-pro']
        response = None
        for m in models_to_try:
            try:
                response = client.models.generate_content(model=m, contents=prompt)
                break
            except Exception as e:
                print(f"Model {m} failed: {e}")
                
        if not response:
            raise Exception("All Gemini models failed")
            
        content = response.text"""

if old_block in content:
    content = content.replace(old_block, new_block)
    with open("update_data.py", "w") as f:
        f.write(content)
    print("Successfully replaced block")
else:
    print("Block not found!")
