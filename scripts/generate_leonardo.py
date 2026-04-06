#!/usr/bin/env python3
"""
Leonardo.ai API 图片生成脚本
用于自动生成公众号配图
"""

import os
import sys
import json
import time
import urllib.request
from datetime import datetime

LEONARDO_API_URL = "https://cloud.leonardo.ai/api/rest/v1"

def get_api_key():
    """获取 API Key"""
    api_key = os.getenv('LEONARDO_API_KEY')
    if not api_key:
        # 尝试从 keychain 读取
        try:
            import subprocess
            result = subprocess.run(
                ['security', 'find-generic-password', '-s', 'openclaw:leonardo:default', '-w'],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                api_key = result.stdout.strip()
        except:
            pass
    return api_key

def generate_image(prompt, width=1024, height=768, model=" Leonardo Creative", num_images=1):
    """
    使用 Leonardo.ai 生成图片
    
    Args:
        prompt: 图片描述
        width: 宽度 (512-1024)
        height: 高度 (512-1024)
        model: 模型名称
        num_images: 生成数量
    """
    api_key = get_api_key()
    if not api_key:
        print("❌ 错误：未找到 LEONARDO_API_KEY")
        print("请设置环境变量：export LEONARDO_API_KEY='your-key'")
        return None
    
    # 1. 创建生成任务
    generation_url = f"{LEONARDO_API_URL}/generations"
    
    payload = {
        "prompt": prompt,
        "modelId": model,
        "width": width,
        "height": height,
        "num_images": num_images,
        "guidance_scale": 7,
        "scheduler": "LEONARDO",
        "presetStyle": "DYNAMIC"
    }
    
    req = urllib.request.Request(
        generation_url,
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
    )
    
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode())
            generation_id = result.get('sdGenerationJob', {}).get('generationId')
            
            if not generation_id:
                print(f"❌ 创建任务失败: {result}")
                return None
            
            print(f"✅ 任务创建成功: {generation_id}")
            
            # 2. 轮询等待结果
            return poll_generation_result(generation_id, api_key)
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def poll_generation_result(generation_id, api_key, max_attempts=30):
    """轮询获取生成结果"""
    
    result_url = f"{LEONARDO_API_URL}/generations/{generation_id}"
    
    for i in range(max_attempts):
        req = urllib.request.Request(
            result_url,
            headers={'Authorization': f'Bearer {api_key}'}
        )
        
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode())
            generations = result.get('generations_by_pk', {})
            
            status = generations.get('status')
            
            if status == 'COMPLETE':
                images = generations.get('generated_images', [])
                urls = [img.get('url') for img in images if img.get('url')]
                print(f"✅ 图片生成完成！共 {len(urls)} 张")
                return urls
            
            elif status == 'FAILED':
                print(f"❌ 生成失败")
                return None
            
            else:
                print(f"⏳ 生成中... ({i+1}/{max_attempts})")
                time.sleep(2)
    
    print("❌ 超时，请稍后查询")
    return None

def download_image(url, output_path=None):
    """下载图片"""
    if not output_path:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f'leonardo_image_{timestamp}.png'
    
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
        "academic": "professional academic style, clean design, deep blue (#1a365d) and gold (#d69e2e) color scheme, trustworthy atmosphere",
        "medical": "medical research theme, clean white background, professional healthcare illustration, stethoscope or microscope elements",
        "tech": "modern tech style, gradient blue background, minimalist geometric design, digital elements",
        "warm": "warm and friendly, soft orange and blue tones, approachable design, human touch"
    }
    
    style_desc = style_prompts.get(style, style_prompts["academic"])
    
    prompt = f"""
Professional cover image for a Chinese academic article titled "{title}".
{ f'Subtitle: "{subtitle}"' if subtitle else '' }

Style: {style_desc}

Requirements:
- Clean and professional composition
- Suitable for medical/academic audience
- No text or letters in the image
- High quality, detailed illustration
- 4:3 aspect ratio composition
- Modern, trustworthy design
"""
    
    urls = generate_image(prompt, width=1024, height=768)
    if urls:
        return download_image(urls[0], f"cover_{datetime.now().strftime('%Y%m%d')}.png")
    return None

def generate_infographic(description, chart_type="data"):
    """生成信息图"""
    
    type_prompts = {
        "data": "clean data visualization, pie chart or bar chart style",
        "flow": "professional flowchart, 3 connected steps, arrows",
        "warning": "warning signs and red flags, caution symbols"
    }
    
    type_desc = type_prompts.get(chart_type, type_prompts["data"])
    
    prompt = f"""
Professional infographic for academic article.
Content: {description}

Style: {type_desc}

Requirements:
- Blue (#1a365d) and gold (#d69e2e) color scheme
- Clean minimalist design
- No text or labels
- White or light gray background
- High quality illustration
- Suitable for WeChat article
"""
    
    urls = generate_image(prompt, width=1024, height=1024)
    if urls:
        return download_image(urls[0], f"infographic_{datetime.now().strftime('%Y%m%d')}.png")
    return None

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate images using Leonardo.ai API')
    parser.add_argument('--prompt', '-p', help='Custom prompt')
    parser.add_argument('--cover', '-c', help='Generate cover with title')
    parser.add_argument('--subtitle', '-s', help='Subtitle for cover')
    parser.add_argument('--style', default='academic', choices=['academic', 'medical', 'tech', 'warm'])
    parser.add_argument('--infographic', '-i', help='Generate infographic with description')
    parser.add_argument('--chart-type', default='data', choices=['data', 'flow', 'warning'])
    
    args = parser.parse_args()
    
    if args.cover:
        generate_cover_image(args.cover, args.subtitle, args.style)
    elif args.infographic:
        generate_infographic(args.infographic, args.chart_type)
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
