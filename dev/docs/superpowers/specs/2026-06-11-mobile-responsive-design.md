# 阅读吧阅读器 - 移动端响应式改版设计

## 1. 概述

###目标
解决移动端阅读体验问题：左侧固定侧栏（导航+作者面板）占用过多空间，导致文章内容过窄（一行仅2-3 字）。

### 方案
采用抽屉式导航：移动端默认隐藏侧栏，通过 Header 汉堡菜单按钮触发左侧抽屉面板。

---

## 2. 移动端行为

### 导航触发
- Header左侧新增汉堡菜单按钮 (☰)
- 点击按钮触发左侧抽屉滑出

### 抽屉内容
- 遮罩层（半透明黑色背景，点击关闭）
- 抽屉面板包含：
  - 关闭按钮 (✕)
  - 导航项：随机、书架
  - 作者列表（可展开文章）

### 抽屉关闭
- 点击遮罩区域
- 点击抽屉内关闭按钮
- 点击导航项跳转后自动关闭

---

## 3. 响应式断点

| 断点 | 布局 |
|------|------|
| ≤ 768px | 移动端：隐藏侧栏，汉堡按钮触发抽屉 |
| > 768px | 桌面端：保持3 列固定布局 |

---

## 4. 组件变化

### 4.1 Header
- 桌面端：Logo + 主题切换按钮
- 移动端：☰ 汉堡按钮 + Logo + 主题切换按钮

### 4.2 NavSidebar
- 桌面端：固定显示，200px 宽度
- 移动端：默认 `display: none`，由抽屉替代

### 4.3 AuthorPanel
- 桌面端：固定显示，240px 宽度
- 移动端：默认 `display: none`，并入抽屉面板

### 4.4 Drawer（新组件）
- **遮罩层**：`position: fixed`，覆盖全屏，`background: rgba(0,0,0,0.5)`
- **抽屉面板**：`position: fixed`，左侧固定，宽度 280px，高度 100%
- **动画**：从左侧滑入，`transform: translateX(-100%)` → `translateX(0)`
- **关闭按钮**：抽屉右上角
- **内容**：复用人均 NavSidebar + AuthorPanel 结构

---

## 5. CSS 变更

### 新增类
```css
/* 抽屉 */
.drawer-overlay { display: none; position: fixed; ... }
.drawer { position: fixed; left: 0; top: 0; bottom: 0; width: 280px; ... }
.drawer.open { transform: translateX(0); }

/* 汉堡按钮 */
.hamburger-btn { display: none; ... }
@media (max-width: 768px) {
  .hamburger-btn { display: block; }
}
```

### 修噕 NavSidebar / AuthorPanel
```css
@media (max-width: 768px) {
  .nav-sidebar, .author-panel { display: none; }
}
```

---

## 6. JavaScript 变更

### 新增 drawer.js
```javascript
const Drawer = {
  isOpen: false,

  open() { /* 显示遮罩 + 滑出抽屉 */ },
  close() { /* 隐藏遮罩 + 滑回抽屉 */ },
  toggle() { /*切换状态 */ }
};
```

### 绑定事件
- 汉堡按钮点击 → `Drawer.toggle()`
- 遮罩点击 → `Drawer.close()`
- 导航项点击 → 跳转 + `Drawer.close()`
- 页面 resize > 768px → `Drawer.close()`

---

## 7. 文件变更

| 文件 | 变更 |
|------|------|
| `css/style.css` | 新增 drawer/hamburger 样式，修噕响应式 |
| `js/drawer.js` | 新建，抽屉逻辑 |
| `index.html` | 引入 drawer.js，添加汉堡按钮 |
| `article/*.html` | 引入 drawer.js，添加汉堡按钮 |
| `random.html` | 引入 drawer.js，添加汉堡按钮 |

---

## 8. 实现步骤

1. CSS：新增 drawer/hamburger 样式
2. JS：新建 drawer.js 实现抽屉逻辑
3. HTML：在各页面 Header 添加汉堡按钮，引入 drawer.js
4. 测试：桌面端/移动端切换验证

---

## 9. 视觉示意

### 移动端默认状态
```
┌─────────────────────────┐
│ ☰  阅读吧      🌙   │  ← Header
├─────────────────────────┤
│                         │
│    文章内容全宽显示     │
│    一行正常字数 │
│                         │
│                         │
└─────────────────────────┘
```

### 移动端抽屉展开状态
```
┌─────────────────────────┐
│ ☰  阅读吧       🌙   │
├─────────────────────────┤
│ ┌──────────┐           │
│ │  ✕       │ 遮罩      │
│ │──────────│           │
│ │ 🎲 随机  │           │
│ │ 📚 书架  │           │
│ │──────────│           │
│ │ 作者列表 │抽屉      │
│ │ ... │ 280px     │
│ └──────────┘           │
└─────────────────────────┘
```