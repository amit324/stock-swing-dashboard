import re

with open("update_data.py", "r") as f:
    content = f.read()

old_parse = """        # Regex to extract blocks
        action_match = re.search(r'ACTION:\s*([^
+]+)', content, re.IGNORECASE)
        reason_match = re.search(r'REASON:\s*(.*?)(?=
+SOURCES:|$)', content, re.IGNORECASE | re.DOTALL)
        sources_match = re.search(r'SOURCES:\s*(.*)', content, re.IGNORECASE | re.DOTALL)"""

new_parse = r"""        # Regex to extract blocks
        action_match = re.search(r'ACTION:\s*([^\n]+)', content, re.IGNORECASE)
        reason_match = re.search(r'REASON:\s*(.*?)(?=\nSOURCES:|$)', content, re.IGNORECASE | re.DOTALL)
        sources_match = re.search(r'SOURCES:\s*(.*)', content, re.IGNORECASE | re.DOTALL)"""

if old_parse in content:
    content = content.replace(old_parse, new_parse)
    with open("update_data.py", "w") as f:
        f.write(content)
    print("Successfully replaced block")
else:
    print("Block not found!")
