import sqlite3

# 连接到SQLite数据库
conn = sqlite3.connect('meiriyiwen.db')
cur = conn.cursor()

# 步骤2: 创建新表（如果已存在则先删除）
cur.execute("DROP TABLE IF EXISTS unique_pages;")
cur.execute("""
    CREATE TABLE unique_pages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        author TEXT,
        title TEXT,
        article TEXT
    );
""")

# 步骤3: 将不重复的条目插入新表
cur.execute("""
    INSERT INTO unique_pages (author, title, article)
    SELECT DISTINCT author, title, article
    FROM contents;
""")

# 步骤4: 重命名并删除原始表
cur.execute("DROP TABLE contents;")
cur.execute("ALTER TABLE unique_pages RENAME TO contents;")


# 提交更改
conn.commit()

# 关闭游标和连接
cur.close()
conn.close()
