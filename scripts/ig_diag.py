"""Diagnose IG publishing without posting anything: creates containers only (they expire unpublished)."""
import os, requests, time
T, U = os.environ["IG_TOKEN"], os.environ["IG_USER_ID"]
B = "https://graph.facebook.com/v23.0"
def req(m, p, **k):
    k["access_token"] = T
    r = requests.request(m, f"{B}/{p}", params=k, timeout=90)
    return r.status_code, r.json()
print("user:", req("GET", U, fields="id,username,account_type")[1])
print("me:", req("GET", "me", fields="id,name")[1])
print("limit:", req("GET", f"{U}/content_publishing_limit", fields="config,quota_usage")[1])
img = "https://whoaneat.com/posts/cold-0.jpg"
print("img container:", req("POST", f"{U}/media", image_url=img, caption="diag")[1])
v = "https://d2ol7oe51mr4n9.cloudfront.net/user_3MI2NyIthUwXHQgnoVDvzfzAvZ9/7a04660a-8e25-4cd1-8327-d0d29fab3fa6.mp4"
s, r = req("POST", f"{U}/media", media_type="REELS", video_url=v, caption="diag")
print("reel container (no share_to_feed):", s, r)
if "id" in r:
    for _ in range(12):
        time.sleep(10); print(" status:", req("GET", r["id"], fields="status_code,status")[1])
