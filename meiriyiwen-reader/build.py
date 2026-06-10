#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
每日一文阅读器 - 构建脚本
将 meiriyiwen.db 中的文章数据导出为 JSON 文件
"""

import json
import re
import sqlite3
from collections import defaultdict
from pathlib import Path

# 项目路径
PROJECT_ROOT = Path(__file__).parent.resolve()
DB_PATH = PROJECT_ROOT / ".." / "meiriyiwen.db"
OUTPUT_DIR = PROJECT_ROOT / "dist" / "data"
ARTICLES_DIR = OUTPUT_DIR / "articles"


def init_directories():
    """创建必要的目录结构"""
    ARTICLES_DIR.mkdir(parents=True, exist_ok=True)
    print(f"目录已创建/确认: {OUTPUT_DIR}")
    print(f"目录已创建/确认: {ARTICLES_DIR}")


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
    cur.execute("SELECT id, title, author FROM pages ORDER BY id")
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
    cur.execute("SELECT author, COUNT(*) as count FROM pages GROUP BY author ORDER BY count DESC, author")
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


def sanitize_filename(name):
    """将作者名转换为安全的文件名"""
    return re.sub(r'[<>:"/\\|?*]', '_', name)


def export_articles_by_author(conn):
    """导出 data/articles/{author}.json - 每个作者的文章详情"""
    cur = conn.cursor()
    cur.execute("SELECT id, title, author, article, url FROM pages ORDER BY id")
    rows = cur.fetchall()

    # 按作者分组
    author_data = defaultdict(list)
    for row in rows:
        author_data[row["author"]].append({
            "id": str(row["id"]),
            "title": row["title"],
            "author": row["author"],
            "article": row["article"],
            "url": row["url"]
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
    print("每日一文阅读器 - 构建脚本")
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

        print("=" * 50)
        print("构建完成!")
        print("=" * 50)
    finally:
        conn.close()


if __name__ == "__main__":
    main()