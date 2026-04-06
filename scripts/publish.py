#!/usr/bin/env python3
"""
WeChat MP Article Publisher
发布文章到微信公众号草稿箱
"""
import os
import sys
import json
import urllib.request
import urllib.parse
import re
from pathlib import Path
from datetime import datetime

# 配置
APP_ID = os.getenv("WECHAT_MP_APP_ID")
APP_SECRET = os.getenv("WECHAT_MP_APP_SECRET")
CONFIG_FILE = os.getenv("WECHAT_MP_CONFIG", str(Path.home() / ".openclaw" / "wechat-config.json"))

def load_config():
    """加载配置"""
    global APP_ID, APP_SECRET
    
    if not APP_ID or not APP_SECRET:
        if Path(CONFIG_FILE).exists():
            with open(CONFIG_FILE) as f:
                config = json.load(f)
                APP_ID = config.get("wechat_mp", {}).get("app_id", APP_ID)
                APP_SECRET = config.get("wechat_mp", {}).get("app_secret", APP_SECRET)
    
    if not APP_ID or not APP_SECRET:
        print("❌ 错误：未配置微信公众号凭证")
        print("请设置环境变量：WECHAT_MP_APP_ID 和 WECHAT_MP_APP_SECRET")
        print(f"或创建配置文件：{CONFIG_FILE}")
        return None
    
    return {"app_id": APP_ID, "app_secret": APP_SECRET}

def get_access_token():
    """获取微信 access_token"""
    config = load_config()
    if not config:
        return None
    
    url = f"https://api.weixin.qq.com/cgi-bin/token"
    params = {
        "grant_type": "client_credential",
        "appid": config["app_id"],
        "secret": config["app_secret"]
    }
    query = urllib.parse.urlencode(params)
    full_url = f"{url}?{query}"
    
    try:
        req = urllib.request.Request(full_url, method='GET')
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        
        if "access_token" in data:
            return data["access_token"]
        else:
            print(f"❌ 获取 token 失败: {data}")
            return None
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def upload_image(access_token, image_path):
    """上传图片获取永久 URL"""
    url = f"https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={access_token}"
    
    boundary = '----WebKitFormBoundary' + os.urandom(16).hex()
    
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    body = (
        f'------{boundary}\r\n'
        f'Content-Disposition: form-data; name="media"; filename="{Path(image_path).name}"\r\n'
        f'Content-Type: image/jpeg\r\n\r\n'
    ).encode('utf-8') + image_data + f'\r\n------{boundary}--\r\n'.encode('utf-8')
    
    req = urllib.request.Request(url, data=body, method='POST')
    req.add_header('Content-Type', f'multipart/form-data; boundary=----{boundary}')
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        return data.get('url')
    except Exception as e:
        print(f"❌ 图片上传失败: {e}")
        return None

def escape_html(text):
    """转义 HTML 特殊字符"""
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    return text

def markdown_to_wechat_html(content):
    """
    Markdown 转微信公众号 HTML（严格符合微信规范）
    微信支持的标签：p, br, section, img, strong, em, a, span, ul, ol, li
    """
    lines = content.split('\n')
    html_parts = []
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # 跳过空行
        if not line:
            i += 1
            continue
        
        # 处理标题
        if line.startswith('# '):
            title = escape_html(line[2:].strip())
            html_parts.append(f'<h1 style="text-align:center;font-size:22px;font-weight:bold;margin:20px 0;">{title}</h1>')
            i += 1
            continue
        
        if line.startswith('## '):
            title = escape_html(line[3:].strip())
            html_parts.append(f'<h2 style="font-size:18px;font-weight:bold;margin:15px 0;color:#1aad19;border-left:4px solid #1aad19;padding-left:10px;">{title}</h2>')
            i += 1
            continue
        
        if line.startswith('### '):
            title = escape_html(line[4:].strip())
            html_parts.append(f'<h3 style="font-size:16px;font-weight:bold;margin:12px 0;">{title}</h3>')
            i += 1
            continue
        
        # 处理分割线
        if line == '---':
            html_parts.append('<p style="text-align:center;margin:15px 0;">————————</p>')
            i += 1
            continue
        
        # 处理引用块
        if line.startswith('> '):
            quote_lines = []
            while i < len(lines) and lines[i].strip().startswith('> '):
                quote_lines.append(lines[i].strip()[2:])
                i += 1
            quote_text = ' '.join(quote_lines)
            quote_text = process_inline_formatting(quote_text)
            html_parts.append(f'<blockquote style="border-left:3px solid #1aad19;padding:10px 15px;margin:15px 0;background:#f8f8f8;color:#666;">{quote_text}</blockquote>')
            continue
        
        # 处理无序列表
        if line.startswith('- ') or line.startswith('* '):
            list_items = []
            while i < len(lines) and (lines[i].strip().startswith('- ') or lines[i].strip().startswith('* ')):
                item_text = lines[i].strip()[2:]
                item_text = process_inline_formatting(item_text)
                list_items.append(f'<li style="margin:8px 0;">{item_text}</li>')
                i += 1
            html_parts.append(f'<ul style="margin:10px 0;padding-left:20px;">{"".join(list_items)}</ul>')
            continue
        
        # 处理有序列表
        if re.match(r'^\d+\. ', line):
            list_items = []
            while i < len(lines) and re.match(r'^\d+\. ', lines[i].strip()):
                item_text = re.sub(r'^\d+\. ', '', lines[i].strip())
                item_text = process_inline_formatting(item_text)
                list_items.append(f'<li style="margin:8px 0;">{item_text}</li>')
                i += 1
            html_parts.append(f'<ol style="margin:10px 0;padding-left:20px;">{"".join(list_items)}</ol>')
            continue
        
        # 处理表格（简化处理为文本）
        if '|' in line and i + 1 < len(lines) and '---' in lines[i + 1]:
            # 跳过表格，转为普通段落
            table_lines = []
            while i < len(lines) and '|' in lines[i]:
                table_lines.append(lines[i])
                i += 1
            # 简单渲染表格行为文本
            table_text = '<br/>'.join(escape_html(l) for l in table_lines if '---' not in l)
            html_parts.append(f'<p style="font-size:14px;line-height:1.6;margin:10px 0;background:#f5f5f5;padding:10px;">{table_text}</p>')
            continue
        
        # 普通段落
        text = process_inline_formatting(line)
        html_parts.append(f'<p style="font-size:16px;line-height:1.8;margin:10px 0;text-align:justify;">{text}</p>')
        i += 1
    
    return '\n'.join(html_parts)

def process_inline_formatting(text):
    """处理行内格式：粗体、斜体、链接、图片"""
    # 转义 HTML
    text = escape_html(text)
    
    # 处理图片 ![alt](url)
    def replace_image(match):
        alt = match.group(1)
        url = match.group(2)
        return f'<img src="{url}" alt="{alt}" style="max-width:100%;margin:10px 0;"/>'
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_image, text)
    
    # 处理链接 [text](url)
    def replace_link(match):
        link_text = match.group(1)
        url = match.group(2)
        return f'<a href="{url}" style="color:#1aad19;text-decoration:none;">{link_text}</a>'
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', replace_link, text)
    
    # 处理粗体 **text**
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong style="color:#000;">\1</strong>', text)
    
    # 处理斜体 *text*
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    
    return text

def add_draft(access_token, title, html_content, author="", digest="", thumb_media_id=None):
    """创建草稿"""
    url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"
    
    article = {
        "title": title,
        "author": author,
        "digest": digest,
        "content": html_content,
        "content_source_url": "",
        "need_open_comment": 1,
        "only_fans_can_comment": 0
    }
    
    # 如果有封面图才添加
    if thumb_media_id:
        article["thumb_media_id"] = thumb_media_id
    
    payload = json.dumps({"articles": [article]}, ensure_ascii=False).encode('utf-8')
    
    req = urllib.request.Request(url, data=payload, method='POST')
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        return data
    except Exception as e:
        return {"errcode": -1, "errmsg": str(e)}

def main():
    import argparse
    parser = argparse.ArgumentParser(description='发布文章到微信公众号')
    parser.add_argument('--file', '-f', required=True, help='Markdown 文件路径')
    parser.add_argument('--title', '-t', help='文章标题（默认从文件第一行提取）')
    parser.add_argument('--author', '-a', default='LitSource', help='作者名')
    parser.add_argument('--digest', '-d', help='文章摘要')
    parser.add_argument('--cover', '-c', help='封面图片路径')
    parser.add_argument('--thumb-media-id', '-m', help='封面图片的永久素材 media_id')
    parser.add_argument('--preview', '-p', action='store_true', help='仅预览，不发布')
    args = parser.parse_args()
    
    # 读取文章
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"❌ 文件不存在: {file_path}")
        return 1
    
    content = file_path.read_text(encoding='utf-8')
    
    # 提取标题
    title = args.title
    if not title:
        # 从第一行提取
        first_line = content.split('\n')[0].strip()
        if first_line.startswith('# '):
            title = first_line[2:]
        else:
            title = "未命名文章"
    
    print(f"📝 文章标题: {title}")
    
    # 转换 HTML
    print("🎨 正在排版...")
    html_content = markdown_to_wechat_html(content)
    
    # 预览模式
    if args.preview:
        preview_file = file_path.with_suffix('.preview.html')
        full_html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - 预览</title>
    <style>
        body {{ max-width: 680px; margin: 20px auto; padding: 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }}
        .container {{ background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
    </style>
</head>
<body>
    <div class="container">
        {html_content}
    </div>
</body>
</html>'''
        preview_file.write_text(full_html, encoding='utf-8')
        print(f"✅ 预览文件已生成: {preview_file}")
        return 0
    
    # 获取 token
    print("🔑 正在获取 access_token...")
    token = get_access_token()
    if not token:
        return 1
    print("✅ Token 获取成功")
    
    # 封面图处理
    thumb_media_id = None
    if args.thumb_media_id:
        thumb_media_id = args.thumb_media_id
        print(f"📷 使用封面图 media_id: {thumb_media_id}")
    elif args.cover and Path(args.cover).exists():
        print("📷 封面图路径已提供，但未上传（使用 --thumb-media-id 参数指定已上传的素材ID）")
    
    # 发布草稿
    print("📤 正在发布到草稿箱...")
    
    # 调试：打印请求内容
    preview_articles = [{
        "title": title,
        "author": args.author,
        "digest": args.digest or f"发布于 {datetime.now().strftime('%Y-%m-%d')}",
        "content": html_content[:200] + "...",
        "content_source_url": "",
        "need_open_comment": 1,
        "only_fans_can_comment": 0
    }]
    
    print(f"\n📤 请求内容预览:")
    print(json.dumps({"articles": preview_articles}, ensure_ascii=False, indent=2)[:800])
    print("...\n")
    
    result = add_draft(
        access_token=token,
        title=title,
        html_content=html_content,
        author=args.author,
        digest=args.digest or f"发布于 {datetime.now().strftime('%Y-%m-%d')}",
        thumb_media_id=args.thumb_media_id
    )
    
    if "media_id" in result:
        print(f"\n✅ 草稿创建成功！")
        print(f"📋 Media ID: {result['media_id']}")
        print(f"\n👉 请登录 https://mp.weixin.qq.com 查看草稿箱并发布")
        return 0
    else:
        print(f"\n❌ 发布失败")
        print(f"完整响应: {result}")
        print(f"错误码: {result.get('errcode')}")
        print(f"错误信息: {result.get('errmsg')}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
