# 移动端响应式改版 实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 实现抽屉式导航，移动端通过汉堡菜单按钮触发侧边抽屉，解决文章内容过窄问题。

**架构：** 移动端（≤768px）隐藏固定侧栏，通过 Header 汉堡按钮触发左侧抽屉面板（包含导航+作者列表）；桌面端（>768px）保持原有 3 列布局。

**技术栈：** 纯 HTML/CSS/JS，无框架依赖。

---

## 文件结构

| 文件 | 职责 |
|------|------|
| `css/style.css` | 新增 drawer/hamburger 样式，修噕移动端响应式 |
| `js/drawer.js` | 新建，抽屉逻辑（open/close/toggle/事件绑定） |
| `index.html` | 引入 drawer.js，Header 添加汉堡按钮 |
| `random.html` | 引入 drawer.js，Header 添加汉堡按钮 |
| `article/*.html` | 引入 drawer.js，Header 添加汉堡按钮（共 1201 个文件） |

---

## 任务列表

### 任务 1：CSS 新增抽屉样式

**文件：**
- 修改：`css/style.css`（末尾添加新样式）

- [ ] **步骤 1：添加 CSS 变量和抽屉基础样式**

在 `css/style.css` 末尾添加：

```css
/* ========================================
   抽屉组件（移动端）
   ======================================== */
.drawer-overlay {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1001;
}

.drawer {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  width: 280px;
  max-width: 80vw;
  background-color: var(--bg-secondary);
  z-index: 1002;
  transform: translateX(-100%);
  transition: transform 0.3s ease;
  overflow-y: auto;
  padding: 16px 0;
}

.drawer.open {
  transform: translateX(0);
}

.drawer-close {
  display: block;
  padding: 12px 20px;
  color: var(--text-secondary);
  text-align: right;
  cursor: pointer;
  font-size: 20px;
}

.drawer-nav {
  border-bottom: 1px solid var(--border);
  padding-bottom: 8px;
  margin-bottom: 8px;
}

.drawer-nav-item {
  display: block;
  padding: 12px 20px;
  color: var(--text-secondary);
  text-decoration: none;
  transition: all 0.2s ease;
}

.drawer-nav-item:hover,
.drawer-nav-item.active {
  color: var(--accent);
  background-color: var(--bg-primary);
}

/* ========================================
   汉堡按钮
   ======================================== */
.hamburger-btn {
  display: none;
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  padding: 8px;
  color: var(--text-primary);
}

@media (max-width: 768px) {
  .hamburger-btn {
    display: block;
  }
}
```

- [ ] **步骤 2：修噕移动端响应式（隐藏固定侧栏）**

找到现有 `@media (max-width: 768px)` 块，将 `.nav-sidebar` 和 `.author-panel` 的 `position: relative` 改为 `display: none`：

```css
@media (max-width: 768px) {
  .nav-sidebar {
    display: none;  /* 由抽屉替代 */
  }

  .author-panel {
    display: none;  /* 由抽屉替代 */
  }

  .content-area {
    margin-left: 0;
    padding: 16px;
  }

  .article-title {
    font-size: 22px;
  }

  .article-body {
    font-size: 16px;
  }
}
```

- [ ] **步骤 3：验证 CSS 语法**

运行：无（纯 CSS 文件，人工检查）

- [ ] **步骤 4：Commit**

```bash
git add css/style.css
git commit -m "feat: add drawer and hamburger button styles"
```

---

### 任务 2：新建 drawer.js

**文件：**
- 创建：`js/drawer.js`

- [ ] **步骤 1：编写 drawer.js**

创建 `js/drawer.js`：

```javascript
const Drawer = {
  isOpen: false,

  /**
   * 打开抽屉
   */
  open() {
    this.isOpen = true;
    document.querySelector('.drawer-overlay').style.display = 'block';
    document.querySelector('.drawer').classList.add('open');
    document.body.style.overflow = 'hidden'; // 防止背景滚动
  },

  /**
   * 关闭抽屉
   */
  close() {
    this.isOpen = false;
    document.querySelector('.drawer-overlay').style.display = 'none';
    document.querySelector('.drawer').classList.remove('open');
    document.body.style.overflow = '';
  },

  /**
   * 切换抽屉状态
   */
  toggle() {
    if (this.isOpen) {
      this.close();
    } else {
      this.open();
    }
  },

  /**
   * 初始化抽屉事件绑定
   */
  init() {
    // 汉堡按钮点击
    const hamburgerBtn = document.querySelector('.hamburger-btn');
    if (hamburgerBtn) {
      hamburgerBtn.addEventListener('click', () => this.toggle());
    }

    // 遮罩点击关闭
    const overlay = document.querySelector('.drawer-overlay');
    if (overlay) {
      overlay.addEventListener('click', () => this.close());
    }

    // 关闭按钮点击
    const closeBtn = document.querySelector('.drawer-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => this.close());
    }

    // 导航项点击后自动关闭
    document.querySelectorAll('.drawer-nav-item, .drawer-author-item').forEach(item => {
      item.addEventListener('click', () => {
        // 延迟关闭，等待跳转
        setTimeout(() => this.close(), 100);
      });
    });

    // 作者项点击（展开文章列表）
    document.querySelectorAll('.drawer-author-item').forEach(item => {
      item.addEventListener('click', () => {
        const authorKey = item.dataset.author;
        // 复用 Bookshelf 的展开逻辑（如果可用）
        if (typeof Bookshelf !== 'undefined' && Bookshelf.selectAuthor) {
          Bookshelf.selectAuthor(authorKey);
        }
      });
    });

    // 窗口 resize > 768px 时关闭抽屉
    window.addEventListener('resize', () => {
      if (window.innerWidth > 768) {
        this.close();
      }
    });
  }
};

//导出给全局使用
window.Drawer = Drawer;
```

- [ ] **步骤 2：验证文件创建**

运行：`ls -la js/drawer.js`

- [ ] **步骤 3：Commit**

```bash
git add js/drawer.js
git commit -m "feat: add drawer navigation component"
```

---

### 任务 3：更新 index.html

**文件：**
- 修改：`index.html`

- [ ] **步骤 1：添加汉堡按钮到 Header**

在 Header 的 logo 前面添加汉堡按钮：

```html
<header class="header">
  <button class="hamburger-btn" aria-label="打开菜单">☰</button>
  <a href="index.html" class="logo">每日一文</a>
  <button class="theme-toggle" aria-label="切换暗黑模式"></button>
</header>
```

- [ ] **步骤 2：在 NavSidebar 下方添加抽屉组件**

在 `</div><!-- .main-layout -->` 之前添加：

```html
<!-- 抽屉组件（移动端） -->
<div class="drawer-overlay"></div>
<div class="drawer">
  <div class="drawer-close">✕</div>
  <div class="drawer-nav">
    <a href="random.html" class="drawer-nav-item">
      <span class="icon">🎲</span> 随机
    </a>
    <a href="index.html" class="drawer-nav-item">
      <span class="icon">📚</span> 书架
    </a>
  </div>
  <div class="drawer-authors" id="drawer-authors">
    <!-- 作者列表由 JS 动态填充 -->
  </div>
</div>
```

- [ ] **步骤 3：引入 drawer.js 并初始化**

在 `</body>` 前添加：

```html
<script src="js/utils.js"></script>
<script src="js/bookshelf.js"></script>
<script src="js/drawer.js"></script>
<script src="js/app.js"></script>
<script>
  Bookshelf.init();
  Drawer.init();
</script>
```

- [ ] **步骤 4：在 drawer.js 中添加作者列表填充逻辑**

更新 `js/drawer.js`，在 `init()` 中添加：

```javascript
// 填充作者列表到抽屉
async function initDrawerAuthors() {
  const container = document.getElementById('drawer-authors');
  if (!container) return;

  try {
    const authors = await Utils.loadJSON('data/authors.json');
    container.innerHTML = authors.map(author => `
      <div class="drawer-author-item" data-author="${Utils.sanitizeAuthor(author.name)}">
        <span class="author-name">${Utils.escapeHtml(author.name)}</span>
        <span class="author-count">(${author.count})</span>
      </div>
    `).join('');

    // 绑定作者点击事件
    container.querySelectorAll('.drawer-author-item').forEach(item => {
      item.addEventListener('click', () => {
        const authorKey = item.dataset.author;
        if (typeof Bookshelf !== 'undefined') {
          Bookshelf.selectAuthor(authorKey);
        }
      });
    });
  } catch (error) {
    console.error('Failed to load authors for drawer:', error);
  }
}
```

并在 `Drawer.init()` 末尾调用 `initDrawerAuthors()`。

- [ ] **步骤 5：Commit**

```bash
git add index.html js/drawer.js
git commit -m "feat: add drawer to index.html"
```

---

### 任务 4：更新 random.html

**文件：**
- 修改：`random.html`

- [ ] **步骤 1：添加汉堡按钮到 Header**

```html
<header class="header">
  <button class="hamburger-btn" aria-label="打开菜单">☰</button>
  <a href="index.html" class="logo">每日一文</a>
  <button class="theme-toggle" aria-label="切换暗黑模式"></button>
</header>
```

- [ ] **步骤 2：添加抽屉组件（仅导航，无作者列表）**

在 `</div><!-- .main-layout -->` 之前添加：

```html
<!-- 抽屉组件（移动端） -->
<div class="drawer-overlay"></div>
<div class="drawer">
  <div class="drawer-close">✕</div>
  <div class="drawer-nav">
    <a href="random.html" class="drawer-nav-item">
      <span class="icon">🎲</span> 随机
    </a>
    <a href="index.html" class="drawer-nav-item">
      <span class="icon">📚</span> 书架
    </a>
  </div>
</div>
```

- [ ] **步骤 3：引入 drawer.js 并初始化**

将 `random.html` 中的脚本改为：

```html
<script src="js/utils.js"></script>
<script src="js/drawer.js"></script>
<script src="js/app.js"></script>
<script>
  Drawer.init();
  (async function() {
    try {
      const articles = await Utils.loadJSON('data/index.json');
      const randomIndex = Math.floor(Math.random() * articles.length);
      const article = articles[randomIndex];
      window.location.href = 'article/' + article.id + '.html';
    } catch (error) {
      console.error('Failed to load articles:', error);
      document.querySelector('.loading').textContent = '加载失败，请刷新重试';
    }
  })();
</script>
```

- [ ] **步骤 4：Commit**

```bash
git add random.html
git commit -m "feat: add drawer to random.html"
```

---

### 任务 5：批量更新 article/*.html

**文件：**
- 修改：`article/*.html`（1201 个文件）

- [ ] **步骤 1：分析 article 模板结构**

运行：`head -30 article/1.html`

- [ ] **步骤 2：编写批量替换脚本**

使用 sed批量处理：

```bash
# 添加汉堡按钮到 Header（紧跟在<header class="header"> 后）
sed -i 's/<header class="header">/<header class="header">\n  <button class="hamburger-btn" aria-label="打开菜单">☰<\/button>/g' article/*.html

# 添加 drawer 组件（在</div> 关闭 main-layout 前）
sed -i 's/<\/div>\n<\/body>/<!-- 抽屉组件（移动端） -->\n<div class="drawer-overlay"><\/div>\n<div class="drawer">\n  <div class="drawer-close">✕<\/div>\n  <div class="drawer-nav">\n    <a href="..\/random.html" class="drawer-nav-item"><span class="icon">🎲<\/span> 随机<\/a>\n    <a href="..\/index.html" class="drawer-nav-item"><span class="icon">📚<\/span> 书架<\/a>\n  <\/div>\n<\/div>\n<\/div>\n<\/body>/g' article/*.html
```

注意：article 页面不需要作者列表，抽屉仅包含导航。

- [ ] **步骤 3：引入 drawer.js**

在 `</body>` 前添加脚本引用：

```bash
# 在最后一个</script> 后添加 drawer.js
sed -i 's|</script>|</script>\n<script src="..\/js\/drawer.js"><\/script>\n<script>Drawer.init();<\/script>|g' article/*.html
```

- [ ] **步骤 4：验证修改**

运行：`grep -c "hamburger-btn" article/1.html`（应为 1）
运行：`grep -c "drawer-overlay" article/1.html`（应为 1）

- [ ] **步骤 5：Commit**

```bash
git add article/
git commit -m "feat: add drawer navigation to all article pages"
```

---

## 自检清单

- [ ] 规格第 2 节（移动端行为）：抽屉触发/关闭/内容 →任务 1-5覆盖
- [ ] 规格第 3 节（响应式断点 768px）→ 任务 1 CSS @media 覆盖
- [ ] 规格第 4 节（组件变化）→ 任务 1-5 覆盖所有组件
- [ ] 规格第 5 节（CSS 变更）→ 任务 1覆盖
- [ ] 规格第 6 节（JS 变更）→ 任务 2-3 覆盖
- [ ] 规格第 7 节（文件变更）→ 任务 1-5 覆盖所有文件
- [ ] 无占位符（无 TODO/待定/后续实现）
- [ ] 类型一致性：Drawer.open/close/toggle/init 在任务 3 中正确调用