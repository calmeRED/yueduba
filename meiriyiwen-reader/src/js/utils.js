const Utils = {
  /**
   * 加载 JSON 数据
   * @param {string} url - JSON 文件路径
   * @returns {Promise<Object>}
   */
  async loadJSON(url) {
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Failed to load ${url}: ${response.status}`);
      }
      return response.json();
    } catch (error) {
      throw new Error(`Failed to load ${url}: ${error.message}`);
    }
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
   * 安全化作者名（用于文件路径）
   * @param {string} author
   * @returns {string}
   */
  sanitizeAuthor(author) {
    return author.replace(/[/\\:*?"<>|]/g, '_');
  }
};

// 导出给全局使用
window.Utils = Utils;