# wechat-mp

面向微信公众号的 Markdown 排版与草稿发布工具。

`wechat-mp` 解决的是公众号内容工作流里最容易碎掉的那一段：**把已经写好的文章，稳定地变成可预览、可上传、可进草稿箱的内容**。

它不是内容策划工具，也不是完整的写稿 Agent，而是更底层、更可靠的**发布基础设施**。

## 它适合做什么

适合这些场景：
- 已经有 Markdown 文章，想转成适合公众号的 HTML
- 想先在本地预览排版效果，再决定要不要发
- 想上传封面或正文图片，拿到 URL / media_id
- 想把文章发布到公众号草稿箱
- 想把这套流程接进更大的 AI 写稿 / 运营 workflow

不适合单独解决这些问题：
- 选题策划
- 标题 / 摘要 brainstorming
- 不同公众号账号之间的运营策略选择
- 从笔记到完整文章的一体化写作流程

这些更适合由上层 `wechat-mp-write` 来做。

## 核心能力

### 1. Markdown → 微信公众号 HTML

把常见 Markdown 结构转成更适合公众号后台的 HTML：
- 标题
- 段落
- 粗体 / 斜体
- 引用
- 列表
- 表格
- 分割线
- 图片 / 链接
- 代码块 / 行内代码
- 增强内容组件（tip / warning / summary / cta）

### 2. 本地预览

在真正发布前先生成本地 HTML，快速检查：
- 段落节奏是否舒服
- 标题层级是否清晰
- 引用 / 表格 / 列表是否容易读
- 整体是否适合手机阅读

### 3. 图片 / 封面素材上传

支持上传图片素材，获取：
- 正文图片 URL
- 永久素材 `media_id`

这一步可以接到封面生成、图片处理、上层发布流程里。

### 4. 草稿箱发布

将已经完成排版的文章发送到公众号草稿箱，作为正式群发前的最后一步。

## 项目定位

这个仓库建议理解成两层架构中的**底层层**：

### `wechat-mp`
负责：
- 排版
- 预览
- 上传素材
- 发布草稿

### `wechat-mp-write`
负责：
- 选题
- 标题 / 摘要 / 封面文案
- 账号选择
- 文章结构设计
- 整体写稿与发布 workflow

一句话：
- `wechat-mp` = **publish engine**
- `wechat-mp-write` = **writing workflow**

## Quick Start

### 1. 配置凭证

推荐使用环境变量：

```bash
export WECHAT_MP_APP_ID="你的公众号 AppID"
export WECHAT_MP_APP_SECRET="你的公众号 AppSecret"
```

也可以用配置文件：

```bash
export WECHAT_MP_CONFIG="$HOME/.openclaw/wechat-config.json"
```

## 使用方式

### 1) 本地排版预览

```bash
python3 scripts/format.py --file article.md --template
```

或者：

```bash
python3 scripts/format.py --file article.md --output article.preview.html --template
```

### 1.0) 选择排版主题

现在支持几套可直接调用的主题：
- `default`
- `wechat-native`
- `medium-clean`
- `notion-soft`
- `tech-dark`

示例：

```bash
python3 scripts/format.py --file article.md --theme wechat-native --template
python3 scripts/format.py --file article.md --theme medium-clean --template
python3 scripts/format.py --file article.md --theme tech-dark --template
```

### 1.1) 使用增强内容组件

支持几种适合公众号阅读的轻量块：

```markdown
::: tip
这是一个重点提示。
:::

::: warning
这里写风险提醒或注意事项。
:::

::: summary
这一节最重要的结论放这里。
:::

::: cta
如果你也想搭这套工作流，可以先从排版 + 草稿发布开始。
:::
```

### 2) 发布到草稿箱

```bash
python3 scripts/publish.py --file article.md --title "文章标题"
```

如果 Markdown 第一行是 `# 文章标题`，且和传入的 `--title` 一致，发布时会自动去掉正文里的重复标题，避免公众号里出现“标题显示两遍”。

带作者和摘要：

```bash
python3 scripts/publish.py \
  --file article.md \
  --title "文章标题" \
  --author "作者名" \
  --digest "文章摘要"
```

### 3) 上传封面或图片素材

```bash
python3 scripts/upload.py --file cover.png --type image
```

如果已经有封面 `media_id`：

```bash
python3 scripts/publish.py \
  --file article.md \
  --title "文章标题" \
  --thumb-media-id "MEDIA_ID"
```

## 推荐工作流

### 最小闭环

1. 写 Markdown
2. 本地预览
3. 上传封面 / 图片
4. 发布到草稿箱
5. 登录 `mp.weixin.qq.com` 检查后手动发布

### 接入 AI 写稿 workflow

1. 上层 Agent 生成标题 / 摘要 / 正文 / 封面文案
2. `wechat-mp` 负责排版
3. `wechat-mp` 负责上传封面素材
4. `wechat-mp` 负责进入草稿箱
5. 人工在后台做最终审核

## Project Structure

```text
wechat-mp/
├── SKILL.md
├── README.md
├── scripts/
│   ├── format.py
│   ├── publish.py
│   ├── upload.py
│   ├── generate_image.py
│   ├── generate_leonardo.py
│   └── generate_openrouter.py
├── references/
│   ├── api.md
│   └── styling.md
└── assets/
    └── template.html
```

## 设计原则

- **先预览，再发布**：重要文章先看效果，不直接盲发
- **发布层与写作层分离**：降低系统耦合
- **本地产物不入库**：截图、封面、media_id 缓存都视为临时输出
- **移动阅读优先**：公众号内容默认先服务手机端阅读体验
- **人工审核保留在最后一步**：不追求完全无人化

## Roadmap

接下来值得继续做的方向：

- [ ] 多公众号账号选择与切换
- [ ] 本地图片自动上传并替换正文链接
- [ ] 更稳健的 Markdown 解析
- [ ] 更完整的组件系统（steps / faq / compare / data-cards）
- [x] 基础模板 / 主题系统
- [ ] 更细颗粒度的品牌主题系统（按账号/栏目）
- [ ] 更完善的错误提示与重试机制
- [ ] 草稿发布结果结构化输出
- [ ] 和 `wechat-mp-write` 的接口进一步标准化

## Notes

- 不要把真实 `AppSecret` 提交到仓库
- 不要把生成图片、缓存文件、临时产物提交到仓库
- 最终群发前，仍然建议在公众号后台人工检查一次
