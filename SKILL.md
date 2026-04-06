---
name: wechat-mp
description: 微信公众号文章排版、素材上传、草稿发布基础设施。支持 Markdown 转公众号 HTML、本地预览、上传图片/封面素材、发布到公众号草稿箱。Use when the user already has article content and needs to: (1) format Markdown for 微信公众号, (2) preview rendering locally, (3) upload images or covers to get URL/media_id, or (4) publish a finished article into a WeChat Official Account draft box. Prefer `wechat-mp-write` when the task is upstream content strategy, drafting, title/digest generation, account selection, or full article packaging.
---

# WeChat MP

Use this skill as the low-level publishing layer for 微信公众号.

## Scope

Do:
- convert Markdown to公众号-compatible HTML
- preview article rendering locally
- upload images or cover assets
- publish completed articles to draft box

Do not use this skill as the first choice for:
- topic ideation
- article drafting from notes
- title/digest brainstorming
- deciding which公众号账号 should receive the article

For those, prefer the higher-level `wechat-mp-write` skill.

## Core workflow

1. Ensure credentials are available.
2. Format Markdown locally first.
3. Upload cover or inline images when needed.
4. Publish to draft box.
5. Review in `mp.weixin.qq.com` before final send.

## Credentials

Prefer environment variables:

```bash
export WECHAT_MP_APP_ID="你的公众号 AppID"
export WECHAT_MP_APP_SECRET="你的公众号 AppSecret"
```

Or point to a config file:

```bash
export WECHAT_MP_CONFIG="$HOME/.openclaw/wechat-config.json"
```

Never commit real credentials into the repository.

## Scripts

### `scripts/format.py`

Convert Markdown into公众号 HTML.

Examples:

```bash
python3 scripts/format.py --file article.md
python3 scripts/format.py --file article.md --template
python3 scripts/format.py --file article.md --output article.preview.html --template
```

Use this first when layout quality matters.

### `scripts/upload.py`

Upload images or permanent materials.

Examples:

```bash
python3 scripts/upload.py --file cover.png --type image
python3 scripts/upload.py --file image.png --temp
```

Use returned `media_id` or image URL in later publishing steps.

### `scripts/publish.py`

Publish a finished article to the draft box.

Examples:

```bash
python3 scripts/publish.py --file article.md --title "文章标题"
python3 scripts/publish.py --file article.md --title "文章标题" --author "作者名" --digest "摘要"
python3 scripts/publish.py --file article.md --title "文章标题" --thumb-media-id "MEDIA_ID"
```

## Operational rules

- Preview before publishing when the article is important.
- Keep paragraphs short for mobile reading.
- Treat local generated images and media ID caches as disposable outputs, not repository source files.
- If publishing fails, report the exact errcode / errmsg.
- Final publication still requires checking the draft inside the公众号后台.

## References

Read these only when needed:
- `references/api.md` for API behavior and payload details
- `references/styling.md` for formatting and style guidance
