import os
import requests
import base64
import json

IMGBB_API_KEY = "48a2f1ded4edf9a06342b279bcd10441"
UPLOAD_URL = "https://api.imgbb.com/1/upload"

def upload_image(filepath):
    with open(filepath, "rb") as file:
        payload = {
            "key": IMGBB_API_KEY,
            "image": base64.b64encode(file.read()).decode('utf-8')
        }
        res = requests.post(UPLOAD_URL, data=payload)

        if res.status_code == 200:
            data = res.json()
            return data["data"]["url"]
        else:
            print(f"Failed to upload {filepath}: {res.text}")
            return None

if __name__ == "__main__":
    images = ["lsd_curves.png", "auc_comparison.png", "makespan_comparison.png"]
    urls = {}
    for img in images:
        if os.path.exists(img):
            url = upload_image(img)
            if url:
                urls[img] = url
                print(f"Uploaded {img}: {url}")
        else:
            print(f"File {img} not found.")

    with open("image_urls.json", "w") as f:
        json.dump(urls, f, indent=4)
