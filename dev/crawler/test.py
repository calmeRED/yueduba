import sqlite3

# 连接到SQLite数据库
conn = sqlite3.connect('meiriyiwen.db')

# 创建一个Cursor对象
cur = conn.cursor()

# 执行SQL语句来更改表名
# cur.execute("ALTER TABLE pages RENAME TO contents;")
cur.execute("DROP TABLE IF EXISTS sqlite_sequence;")

# 提交事务
conn.commit()

# 关闭Cursor和连接
cur.close()
conn.close()


