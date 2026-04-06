#!/usr/bin/env python3
"""
WeChat MP Article Formatter
Markdown 转公众号排版格式
"""
import re
import sys
from html import escape
from pathlib import Path

# 默认样式配置
BASE_STYLES = {
    "body": "font-size:16px;line-height:1.8;margin:10px 0;color:#333;text-align:justify;",
    "h1": "font-size:22px;font-weight:bold;text-align:center;margin:25px 0;color:#000;line-height:1.4;",
    "h2": "font-size:18px;font-weight:bold;margin:20px 0;color:#1aad19;border-left:4px solid #1aad19;padding-left:10px;line-height:1.5;",
    "h3": "font-size:16px;font-weight:bold;margin:15px 0;color:#444;line-height:1.5;",
    "strong": "color:#000;font-weight:bold;",
    "blockquote": "border-left:3px solid #1aad19;padding:10px 15px;margin:15px 0;background:#f8f8f8;color:#666;font-size:15px;",
    "link": "color:#1aad19;text-decoration:none;",
    "list_item": "margin:8px 0;padding-left:5px;",
    "image": "max-width:100%;margin:15px auto;display:block;border-radius:6px;",
    "table": "width:100%;border-collapse:collapse;margin:15px 0;font-size:14px;",
    "table_header": "background:#f5f5f5;padding:10px;border:1px solid #ddd;font-weight:bold;",
    "table_cell": "padding:10px;border:1px solid #ddd;vertical-align:top;",
    "divider": "border:none;border-top:1px solid #eee;margin:20px 0;",
    "code_block": "background:#f6f8fa;padding:15px;border-radius:8px;overflow-x:auto;font-size:14px;line-height:1.6;color:#333;",
    "inline_code": "background:#f6f8fa;color:#c7254e;padding:2px 6px;border-radius:4px;font-family:Menlo,Monaco,Consolas,monospace;font-size:0.92em;",
    "tip": "margin:18px 0;padding:14px 16px;background:#f6ffed;border-left:4px solid #52c41a;border-radius:8px;color:#2f5d1d;",
    "warning": "margin:18px 0;padding:14px 16px;background:#fff7e6;border-left:4px solid #fa8c16;border-radius:8px;color:#8c4a00;",
    "summary": "margin:18px 0;padding:14px 16px;background:#f0f5ff;border-left:4px solid #2f54eb;border-radius:8px;color:#1d39c4;",
    "cta": "margin:22px 0;padding:16px 18px;background:#fffbe6;border:1px solid #ffe58f;border-radius:10px;color:#614700;",
    "page_bg": "#f5f5f5",
    "page_font": "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif",
    "container_bg": "white",
    "container_shadow": "0 2px 10px rgba(0,0,0,0.1)",
}

THEMES = {
    "default": {},
    "wechat-native": {
        "body": "font-size:17px;line-height:1.78;margin:12px 0;color:#2f2f2f;text-align:justify;",
        "h1": "font-size:24px;font-weight:700;text-align:left;margin:8px 0 24px;color:#111;line-height:1.4;",
        "h2": "font-size:19px;font-weight:700;margin:28px 0 14px;color:#111;line-height:1.45;border-left:none;padding-left:0;",
        "h3": "font-size:17px;font-weight:700;margin:20px 0 12px;color:#222;line-height:1.45;",
        "blockquote": "border-left:3px solid #d9d9d9;padding:2px 0 2px 16px;margin:20px 0;background:transparent;color:#666;font-size:16px;",
        "link": "color:#576b95;text-decoration:none;",
        "table_header": "background:#fafafa;padding:10px;border:1px solid #e5e5e5;font-weight:bold;",
        "table_cell": "padding:10px;border:1px solid #e5e5e5;vertical-align:top;",
        "tip": "margin:18px 0;padding:14px 16px;background:#f7f7f7;border-left:3px solid #d9d9d9;border-radius:6px;color:#555;",
        "summary": "margin:18px 0;padding:14px 16px;background:#f7f7f7;border-left:3px solid #07c160;border-radius:6px;color:#333;",
        "cta": "margin:22px 0;padding:16px 18px;background:#f7f7f7;border:1px solid #e5e5e5;border-radius:8px;color:#333;",
    },
    "medium-clean": {
        "body": "font-size:18px;line-height:1.9;margin:14px 0;color:#242424;text-align:left;",
        "h1": "font-size:30px;font-weight:800;text-align:left;margin:10px 0 28px;color:#1a1a1a;line-height:1.25;",
        "h2": "font-size:24px;font-weight:800;margin:34px 0 16px;color:#1a1a1a;border-left:none;padding-left:0;line-height:1.35;",
        "h3": "font-size:20px;font-weight:700;margin:26px 0 12px;color:#1f1f1f;line-height:1.4;",
        "blockquote": "border-left:4px solid #1a8917;padding:4px 0 4px 18px;margin:24px 0;background:transparent;color:#555;font-size:17px;",
        "link": "color:#1a8917;text-decoration:none;",
        "code_block": "background:#f9f9f9;padding:18px;border-radius:8px;overflow-x:auto;font-size:14px;line-height:1.7;color:#333;",
        "tip": "margin:20px 0;padding:16px 18px;background:#f3fdf4;border-left:4px solid #1a8917;border-radius:8px;color:#216e1f;",
        "summary": "margin:20px 0;padding:16px 18px;background:#f7f7f7;border-left:4px solid #1a8917;border-radius:8px;color:#333;",
    },
    "notion-soft": {
        "body": "font-size:16px;line-height:1.85;margin:10px 0;color:#37352f;text-align:justify;",
        "h1": "font-size:28px;font-weight:700;text-align:left;margin:8px 0 24px;color:#2f3437;line-height:1.3;",
        "h2": "font-size:22px;font-weight:700;margin:28px 0 14px;color:#2f3437;border-left:none;padding-left:0;line-height:1.4;",
        "h3": "font-size:18px;font-weight:600;margin:22px 0 10px;color:#37352f;line-height:1.45;",
        "blockquote": "border-left:3px solid #d3d1cb;padding:4px 0 4px 16px;margin:18px 0;background:#fbfbfa;color:#6b6b6b;font-size:15px;",
        "link": "color:#0b6e99;text-decoration:none;",
        "table_header": "background:#f7f6f3;padding:10px;border:1px solid #e9e9e7;font-weight:bold;",
        "table_cell": "padding:10px;border:1px solid #e9e9e7;vertical-align:top;",
        "inline_code": "background:#f1f1ef;color:#eb5757;padding:2px 6px;border-radius:4px;font-family:Menlo,Monaco,Consolas,monospace;font-size:0.92em;",
        "code_block": "background:#f7f6f3;padding:16px;border-radius:8px;overflow-x:auto;font-size:14px;line-height:1.6;color:#37352f;",
        "tip": "margin:18px 0;padding:14px 16px;background:#f7f6f3;border-left:4px solid #9b9a97;border-radius:8px;color:#37352f;",
        "warning": "margin:18px 0;padding:14px 16px;background:#fff4e5;border-left:4px solid #d9730d;border-radius:8px;color:#8a4b08;",
        "summary": "margin:18px 0;padding:14px 16px;background:#eef3ff;border-left:4px solid #4c6ef5;border-radius:8px;color:#2b4acb;",
    },
    "tech-dark": {
        "body": "font-size:16px;line-height:1.85;margin:10px 0;color:#d7dde7;text-align:justify;",
        "h1": "font-size:28px;font-weight:800;text-align:left;margin:8px 0 24px;color:#ffffff;line-height:1.3;",
        "h2": "font-size:21px;font-weight:700;margin:28px 0 14px;color:#7cc7ff;border-left:4px solid #2f9bff;padding-left:12px;line-height:1.4;",
        "h3": "font-size:18px;font-weight:700;margin:20px 0 10px;color:#dbeafe;line-height:1.45;",
        "strong": "color:#ffffff;font-weight:bold;",
        "blockquote": "border-left:3px solid #2f9bff;padding:10px 15px;margin:15px 0;background:#111a2c;color:#bcd0ee;font-size:15px;",
        "link": "color:#7cc7ff;text-decoration:none;",
        "table_header": "background:#162033;padding:10px;border:1px solid #2b3952;font-weight:bold;",
        "table_cell": "padding:10px;border:1px solid #2b3952;vertical-align:top;",
        "divider": "border:none;border-top:1px solid #24324a;margin:22px 0;",
        "code_block": "background:#111827;padding:16px;border-radius:8px;overflow-x:auto;font-size:14px;line-height:1.6;color:#d1e7ff;",
        "inline_code": "background:#1f2937;color:#7dd3fc;padding:2px 6px;border-radius:4px;font-family:Menlo,Monaco,Consolas,monospace;font-size:0.92em;",
        "tip": "margin:18px 0;padding:14px 16px;background:#112a1f;border-left:4px solid #22c55e;border-radius:8px;color:#b7f7c5;",
        "warning": "margin:18px 0;padding:14px 16px;background:#2b1d12;border-left:4px solid #f59e0b;border-radius:8px;color:#ffd8a8;",
        "summary": "margin:18px 0;padding:14px 16px;background:#111a2c;border-left:4px solid #2f9bff;border-radius:8px;color:#bcd0ee;",
        "cta": "margin:22px 0;padding:16px 18px;background:#0f172a;border:1px solid #2f9bff;border-radius:10px;color:#dbeafe;",
        "page_bg": "#0b1020",
        "container_bg": "#0f172a",
        "container_shadow": "0 4px 24px rgba(0,0,0,0.35)",
    },
}

STYLES = dict(BASE_STYLES)

BLOCK_TAGS = (
    '<h1', '<h2', '<h3', '<blockquote', '<ul', '<ol', '<table', '<hr', '<pre',
    '<div', '<img', '<p'
)


def format_paragraph(text):
    """格式化段落"""
    text = text.strip()
    if not text:
        return ""
    if text.startswith(BLOCK_TAGS):
        return text
    return f'<p style="{STYLES["body"]}">{text}</p>'


def render_inline(text):
    """处理行内格式，尽量避免 Markdown 残留。"""
    text = escape(text)

    # 图片
    text = re.sub(
        r'!\[([^\]]*)\]\(([^)\s]+(?:\s+"[^"]+")?)\)',
        lambda m: f'<img src="{escape(m.group(2).split(" \"")[0], quote=True)}" alt="{escape(m.group(1), quote=True)}" style="{STYLES["image"]}" />',
        text,
    )

    # 链接
    text = re.sub(
        r'\[([^\]]+)\]\(([^)\s]+(?:\s+"[^"]+")?)\)',
        lambda m: f'<a href="{escape(m.group(2).split(" \"")[0], quote=True)}" style="{STYLES["link"]}">{m.group(1)}</a>',
        text,
    )

    # 行内代码
    text = re.sub(
        r'`([^`]+)`',
        lambda m: f'<code style="{STYLES["inline_code"]}">{m.group(1)}</code>',
        text,
    )

    # 粗体 / 斜体
    text = re.sub(
        r'\*\*([^*]+?)\*\*',
        lambda m: f'<strong style="{STYLES["strong"]}">{m.group(1)}</strong>',
        text,
    )
    text = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'<em>\1</em>', text)

    return text


def render_list(lines, ordered=False):
    tag = 'ol' if ordered else 'ul'
    html_items = []
    for line in lines:
        item = re.sub(r'^\s*(?:\d+\. |[-*] )', '', line).strip()
        html_items.append(f'<li style="{STYLES["list_item"]}">{render_inline(item)}</li>')
    return f'<{tag} style="margin:10px 0;padding-left:20px;">{"".join(html_items)}</{tag}>'


def render_table(block):
    lines = [line.strip() for line in block.splitlines() if line.strip()]
    if len(lines) < 2:
        return format_paragraph(render_inline(block))

    headers = [render_inline(cell.strip()) for cell in lines[0].strip('|').split('|')]
    rows = []
    for line in lines[2:]:
        cells = [render_inline(cell.strip()) for cell in line.strip('|').split('|')]
        rows.append(cells)

    html = [f'<table style="{STYLES["table"]}"><thead><tr>']
    html.extend(f'<th style="{STYLES["table_header"]}">{header}</th>' for header in headers)
    html.append('</tr></thead><tbody>')
    for row in rows:
        html.append('<tr>')
        for cell in row:
            html.append(f'<td style="{STYLES["table_cell"]}">{cell}</td>')
        html.append('</tr>')
    html.append('</tbody></table>')
    return ''.join(html)


def render_fenced_block(kind, body):
    labels = {
        'tip': ('提示', STYLES['tip']),
        'warning': ('注意', STYLES['warning']),
        'summary': ('小结', STYLES['summary']),
        'cta': ('行动建议', STYLES['cta']),
    }
    title, style = labels[kind]
    inner = '<br/>'.join(render_inline(line.strip()) for line in body.strip().splitlines() if line.strip())
    return f'<div style="{style}"><strong>{title}：</strong>{inner}</div>'


def strip_unconverted_markdown(text):
    """尽量清理不该残留到最终内容里的常见 Markdown 痕迹。"""
    text = re.sub(r'(^|>)(\s*#{1,6}\s+)', r'\1', text)
    text = re.sub(r'(^|\n)\s*[-*]\s+', r'\1', text)
    text = re.sub(r'(^|\n)\s*\d+\.\s+', r'\1', text)
    return text


def build_styles(theme='default', custom_styles=None):
    styles = dict(BASE_STYLES)
    styles.update(THEMES.get(theme, {}))
    if custom_styles:
        styles.update(custom_styles)
    return styles


def markdown_to_wechat(content, custom_styles=None, theme='default'):
    """将 Markdown 转换为微信公众号 HTML。"""
    global STYLES
    STYLES = build_styles(theme, custom_styles)

    # fenced components
    content = re.sub(
        r'::: *(tip|warning|summary|cta)\n([\s\S]*?)\n:::',
        lambda m: render_fenced_block(m.group(1), m.group(2)),
        content,
    )

    # fenced code blocks
    content = re.sub(
        r'```(?:([\w+-]+)\n)?([\s\S]*?)```',
        lambda m: f'<pre style="{STYLES["code_block"]}"><code>{escape(m.group(2).strip())}</code></pre>',
        content,
    )

    blocks = re.split(r'\n\s*\n', content.strip())
    rendered = []

    for block in blocks:
        block = block.strip()
        if not block:
            continue
        if block.startswith(BLOCK_TAGS):
            rendered.append(block)
            continue
        if re.fullmatch(r'---+', block):
            rendered.append(f'<hr style="{STYLES["divider"]}" />')
            continue

        lines = [line.rstrip() for line in block.splitlines() if line.strip()]
        if len(lines) >= 2 and all('|' in line for line in lines[:2]) and re.match(r'^\|?\s*[-: ]+(?:\|\s*[-: ]+)+\|?\s*$', lines[1]):
            rendered.append(render_table(block))
            continue
        if not lines:
            continue

        if all(re.match(r'^\d+\.\s+', line.strip()) for line in lines):
            rendered.append(render_list(lines, ordered=True))
            continue
        if all(re.match(r'^[-*]\s+', line.strip()) for line in lines):
            rendered.append(render_list(lines, ordered=False))
            continue
        if all(line.strip().startswith('> ') for line in lines):
            quote = ' '.join(render_inline(line.strip()[2:]) for line in lines)
            rendered.append(f'<blockquote style="{STYLES["blockquote"]}">{quote}</blockquote>')
            continue

        if len(lines) == 1 and re.match(r'^###\s+', lines[0]):
            rendered.append(f'<h3 style="{STYLES["h3"]}">{render_inline(re.sub(r"^###\s+", "", lines[0]).strip())}</h3>')
            continue
        if len(lines) == 1 and re.match(r'^##\s+', lines[0]):
            rendered.append(f'<h2 style="{STYLES["h2"]}">{render_inline(re.sub(r"^##\s+", "", lines[0]).strip())}</h2>')
            continue
        if len(lines) == 1 and re.match(r'^#\s+', lines[0]):
            rendered.append(f'<h1 style="{STYLES["h1"]}">{render_inline(re.sub(r"^#\s+", "", lines[0]).strip())}</h1>')
            continue

        paragraph = ' '.join(line.strip() for line in lines)
        paragraph = strip_unconverted_markdown(paragraph)
        rendered.append(format_paragraph(render_inline(paragraph)))

    return '\n'.join(part for part in rendered if part)


def add_wechat_template(html_content, title=""):
    """添加微信公众号模板"""
    return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ margin: 0; padding: 20px; background: {STYLES["page_bg"]}; font-family: {STYLES["page_font"]}; }}
        .article {{ max-width: 680px; margin: 0 auto; background: {STYLES["container_bg"]}; padding: 30px; border-radius: 8px; box-shadow: {STYLES["container_shadow"]}; }}
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
    parser.add_argument('--theme', default='default', choices=sorted(THEMES.keys()), help='排版风格主题')
    parser.add_argument('--template', action='store_true', help='添加完整 HTML 模板')
    args = parser.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"❌ 文件不存在: {file_path}")
        return 1

    content = file_path.read_text(encoding='utf-8')

    title = args.title or ""
    if not title:
        first_line = content.split('\n')[0].strip()
        if first_line.startswith('# '):
            title = first_line[2:]

    print(f"📝 正在排版: {title or file_path.name} (theme={args.theme})")

    html = markdown_to_wechat(content, theme=args.theme)

    if args.template:
        html = add_wechat_template(html, title)
        output_ext = '.html'
    else:
        output_ext = '.wechat.html'

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = file_path.with_suffix(output_ext)

    output_path.write_text(html, encoding='utf-8')
    print(f"✅ 排版完成: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
