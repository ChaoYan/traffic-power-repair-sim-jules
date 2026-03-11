import base64
import requests

API_KEY = "48a2f1ded4edf9a06342b279bcd10441"
url = "https://api.imgbb.com/1/upload"

images_to_upload = ["lsd_curve.png", "auc_bar.png", "makespan_bar.png"]
urls = {}

for img_path in images_to_upload:
    with open(img_path, "rb") as file:
        payload = {
            "key": API_KEY,
            "image": base64.b64encode(file.read()),
        }
        response = requests.post(url, data=payload)
        result = response.json()
        if result.get("success"):
            img_url = result["data"]["url"]
            urls[img_path] = img_url
            print(f"Uploaded {img_path}: {img_url}")
        else:
            print(f"Failed to upload {img_path}: {result}")

with open("img_urls.txt", "w") as f:
    for k, v in urls.items():
        f.write(f"{k}: {v}\n")
