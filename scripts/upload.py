#!/usr/bin/env python3
"""
WeChat MP Asset Uploader
上传图片素材到微信公众号
"""
import os
import sys
import json
import urllib.request
import urllib.parse
from pathlib import Path
import mimetypes

APP_ID = os.getenv("WECHAT_MP_APP_ID")
APP_SECRET = os.getenv("WECHAT_MP_APP_SECRET")
CONFIG_FILE = os.getenv("WECHAT_MP_CONFIG", "/Users/yandong/.openclaw/wechat-config.json")

def load_config():
    """加载配置"""
    global APP_ID, APP_SECRET
    
    if not APP_ID or not APP_SECRET:
        if Path(CONFIG_FILE).exists():
            with open(CONFIG_FILE) as f:
                config = json.load(f)
                APP_ID = config.get("wechat_mp", {}).get("app_id", APP_ID)
                APP_SECRET = config.get("wechat_mp", {}).get("app_secret", APP_SECRET)
    
    return {"app_id": APP_ID, "app_secret": APP_SECRET} if APP_ID and APP_SECRET else None

def get_access_token():
    """获取 access_token"""
    config = load_config()
    if not config:
        print("❌ 未配置微信公众号凭证")
        return None
    
    url = f"https://api.weixin.qq.com/cgi-bin/token"
    params = {
        "grant_type": "client_credential",
        "appid": config["app_id"],
        "secret": config["app_secret"]
    }
    query = urllib.parse.urlencode(params)
    
    req = urllib.request.Request(f"{url}?{query}", method='GET')
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    
    return data.get("access_token")

def upload_image(access_token, image_path):
    """
    上传图片获取永久 URL
    用于图文消息内的图片
    """
    url = f"https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={access_token}"
    
    boundary = '----WebKitFormBoundary' + os.urandom(16).hex()
    
    # 读取图片
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    # 构建 multipart/form-data
    filename = Path(image_path).name
    body = (
        f'------{boundary}\r\n'
        f'Content-Disposition: form-data; name="media"; filename="{filename}"\r\n'
        f'Content-Type: image/jpeg\r\n\r\n'
    ).encode('utf-8') + image_data + f'\r\n------{boundary}--\r\n'.encode('utf-8')
    
    req = urllib.request.Request(url, data=body, method='POST')
    req.add_header('Content-Type', f'multipart/form-data; boundary=----{boundary}')
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        
        if 'url' in data:
            return {'success': True, 'url': data['url']}
        else:
            return {'success': False, 'error': data.get('errmsg', 'Unknown error')}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def upload_material(access_token, file_path, media_type='image'):
    """
    上传永久素材
    media_type: image, voice, video, thumb
    """
    url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={access_token}&type={media_type}"
    
    boundary = '----WebKitFormBoundary' + os.urandom(16).hex()
    
    with open(file_path, 'rb') as f:
        file_data = f.read()
    
    filename = Path(file_path).name
    content_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
    
    body = (
        f'------{boundary}\r\n'
        f'Content-Disposition: form-data; name="media"; filename="{filename}"\r\n'
        f'Content-Type: {content_type}\r\n\r\n'
    ).encode('utf-8') + file_data + f'\r\n------{boundary}--\r\n'.encode('utf-8')
    
    req = urllib.request.Request(url, data=body, method='POST')
    req.add_header('Content-Type', f'multipart/form-data; boundary=----{boundary}')
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        
        if 'media_id' in data:
            return {'success': True, 'media_id': data['media_id'], 'url': data.get('url', '')}
        else:
            return {'success': False, 'error': data.get('errmsg', 'Unknown error')}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def validate_image(path):
    """验证图片是否符合要求"""
    if not Path(path).exists():
        return False, "文件不存在"
    
    size = Path(path).stat().st_size
    if size > 2 * 1024 * 1024:  # 2MB
        return False, f"图片过大 ({size/1024/1024:.1f}MB > 2MB)"
    
    ext = Path(path).suffix.lower()
    if ext not in ['.jpg', '.jpeg', '.png', '.gif']:
        return False, f"不支持的格式 ({ext})"
    
    return True, "OK"

def main():
    import argparse
    parser = argparse.ArgumentParser(description='上传素材到微信公众号')
    parser.add_argument('--file', '-f', required=True, help='要上传的文件路径')
    parser.add_argument('--type', '-t', default='image', 
                       choices=['image', 'voice', 'video', 'thumb'],
                       help='素材类型')
    parser.add_argument('--temp', action='store_true', 
                       help='临时素材（默认永久）')
    args = parser.parse_args()
    
    file_path = Path(args.file)
    
    # 验证图片
    if args.type == 'image':
        valid, msg = validate_image(file_path)
        if not valid:
            print(f"❌ {msg}")
            return 1
    
    # 获取 token
    print("🔑 正在获取 access_token...")
    token = get_access_token()
    if not token:
        return 1
    print("✅ Token 获取成功")
    
    # 上传
    print(f"📤 正在上传: {file_path.name}")
    
    if args.temp or args.type == 'thumb':
        # 临时素材（用于图文消息内图片）
        result = upload_image(token, file_path)
    else:
        # 永久素材
        result = upload_material(token, file_path, args.type)
    
    if result['success']:
        print(f"\n✅ 上传成功！")
        if 'url' in result:
            print(f"🔗 图片 URL: {result['url']}")
        if 'media_id' in result:
            print(f"🆔 Media ID: {result['media_id']}")
        return 0
    else:
        print(f"\n❌ 上传失败: {result.get('error', 'Unknown error')}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
