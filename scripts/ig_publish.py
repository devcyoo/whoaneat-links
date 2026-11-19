"""Publish due Reels from queue/instagram.json via the official Instagram Graph API (Facebook Login, Page token)."""
import json, os, sys, time, datetime as dt, requests

API = "https://graph.facebook.com/v23.0"
TOKEN, IG_USER = os.environ["IG_TOKEN"], os.environ.get("IG_USER_ID", "").strip()
QUEUE = "queue/instagram.json"

def call(method, path, **params):
    params["access_token"] = TOKEN
    r = requests.request(method, f"{API}/{path}", params=params, timeout=60)
    data = r.json()
    if r.status_code >= 400 or "error" in data:
        raise RuntimeError(data.get("error", data))
    return data

def publish(item):
    c = call("POST", f"{IG_USER}/media", media_type="REELS", video_url=item["video_url"],
             caption=item["caption"], share_to_feed="true")["id"]
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

def resolve_account():
    """Accept a Page token or a user token; find the Page linked to Instagram and use its token."""
    global IG_USER, TOKEN
    dbg = call("GET", "debug_token", input_token=TOKEN).get("data", {})
    exp = dbg.get("expires_at", 0)
    print("token type:", dbg.get("type"), "| expires:", "never" if not exp else dt.datetime.fromtimestamp(exp, dt.timezone.utc).isoformat())
    if dbg.get("type") == "USER":
        pages = call("GET", "me/accounts", fields="name,access_token,instagram_business_account").get("data", [])
        page = next((p for p in pages if p.get("instagram_business_account")), None)
        if not page:
            raise RuntimeError("no Facebook Page linked to an Instagram account was found for this token")
        print("using Page:", page["name"])
        TOKEN = page["access_token"]
        IG_USER = IG_USER or page["instagram_business_account"]["id"]
    elif not IG_USER:
        IG_USER = call("GET", "me", fields="instagram_business_account")["instagram_business_account"]["id"]

def main():
    global IG_USER, TOKEN
    resolve_account()
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
