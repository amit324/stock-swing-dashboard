import re

with open(".github/workflows/update.yml", "r") as f:
    content = f.read()

if "workflow_dispatch:" not in content:
    content = content.replace("on:\n  schedule:", "on:\n  workflow_dispatch:\n  schedule:")
    with open(".github/workflows/update.yml", "w") as f:
        f.write(content)
