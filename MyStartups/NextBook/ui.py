import logging
import tkinter as tk
from tkinter import ttk, messagebox, font

"""
NextBook Agent UI模块
提供用户界面的创建和管理功能
"""

class NextBookUI:
    def __init__(self, app_core, config):
        self.app_core = app_core
        self.config = config
        self.logger = logging.getLogger("nextbook")
        
        # 初始化Tkinter
        self.root = tk.Tk()
        self.root.title("NextBook - 智能阅读助手")
        self.root.geometry("800x600")
        
        # 设置应用图标（如果有）
        # self.root.iconbitmap("path/to/icon.ico")
        
        # 设置应用关闭事件处理
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # 设置默认字体和颜色
        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(size=12)
        self.root.option_add("*Font", self.default_font)
        
        # 设置主题颜色
        self.bg_color = "#f5f5f5"  # 浅灰色背景
        self.accent_color = "#4caf50"  # 绿色强调色
        self.root.configure(bg=self.bg_color)
        
        print("UI初始化完成")
    
    def run(self):
        """启动UI并阻塞直到UI关闭"""
        print("UI正在运行...")
        
        try:
            self.show_main_window()
            self.start_event_loop()
        except Exception as e:
            self.logger.error(f"UI运行错误: {str(e)}")
            raise
    
    def show_main_window(self):
        """显示主窗口"""
        print("正在构建主窗口...")
        
        # 创建主框架，添加边框以便于调试
        main_frame = ttk.Frame(self.root, padding=10, relief="ridge", borderwidth=1)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建菜单栏
        self._create_menu()
        print("菜单已创建")
        
        # 创建工具栏
        self._create_toolbar(main_frame)
        print("工具栏已创建")
        
        # 创建主内容区域
        self._create_main_content(main_frame)
        print("主内容区已创建")
        
        # 创建状态栏
        self._create_status_bar()
        print("状态栏已创建")
        
        self.logger.info("显示主窗口")
        print("主窗口已显示")
    
    def _create_menu(self):
        """创建菜单栏"""
        menu_bar = tk.Menu(self.root)
        
        # 文件菜单
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="打开文件", command=self.open_file)
        file_menu.add_command(label="导入书籍", command=self.import_book)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.on_close)
        menu_bar.add_cascade(label="文件", menu=file_menu)
        
        # 编辑菜单
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="设置", command=self.show_settings)
        menu_bar.add_cascade(label="编辑", menu=edit_menu)
        
        # 帮助菜单
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="使用帮助", command=self.show_help)
        help_menu.add_command(label="关于", command=self.show_about)
        menu_bar.add_cascade(label="帮助", menu=help_menu)
        
        self.root.config(menu=menu_bar)
    
    def _create_toolbar(self, parent):
        """创建工具栏"""
        toolbar = ttk.Frame(parent, relief="raised", borderwidth=1)
        toolbar.pack(fill=tk.X, pady=5)
        
        # 添加工具栏按钮
        ttk.Button(toolbar, text="打开", command=self.open_file).pack(side=tk.LEFT, padx=5, pady=3)
        ttk.Button(toolbar, text="导入", command=self.import_book).pack(side=tk.LEFT, padx=5, pady=3)
        ttk.Button(toolbar, text="设置", command=self.show_settings).pack(side=tk.LEFT, padx=5, pady=3)
        
        # 添加一个明显的分隔线
        ttk.Separator(toolbar, orient="vertical").pack(side=tk.LEFT, fill="y", padx=5, pady=3)
    
    def _create_main_content(self, parent):
        """创建主内容区域"""
        # 创建一个PanedWindow来分隔左右面板
        paned = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 创建左侧书架面板
        left_panel = ttk.Frame(paned, relief="sunken", borderwidth=1, width=200)
        paned.add(left_panel, weight=1)
        
        # 书架标题 - 使用大字体和颜色
        title_frame = ttk.Frame(left_panel)
        title_frame.pack(fill=tk.X, pady=5)
        title_label = ttk.Label(title_frame, text="我的书架", font=("Arial", 14, "bold"))
        title_label.pack(anchor=tk.W, padx=5)
        
        # 书籍列表，添加滚动条
        list_frame = ttk.Frame(left_panel)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.book_list = tk.Listbox(list_frame, width=25, height=20, 
                                   bg="white", fg="black",
                                   selectbackground=self.accent_color,
                                   font=("Arial", 12),
                                   yscrollcommand=scrollbar.set)
        self.book_list.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.book_list.yview)
        
        # 添加示例书籍
        for i in range(1, 15):  # 增加更多示例以显示滚动效果
            self.book_list.insert(tk.END, f"示例书籍 {i}")
        
        # 绑定选择事件
        self.book_list.bind('<<ListboxSelect>>', self.on_book_select)
        
        # 创建右侧内容区域
        right_panel = ttk.Frame(paned, relief="sunken", borderwidth=1)
        paned.add(right_panel, weight=3)  # 右侧面板占更多空间
        
        # 内容区标题
        content_title = ttk.Label(right_panel, text="内容预览", font=("Arial", 14, "bold"))
        content_title.pack(anchor=tk.W, padx=5, pady=5)
        
        # 文本显示区，添加滚动条
        text_frame = ttk.Frame(right_panel)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        text_scroll = ttk.Scrollbar(text_frame)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.content_text = tk.Text(text_frame, wrap=tk.WORD, 
                                   bg="white", fg="black",
                                   font=("Arial", 12),
                                   padx=10, pady=10,
                                   yscrollcommand=text_scroll.set)
        self.content_text.pack(fill=tk.BOTH, expand=True)
        text_scroll.config(command=self.content_text.yview)
        
        welcome_message = """欢迎使用NextBook智能阅读助手!

这是一个AI驱动的阅读辅助工具，帮助您更高效地阅读和理解内容。

使用方法:
1. 从左侧书架选择一本书籍
2. 或使用顶部菜单导入新书籍
3. 使用智能工具分析和理解文本内容

祝您阅读愉快！
"""
        self.content_text.insert(tk.END, welcome_message)
    
    def _create_status_bar(self):
        """创建状态栏"""
        status_bar = ttk.Frame(self.root, relief="sunken", borderwidth=1)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(status_bar, text="就绪", anchor=tk.W, padding=(5, 2))
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 添加版本标签
        version_label = ttk.Label(status_bar, text="v0.1.0", padding=(5, 2))
        version_label.pack(side=tk.RIGHT)
    
    def start_event_loop(self):
        """启动事件循环"""
        print("启动事件循环...")
        self.root.update()  # 强制立即更新界面
        self.root.mainloop()
        self.logger.info("用户关闭了UI")
    
    def on_close(self):
        """处理窗口关闭事件"""
        if messagebox.askokcancel("退出", "确定要退出NextBook吗?"):
            self.root.destroy()
    
    # UI事件处理函数
    def open_file(self):
        self.status_label.config(text="打开文件...")
        messagebox.showinfo("功能提示", "打开文件功能尚未实现")
    
    def import_book(self):
        self.status_label.config(text="导入书籍...")
        messagebox.showinfo("功能提示", "导入书籍功能尚未实现")
    
    def show_settings(self):
        self.status_label.config(text="打开设置...")
        messagebox.showinfo("功能提示", "设置功能尚未实现")
    
    def show_help(self):
        messagebox.showinfo("帮助", "NextBook智能阅读助手\n版本: 0.1.0\n\n这是一个基于AI的阅读助手应用，帮助您更高效地阅读和理解内容。")
    
    def show_about(self):
        messagebox.showinfo("关于", "NextBook智能阅读助手\n版本: 0.1.0\n\n© 2025 NextBook团队")
    
    def on_book_select(self, event):
        """处理书籍选择事件"""
        if self.book_list.curselection():
            selected = self.book_list.get(self.book_list.curselection())
            self.status_label.config(text=f"已选择: {selected}")
            self.content_text.delete(1.0, tk.END)
            self.content_text.insert(tk.END, f"您选择了: {selected}\n\n这里将显示书籍内容...")

def create_ui(app_core, config):
    """创建并返回UI实例"""
    return NextBookUI(app_core, config)
