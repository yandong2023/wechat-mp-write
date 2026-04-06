#!/usr/bin/env python3
"""
OpenRouter API 图像生成脚本
支持多种图像生成模型
"""

import os
import sys
import json
import urllib.request
from datetime import datetime

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/images/generations"

def get_api_key():
    """获取 OpenRouter API Key"""
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        # 尝试从 keychain 读取
        try:
            import subprocess
            result = subprocess.run(
                ['security', 'find-generic-password', '-s', 'openclaw:openrouter:default', '-w'],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                api_key = result.stdout.strip()
        except:
            pass
    return api_key

def generate_image(prompt, model="stabilityai/stable-diffusion-xl", size="1024x1024", n=1):
    """
    使用 OpenRouter 生成图片
    
    Args:
        prompt: 图片描述
        model: 模型名称
        size: 图片尺寸 (1024x1024, 1024x1792, 1792x1024)
        n: 生成数量
    """
    api_key = get_api_key()
    if not api_key:
        print("❌ 错误：未找到 OPENROUTER_API_KEY")
        print("请设置环境变量：export OPENROUTER_API_KEY='your-key'")
        return None
    
    payload = {
        "model": model,
        "prompt": prompt,
        "n": n,
        "size": size
    }
    
    req = urllib.request.Request(
        OPENROUTER_API_URL,
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
            'HTTP-Referer': 'https://openclaw.ai',
            'X-Title': 'OpenClaw WeChat Assistant'
        }
    )
    
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode())
            
            if 'data' in result:
                urls = [item['url'] for item in result['data'] if 'url' in item]
                print(f"✅ 图片生成成功！共 {len(urls)} 张")
                return urls
            else:
                print(f"❌ 生成失败: {result}")
                return None
                
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"❌ HTTP 错误 {e.code}: {error_body}")
        return None
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def download_image(url, output_path=None):
    """下载图片"""
    if not output_path:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f'openrouter_image_{timestamp}.png'
    
    try:
        urllib.request.urlretrieve(url, output_path)
        print(f"✅ 图片已保存: {output_path}")
        return output_path
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return None

def generate_cover_image(title, subtitle=None, style="academic"):
    """生成公众号封面图"""
    
    style_prompts = {
        "academic": "professional academic style, clean design, deep blue and gold color scheme, trustworthy atmosphere, minimalist",
        "medical": "medical research theme, clean white background, professional healthcare illustration, microscope or books",
        "tech": "modern tech style, gradient blue background, minimalist geometric design, digital network elements",
        "warm": "warm and friendly, soft orange and blue tones, approachable design, human touch"
    }
    
    style_desc = style_prompts.get(style, style_prompts["academic"])
    
    prompt = f"""
Professional cover image for a Chinese academic article titled "{title}".
{ f'Subtitle theme: "{subtitle}"' if subtitle else '' }

Style: {style_desc}

Requirements:
- Clean and professional composition
- Suitable for medical/academic audience
- No text, no letters, no words in the image
- High quality, detailed illustration
- 16:9 aspect ratio composition
- Modern, trustworthy design
- Professional lighting
"""
    
    urls = generate_image(prompt, size="1792x1024")
    if urls:
        return download_image(urls[0], f"cover_{datetime.now().strftime('%Y%m%d')}.png")
    return None

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate images using OpenRouter API')
    parser.add_argument('--prompt', '-p', help='Custom prompt')
    parser.add_argument('--cover', '-c', help='Generate cover with title')
    parser.add_argument('--subtitle', '-s', help='Subtitle for cover')
    parser.add_argument('--style', default='academic', choices=['academic', 'medical', 'tech', 'warm'])
    
    args = parser.parse_args()
    
    if args.cover:
        generate_cover_image(args.cover, args.subtitle, args.style)
    elif args.prompt:
        urls = generate_image(args.prompt)
        if urls:
            for url in urls:
                download_image(url)
    else:
        # 测试
        print("🎨 测试生成封面图...")
        generate_cover_image(
            "你引用的文献可能是假的",
            "文献核查实战技巧",
            "academic"
        )
