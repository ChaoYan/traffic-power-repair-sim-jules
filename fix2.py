import re

with open("sim_engine.py", "r") as f:
    lines = f.readlines()

# Find where EnhancedSimEngine starts, and delete everything from the previous one.
# We will just write a clean sim_engine.py

with open("sim_engine.py", "r") as f:
    text = f.read()

cleaned = re.sub(r'class EnhancedSimEngine.*?class EnhancedSimEngine', 'class EnhancedSimEngine', text, flags=re.DOTALL)

with open("sim_engine.py", "w") as f:
    f.write(cleaned)
