# 阅读吧阅读器 实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 构建一个纯前端 GitHub Pages 阅读器，支持书架导航、随机阅读和暗黑模式

**架构：** 多页面静态站点 + 构建时数据导出。构建脚本将 SQLite 数据转换为 JSON 文件和预渲染 HTML 页面，前端纯 HTML/CSS/JS 无框架依赖。

**技术栈：** Python 3（构建脚本）、纯 HTML/CSS/JS（前端）

---

## 文件结构

```
meiriyiwen-reader/
├── build.py                    # 构建脚本：SQLite → JSON + HTML
├── src/
│   ├── index.html # 书架入口页面
│   ├── random.html            # 随机跳转页
│   ├── 404.html               # 404 页面
│   ├── css/
│   │   └── style.css          # 全局样式（含暗黑模式）
│   ├── js/
│   │   ├── app.js             # 主逻辑（导航、主题切换）
│   │   ├── bookshelf.js       # 书架逻辑（加载作者/文章）
│   │   └── utils.js           # 工具函数
│   └── templates/
│       └── article.html       # 文章详情页模板
└── dist/ # 构建输出（部署到 GitHub Pages）
    ├── index.html
    ├── random.html
    ├── 404.html
    ├── css/
    │   └── style.css
    ├── js/
    │   ├── app.js
    │   ├── bookshelf.js
    │   └── utils.js
    └── data/
        ├── index.json          # 文章摘要索引
        ├── authors.json        # 作者列表
        └── articles/           # 按作者分片的文章数据
            ├── 汪曾祺.json
            └── ...
```

---

## 任务 1：构建脚本（build.py）

**文件：**
- 创建：`meiriyiwen-reader/build.py`

```python
#!/usr/bin/env python3
"""
阅读吧阅读器构建脚本
从 meiriyiwen.db 导出数据并生成静态站点
"""
import sqlite3
import json
import os
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / 'meiriyiwen.db'
OUTPUT_DIR = Path(__file__).parent / 'dist'
DATA_DIR = OUTPUT_DIR / 'data'
ARTICLE_DIR = OUTPUT_DIR / 'article'

def get_db_connection():
    return sqlite3.connect(DB_PATH)

def export_index_json(conn):
    """导出文章摘要索引（用于随机功能）"""
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, author FROM pages ORDER BY id')
    articles = [{'id': str(row[0]), 'title': row[1], 'author': row[2]} for row in cursor.fetchall()]
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(DATA_DIR / 'index.json', 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    return len(articles)

def export_authors_json(conn):
    """导出作者列表"""
    cursor = conn.cursor()
    cursor.execute('SELECT author, COUNT(*) as count FROM pages GROUP BY author ORDER BY author')
    authors = [{'name': row[0], 'count': row[1]} for row in cursor.fetchall()]
    with open(DATA_DIR / 'authors.json', 'w', encoding='utf-8') as f:
        json.dump(authors, f, ensure_ascii=False, indent=2)
    return authors

def export_articles_by_author(conn, authors):
    """按作者导出文章详情"""
    cursor = conn.cursor()
    ARTICLE_DIR.mkdir(parents=True, exist_ok=True)
    for author_data in authors:
        author = author_data['name']
        cursor.execute('SELECT id, title, author, article, url FROM pages WHERE author = ?', (author,))
        articles = [{
            'id': str(row[0]),
            'title': row[1],
            'author': row[2],
            'article': row[3],
            'url': row[4]
        } for row in cursor.fetchall()]
        safe_author = author.replace('/', '_').replace('\\', '_')
        with open(DATA_DIR / 'articles' / f'{safe_author}.json', 'w', encoding='utf-8') as f:
            json.dump({'name': author, 'articles': articles}, f, ensure_ascii=False, indent=2)

def main():
    conn = get_db_connection()
    print('正在导出 index.json...')
    total = export_index_json(conn)
    print(f'已导出 {total}篇文章摘要')
    print('正在导出 authors.json...')
    authors = export_authors_json(conn)
    print(f'已导出 {len(authors)} 位作者')
    print('正在按作者导出文章...')
    export_articles_by_author(conn, authors)
    print('构建完成！')

if __name__ == '__main__':
    main()
```

- [ ] **步骤 1：创建 build.py 构建脚本**

- [ ] **步骤 2：运行脚本验证数据导出**

运行：`python meiriyiwen-reader/build.py`
预期：输出 "构建完成！"，生成 `dist/data/` 下的 JSON 文件

- [ ] **步骤 3：检查生成的 JSON 文件内容**

运行：`head -20 meiriyiwen-reader/dist/data/index.json`
预期：显示文章摘要列表

- [ ] **步骤 4：Commit**

```bash
git add meiriyiwen-reader/build.py
git commit -m "feat: 添加构建脚本 build.py"
```

---

## 任务 2：全局样式（style.css）

**文件：**
- 创建：`meiriyiwen-reader/src/css/style.css`

```css
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  --bg-primary: #fafafa;
  --bg-secondary: #ffffff;
  --bg-card: #ffffff;
  --text-primary: #1a1a1a;
  --text-secondary: #666666;
  --accent: #4a90d9;
  --border: #e5e5e5;
  --sidebar-width: 200px;
  --panel-width: 240px;
  --header-height: 56px;
}

body.dark {
  --bg-primary: #1a1a1a;
  --bg-secondary: #2d2d2d;
  --bg-card: #333333;
  --text-primary: #e8e8e8;
  --text-secondary: #a0a0a0;
  --accent: #6ba3e8;
  --border: #404040;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
  transition: background 0.3s, color 0.3s;
  min-height: 100vh;
}

/* Header */
.header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: var(--header-height);
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  z-index: 100;
}

.logo {
  font-size: 18px;
  font-weight: 600;
  color: var(--accent);
  text-decoration: none;
}

.theme-toggle {
  width: 48px;
  height: 28px;
  border-radius: 14px;
  background: var(--border);
  border: none;
  cursor: pointer;
  position: relative;
  transition: background 0.3s;
}

.theme-toggle::after {
  content: '☀️';
  position: absolute;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: white;
  top: 3px;
  left: 3px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  transition: transform 0.3s;
}

body.dark .theme-toggle {
  background: var(--accent);
}

body.dark .theme-toggle::after {
  content: '🌙';
  transform: translateX(20px);
}

/* Main Layout */
.main-layout {
  display: flex;
  padding-top: var(--header-height);
  min-height: 100vh;
}

/* Navigation Sidebar */
.nav-sidebar {
  width: var(--sidebar-width);
  background: var(--bg-secondary);
  border-right: 1px solid var(--border);
  position: fixed;
  top: var(--header-height);
  left: 0;
  bottom: 0;
  padding: 16px 0;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  cursor: pointer;
  color: var(--text-secondary);
  transition: all 0.2s;
  font-size: 14px;
  text-decoration: none;
}

.nav-item:hover {
  background: var(--border);
  color: var(--text-primary);
}

.nav-item.active {
  color: var(--accent);
  background: var(--bg-primary);
  border-left: 3px solid var(--accent);
}

.nav-item .icon {
  margin-right: 10px;
  font-size: 16px;
}

/* Author Panel */
.author-panel {
  width: var(--panel-width);
  background: var(--bg-secondary);
  border-right: 1px solid var(--border);
  position: fixed;
  top: var(--header-height);
  left: var(--sidebar-width);
  bottom: 0;
  overflow-y: auto;
  padding: 16px 0;
}

.panel-title {
  padding: 0 16px 12px;
  font-size: 12px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.author-item {
  padding: 10px 16px;
  cursor: pointer;
  transition: background 0.2s;
  font-size: 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.author-item:hover {
  background: var(--border);
}

.author-item.active {
  background: var(--accent);
  color: white;
}

.author-count {
  font-size: 12px;
  color: var(--text-secondary);
}

.author-item.active .author-count {
  color: rgba(255, 255, 255, 0.7);
}

/* Article List in Panel */
.article-list {
  display: none;
  padding: 8px 0;
  background: var(--bg-primary);
}

.article-list.expanded {
  display: block;
}

.article-list-item {
  padding: 8px 16px 8px 32px;
  cursor: pointer;
  font-size: 13px;
  color: var(--text-secondary);
  transition: color 0.2s;
}

.article-list-item:hover {
  color: var(--accent);
}

/* Main Content */
.content-area {
  margin-left: calc(var(--sidebar-width) + var(--panel-width));
  padding: 40px 60px;
  width: calc(100% - var(--sidebar-width) - var(--panel-width));
  max-width: 800px;
}

/* Article View */
.article-header {
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--border);
}

.article-title {
  font-size: 28px;
  line-height: 1.3;
  margin-bottom: 12px;
}

.article-author {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.article-source {
  font-size: 12px;
  color: var(--text-secondary);
}

.article-source a {
  color: var(--accent);
  text-decoration: none;
}

.article-body {
  font-size: 18px;
  line-height: 1.8;
  color: var(--text-primary);
}

.article-body p {
  margin-bottom: 1.2em;
  text-align: justify;
}

/* Welcome View */
.welcome-view {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
}

.welcome-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.welcome-title {
  font-size: 24px;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.welcome-desc {
  font-size: 16px;
  line-height: 1.6;
}

/* Loading State */
.loading {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .nav-sidebar {
    width: 100%;
    position: relative;
    top: 0;
    display: flex;
    border-right: none;
    border-bottom: 1px solid var(--border);
  }

  .author-panel {
    position: relative;
    top: 0;
    left: 0;
    width: 100%;
    max-height: 200px;
    border-right: none;
    border-bottom: 1px solid var(--border);
  }

  .content-area {
    margin-left: 0;
    width: 100%;
    padding: 24px 20px;
  }
}
```

- [ ] **步骤 1：创建 style.css**

- [ ] **步骤 2：验证 CSS 语法**

检查文件是否存在且内容正确

- [ ] **步骤 3：Commit**

```bash
git add meiriyiwen-reader/src/css/style.css
git commit -m "feat: 添加全局样式（含暗黑模式 CSS变量）"
```

---

## 任务 3：工具函数（utils.js）

**文件：**
- 创建：`meiriyiwen-reader/src/js/utils.js`

```javascript
/**
 * 工具函数
 */
const Utils = {
  /**
   * 加载 JSON 数据
   * @param {string} url - JSON 文件路径
   * @returns {Promise<Object>}
   */
  async loadJSON(url) {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Failed to load ${url}: ${response.status}`);
    }
    return response.json();
  },

  /**
   * 获取暗黑模式状态
   * @returns {boolean}
   */
  isDarkMode() {
    return localStorage.getItem('theme') === 'dark';
  },

  /**
   * 设置暗黑模式状态
   * @param {boolean} isDark
   */
  setDarkMode(isDark) {
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    document.body.classList.toggle('dark', isDark);
  },

  /**
   * 初始化暗黑模式
   */
  initTheme() {
    const isDark = this.isDarkMode();
    document.body.classList.toggle('dark', isDark);
  },

  /**
   * 获取 URL 参数
   * @param {string} name - 参数名
   * @returns {string|null}
   */
  getQueryParam(name) {
    const params = new URLSearchParams(window.location.search);
    return params.get(name);
  },

  /**
   * 安全化作者名（用于文件路径）
   * @param {string} author
   * @returns {string}
   */
  sanitizeAuthor(author) {
    return author.replace('/', '_').replace('\\', '_');
  }
};

// 导出给全局使用
window.Utils = Utils;
```

- [ ] **步骤 1：创建 utils.js**

- [ ] **步骤 2：Commit**

```bash
git add meiriyiwen-reader/src/js/utils.js
git commit -m "feat: 添加工具函数 utils.js"
```

---

## 任务 4：书架逻辑（bookshelf.js）

**文件：**
- 创建：`meiriyiwen-reader/src/js/bookshelf.js`

```javascript
/**
 * 书架逻辑
 */
const Bookshelf = {
  currentAuthor: null,

  /**
   * 初始化书架
   */
  async init() {
    Utils.initTheme();
    await this.loadAuthors();
  },

  /**
   * 加载作者列表
   */
  async loadAuthors() {
    const container = document.getElementById('author-list');
    if (!container) return;

    container.innerHTML = '<div class="loading">加载中...</div>';

    try {
      const authors = await Utils.loadJSON('data/authors.json');
      this.renderAuthors(authors);
    } catch (error) {
      container.innerHTML = '<div class="loading">加载失败</div>';
      console.error('Failed to load authors:', error);
    }
  },

  /**
   * 渲染作者列表
   * @param {Array} authors - 作者数据
   */
  renderAuthors(authors) {
    const container = document.getElementById('author-list');
    container.innerHTML = authors.map(author => `
      <div class="author-item" data-author="${Utils.sanitizeAuthor(author.name)}">
        <span class="author-name">${author.name}</span>
        <span class="author-count">(${author.count})</span>
      </div>
    `).join('');

    //绑定点击事件
    container.querySelectorAll('.author-item').forEach(item => {
      item.addEventListener('click', () => this.selectAuthor(item.dataset.author));
    });
  },

  /**
   * 选择作者，加载该作者文章列表
   * @param {string} authorKey - 安全化后的作者名
   */
  async selectAuthor(authorKey) {
    // 更新高亮状态
    document.querySelectorAll('.author-item').forEach(item => {
      item.classList.toggle('active', item.dataset.author === authorKey);
    });

    // 显示文章列表
    let articleList = document.getElementById('article-list-' + authorKey);
    if (!articleList) {
      // 需要加载该作者的文章
      const authorName = this.getAuthorNameFromKey(authorKey);
      try {
        const data = await Utils.loadJSON(`data/articles/${authorKey}.json`);
        this.renderArticleList(authorKey, data.articles);
        articleList = document.getElementById('article-list-' + authorKey);
      } catch (error) {
        console.error('Failed to load articles:', error);
        return;
      }
    }

    // 切换展开状态
    document.querySelectorAll('.article-list').forEach(list => {
      if (list.id === 'article-list-' + authorKey) {
        list.classList.toggle('expanded');
      } else {
        list.classList.remove('expanded');
      }
    });
  },

  /**
   *渲染文章列表
   * @param {string} authorKey
   * @param {Array} articles
   */
  renderArticleList(authorKey, articles) {
    const container = document.getElementById('author-list');
    const authorItem = container.querySelector(`[data-author="${authorKey}"]`);
    const listHtml = `
      <div class="article-list" id="article-list-${authorKey}">
        ${articles.map(article => `
          <div class="article-list-item" data-id="${article.id}">
            ${article.title}
          </div>
        `).join('')}
      </div>
    `;
    authorItem.insertAdjacentHTML('afterend', listHtml);

    // 绑定文章点击事件
    container.querySelectorAll(`#article-list-${authorKey} .article-list-item`).forEach(item => {
      item.addEventListener('click', () => {
        window.location.href = `article/${item.dataset.id}.html`;
      });
    });
  },

  /**
   * 从 key 获取原始作者名
   * @param {string} authorKey
   * @returns {string}
   */
  getAuthorNameFromKey(authorKey) {
    return authorKey.replace(/_/g, '/');
  }
};

// 导出给全局使用
window.Bookshelf = Bookshelf;
```

- [ ] **步骤 1：创建 bookshelf.js**

- [ ] **步骤 2：Commit**

```bash
git add meiriyiwen-reader/src/js/bookshelf.js
git commit -m "feat: 添加书架逻辑 bookshelf.js"
```

---

## 任务 5：主逻辑（app.js）

**文件：**
- 创建：`meiriyiwen-reader/src/js/app.js`

```javascript
/**
 * 主逻辑
 */
const App = {
  /**
   * 初始化应用
   */
  init() {
    Utils.initTheme();
    this.bindEvents();
  },

  /**
   * 绑定全局事件
   */
  bindEvents() {
    // 主题切换按钮
    const themeToggle = document.querySelector('.theme-toggle');
    if (themeToggle) {
      themeToggle.addEventListener('click', () => this.toggleTheme());
    }

    // 导航项点击
    document.querySelectorAll('.nav-item').forEach(item => {
      item.addEventListener('click', (e) => {
        const action = e.currentTarget.dataset.action;
        if (action === 'random') {
          window.location.href = 'random.html';
        }
      });
    });
  },

  /**
   * 切换暗黑模式
   */
  toggleTheme() {
    const isDark = !Utils.isDarkMode();
    Utils.setDarkMode(isDark);
  }
};

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', () => App.init());
```

- [ ] **步骤 1：创建 app.js**

- [ ] **步骤 2：Commit**

```bash
git add meiriyiwen-reader/src/js/app.js
git commit -m "feat: 添加主逻辑 app.js"
```

---

## 任务 6：书架入口页（index.html）

**文件：**
- 创建：`meiriyiwen-reader/src/index.html`

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>阅读吧 - 阅读器</title>
  <link rel="stylesheet" href="css/style.css">
</head>
<body>
  <header class="header">
    <a href="index.html" class="logo">阅读吧</a>
    <button class="theme-toggle" aria-label="切换暗黑模式"></button>
  </header>

  <div class="main-layout">
    <nav class="nav-sidebar">
      <a href="random.html" class="nav-item" data-action="random">
        <span class="icon">🎲</span>
        随机
      </a>
      <span class="nav-item active">
        <span class="icon">📚</span>
        书架
      </span>
    </nav>

    <aside class="author-panel">
      <div class="panel-title">作者列表</div>
      <div id="author-list">
        <div class="loading">加载中...</div>
      </div>
    </aside>

    <main class="content-area" id="main-content">
      <div class="welcome-view">
        <div class="welcome-icon">📖</div>
        <h1 class="welcome-title">阅读吧</h1>
        <p class="welcome-desc">
          从左侧选择一个作者<br>
          开始你的阅读之旅
        </p>
      </div>
    </main>
  </div>

  <script src="js/utils.js"></script>
  <script src="js/bookshelf.js"></script>
  <script src="js/app.js"></script>
  <script>
    // 初始化书架
    Bookshelf.init();
  </script>
</body>
</html>
```

- [ ] **步骤 1：创建 index.html**

- [ ] **步骤 2：Commit**

```bash
git add meiriyiwen-reader/src/index.html
git commit -m "feat: 添加书架入口页 index.html"
```

---

## 任务 7：随机跳转页（random.html）

**文件：**
- 创建：`meiriyiwen-reader/src/random.html`

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>随机阅读 - 阅读吧</title>
  <link rel="stylesheet" href="css/style.css">
</head>
<body>
  <header class="header">
    <a href="index.html" class="logo">阅读吧</a>
    <button class="theme-toggle" aria-label="切换暗黑模式"></button>
  </header>

  <div class="main-layout">
    <nav class="nav-sidebar">
      <a href="random.html" class="nav-item active" data-action="random">
        <span class="icon">🎲</span>
        随机
      </a>
      <a href="index.html" class="nav-item">
        <span class="icon">📚</span>
        书架
      </a>
    </nav>

    <div style="margin-left: calc(var(--sidebar-width) + var(--panel-width)); padding: 40px;">
      <div class="loading">正在随机选取文章...</div>
    </div>
  </div>

  <script src="js/utils.js"></script>
  <script src="js/app.js"></script>
  <script>
    (async function() {
      try {
        const articles = await Utils.loadJSON('data/index.json');
        const randomIndex = Math.floor(Math.random() * articles.length);
        const article = articles[randomIndex];
        window.location.href = `article/${article.id}.html`;
      } catch (error) {
        console.error('Failed to load articles:', error);
        document.querySelector('.loading').textContent = '加载失败，请刷新重试';
      }
    })();
  </script>
</body>
</html>
```

- [ ] **步骤 1：创建 random.html**

- [ ] **步骤 2：Commit**

```bash
git add meiriyiwen-reader/src/random.html
git commit -m "feat: 添加随机跳转页 random.html"
```

---

## 任务 8：文章详情页模板（article.html）

**文件：**
- 创建：`meiriyiwen-reader/src/templates/article.html`

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{title}} - 阅读吧</title>
  <link rel="stylesheet" href="../css/style.css">
</head>
<body>
  <header class="header">
    <a href="../index.html" class="logo">阅读吧</a>
    <button class="theme-toggle" aria-label="切换暗黑模式"></button>
  </header>

  <div class="main-layout">
    <nav class="nav-sidebar">
      <a href="../random.html" class="nav-item" data-action="random">
        <span class="icon">🎲</span>
        随机
      </a>
      <a href="../index.html" class="nav-item">
        <span class="icon">📚</span>
        书架
      </a>
    </nav>

    <article class="content-area">
      <div class="article-header">
        <h1 class="article-title">{{title}}</h1>
        <div class="article-author">{{author}}</div>
        {{#url}}
        <div class="article-source">
          原文：<a href="{{url}}" target="_blank" rel="noopener">查看原文</a>
        </div>
        {{/url}}
      </div>
      <div class="article-body">
        {{article}}
      </div>
    </article>
  </div>

  <script src="../js/utils.js"></script>
  <script src="../js/app.js"></script>
</body>
</html>
```

- [ ] **步骤 1：创建 article.html 模板**

- [ ] **步骤 2：Commit**

```bash
git add meiriyiwen-reader/src/templates/article.html
git commit -m "feat: 添加文章详情页模板"
```

---

## 任务 9：完善构建脚本（生成 HTML页面）

**文件：**
- 修改：`meiriyiwen-reader/build.py`

```python
#!/usr/bin/env python3
"""
阅读吧阅读器构建脚本
从 meiriyiwen.db 导出数据并生成静态站点
"""
import sqlite3
import json
import os
import re
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / 'meiriyiwen.db'
OUTPUT_DIR = Path(__file__).parent / 'dist'
SRC_DIR = Path(__file__).parent / 'src'
DATA_DIR = OUTPUT_DIR / 'data'
ARTICLE_DIR = OUTPUT_DIR / 'article'
TEMPLATE_DIR = SRC_DIR / 'templates'

def get_db_connection():
    return sqlite3.connect(DB_PATH)

def get_article_template():
    template_path = TEMPLATE_DIR / 'article.html'
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()

def render_template(template, data):
    """简单的模板渲染"""
    result = template
    for key, value in data.items():
        if isinstance(value, str):
            result = result.replace(f'{{{{{key}}}}}', value)
        else:
            # 处理条件块 {{#url}}...{{/url}}
            if value:
                result = re.sub(r'\{\{#' + key + r'\}\}.*?\{\{/' + key + r'\}', '', result)
            else:
                match = re.search(r'\{\{#' + key + r'\}\}.*?\{\{/' + key + r'\}', result, re.DOTALL)
                if match:
                    result = result[:match.start()] + result[match.end():]
    return result

def export_index_json(conn):
    """导出文章摘要索引（用于随机功能）"""
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, author FROM pages ORDER BY id')
    articles = [{'id': str(row[0]), 'title': row[1], 'author': row[2]} for row in cursor.fetchall()]
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(DATA_DIR / 'index.json', 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    return articles

def export_authors_json(conn):
    """导出作者列表"""
    cursor = conn.cursor()
    cursor.execute('SELECT author, COUNT(*) as count FROM pages GROUP BY author ORDER BY author')
    authors = [{'name': row[0], 'count': row[1]} for row in cursor.fetchall()]
    with open(DATA_DIR / 'authors.json', 'w', encoding='utf-8') as f:
        json.dump(authors, f, ensure_ascii=False, indent=2)
    return authors

def export_articles_by_author(conn, authors):
    """按作者导出文章详情"""
    cursor = conn.cursor()
    ARTICLE_DIR.mkdir(parents=True, exist_ok=True)
    for author_data in authors:
        author = author_data['name']
        cursor.execute('SELECT id, title, author, article, url FROM pages WHERE author = ?', (author,))
        articles = [{
            'id': str(row[0]),
            'title': row[1],
            'author': row[2],
            'article': row[3],
            'url': row[4]
        } for row in cursor.fetchall()]
        safe_author = author.replace('/', '_').replace('\\', '_')
        with open(DATA_DIR / 'articles' / f'{safe_author}.json', 'w', encoding='utf-8') as f:
            json.dump({'name': author, 'articles': articles}, f, ensure_ascii=False, indent=2)

def generate_article_pages(conn):
    """生成每篇文章的 HTML 页面"""
    template = get_article_template()
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, author, article, url FROM pages ORDER BY id')
    
    for row in cursor.fetchall():
        article_id, title, author, article, url = row
        # 转换文章正文（简单的段落分割）
        article_html = '\n'.join(f'<p>{p.strip()}</p>' for p in article.split('\n') if p.strip())
        
        data = {
            'title': title,
            'author': author,
            'article': article_html,
            'url': url or ''
        }
        
        html = render_template(template, data)
        article_path = ARTICLE_DIR / f'{article_id}.html'
        with open(article_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f'Generated: article/{article_id}.html')

def copy_static_files():
    """复制静态资源到 dist"""
    # CSS
    css_src = SRC_DIR / 'css' / 'style.css'
    css_dst = OUTPUT_DIR / 'css' / 'style.css'
    css_dst.parent.mkdir(parents=True, exist_ok=True)
    with open(css_src, 'r', encoding='utf-8') as f:
        content = f.read()
    # 修正 CSS 中的相对路径（因为 article 页面在子目录）
    content = content.replace(/var\(--panel-width\)/g, 'calc(var(--sidebar-width) + var(--panel-width))')
    with open(css_dst, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # JS
    for js_file in ['utils.js', 'bookshelf.js', 'app.js']:
        src = SRC_DIR / 'js' / js_file
        dst = OUTPUT_DIR / 'js' / js_file
        dst.parent.mkdir(parents=True, exist_ok=True)
        with open(src, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(dst, 'w', encoding='utf-8') as f:
            f.write(content)
    
    # HTML入口页
    for html_file in ['index.html', 'random.html']:
        src = SRC_DIR / html_file
        dst = OUTPUT_DIR / html_file
        with open(src, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(dst, 'w', encoding='utf-8') as f:
            f.write(content)
    
    # 404 页
    src_404 = SRC_DIR / '404.html'
    dst_404 = OUTPUT_DIR / '404.html'
    if src_404.exists():
        with open(src_404, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(dst_404, 'w', encoding='utf-8') as f:
            f.write(content)

def main():
    # 创建目录
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ARTICLE_DIR.mkdir(parents=True, exist_ok=True)
    
    conn = get_db_connection()
    
    print('正在导出 index.json...')
    articles = export_index_json(conn)
    print(f'已导出 {len(articles)} 篇文章摘要')
    
    print('正在导出 authors.json...')
    authors = export_authors_json(conn)
    print(f'已导出 {len(authors)} 位作者')
    
    print('正在按作者导出文章...')
    export_articles_by_author(conn, authors)
    
    print('正在生成文章详情页...')
    generate_article_pages(conn)
    
    print('正在复制静态资源...')
    copy_static_files()
    
    print('构建完成！')

if __name__ == '__main__':
    main()
```

- [ ] **步骤 1：更新 build.py，添加 HTML 生成逻辑**

- [ ] **步骤 2：运行构建脚本验证**

运行：`python meiriyiwen-reader/build.py`
预期：生成 `dist/` 下所有文件

- [ ] **步骤 3：检查生成的 article 页面**

运行：`ls meiriyiwen-reader/dist/article/ | head -10`
预期：显示 `1.html`, `2.html` 等文章页面

- [ ] **步骤 4：Commit**

```bash
git add meiriyiwen-reader/build.py
git commit -m "feat: 完善构建脚本，添加 HTML 生成功能"
```

---

## 任务 10：404 页面

**文件：**
- 创建：`meiriyiwen-reader/src/404.html`

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>404 - 阅读吧</title>
  <link rel="stylesheet" href="css/style.css">
</head>
<body>
  <header class="header">
    <a href="index.html" class="logo">阅读吧</a>
    <button class="theme-toggle" aria-label="切换暗黑模式"></button>
  </header>

  <div class="main-layout" style="justify-content: center; align-items: center;">
    <div class="welcome-view">
      <div class="welcome-icon">🔍</div>
      <h1 class="welcome-title">404 - 页面未找到</h1>
      <p class="welcome-desc">
        抱歉，找不到你要的文章<br>
        <a href="index.html" style="color: var(--accent);">返回书架</a>
     </p>
    </div>
  </div>

  <script src="js/utils.js"></script>
  <script src="js/app.js"></script>
</body>
</html>
```

- [ ] **步骤 1：创建 404.html**

- [ ] **步骤 2：Commit**

```bash
git add meiriyiwen-reader/src/404.html
git commit -m "feat: 添加 404 页面"
```

---

## 任务 11：最终验证

**验证清单：**

- [ ] **步骤1：运行完整构建**

运行：`python meiriyiwen-reader/build.py`
预期：成功生成所有文件，无报错

- [ ] **步骤 2：检查文件数量**

运行：`find meiriyiwen-reader/dist -type f | wc -l`（或 Windows 等效命令）
预期：约 1021 个 article/*.html + 3 个 JSON + 4 个 HTML + 3 个 JS + 1 个 CSS ≈ 1033 个文件

- [ ] **步骤 3：检查 index.html 能否正常加载**

验证 CSS 路径、JS 引用是否正确

- [ ] **步骤 4：Commit 所有剩余文件**

```bash
git add meiriyiwen-reader/
git commit -m "feat: 完成阅读吧阅读器开发"
```

---

## 规格覆盖度检查

| 规格需求 | 对应任务 |
|---------|---------|
| 随机阅读 |任务 7（random.html）+ 任务 9（build.py 生成） |
| 书架导航 | 任务 4（bookshelf.js）+ 任务 6（index.html） |
| 暗黑模式 | 任务 2（style.css）+ 任务 3（utils.js）+ 任务 5（app.js） |
| 多页面模式 | 任务 9（build.py 生成 article/*.html） |
| 按作者分片数据 | 任务 1（build.py）+ 任务 4（bookshelf.js 加载） |
| 404页面 | 任务 10（404.html） |

**遗漏项检查：** 无

---

计划已完成并保存到 `docs/superpowers/plans/2026-06-09-meiriyiwen-reader-plan.md`。

**两种执行方式：**

**1. 子代理驱动（推荐）** - 每个任务调度一个新的子代理，任务间进行审查，快速迭代

**2. 内联执行** - 在当前会话中使用 executing-plans 执行任务，批量执行并设有检查点

**选哪种方式？**