import wandb
import matplotlib.pyplot as plt
import requests
import base64
import os

WANDB_API_KEY = "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"
IMGBB_API_KEY = "48a2f1ded4edf9a06342b279bcd10441"
PROJECT_NAME = "traffic-power-repair-sim"
ENTITY = "chaoyan"

wandb.login(key=WANDB_API_KEY)
api = wandb.Api()

runs = api.runs(f"{ENTITY}/{PROJECT_NAME}")

data = {"S1": {}, "S2": {}, "S3": {}, "S4": {}}

# we need pandas or just parse the list of dicts manually
for run in runs:
    strategy = run.name
    if strategy in data and not data[strategy]:
        hist = run.history(keys=["Time", "LSD_kW"], pandas=False)
        data[strategy]["time"] = [h.get("Time") for h in hist if "Time" in h]
        data[strategy]["load"] = [h.get("LSD_kW") for h in hist if "LSD_kW" in h]

        data[strategy]["auc"] = run.summary.get("AUC", 0)
        data[strategy]["makespan"] = run.summary.get("Makespan", 0)

# 1. Plot LSD curves
plt.figure(figsize=(10, 5))
for strategy in ["S1", "S2", "S3", "S4"]:
    if "time" in data[strategy] and data[strategy]["time"]:
        t = data[strategy]["time"]
        l = data[strategy]["load"]
        plt.step(t, l, where='post', label=f"{strategy} (AUC={data[strategy]['auc']:.1f})")

plt.xlabel("Time (hours)")
plt.ylabel("Restored Load LSD (kW)")
plt.title("Restored Load Over Time by Strategy")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("lsd_plot.png")
plt.close()

# 2. Plot AUC Bar chart
strategies = ["S1", "S2", "S3", "S4"]
aucs = [data[s].get("auc", 0) for s in strategies]

plt.figure(figsize=(6, 5))
bars = plt.bar(strategies, aucs, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
plt.xlabel("Strategy")
plt.ylabel("AUC (kW*h)")
plt.title("AUC Comparison")
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval, f'{yval:.1f}', ha='center', va='bottom')
plt.grid(axis='y')
plt.tight_layout()
plt.savefig("auc_plot.png")
plt.close()

# 3. Plot Makespan Bar chart
makespans = [data[s].get("makespan", 0) for s in strategies]

plt.figure(figsize=(6, 5))
bars = plt.bar(strategies, makespans, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
plt.xlabel("Strategy")
plt.ylabel("Makespan (hours)")
plt.title("Makespan Comparison")
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval, f'{yval:.2f}', ha='center', va='bottom')
plt.grid(axis='y')
plt.tight_layout()
plt.savefig("makespan_plot.png")
plt.close()

# Upload to imgbb
def upload_image(filepath):
    with open(filepath, "rb") as file:
        encoded_string = base64.b64encode(file.read()).decode('utf-8')

    url = "https://api.imgbb.com/1/upload"
    payload = {
        "key": IMGBB_API_KEY,
        "image": encoded_string
    }

    response = requests.post(url, data=payload)
    if response.status_code == 200:
        return response.json()["data"]["url"]
    else:
        print(f"Error uploading {filepath}: {response.text}")
        return None

urls = {}
for img in ["lsd_plot.png", "auc_plot.png", "makespan_plot.png"]:
    print(f"Uploading {img}...")
    url = upload_image(img)
    if url:
        print(f"Uploaded: {url}")
        urls[img] = url

with open("image_urls.txt", "w") as f:
    for img, url in urls.items():
        f.write(f"{img}: {url}\n")
