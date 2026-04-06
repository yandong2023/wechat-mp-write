#!/usr/bin/env python3
"""
使用 DALL-E 3 生成公众号配图
"""

import os
import sys
import json
import urllib.request
from datetime import datetime

def generate_image(prompt, output_path=None, size="1024x1024", quality="standard"):
    """
    使用 DALL-E 3 生成图片
    
    Args:
        prompt: 图片描述（英文效果最佳）
        output_path: 输出路径
        size: 图片尺寸 (1024x1024, 1024x1792, 1792x1024)
        quality: 质量 (standard, hd)
    """
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        # 尝试从 codex 配置读取
        try:
            import subprocess
            result = subprocess.run(['security', 'find-generic-password', '-s', 'openclaw:codex:default', '-w'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                api_key = result.stdout.strip()
        except:
            pass
    
    if not api_key:
        print("❌ 错误：未找到 OpenAI API Key")
        print("请设置环境变量：export OPENAI_API_KEY='your-key'")
        return None
    
    url = "https://api.openai.com/v1/images/generations"
    
    data = {
        "model": "dall-e-3",
        "prompt": prompt,
        "n": 1,
        "size": size,
        "quality": quality
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
    )
    
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode())
            image_url = result['data'][0]['url']
            
            # 下载图片
            if not output_path:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_path = f'generated_image_{timestamp}.png'
            
            urllib.request.urlretrieve(image_url, output_path)
            print(f'✅ 图片生成成功: {output_path}')
            return output_path
            
    except Exception as e:
        print(f'❌ 生成失败: {e}')
        return None


def generate_cover_image(title, subtitle=None, style="academic"):
    """生成公众号封面图"""
    
    style_prompts = {
        "academic": "professional academic style, clean design, blue and gold color scheme",
        "medical": "medical research theme, clean white background, professional illustration",
        "tech": "modern tech style, gradient background, minimalist design",
        "warm": "warm and friendly, soft colors, approachable design"
    }
    
    style_desc = style_prompts.get(style, style_prompts["academic"])
    
    prompt = f"""
Create a professional WeChat article cover image for a Chinese academic/medical article.
Title: "{title}"
{ f'Subtitle: "{subtitle}"' if subtitle else '' }

Style requirements:
- {style_desc}
- Clean typography with Chinese characters
- Professional and trustworthy appearance
- Suitable for medical/academic audience
- No text in the image itself (just visual elements)
- 16:9 aspect ratio composition
- High quality, modern design
"""
    
    return generate_image(prompt, size="1792x1024", quality="hd")


def generate_infographic(data_description, chart_type="chart"):
    """生成信息图"""
    
    prompt = f"""
Create a clean, professional infographic for a Chinese academic article.
Content: {data_description}

Style requirements:
- Clean data visualization style
- Blue and gold color scheme (#1a365d, #d69e2e)
- Easy to understand at a glance
- Professional typography
- Suitable for WeChat article
- White or light gray background
- No text labels (just visual representation)
"""
    
    return generate_image(prompt, size="1024x1024", quality="hd")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate images for WeChat articles using DALL-E 3')
    parser.add_argument('--prompt', '-p', help='Custom prompt for image generation')
    parser.add_argument('--cover', '-c', help='Generate cover image with this title')
    parser.add_argument('--subtitle', '-s', help='Subtitle for cover image')
    parser.add_argument('--style', default='academic', choices=['academic', 'medical', 'tech', 'warm'])
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--size', default='1024x1024', choices=['1024x1024', '1024x1792', '1792x1024'])
    parser.add_argument('--hd', action='store_true', help='Use HD quality')
    
    args = parser.parse_args()
    
    quality = 'hd' if args.hd else 'standard'
    
    if args.cover:
        generate_cover_image(args.cover, args.subtitle, args.style)
    elif args.prompt:
        generate_image(args.prompt, args.output, args.size, quality)
    else:
        # 测试生成
        print("🎨 测试生成封面图...")
        generate_cover_image(
            "你引用的文献可能是假的",
            "文献核查实战技巧",
            "academic"
        )
