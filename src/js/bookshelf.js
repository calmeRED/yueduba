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
        <span class="author-name">${Utils.escapeHtml(author.name)}</span>
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
   * 渲染文章列表
   * @param {string} authorKey
   * @param {Array} articles
   */
  renderArticleList(authorKey, articles) {
    const container = document.getElementById('author-list');
    const authorItem = container.querySelector(`[data-author="${authorKey}"]`);
    const listHtml = `
      <div class="article-list" id="article-list-${authorKey}">
        ${articles.map(article => `
          <div class="article-list-item" data-id="${Utils.escapeHtml(article.id)}">
            ${Utils.escapeHtml(article.title)}
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
  }
};

// 导出给全局使用
window.Bookshelf = Bookshelf;