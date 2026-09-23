import re

path = "apps/api/app/modules/recommendations/seed_catalogue.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

new_content, count = re.subn(r'"url":\s*"https://mock\.igotkarmayogi\.gov\.in[^"]*"', '"url": None', content)
print(f"Replaced {count} occurrences in {path}")

with open(path, "w", encoding="utf-8") as f:
    f.write(new_content)
