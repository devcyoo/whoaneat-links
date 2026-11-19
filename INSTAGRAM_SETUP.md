# WhoaNeat Instagram auto-publish: one-time setup

Runs on GitHub Actions (free). It needs no Mac and no Claude session. Every 30 minutes it posts the next due Reel from queue/instagram.json, at most one per run, using Instagram's official Content Publishing API. The videos are pulled straight from their public Higgsfield URLs.

## 1. Make sure @whoa.neat is a Professional account
In the Instagram app: Settings → Account type and tools → it must be **Business** or **Creator**. Personal accounts can't use the API.

## 2. Meta app and token (Facebook login route; "Instagram login" now needs a business portfolio)
1. @whoa.neat must be linked to a Facebook Page (Instagram app → Edit profile → Page).
2. App "WhoaNeat Publisher" → Use cases → Customize → **API setup with Facebook login**. Add these permissions: instagram_basic, instagram_content_publish, pages_show_list, pages_read_engagement, business_management.
3. Graph API Explorer (developers.facebook.com/tools/explorer) → app WhoaNeat Publisher → User Token with those permissions → Generate → choose the Page and @whoa.neat.
4. Access Token Debugger → **Extend Access Token** (gives a long-lived user token).
5. In the Explorer, with the long-lived token, run `me/accounts?fields=name,access_token,instagram_business_account`. The Page's `access_token` is `IG_TOKEN` (it never expires), and `instagram_business_account.id` is `IG_USER_ID`.

## 3. Add 2 GitHub secrets
`gh secret set IG_TOKEN -R devcyoo/whoaneat-links` and `gh secret set IG_USER_ID -R devcyoo/whoaneat-links` (paste at the prompt). GH_PAT is no longer needed.

## 4. Test it
Actions tab → "Instagram auto-publish" → **Run workflow**. Nothing posts until the first scheduled time. For an instant test, set one item's `publish_at` to a past time and run the workflow again.

## Adding new videos
Append an item to queue/instagram.json:
`{"name": ..., "video_url": "<public mp4 url>", "caption": ..., "publish_at": "<ISO time, UTC>", "status": "pending"}`
