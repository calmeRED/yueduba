#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
阅读吧阅读器 - 构建脚本
将 meiriyiwen.db 中的文章数据导出为 JSON 文件
"""

import json
import re
import sqlite3
from collections import defaultdict
from pathlib import Path

# 项目路径
PROJECT_ROOT = Path(__file__).parent.parent.resolve()  # 改为项目根目录
SRC_DIR = PROJECT_ROOT / "src"
DB_PATH = PROJECT_ROOT / "crawler" / "data" / "meiriyiwen.db"
OUTPUT_DIR = PROJECT_ROOT  # 输出到项目根目录
DATA_DIR = OUTPUT_DIR / "data"
ARTICLES_DIR = DATA_DIR / "articles"
ARTICLE_DIR = OUTPUT_DIR / "article"
TEMPLATE_DIR = SRC_DIR / "templates"


def init_directories():
    """创建必要的目录结构"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ARTICLES_DIR.mkdir(parents=True, exist_ok=True)
    ARTICLE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"目录已创建/确认: {DATA_DIR}")
    print(f"目录已创建/确认: {ARTICLES_DIR}")
    print(f"目录已创建/确认: {ARTICLE_DIR}")


def connect_db():
    """连接 SQLite 数据库"""
    db_path = DB_PATH.resolve()
    print(f"连接数据库: {db_path}")
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"数据库连接失败: {e}")
        raise


def export_index(conn):
    """导出 data/index.json - 文章摘要列表"""
    cur = conn.cursor()
    cur.execute("SELECT id, title, author FROM contents ORDER BY id")
    rows = cur.fetchall()

    articles = [{"id": str(row["id"]), "title": row["title"], "author": row["author"]} for row in rows]

    output_path = OUTPUT_DIR / "index.json"
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
    except OSError as e:
        print(f"写入 index.json 失败: {e}")
        raise

    print(f"导出 index.json: {len(articles)} 条记录 -> {output_path}")


def export_authors(conn):
    """导出 data/authors.json - 作者列表及文章数量"""
    cur = conn.cursor()
    cur.execute("SELECT author, COUNT(*) as count FROM contents GROUP BY author ORDER BY count DESC, author")
    rows = cur.fetchall()

    authors = [{"name": row["author"], "count": row["count"]} for row in rows]

    output_path = OUTPUT_DIR / "authors.json"
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(authors, f, ensure_ascii=False, indent=2)
    except OSError as e:
        print(f"写入 authors.json 失败: {e}")
        raise

    print(f"导出 authors.json: {len(authors)} 位作者 -> {output_path}")


def get_article_template():
    """读取文章模板文件"""
    template_path = TEMPLATE_DIR / "article.html"
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except OSError as e:
        print(f"读取模板文件失败: {template_path} - {e}")
        raise


def render_template(template, data):
    """简单的模板渲染 - 替换 {{key}} 占位符"""
    result = template
    for key, value in data.items():
        if isinstance(value, str):
            result = result.replace(f'{{{{{key}}}}}', value)
    return result


def generate_article_pages(conn):
    """生成每篇文章的 HTML 页面"""
    template = get_article_template()
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, author, article FROM contents ORDER BY id')

    count = 0
    for row in cursor.fetchall():
        article_id, title, author, article = row
        # 转换文章正文（简单的段落分割）
        article_html = '\n'.join(f'<p>{p.strip()}</p>' for p in article.split('\n') if p.strip())

        data = {
            'title': title,
            'author': author,
            'article': article_html,
            'url': ''
        }

        html = render_template(template, data)
        article_path = ARTICLE_DIR / f'{article_id}.html'
        try:
            with open(article_path, 'w', encoding='utf-8') as f:
                f.write(html)
        except OSError as e:
            print(f"写入文章页面失败: {article_path} - {e}")
            continue
        count += 1

    print(f"生成文章 HTML 页面: {count} 篇 -> {ARTICLE_DIR}")


def copy_static_files():
    """复制静态资源到 OUTPUT_DIR"""
    # CSS
    css_src = SRC_DIR / 'css' / 'style.css'
    css_dst = OUTPUT_DIR / 'css' / 'style.css'
    css_dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(css_src, 'r', encoding='utf-8') as f:
            with open(css_dst, 'w', encoding='utf-8') as f_out:
                f_out.write(f.read())
        print(f"复制静态文件: {css_src} -> {css_dst}")
    except OSError as e:
        print(f"复制 CSS失败: {css_src} - {e}")

    # JS
    for js_file in ['utils.js', 'bookshelf.js', 'app.js']:
        src = SRC_DIR / 'js' / js_file
        dst = OUTPUT_DIR / 'js' / js_file
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(src, 'r', encoding='utf-8') as f:
                with open(dst, 'w', encoding='utf-8') as f_out:
                    f_out.write(f.read())
            print(f"复制静态文件: {src} -> {dst}")
        except OSError as e:
            print(f"复制 JS 文件失败: {src} - {e}")

    # HTML入口页
    for html_file in ['index.html', 'random.html']:
        src = SRC_DIR / html_file
        dst = OUTPUT_DIR / html_file
        if src.exists():
            try:
                with open(src, 'r', encoding='utf-8') as f:
                    with open(dst, 'w', encoding='utf-8') as f_out:
                        f_out.write(f.read())
                print(f"复制静态文件: {src} -> {dst}")
            except OSError as e:
                print(f"复制 HTML 文件失败: {src} - {e}")


def sanitize_filename(name):
    """将作者名转换为安全的文件名"""
    return re.sub(r'[<>:"/\\|?*]', '_', name)


def export_articles_by_author(conn):
    """导出 data/articles/{author}.json - 每个作者的文章详情"""
    cur = conn.cursor()
    cur.execute("SELECT id, title, author, article FROM contents ORDER BY id")
    rows = cur.fetchall()

    # 按作者分组
    author_data = defaultdict(list)
    for row in rows:
        author_data[row["author"]].append({
            "id": str(row["id"]),
            "title": row["title"],
            "author": row["author"],
            "article": row["article"]
        })

    # 导出每个作者的 JSON 文件
    for author, articles in author_data.items():
        filename = sanitize_filename(author) + ".json"
        output_path = ARTICLES_DIR / filename

        data = {"name": author, "articles": articles}
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except OSError as e:
            print(f"写入 {filename} 失败: {e}")
            continue

        print(f"导出 {filename}: {len(articles)} 篇文章")

    print(f"共导出 {len(author_data)} 个作者文件")


def main():
    print("=" * 50)
    print("阅读吧阅读器 - 构建脚本")
    print("=" * 50)

    # 1. 创建目录
    init_directories()

    # 2. 连接数据库
    conn = connect_db()

    try:
        # 3. 导出 index.json
        export_index(conn)

        # 4. 导出 authors.json
        export_authors(conn)

        # 5. 导出各作者文章
        export_articles_by_author(conn)

        # 6. 生成文章 HTML 页面
        generate_article_pages(conn)

        # 7. 复制静态资源
        copy_static_files()

        print("=" * 50)
        print("构建完成!")
        print("=" * 50)
    finally:
        conn.close()


if __name__ == "__main__":
    main()