import re
with open("sim_engine.py", "r") as f:
    content = f.read()

# remove dummy get_travel_time from EnhancedSimEngine
content = re.sub(r'    def get_travel_time.*?pass\n\n', '', content, flags=re.DOTALL)
with open("sim_engine.py", "w") as f:
    f.write(content)
