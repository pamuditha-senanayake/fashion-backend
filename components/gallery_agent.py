# agents/gallery_agent.py
import requests
from fastapi import APIRouter, HTTPException, Query
from pathlib import Path

router = APIRouter()

# 👇 Directly insert token & page id (not using env)
PAGE_ACCESS_TOKEN = "EAALaVutBE04BPvQ2Io2QmTzEqbCsv6BlrbZCNFu5ZClOhZCVdzZBGiXTJZB0L2YPFnBRxTlZC3y41wfTlvxQYK36lFsOEQTCMoq2ZAmx0ri7X0l4kZBslcVluBO2wDLZBDecYZCenIcnkQyuHMA7hsd2TiwGJmDtwSHpaGHhGb5bfSrSQYsZCKfcGzdZBdpmmZAvfVtXVJ3GcUVjBGOAGDiIC8aUzDigsgLcT86wO2ZAOggHMn9CHTgjXsJMHAeUMaegZDZD"
PAGE_ID = "108389977731191"

DOWNLOAD_FOLDER = Path("downloads")
DOWNLOAD_FOLDER.mkdir(exist_ok=True)


@router.get("/fetch_gallery")
def fetch_gallery(limit: int = 20, refresh: bool = Query(False)):
    """
    Load images already downloaded in `downloads` folder.
    If refresh=True, fetch new posts from FB Graph API and download new images.
    """
    print("[Gallery] Starting fetch_gallery, refresh:", refresh)

    # 1️⃣ Load already downloaded images
    local_images = []
    for f in DOWNLOAD_FOLDER.glob("*.jpg"):
        img_id = f.stem.replace("post_", "")
        local_images.append({
            "id": img_id,
            "url": f"/downloads/{f.name}",  # frontend can access via static route
            "local_path": str(f),
            "permalink": "#",  # optional, no permalink for old local images
        })

    # Return only local images if no refresh
    if not refresh:
        print(f"[Gallery] Returning {len(local_images)} local images only")
        return local_images[:limit]

    # 2️⃣ Fetch from FB Graph API
    url = (
        f"https://graph.facebook.com/v23.0/{PAGE_ID}/posts"
        f"?fields=id,message,created_time,permalink_url,full_picture"
        f"&limit={limit}"
        f"&access_token={PAGE_ACCESS_TOKEN}"
    )
    print("[Gallery] Requesting URL:", url)

    try:
        resp = requests.get(url)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Request failed: {e}")

    data = resp.json().get("data", [])
    new_images = []

    for post in data:
        img_url = post.get("full_picture")
        if img_url:
            filename = DOWNLOAD_FOLDER / f"post_{post['id']}.jpg"
            if not filename.exists():  # only download new ones
                try:
                    img_data = requests.get(img_url).content
                    with open(filename, "wb") as f:
                        f.write(img_data)
                    print(f"[Gallery] Downloaded {filename}")
                except Exception as e:
                    print(f"[Gallery] Failed to download {img_url}: {e}")
                    continue

            new_images.append({
                "id": post["id"],
                "message": post.get("message"),
                "url": f"/downloads/{filename.name}",
                "local_path": str(filename),
                "permalink": post.get("permalink_url"),
                "created_time": post.get("created_time"),
            })

    # 3️⃣ Combine local and new images (deduplicate by id)
    combined = {img['id']: img for img in local_images + new_images}
    print(f"[Gallery] Returning {len(combined)} total images")
    return list(combined.values())[:limit]
