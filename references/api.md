# 微信公众号 API 参考

## 接口域名

- 通用域名: `https://api.weixin.qq.com`

## 认证接口

### 获取 Access Token

```
GET https://api.weixin.qq.com/cgi-bin/token
```

**参数：**

| 参数 | 必填 | 说明 |
|------|------|------|
| grant_type | 是 | 固定值: client_credential |
| appid | 是 | 公众号 AppID |
| secret | 是 | 公众号 AppSecret |

**返回：**
```json
{
  "access_token": "ACCESS_TOKEN",
  "expires_in": 7200
}
```

**注意：**
- Access Token 有效期 7200 秒（2小时）
- 建议缓存并提前刷新
- 调用次数限制：2000次/天

## 草稿箱接口

### 添加草稿

```
POST https://api.weixin.qq.com/cgi-bin/draft/add
```

**请求体：**
```json
{
  "articles": [
    {
      "title": "文章标题",
      "author": "作者",
      "digest": "摘要",
      "content": "HTML内容",
      "content_source_url": "原文链接",
      "thumb_media_id": "封面图media_id",
      "need_open_comment": 1,
      "only_fans_can_comment": 0,
      "pic_crop_235_1": "封面裁剪参数",
      "pic_crop_1_1": "封面裁剪参数"
    }
  ]
}
```

**返回：**
```json
{
  "media_id": "MEDIA_ID"
}
```

### 获取草稿

```
POST https://api.weixin.qq.com/cgi-bin/draft/get
```

### 删除草稿

```
POST https://api.weixin.qq.com/cgi-bin/draft/delete
```

## 素材管理接口

### 上传图片（获取永久 URL）

```
POST https://api.weixin.qq.com/cgi-bin/media/uploadimg
```

**说明：**
- Content-Type: multipart/form-data
- 返回图片 URL，可用于图文消息

### 上传图文消息内的图片

```
POST https://api.weixin.qq.com/cgi-bin/media/uploadnews
```

**说明：**
- 上传后返回 media_id
- 用于草稿箱的 thumb_media_id

### 新增永久素材

```
POST https://api.weixin.qq.com/cgi-bin/material/add_material
```

**类型：**
- image: 图片
- voice: 语音
- video: 视频
- thumb: 缩略图

## 发布接口

### 发布草稿

```
POST https://api.weixin.qq.com/cgi-bin/freepublish/submit
```

**参数：**
```json
{
  "media_id": "DRAFT_MEDIA_ID"
}
```

**注意：**
- 发布后文章进入审核流程
- 审核通过后可见

### 获取发布状态

```
POST https://api.weixin.qq.com/cgi-bin/freepublish/get
```

## 错误码对照

| 错误码 | 说明 |
|--------|------|
| -1 | 系统繁忙 |
| 0 | 请求成功 |
| 40001 | access_token 失效 |
| 40002 | grant_type 错误 |
| 40003 | 不合法的 OpenID |
| 40004 | 不合法的媒体文件类型 |
| 40005 | 不合法的文件类型 |
| 40006 | 不合法的文件大小 |
| 40007 | 不合法的 media_id |
| 40008 | 不合法的消息类型 |
| 40009 | 不合法的图片文件大小 |
| 40010 | 不合法的语音文件大小 |
| 40011 | 不合法的视频文件大小 |
| 40012 | 不合法的缩略图文件大小 |
| 40013 | 不合法的 AppID |
| 41001 | 缺少 access_token 参数 |
| 41002 | 缺少 appid 参数 |
| 41004 | 缺少 secret 参数 |
| 42001 | access_token 超时 |
| 43001 | 需要 GET 请求 |
| 43002 | 需要 POST 请求 |
| 44002 | POST 数据包为空 |
| 44003 | 图文消息内容为空 |
| 45009 | 接口调用超过频率限制 |
| 47001 | 解析 JSON/XML 内容错误 |

## 频率限制

| 接口 | 限制 |
|------|------|
| 获取 access_token | 2000次/天 |
| 上传图片 | 5000次/天 |
| 添加草稿 | 100次/天 |
| 发布文章 | 100次/天 |

## 内容安全

### 检查文本安全

```
POST https://api.weixin.qq.com/wxa/msg_sec_check
```

**说明：**
- 检查内容是否包含敏感词
- 建议在发布前调用

## 最佳实践

1. **Token 管理**
   - 缓存 access_token
   - 提前 5 分钟刷新
   - 处理并发刷新问题

2. **错误处理**
   - 遇到 40001 错误立即刷新 token
   - 实现指数退避重试
   - 记录错误日志

3. **图片处理**
   - 压缩图片 < 2MB
   - 使用 JPG 格式
   - 封面图尺寸 900x500

4. **内容优化**
   - 摘要控制在 120 字内
   - 标题不超过 64 字
   - 正文图片使用 HTTPS
