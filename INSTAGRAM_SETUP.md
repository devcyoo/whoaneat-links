# WhoaNeat Instagram auto-publish: one-time setup

Runs on GitHub Actions (free). It needs no Mac and no Claude session. Every 30 minutes it posts the next due Reel from queue/instagram.json, at most one per run, using Instagram's official Content Publishing API. The videos are pulled straight from their public Higgsfield URLs.

## 1. Make sure @whoa.neat is a Professional account
In the Instagram app: Settings → Account type and tools → it must be **Business** or **Creator**. Personal accounts can't use the API.

## 2. Create the Meta app (about 5 minutes)
1. Go to developers.facebook.com → My Apps → **Create app** → use case **"Manage messaging & content on Instagram"** → no business portfolio needed → Create.
2. In the app: **Instagram → API setup with Instagram login** → section **"Generate access tokens"** → **Add account** → log in as **whoa.neat** → allow the permissions (instagram_business_basic, instagram_business_content_publish).
3. Click **Generate token** next to whoa.neat and copy it. This is a long-lived token, valid for 60 days and refreshed weekly by the workflow.
4. Copy the **Instagram user ID** shown next to the account (a long number).

The app can stay in **Development mode**: the app's own admin and tester accounts can publish without App Review.

## 3. Add 3 GitHub secrets
In the repo devcyoo/whoaneat-links → Settings → Secrets and variables → Actions → New repository secret:
- `IG_TOKEN`: the token from step 2.3
- `IG_USER_ID`: the user ID from step 2.4
- `GH_PAT`: a fine-grained GitHub token for this repo only, with **Secrets: Read and write**. The weekly job uses it to save the refreshed IG_TOKEN.

## 4. Test it
Actions tab → "Instagram auto-publish" → **Run workflow**. Nothing posts until the first scheduled time. For an instant test, set one item's `publish_at` to a past time and run the workflow again.

## Adding new videos
Append an item to queue/instagram.json:
`{"name": ..., "video_url": "<public mp4 url>", "caption": ..., "publish_at": "<ISO time, UTC>", "status": "pending"}`
