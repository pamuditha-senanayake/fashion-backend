# agents/gallery_agent.py
import requests
import os
from fastapi import APIRouter, HTTPException

router = APIRouter()
#
# PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")
# PAGE_ID = os.getenv("FB_PAGE_ID")  # Your page ID

PAGE_ACCESS_TOKEN = "EAALaVutBE04BPieZC45aYEtcCtDTCnu5O065y75wkt2HCe0bIARMwKmMm5iIUeAozZBXcxzLI0WatpZBJ840ycOQ1lZApmHwTqXPqiyiJMb24h0cpMP9DZBCn5ddTs9IaRr23xtnVuefdZCaYSPeQuXxKZB8k8KZB6yO2ZAuNAuNE4ccVEILpdIgxTr5JcLFrmq9NGyOSxIHd38bRkJnTGBMZBMnscqPdyLEawxugWEwksbOMQ67iUVljekDc4hgZDZD"
PAGE_ID = "108389977731191"

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@router.get("/fetch_gallery")
def fetch_gallery(limit: int = 20):
    """
    Fetch latest posts from FB page and return images & links
    """
    print("Starting fetch_gallery...")  # DEBUG

    if not PAGE_ACCESS_TOKEN or not PAGE_ID:
        print("FB credentials missing!")  # DEBUG
        raise HTTPException(status_code=500, detail="FB credentials not set in environment")

    url = (
        f"https://graph.facebook.com/v23.0/{PAGE_ID}/posts"
        f"?fields=id,message,created_time,permalink_url,full_picture"
        f"&limit={limit}"
        f"&access_token={PAGE_ACCESS_TOKEN}"
    )

    print(f"Requesting URL: {url}")  # DEBUG

    try:
        resp = requests.get(url)
        print(f"Response status code: {resp.status_code}")  # DEBUG
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")  # DEBUG
        raise HTTPException(status_code=500, detail=f"Request failed: {e}")

    data = resp.json().get("data", [])
    print(f"Number of posts fetched: {len(data)}")  # DEBUG

    images = []

    for i, post in enumerate(data, start=1):
        img_url = post.get("full_picture")
        if img_url:
            filename = f"{DOWNLOAD_FOLDER}/post_{i}.jpg"
            try:
                img_data = requests.get(img_url).content
                with open(filename, "wb") as f:
                    f.write(img_data)
                print(f"Saved image {filename}")  # DEBUG
            except Exception as e:
                print(f"Failed to download image {img_url}: {e}")  # DEBUG
                continue

            images.append({
                "id": post["id"],
                "message": post.get("message"),
                "url": img_url,
                "local_path": filename,
                "permalink": post.get("permalink_url"),
                "created_time": post.get("created_time"),
            })

    print(f"Total images returned: {len(images)}")  # DEBUG
    return images
