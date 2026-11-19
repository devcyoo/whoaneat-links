"""Extend the 60-day Instagram token and store the new one in the repo secret IG_TOKEN."""
import os, base64, requests
from nacl import encoding, public

tok = requests.get("https://graph.instagram.com/refresh_access_token",
                   params={"grant_type": "ig_refresh_token", "access_token": os.environ["IG_TOKEN"]},
                   timeout=60).json()["access_token"]
repo, h = os.environ["REPO"], {"Authorization": f"Bearer {os.environ['GH_PAT']}",
                               "Accept": "application/vnd.github+json"}
key = requests.get(f"https://api.github.com/repos/{repo}/actions/secrets/public-key", headers=h, timeout=30).json()
box = public.SealedBox(public.PublicKey(key["key"].encode(), encoding.Base64Encoder()))
enc = base64.b64encode(box.encrypt(tok.encode())).decode()
r = requests.put(f"https://api.github.com/repos/{repo}/actions/secrets/IG_TOKEN", headers=h,
                 json={"encrypted_value": enc, "key_id": key["key_id"]}, timeout=30)
r.raise_for_status()
print("IG_TOKEN refreshed")
