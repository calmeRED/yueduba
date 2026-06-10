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