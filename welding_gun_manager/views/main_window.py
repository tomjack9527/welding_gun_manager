# welding_gun_manager/views/main_window.py（完整更新版）
import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from controllers.gun_controller import GunController
from controllers.preset_controller import PresetController
from controllers.file_controller import FileController
from controllers.user_controller import UserController
from services.file_service import FileService
from services.preset_service import PresetService
from models.database import Database
from models.entities import WeldingGun
from views.login_dialog import LoginDialog


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("焊接枪管理系统")
        self.root.geometry("1200x700")
        
        # 初始化数据库
        self.db = Database()
        
        # 初始化服务层
        self.file_service = FileService()
        self.preset_service = PresetService()
        
        # 初始化控制器
        self.gun_controller = GunController(self.db)
        self.preset_controller = PresetController(self.db)
        self.file_controller = FileController(self.file_service)
        self.user_controller = UserController(self.db)
        
        # 用户登录
        if not self.user_login():
            self.root.destroy()
            return
        
        # UI设置
        self.setup_ui()
        
        # 加载初始数据
        self.load_initial_data()
        
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def user_login(self):
        """用户登录"""
        # 显示登录对话框
        login_dialog = LoginDialog(self.root)
        
        if not login_dialog.result:
            return False
        
        username = login_dialog.result['username']
        password = login_dialog.result['password']
        
        # 验证用户
        user = self.user_controller.login(username, password)
        if not user:
            messagebox.showerror("登录失败", "用户名或密码错误")
            return False
        
        return True
    
    def setup_ui(self):
        """设置用户界面"""
        # 创建菜单栏
        self.setup_menu()
        
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 左侧导航栏
        self.setup_sidebar(main_frame)
        
        # 右侧内容区域
        self.setup_content_area(main_frame)
        
        # 状态栏
        self.setup_statusbar()
        
        # 根据权限更新界面状态
        self.update_ui_by_permission()
    
    def update_ui_by_permission(self):
        """根据权限更新界面状态"""
        is_admin = self.user_controller.is_admin()
        
        # 更新菜单项状态
        menubar = self.root.children['!menu']
        edit_menu = menubar.children['edit']
        
        # 根据权限启用/禁用编辑功能
        for item in ['添加工枪', '编辑工枪', '删除工枪']:
            index = edit_menu.index(item)
            if index >= 0:
                edit_menu.entryconfig(index, state='normal' if is_admin else 'disabled')
        
        # 更新按钮状态
        for child in self.gun_frame.winfo_children():
            if isinstance(child, ttk.Frame):
                for btn in child.winfo_children():
                    if isinstance(btn, ttk.Button):
                        if btn['text'] in ['添加', '编辑', '删除']:
                            btn.config(state='normal' if is_admin else 'disabled')
    
    def setup_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="导入数据", command=self.import_data)
        file_menu.add_command(label="导出数据", command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label="切换用户", command=self.switch_user)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.on_closing)
        
        # 编辑菜单
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="编辑", menu=edit_menu)
        edit_menu.add_command(label="添加工枪", command=self.add_gun)
        edit_menu.add_command(label="编辑工枪", command=self.edit_gun)
        edit_menu.add_command(label="删除工枪", command=self.delete_gun)
        
        # 用户菜单（仅管理员可见）
        if self.user_controller.is_admin():
            user_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="用户管理", menu=user_menu)
            user_menu.add_command(label="用户列表", command=self.show_users)
            user_menu.add_command(label="添加用户", command=self.add_user)
        
        # 视图菜单
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="视图", menu=view_menu)
        view_menu.add_command(label="刷新", command=self.refresh_data)
        view_menu.add_command(label="显示所有", command=self.show_all)
        view_menu.add_command(label="显示活跃", command=self.show_active)
        
        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="同步数据", command=self.sync_data)
        tools_menu.add_command(label="备份数据库", command=self.backup_database)
        tools_menu.add_command(label="恢复数据库", command=self.restore_database)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)
        help_menu.add_command(label="使用手册", command=self.show_manual)
    
    def setup_sidebar(self, parent):
        """创建左侧导航栏"""
        sidebar = ttk.Frame(parent, width=200, relief=tk.RAISED, borderwidth=1)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        # 用户信息
        user_frame = ttk.Frame(sidebar)
        user_frame.pack(fill=tk.X, padx=5, pady=10)
        
        current_user = self.user_controller.get_current_user()
        role_text = "管理员" if current_user.is_admin() else "普通用户"
        
        ttk.Label(user_frame, text=f"用户: {current_user.username}", 
                 font=("Arial", 10, "bold")).pack(anchor=tk.W)
        ttk.Label(user_frame, text=f"角色: {role_text}", 
                 font=("Arial", 9)).pack(anchor=tk.W)
        
        # 切换用户按钮
        ttk.Button(user_frame, text="切换用户", 
                  command=self.switch_user).pack(pady=5, fill=tk.X)
        
        # 导航按钮
        nav_buttons = [
            ("工枪管理", self.show_gun_management),
            ("预设管理", self.show_preset_management),
            ("文件管理", self.show_file_management),
        ]
        
        # 仅管理员可见的菜单项
        if self.user_controller.is_admin():
            nav_buttons.append(("统计报表", self.show_statistics))
            nav_buttons.append(("系统设置", self.show_settings))
        
        for text, command in nav_buttons:
            btn = ttk.Button(sidebar, text=text, command=command, width=20)
            btn.pack(pady=2, padx=5, fill=tk.X)
    
    def setup_content_area(self, parent):
        """创建右侧内容区域"""
        # 创建笔记本（标签页）
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 工枪管理标签页
        self.gun_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.gun_frame, text="工枪管理")
        self.setup_gun_tab()
        
        # 预设管理标签页
        self.preset_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.preset_frame, text="预设管理")
        self.setup_preset_tab()
        
        # 文件管理标签页
        self.file_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.file_frame, text="文件管理")
        self.setup_file_tab()
        
        # 默认显示第一个标签页
        self.notebook.select(0)
    
    def setup_gun_tab(self):
        """设置工枪管理标签页"""
        # 搜索框
        search_frame = ttk.Frame(self.gun_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_frame, text="搜索:").pack(side=tk.LEFT, padx=5)
        self.gun_search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.gun_search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind('<Return>', lambda e: self.search_guns())
        
        ttk.Button(search_frame, text="搜索", 
                  command=self.search_guns).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="重置", 
                  command=self.reset_gun_search).pack(side=tk.LEFT)
        
        # 工枪列表
        list_frame = ttk.Frame(self.gun_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建Treeview
        columns = ("ID", "型号", "品牌", "状态", "创建时间", "备注")
        self.gun_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=20)
        
        # 设置列标题
        for col in columns:
            self.gun_tree.heading(col, text=col)
            self.gun_tree.column(col, width=100, minwidth=50)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.gun_tree.yview)
        self.gun_tree.configure(yscrollcommand=scrollbar.set)
        
        self.gun_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定选择事件
        self.gun_tree.bind('<<TreeviewSelect>>', self.on_gun_select)
        
        # 按钮框架
        btn_frame = ttk.Frame(self.gun_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.add_btn = ttk.Button(btn_frame, text="添加", command=self.add_gun)
        self.add_btn.pack(side=tk.LEFT, padx=2)
        
        self.edit_btn = ttk.Button(btn_frame, text="编辑", command=self.edit_gun)
        self.edit_btn.pack(side=tk.LEFT, padx=2)
        
        self.delete_btn = ttk.Button(btn_frame, text="删除", command=self.delete_gun)
        self.delete_btn.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(btn_frame, text="刷新", command=self.refresh_guns).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="导出", command=self.export_guns).pack(side=tk.LEFT, padx=2)
    
    def setup_preset_tab(self):
        """设置预设管理标签页"""
        ttk.Label(self.preset_frame, text="预设管理功能开发中...",
                 font=("Arial", 12)).pack(expand=True)
    
    def setup_file_tab(self):
        """设置文件管理标签页"""
        ttk.Label(self.file_frame, text="文件管理功能开发中...",
                 font=("Arial", 12)).pack(expand=True)
    
    def setup_statusbar(self):
        """创建状态栏"""
        self.statusbar = ttk.Frame(self.root, relief=tk.SUNKEN, borderwidth=1)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        current_user = self.user_controller.get_current_user()
        role_text = "管理员" if current_user.is_admin() else "普通用户"
        
        self.status_label = ttk.Label(self.statusbar, 
                                     text=f"当前用户: {current_user.username} ({role_text})")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        self.time_label = ttk.Label(self.statusbar, text="")
        self.time_label.pack(side=tk.RIGHT, padx=5)
        
        # 更新时间显示
        self.update_time()
    
    def update_time(self):
        """更新时间显示"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=now)
        self.root.after(1000, self.update_time)
    
    def switch_user(self):
        """切换用户"""
        if messagebox.askyesno("切换用户", "确定要切换用户吗？当前操作将保存。"):
            # 登出当前用户
            self.user_controller.logout()
            
            # 重新登录
            if not self.user_login():
                self.root.destroy()
                return
            
            # 更新界面
            self.update_ui_by_permission()
            
            # 更新状态栏
            current_user = self.user_controller.get_current_user()
            role_text = "管理员" if current_user.is_admin() else "普通用户"
            self.status_label.config(text=f"当前用户: {current_user.username} ({role_text})")
            
            # 刷新数据
            self.refresh_guns()
    
    def check_permission(self, action):
        """检查权限"""
        if action == "add" and not self.user_controller.can_add():
            messagebox.showwarning("权限不足", "您没有添加权限，请使用管理员账号登录")
            return False
        elif action == "edit" and not self.user_controller.can_edit():
            messagebox.showwarning("权限不足", "您没有编辑权限，请使用管理员账号登录")
            return False
        elif action == "delete" and not self.user_controller.can_delete():
            messagebox.showwarning("权限不足", "您没有删除权限，请使用管理员账号登录")
            return False
        return True
    
    def load_initial_data(self):
        """加载初始数据"""
        self.refresh_guns()
    
    def refresh_guns(self):
        """刷新工枪列表"""
        try:
            # 清空现有数据
            for item in self.gun_tree.get_children():
                self.gun_tree.delete(item)
            
            # 从数据库加载数据
            guns = self.gun_controller.get_all_guns()
            
            # 添加到Treeview
            for gun in guns:
                created_at = gun.get('created_at')
                notes = gun.get('notes', '')
                
                # 处理时间格式
                time_str = ""
                if created_at:
                    if hasattr(created_at, 'strftime'):
                        time_str = created_at.strftime("%Y-%m-%d")
                    else:
                        time_str = str(created_at)[:10]
                
                self.gun_tree.insert('', 'end', values=(
                    gun.get('id'),
                    gun.get('model'),
                    gun.get('brand'),
                    gun.get('status', '正常'),
                    time_str,
                    notes[:50] + "..." if len(notes) > 50 else notes
                ))
            
            self.root.title(f"焊接枪管理系统 - 当前用户: {self.user_controller.get_current_user().username}")
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("错误", f"加载数据时出错: {str(e)}")
    
    # ...（其他方法保持不变，但需要在每个操作前添加权限检查）...
    
    def add_gun(self):
        """添加工枪"""
        if not self.check_permission("add"):
            return
        
        from .gun_dialog import GunDialog
        
        dialog = GunDialog(self.root, title="添加工枪")
        if dialog.result:
            try:
                self.gun_controller.add_gun(dialog.result)
                self.refresh_guns()
                messagebox.showinfo("成功", "工枪添加成功")
            except Exception as e:
                messagebox.showerror("错误", f"添加失败: {str(e)}")
    
    def edit_gun(self):
        """编辑工枪"""
        if not self.check_permission("edit"):
            return
        
        selection = self.gun_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要编辑的工枪")
            return
        
        item = self.gun_tree.item(selection[0])
        gun_id = item['values'][0]
        
        try:
            gun_data = self.gun_controller.get_gun_by_id(gun_id)
            if gun_data:
                from .gun_dialog import GunDialog
                from models.entities import WeldingGun
                
                # 将字典转换为WeldingGun对象
                gun_obj = WeldingGun.from_dict(gun_data)
                
                dialog = GunDialog(self.root, title="编辑工枪", gun=gun_obj)
                if dialog.result:
                    self.gun_controller.update_gun(gun_id, dialog.result)
                    self.refresh_guns()
                    messagebox.showinfo("成功", "工枪更新成功")
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("错误", f"编辑失败: {str(e)}")
    
    def delete_gun(self):
        """删除工枪"""
        if not self.check_permission("delete"):
            return
        
        selection = self.gun_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的工枪")
            return
        
        if not messagebox.askyesno("确认", "确定要删除选中的工枪吗？"):
            return
        
        item = self.gun_tree.item(selection[0])
        gun_id = item['values'][0]
        
        try:
            self.gun_controller.delete_gun(gun_id)
            self.refresh_guns()
            messagebox.showinfo("成功", "工枪删除成功")
        except Exception as e:
            messagebox.showerror("错误", f"删除失败: {str(e)}")
    
    # ...（其他方法：search_guns, reset_gun_search, on_gun_select等保持不变）...
    
    def show_users(self):
        """显示用户列表"""
        if not self.user_controller.is_admin():
            messagebox.showwarning("权限不足", "只有管理员可以查看用户列表")
            return
        
        from views.user_dialog import UserDialog
        UserDialog(self.root, self.user_controller)
    
    def add_user(self):
        """添加用户"""
        if not self.user_controller.is_admin():
            messagebox.showwarning("权限不足", "只有管理员可以添加用户")
            return
        
        from views.user_dialog import UserDialog
        UserDialog(self.root, self.user_controller, mode='add')
    
    # ...（其他方法保持不变）...

    def on_closing(self):
        """关闭窗口事件"""
        if messagebox.askokcancel("退出", "确定要退出程序吗？"):
            try:
                self.db.close()
            except:
                pass
            self.root.destroy()