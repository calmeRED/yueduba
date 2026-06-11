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
    document.querySelectorAll('.drawer-nav-item').forEach(item => {
      item.addEventListener('click', () => {
        // 延迟关闭，等待跳转
        setTimeout(() => this.close(), 100);
      });
    });

    // 窗口 resize > 768px 时关闭抽屉
    window.addEventListener('resize', () => {
      if (window.innerWidth > 768) {
        this.close();
      }
    });

    // 初始化抽屉内的作者列表
    this.initAuthors();
  },

  /**
   * 初始化抽屉内的作者列表
   */
  async initAuthors() {
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
          // 复用 Bookshelf 的展开逻辑（如果可用）
          if (typeof Bookshelf !== 'undefined' && Bookshelf.selectAuthor) {
            Bookshelf.selectAuthor(authorKey);
          }
          // 延迟关闭，等待跳转
          setTimeout(() => this.close(), 100);
        });
      });
    } catch (error) {
      console.error('Failed to load authors for drawer:', error);
    }
  }
};

// 导出给全局使用
window.Drawer = Drawer;