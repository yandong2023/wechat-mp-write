---
name: wechat-mp
description: 微信公众号文章排版、编辑和发布。支持 Markdown 转公众号格式、自动排版、草稿发布、素材管理。Use when: (1) 发布文章到微信公众号，(2) 将 Markdown 转换为公众号排版格式，(3) 管理公众号素材和图片，(4) 批量发布或定时发布内容。
---

# 微信公众号运营助手

专业的微信公众号文章排版和发布工具。

## 核心功能

1. **Markdown 转公众号排版** - 自动转换格式、添加样式
2. **发布草稿** - 上传文章到公众号草稿箱
3. **素材管理** - 上传图片、获取 media_id
4. **批量发布** - 支持多篇内容批量处理

## 快速开始

### 1. 配置凭证

确保环境变量已设置：
```bash
export WECHAT_MP_APP_ID="wx672539caabdcc349"
export WECHAT_MP_APP_SECRET="32f4359cc7795a982c291e93b377092c"
```

或使用配置文件：
```bash
export WECHAT_MP_CONFIG="/Users/yandong/.openclaw/wechat-config.json"
```

### 2. 发布文章

```bash
# 直接发布 Markdown 文件
python3 scripts/publish.py --file article.md --title "文章标题"

# 带封面图
python3 scripts/publish.py --file article.md --title "标题" --cover cover.png

# 只排版不发布
python3 scripts/format.py --file article.md --output formatted.html
```

## 排版规范

### 支持的 Markdown 元素

| Markdown | 公众号效果 |
|----------|-----------|
| `# 标题` | 大号标题（自动居中） |
| `## 副标题` | 次级标题 |
| `**粗体**` | 公众号强调样式 |
| `- 列表` | 带样式的列表 |
| `| 表格 |` | 居中表格 |
| `![图](url)` | 自动上传获取永久链接 |

### 特殊样式

**引用框：**
```markdown
> 💡 提示：这是重点内容
```

**分割符：**
```markdown
---
```

**互动模块：**
```markdown
## 互动
选择你的答案：
- [ ] A. 选项一
- [ ] B. 选项二
```

## 工作流

### 标准发布流程

1. **准备内容** - 编写 Markdown 格式文章
2. **本地预览** - 使用 `format.py` 生成 HTML 预览
3. **上传图片** - 自动处理文章中的本地图片
4. **发布草稿** - 上传到公众号草稿箱
5. **微信内预览** - 登录 mp.weixin.qq.com 查看

### 批量发布

```bash
# 批量发布目录下所有文章
python3 scripts/publish.py --batch ./articles/

# 带延迟（避免频率限制）
python3 scripts/publish.py --batch ./articles/ --delay 60
```

## 文件结构

```
wechat-mp/
├── SKILL.md              # 本文件
├── scripts/
│   ├── publish.py        # 发布脚本
│   ├── format.py         # 排版转换
│   └── upload.py         # 素材上传
├── references/
│   ├── api.md            # 微信 API 文档
│   └── styling.md        # 排版样式指南
└── assets/
    ├── template.html     # HTML 模板
    └── default-cover.png # 默认封面
```

## 高级用法

### 自定义模板

编辑 `assets/template.html` 修改默认样式：
- 字体大小、行距
- 颜色主题
- 引用框样式
- 分割线样式

### 定时发布

使用 cron 定时任务：
```bash
# 每天早上 8 点发布
0 8 * * * cd /Users/yandong/clawd && python3 skills/wechat-mp/scripts/publish.py --file today.md
```

## 故障排查

| 问题 | 解决方案 |
|------|---------|
| access_token 失效 | 自动刷新，如频繁失败检查 AppSecret |
| 图片上传失败 | 检查图片大小（<2MB）和格式（jpg/png） |
| 内容被截断 | 检查是否超过公众号字数限制 |
| 格式错乱 | 使用 `--preview` 先本地预览 |

## 参考文档

- **API 详情**: 见 [references/api.md](references/api.md)
- **排版规范**: 见 [references/styling.md](references/styling.md)
- **微信官方文档**: https://developers.weixin.qq.com/doc/offiaccount/
