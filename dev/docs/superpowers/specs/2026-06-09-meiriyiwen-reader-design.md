# 每日一文阅读器 - 设计规格说明

## 1. 概述

### 项目背景
- 基于现有 `meiriyiwen.db` 数据（1021 篇文章）构建 GitHub Pages 阅读器
- 参考样式：`toTheEnd`（保留文章模块和书架模块，无需声音模块）
- 新增暗黑模式切换功能

### 核心功能
1. **随机阅读** — 点击随机选取一篇文章阅读
2. **书架导航** — 按作者分类浏览文章
3. **暗黑模式** — 明暗主题切换

---

## 2. 技术方案

### 技术栈
- **纯前端** HTML/CSS/JS，无构建框架
- **GitHub Pages** 原生托管

### 路由模式
- **多页面模式**：每篇文章生成独立 HTML 文件
- URL 结构：
  - `index.html` — 书架入口
  - `article/{id}.html` — 文章详情页
  - `random.html` — 随机跳转页
  - `404.html` — 404 页面

### 数据加载策略
- 构建时从 SQLite 导出静态 JSON 文件
- 前端按需加载，无需运行时数据库查询

---

## 3. 数据结构

### 构建产物（`/data` 目录）

```
data/
├── index.json # 全量文章摘要索引（用于随机功能）
├── authors.json # 作者列表（name + articleCount）
└── articles/
    ├── 汪曾祺.json   # 该作者所有文章内容
    ├── 朱自清.json
    └── ...
```

### `index.json` 结构
```json
[
  { "id": "1", "title": "故乡，是心上的那首诗", "author": "汪曾祺" },
  { "id": "2", "title": "荷塘月色", "author": "朱自清" }
]
```
- 用途：随机功能只需加载此文件（1021 条，体积小）
- 体积估算：~80KB

### `authors.json` 结构
```json
[
  { "name": "汪曾祺", "count": 12 },
  { "name": "朱自清", "count": 8 }
]
```
- 用途：书架入口页加载，显示作者列表
- 体积估算：< 5KB

### `articles/{author}.json` 结构
```json
{
  "name": "汪曾祺",
  "articles": [
    { "id": "1", "title": "故乡，是心上的那首诗", "article": "正文内容...", "url": "原文地址" },
    { "id": "5", "title": "葡萄月令", "article": "正文内容...", "url": "原文地址" }
  ]
}
```
- 用途：用户点击作者后加载该作者全部作品
- 加载时机：用户点进作者时才请求，按需加载

---

## 4. 页面设计

### 4.1 整体布局

```
┌────────────────────────────────────────────────────────────┐
│  Header: Logo + 暗黑模式切换按钮                              │
├──────────┬─────────────────┬──────────────────────────────┤
│  导航栏 │  作者/文章面板    │  主内容区                      │
│  200px   │  240px          │  自适应                        │
│          │                 │                              │
│  🎲 随机  │  作者列表        │  index: 书架说明 │
│  📚 书架  │  (点击展开文章)  │  article: 文章正文 │
│          │                 │                              │
└──────────┴─────────────────┴──────────────────────────────┘
```

### 4.2 导航栏（左侧200px）
- **随机入口**：点击跳转 `random.html`，随机展示一篇文章
- **书架入口**：点击显示/隐藏作者列表面板

### 4.3 作者/文章面板（中间 240px）
- 显示作者列表（从 `authors.json` 加载）
- 点击作者后，下方展开该作者文章列表
- 文章列表项显示标题

### 4.4 主内容区（右侧自适应）
- `index.html` 加载时显示欢迎/说明
- `article/{id}.html` 显示文章详情（标题 + 作者 + 正文）

### 4.5 暗黑模式
- Header 切换按钮
- 切换时修改 CSS 变量，影响全局颜色
- 状态持久化到 `localStorage`

---

## 5. 组件清单

### 5.1 Header
- Logo文字「每日一文」
- 暗黑模式切换按钮（☀️/🌙）
- 固定定位，高度 56px

### 5.2 NavSidebar
- 两个入口：「随机」「书架」
- 宽度 200px，固定定位
- 当前激活项高亮（左侧3px 边框 + 文字变色）

### 5.3 AuthorPanel
- 作者列表（从 `authors.json` 加载）
- 每个作者显示「姓名 + 数量」
- 点击作者展开文章列表（子级列表）
- 宽度 240px

### 5.4 ArticleView
- 返回按钮（点击回书架视图）
- 文章标题（h1）
- 文章作者
- 文章正文（`<p>` 分段）

### 5.5 RandomPage
- 加载 `index.json`
- 随机选取一篇
- 自动跳转至 `article/{id}.html`

---

## 6. 构建脚本

### 6.1 依赖
- Python 3 + `sqlite3`（标准库）+ `requests` + `beautifulsoup4`
- Node.js（可选，用于 SPA 框架）

### 6.2 构建流程
```
1. 读取 meiriyiwen.db
2. 生成 data/index.json（所有文章摘要）
3. 生成 data/authors.json（作者列表 + 计数）
4. 生成 data/articles/{author}.json（每个作者的文章详情）
5. 生成 HTML页面：
   - index.html（书架入口）
   - article/{id}.html（每篇文章详情，内容内嵌）
   - random.html（随机跳转页）
6. 输出到 /dist 目录
```

### 6.3 构建命令
```bash
python build.py
```

---

## 7. 文件结构

```
meiriyiwen-reader/
├── build.py              # 构建脚本
├── src/
│   ├── index.html        # 书架入口
│   ├── random.html       # 随机跳转页
│   ├── css/
│   │   └── style.css     # 样式（含暗黑模式变量）
│   ├── js/
│   │   ├── app.js        # 主逻辑
│   │   ├── bookshelf.js  # 书架逻辑
│   │   └── random.js     # 随机逻辑
│   └── templates/
│       └── article.html  # 文章详情模板
├── data/
│   ├── index.json
│   ├── authors.json
│   └── articles/
│       └── *.json
└── dist/ # 构建输出（部署到 GitHub Pages）
    ├── index.html
    ├── random.html
    ├── article/
    │   └── *.html
    └── data/
        └── *.json
```

---

## 8. 视觉风格

### 8.1 配色方案

**亮色模式：**
| 变量 | 值 | 用途 |
|------|-----|------|
| `--bg-primary` | `#fafafa` | 页面背景 |
| `--bg-secondary` | `#ffffff` | 侧边栏背景 |
| `--text-primary` | `#1a1a1a` | 主文字 |
| `--text-secondary` | `#666666` | 次要文字 |
| `--accent` | `#4a90d9` | 强调色/高亮 |
| `--border` | `#e5e5e5` | 边框 |

**暗色模式：**
| 变量 | 值 |
|------|-----|
| `--bg-primary` | `#1a1a1a` |
| `--bg-secondary` | `#2d2d2d` |
| `--text-primary` | `#e8e8e8` |
| `--text-secondary` | `#a0a0a0` |
| `--accent` | `#6ba3e8` |
| `--border` | `#404040` |

### 8.2 字体
- 系统字体栈：`-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif`

### 8.3 间距
- 基础间距单位：8px
- 侧边栏宽度：200px + 240px
- 主内容区内边距：40px 60px（桌面）/ 24px 20px（移动）

---

## 9. 待确认事项

- [ ] 数据库中每篇文章是否有分类/标签信息？如有，书架是否需要支持分类筛选？
- [ ] 是否需要搜索功能？
- [ ] 移动端布局是否需要特别处理？
- [ ] 是否需要「上一篇/下一篇」导航？

---

## 10. 构建产物示例

### `index.html` 加载流程
1. 加载 `data/authors.json` → 显示作者列表
2. 用户点作者 → 加载 `data/articles/{author}.json` → 显示文章列表
3. 用户点文章 → 跳转 `article/{id}.html`

### `random.html` 流程
1. 加载 `data/index.json`
2. 随机选取一篇
3. `window.location.href = 'article/' + id + '.html'`

### `article/{id}.html`
- 内容已内嵌，直接显示
- 包含导航栏和暗黑模式脚本