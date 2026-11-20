"""Publish due Reels from queue/instagram.json via the official Instagram API (Instagram Login)."""
import json, os, sys, time, datetime as dt, requests

API = "https://graph.instagram.com/v23.0"
TOKEN, IG_USER = os.environ["IG_TOKEN"], os.environ["IG_USER_ID"]
QUEUE = "queue/instagram.json"

def call(method, path, **params):
    params["access_token"] = TOKEN
    r = requests.request(method, f"{API}/{path}", params=params, timeout=60)
    data = r.json()
    if r.status_code >= 400 or "error" in data:
        raise RuntimeError(data.get("error", data))
    return data

def wait(c):
    for _ in range(40):
        st = call("GET", c, fields="status_code")
        if st["status_code"] == "FINISHED": return
        if st["status_code"] in ("ERROR", "EXPIRED"): raise RuntimeError(f"container {c}: {st}")
        time.sleep(15)
    raise RuntimeError(f"container {c} still processing")

def create(item):
    t = item.get("type", "reel")
    if t == "image":
        return call("POST", f"{IG_USER}/media", image_url=item["image_url"], caption=item["caption"])["id"]
    if t == "carousel":
        kids = [call("POST", f"{IG_USER}/media", image_url=u, is_carousel_item="true")["id"] for u in item["image_urls"]]
        for k in kids: wait(k)
        return call("POST", f"{IG_USER}/media", media_type="CAROUSEL", children=",".join(kids), caption=item["caption"])["id"]
    return call("POST", f"{IG_USER}/media", media_type="REELS", video_url=item["video_url"],
                caption=item["caption"], share_to_feed="true")["id"]

def publish(item):
    c = create(item)
    for _ in range(40):                       # wait up to ~10 min for Instagram to process the video
        st = call("GET", c, fields="status_code,status")
        if st["status_code"] == "FINISHED":
            break
        if st["status_code"] in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"container {c}: {st}")
        time.sleep(15)
    else:
        raise RuntimeError(f"container {c} still processing")
    media_id = call("POST", f"{IG_USER}/media_publish", creation_id=c)["id"]
    link = call("GET", media_id, fields="permalink").get("permalink", "")
    return media_id, link

def main():
    q = json.load(open(QUEUE))
    now = dt.datetime.now(dt.timezone.utc)
    done_one = False
    for item in q:
        if item.get("status") != "pending" or done_one:
            continue
        if dt.datetime.fromisoformat(item["publish_at"]) > now:
            continue
        try:
            item["ig_media_id"], item["permalink"] = publish(item)
            item["status"], item["published_at"] = "published", now.isoformat()
            print("published", item["name"], item["permalink"])
        except Exception as e:
            item["attempts"] = item.get("attempts", 0) + 1
            item["last_error"] = str(e)[:500]
            if item["attempts"] >= 3:
                item["status"] = "failed"
            print("ERROR", item["name"], e, file=sys.stderr)
        done_one = True                        # at most one post per run keeps posts spaced out
    json.dump(q, open(QUEUE, "w"), indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
