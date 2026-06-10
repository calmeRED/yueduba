import sqlite3
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# 打开并读取url.txt文件的所有行
with open('meiriyiwen.txt', 'r') as file:
    urls = file.readlines()
urls = [url.strip() for url in urls[::-1]]

# 创建或打开SQLite数据库
conn = sqlite3.connect('meiriyiwen.db')
cursor = conn.cursor()

# 获取数据库中所有表的名称
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

# 删除每个表中的所有数据
for table_name in tables:
    print(f"Clearing table: {table_name[0]}")
    cursor.execute(f"DELETE FROM {table_name[0]}")

# 创建一个表来存储页面内容
cursor.execute('''
CREATE TABLE IF NOT EXISTS pages (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    article TEXT NOT NULL,
    url TEXT NOT NULL
)
''')

for url in tqdm(urls):
    url = url.strip()  # 移除行尾的换行符
    # 使用requests获取页面内容
    response = requests.get(url)
    html_content = response.text

    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # 只存储<article id="_tl_editor" class="tl_specified_content">下的内容
    specified_content = soup.find('article', {'id': '_tl_editor'})
    # 提取标题
    title = specified_content.find('h1').text.strip()

    # 提取作者
    author = specified_content.find('address').text.strip()

    # 移除<h1>和<address>标签以及它们的内容
    [s.extract() for s in specified_content(['h1', 'address'])]

    # 剩余的内容即为文章内容
    article = "\n".join(specified_content.stripped_strings)

    # 将页面内容插入表中
    cursor.execute('INSERT INTO pages (title, author, article, url) VALUES (?, ?, ?, ?)', (title, author, article, url))

# 提交更改并关闭数据库连接
conn.commit()
conn.close()

print("所有页面内容已成功存储到SQLite数据库中。")
