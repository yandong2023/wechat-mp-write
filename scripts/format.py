#!/usr/bin/env python3
"""
WeChat MP Article Formatter
Markdown 转公众号排版格式
"""
import re
import sys
from pathlib import Path

# 默认样式配置
STYLES = {
    "body": "font-size:16px;line-height:1.8;margin:10px 0;color:#333;",
    "h1": "font-size:22px;font-weight:bold;text-align:center;margin:25px 0;color:#000;",
    "h2": "font-size:18px;font-weight:bold;margin:20px 0;color:#1aad19;border-left:4px solid #1aad19;padding-left:10px;",
    "h3": "font-size:16px;font-weight:bold;margin:15px 0;color:#444;",
    "strong": "color:#000;font-weight:bold;",
    "blockquote": "border-left:3px solid #1aad19;padding:10px 15px;margin:15px 0;background:#f8f8f8;color:#666;font-size:15px;",
    "link": "color:#1aad19;text-decoration:none;",
    "list_item": "margin:8px 0;padding-left:5px;",
    "image": "max-width:100%;margin:15px 0;display:block;",
    "table": "width:100%;border-collapse:collapse;margin:15px 0;font-size:14px;",
    "table_header": "background:#f5f5f5;padding:10px;border:1px solid #ddd;font-weight:bold;",
    "table_cell": "padding:10px;border:1px solid #ddd;",
    "divider": "border:none;border-top:1px solid #eee;margin:20px 0;",
}

def format_paragraph(text):
    """格式化段落"""
    if not text.strip():
        return ""
    
    # 如果已经包含 HTML 标签，不处理
    if text.strip().startswith('<'):
        return text
    
    return f'<p style="{STYLES["body"]}"\u003e{text.strip()}</p>'

def markdown_to_wechat(content, custom_styles=None):
    """
    将 Markdown 转换为微信公众号 HTML
    
    Args:
        content: Markdown 内容
        custom_styles: 自定义样式字典
    
    Returns:
        微信公众号格式的 HTML
    """
    if custom_styles:
        STYLES.update(custom_styles)
    
    # 保存代码块（防止被转换）
    code_blocks = []
    def save_code(match):
        code_blocks.append(match.group(0))
        return f"___CODE_BLOCK_{len(code_blocks)-1}___"
    
    content = re.sub(r'```[\s\S]*?```', save_code, content)
    content = re.sub(r'`[^`]+`', save_code, content)
    
    # 处理标题
    content = re.sub(
        r'^# (.+)$',
        lambda m: f'<h1 style="{STYLES["h1"]}"\u003e{m.group(1).strip()}</h1>',
        content,
        flags=re.MULTILINE
    )
    content = re.sub(
        r'^## (.+)$',
        lambda m: f'<h2 style="{STYLES["h2"]}"\u003e{m.group(1).strip()}</h2>',
        content,
        flags=re.MULTILINE
    )
    content = re.sub(
        r'^### (.+)$',
        lambda m: f'<h3 style="{STYLES["h3"]}"\u003e{m.group(1).strip()}</h3>',
        content,
        flags=re.MULTILINE
    )
    
    # 处理粗体和斜体
    content = re.sub(
        r'\*\*(.+?)\*\*',
        lambda m: f'<strong style="{STYLES["strong"]}"\u003e{m.group(1)}</strong>',
        content
    )
    content = re.sub(r'\*(.+?)\*', r'<em\u003e\1</em>', content)
    
    # 处理引用块
    def format_quote(match):
        text = match.group(1).strip()
        # 特殊引用样式（带 emoji）
        if text.startswith('💡') or text.startswith('⚠️') or text.startswith('📌'):
            return f'<blockquote style="{STYLES["blockquote"]}"\u003e<strong\u003e{text[:2]}</strong>{text[2:]}</blockquote>'
        return f'<blockquote style="{STYLES["blockquote"]}"\u003e{text}</blockquote>'
    
    content = re.sub(r'^\> (.+)$', format_quote, content, flags=re.MULTILINE)
    
    # 处理有序列表
    def format_ol(match):
        items = match.group(0).strip().split('\n')
        html_items = []
        for item in items:
            if re.match(r'^\d+\. ', item):
                text = re.sub(r'^\d+\. ', '', item)
                html_items.append(f'<li style="{STYLES["list_item"]}"\u003e{text}</li>')
        return f'<ol style="margin:10px 0;padding-left:20px;"\u003e{"".join(html_items)}</ol>'
    
    content = re.sub(r'(^\d+\. .+\n?)+', format_ol, content, flags=re.MULTILINE)
    
    # 处理无序列表
    def format_ul(match):
        items = match.group(0).strip().split('\n')
        html_items = []
        for item in items:
            if item.startswith('- ') or item.startswith('* '):
                text = item[2:]
                html_items.append(f'<li style="{STYLES["list_item"]}"\u003e{text}</li>')
        return f'<ul style="margin:10px 0;padding-left:20px;"\u003e{"".join(html_items)}</ul>'
    
    content = re.sub(r'(^- .+\n?)+', format_ul, content, flags=re.MULTILINE)
    content = re.sub(r'(^\* .+\n?)+', format_ul, content, flags=re.MULTILINE)
    
    # 处理表格
    def format_table(match):
        lines = match.group(0).strip().split('\n')
        if len(lines) < 2:
            return match.group(0)
        
        # 表头
        headers = [cell.strip() for cell in lines[0].split('|') if cell.strip()]
        # 数据行
        rows = []
        for line in lines[2:]:  # 跳过表头和分隔符
            cells = [cell.strip() for cell in line.split('|') if cell.strip()]
            if cells:
                rows.append(cells)
        
        html = f'<table style="{STYLES["table"]}"\u003e<thead><tr>'
        for header in headers:
            html += f'<th style="{STYLES["table_header"]}"\u003e{header}</th>'
        html += '</tr></thead><tbody>'
        
        for row in rows:
            html += '<tr>'
            for cell in row:
                html += f'<td style="{STYLES["table_cell"]}"\u003e{cell}</td>'
            html += '</tr>'
        
        html += '</tbody></table>'
        return html
    
    content = re.sub(r'\|.+\|\n\|[-:\s|]+\|\n(\|.+\|\n?)+', format_table, content)
    
    # 处理链接
    content = re.sub(
        r'\[([^\]]+)\]\(([^)]+)\)',
        lambda m: f'<a href="{m.group(2)}" style="{STYLES["link"]}"\u003e{m.group(1)}</a>',
        content
    )
    
    # 处理图片
    content = re.sub(
        r'!\[([^\]]*)\]\(([^)]+)\)',
        lambda m: f'<img src="{m.group(2)}" alt="{m.group(1)}" style="{STYLES["image"]}" /\u003e',
        content
    )
    
    # 处理分割线
    content = re.sub(
        r'^---+$',
        lambda m: f'<hr style="{STYLES["divider"]}" /\u003e',
        content,
        flags=re.MULTILINE
    )
    
    # 恢复代码块
    for i, code in enumerate(code_blocks):
        # 简单处理代码块，用 pre 标签
        code_html = f'<pre style="background:#f5f5f5;padding:15px;border-radius:5px;overflow-x:auto;font-size:14px;line-height:1.6;"\u003e{code}</pre>'
        content = content.replace(f"___CODE_BLOCK_{i}___", code_html)
    
    # 处理段落（分段）
    paragraphs = []
    current = []
    
    for line in content.split('\n'):
        if line.strip().startswith('<'):
            # 如果已经积累了内容，先保存
            if current:
                paragraphs.append(format_paragraph('\n'.join(current)))
                current = []
            paragraphs.append(line)
        elif line.strip():
            current.append(line)
        else:
            if current:
                paragraphs.append(format_paragraph('\n'.join(current)))
                current = []
    
    if current:
        paragraphs.append(format_paragraph('\n'.join(current)))
    
    return '\n'.join(p for p in paragraphs if p)

def add_wechat_template(html_content, title=""):
    """添加微信公众号模板"""
    return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ margin: 0; padding: 20px; background: #f5f5f5; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif; }}
        .article {{ max-width: 680px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
    </style>
</head>
<body>
    <div class="article">
        {html_content}
    </div>
</body>
</html>'''

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Markdown 转公众号排版')
    parser.add_argument('--file', '-f', required=True, help='Markdown 文件路径')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--title', '-t', help='文章标题')
    parser.add_argument('--template', action='store_true', help='添加完整 HTML 模板')
    args = parser.parse_args()
    
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"❌ 文件不存在: {file_path}")
        return 1
    
    content = file_path.read_text(encoding='utf-8')
    
    # 提取标题
    title = args.title or ""
    if not title:
        first_line = content.split('\n')[0].strip()
        if first_line.startswith('# '):
            title = first_line[2:]
    
    print(f"📝 正在排版: {title or file_path.name}")
    
    # 转换
    html = markdown_to_wechat(content)
    
    if args.template:
        html = add_wechat_template(html, title)
        output_ext = '.html'
    else:
        output_ext = '.wechat.html'
    
    # 输出
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = file_path.with_suffix(output_ext)
    
    output_path.write_text(html, encoding='utf-8')
    print(f"✅ 排版完成: {output_path}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
