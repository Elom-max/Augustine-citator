#!/usr/bin/env python3
"""Minimal Markdown -> HTML renderer for AppSource policy pages.

Handles: headings (#, ##, ###), paragraphs (with line-wrap join), bullet
lists (with multi-line continuation), bold/italic/code inline, autolinks
(<https://...>) and Markdown links ([text](url)).

Usage: render_md.py SRC.md DST.html "Page title"
"""
import sys
import re
import html
from pathlib import Path


CSS = (
    "body{font-family:system-ui,sans-serif;max-width:760px;margin:40px auto;"
    "padding:0 20px;line-height:1.6;color:#2c1810}"
    "h1,h2,h3{font-family:Georgia,serif}"
    "h1{border-bottom:1px solid #d4c9b8;padding-bottom:8px}"
    "code{background:#f5f0e8;padding:2px 6px;border-radius:3px;"
    "font-family:Menlo,monospace}"
    "a{color:#b8422c}"
)


def inline(body: str) -> str:
    body = html.escape(body)
    body = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', body)
    body = re.sub(r'\*(.+?)\*', r'<em>\1</em>', body)
    body = re.sub(r'`(.+?)`', r'<code>\1</code>', body)
    body = re.sub(r'&lt;(https?://[^&\s]+)&gt;', r'<a href="\1">\1</a>', body)
    body = re.sub(r'\[(.+?)\]\((https?://[^)]+)\)', r'<a href="\2">\1</a>', body)
    return body


def render(text: str) -> str:
    out: list[str] = []
    buf: list[str] = []
    in_list = False

    def flush_paragraph() -> None:
        nonlocal buf
        if buf:
            out.append('<p>' + inline(' '.join(buf)) + '</p>')
            buf = []

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            out.append('</ul>')
            in_list = False

    for raw_line in text.split('\n'):
        line = raw_line.rstrip()
        if not line.strip():
            flush_paragraph()
            close_list()
            continue
        if line.startswith('### '):
            flush_paragraph(); close_list()
            out.append(f'<h3>{inline(line[4:])}</h3>')
            continue
        if line.startswith('## '):
            flush_paragraph(); close_list()
            out.append(f'<h2>{inline(line[3:])}</h2>')
            continue
        if line.startswith('# '):
            flush_paragraph(); close_list()
            out.append(f'<h1>{inline(line[2:])}</h1>')
            continue
        if line.startswith('- '):
            flush_paragraph()
            if not in_list:
                out.append('<ul>')
                in_list = True
            out.append(f'  <li>{inline(line[2:])}</li>')
            continue
        if in_list and (raw_line.startswith('  ') or raw_line.startswith('\t')):
            last = out[-1]
            if last.endswith('</li>'):
                out[-1] = last[:-5] + ' ' + inline(line.strip()) + '</li>'
            continue
        close_list()
        buf.append(line)

    flush_paragraph()
    close_list()
    return '\n'.join(out)


def main() -> int:
    if len(sys.argv) != 4:
        print('Usage: render_md.py SRC.md DST.html TITLE', file=sys.stderr)
        return 2
    src, dst, title = sys.argv[1], sys.argv[2], sys.argv[3]
    body = render(Path(src).read_text(encoding='utf-8'))
    safe_title = html.escape(title)
    page = (
        '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">'
        f'<title>{safe_title}</title>'
        f'<style>{CSS}</style>'
        '</head><body>'
        f'{body}'
        '</body></html>'
    )
    Path(dst).write_text(page, encoding='utf-8')
    return 0


if __name__ == '__main__':
    sys.exit(main())
