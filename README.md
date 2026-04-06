# wechat-mp

微信公众号文章排版与草稿发布工具。

这个仓库更偏**发布基础设施**，适合把已经写好的 Markdown 文章：
- 转成适合公众号的 HTML
- 本地预览排版效果
- 上传封面/图片素材
- 发布到公众号草稿箱

如果你要做的是**从选题、标题、摘要、封面文案，到最终文章写作与账号选择的一整套写稿 workflow**，建议配合更上层的 `wechat-mp-write` skill 使用。

## Features

- Markdown → 微信公众号 HTML
- 本地 HTML 预览
- 图片/封面素材上传
- 草稿箱发布
- 纯 Python 标准库实现，依赖轻

## Project Structure

```text
wechat-mp/
├── SKILL.md
├── README.md
├── scripts/
│   ├── format.py      # Markdown 转公众号 HTML
│   ├── publish.py     # 发布文章到草稿箱
│   ├── upload.py      # 上传图片/永久素材
│   ├── generate_image.py
│   ├── generate_leonardo.py
│   └── generate_openrouter.py
├── references/
│   ├── api.md
│   └── styling.md
└── assets/
    └── template.html
```

## Quick Start

### 1. 配置凭证

推荐使用环境变量：

```bash
export WECHAT_MP_APP_ID="你的公众号 AppID"
export WECHAT_MP_APP_SECRET="你的公众号 AppSecret"
```

也可以指定配置文件：

```bash
export WECHAT_MP_CONFIG="$HOME/.openclaw/wechat-config.json"
```

## Usage

### 1) 本地排版预览

```bash
python3 scripts/format.py --file article.md --template
```

或显式指定输出路径：

```bash
python3 scripts/format.py --file article.md --output article.preview.html --template
```

### 2) 发布到草稿箱

```bash
python3 scripts/publish.py --file article.md --title "文章标题"
```

带作者和摘要：

```bash
python3 scripts/publish.py \
  --file article.md \
  --title "文章标题" \
  --author "你的署名" \
  --digest "文章摘要"
```

### 3) 上传封面或图片素材

上传永久素材：

```bash
python3 scripts/upload.py --file cover.png --type image
```

如果你已经拿到了封面 `media_id`，发布时可以直接带上：

```bash
python3 scripts/publish.py \
  --file article.md \
  --title "文章标题" \
  --thumb-media-id "MEDIA_ID"
```

## Recommended Workflow

1. 先写 Markdown
2. 用 `format.py` 本地预览
3. 准备并上传封面素材
4. 用 `publish.py` 发到草稿箱
5. 登录 `mp.weixin.qq.com` 最终检查并手动发布

## Notes

- 不要把真实 `AppSecret` 提交到仓库
- 本仓库不包含真实业务文章和本地生成图片
- 生成类脚本（如封面生成）更适合本地实验，不建议把批量生成产物直接提交

## Future Improvements

- 更稳健的 Markdown 解析
- 多公众号账号选择
- 本地图片自动上传替换
- 更完整的模板系统
- 更好的错误提示与重试逻辑
