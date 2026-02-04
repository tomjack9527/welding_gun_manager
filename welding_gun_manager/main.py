#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
焊接枪管理系统 - 主程序
Welding Gun Management System - Main Application
"""

import os
import sys
import json
import sqlite3
import datetime
import threading
import traceback
from pathlib import Path

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 第三方库导入
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog, simpledialog
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import pandas as pd
    from PIL import Image, ImageTk
except ImportError as e:
    print(f"缺少依赖库: {e}")
    print("请安装所需库: pip install matplotlib pandas pillow")
    sys.exit(1)

# 本地模块导入
try:
    from controllers.gun_controller import GunController
    from controllers.user_controller import UserController
    from controllers.preset_controller import PresetController
    from controllers.file_controller import FileController
    from models.database import Database
    from models.entities import WeldingGun, User, Preset
    from views.login_dialog import LoginDialog
    from views.main_window import MainWindow
    from views.dialogs import *
    from services.file_service import FileService
    from services.preset_service import PresetService
except ImportError as e:
    print(f"模块导入错误: {e}")
    print("请确保所有模块文件都存在")
    traceback.print_exc()
    sys.exit(1)


class WeldingGunManager:
    """焊接枪管理系统主类"""
    
    def __init__(self):
        """初始化应用程序"""
        self.root = None
        self.current_user = None
        self.is_admin = False
        
        # 控制器
        self.gun_controller = None
        self.user_controller = None
        self.preset_controller = None
        self.file_controller = None
        
        # 视图
        self.main_window = None
        
        # 数据库
        self.db = None
        
        # 应用设置
        self.settings = self.load_settings()
        
        # 应用状态
        self.app_state = {
            'logged_in': False,
            'current_view': None,
            'search_filter': '',
            'sort_by': 'name',
            'sort_order': 'asc'
        }
    
    def load_settings(self):
        """加载应用设置"""
        settings_file = os.path.join(current_dir, 'config', 'settings.json')
        default_settings = {
            'theme': 'light',
            'language': 'zh_CN',
            'auto_save': True,
            'backup_interval': 3600,  # 秒
            'default_view': 'dashboard',
            'recent_files': [],
            'window_size': {'width': 1200, 'height': 800},
            'max_log_size': 10000,
            'export_format': 'excel'
        }
        
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # 合并设置，确保所有默认键都存在
                    for key in default_settings:
                        if key not in loaded:
                            loaded[key] = default_settings[key]
                    return loaded
            except Exception as e:
                print(f"加载设置失败: {e}, 使用默认设置")
        
        return default_settings
    
    def save_settings(self):
        """保存应用设置"""
        settings_file = os.path.join(current_dir, 'config', 'settings.json')
        try:
            os.makedirs(os.path.dirname(settings_file), exist_ok=True)
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存设置失败: {e}")
    
    def initialize_database(self):
        """初始化数据库"""
        try:
            self.db = Database()
            if not self.db.initialize():
                messagebox.showerror("数据库错误", "数据库初始化失败")
                return False
            
            # 创建控制器
            self.gun_controller = GunController(self.db)
            self.user_controller = UserController(self.db)
            self.preset_controller = PresetController(self.db)
            self.file_controller = FileController()
            
            # 检查是否有用户，如果没有则创建默认用户
            if not self.user_controller.get_all_users():
                self.create_default_users()
            
            return True
            
        except Exception as e:
            messagebox.showerror("初始化错误", f"数据库初始化失败: {str(e)}")
            traceback.print_exc()
            return False
    
    def create_default_users(self):
        """创建默认用户"""
        default_users = [
            {
                'username': 'system',
                'password': 'manager',
                'role': 'admin',
                'full_name': '系统管理员',
                'email': 'admin@welding.com',
                'created_at': datetime.datetime.now().isoformat()
            },
            {
                'username': 'administrator',
                'password': None,  # 无密码
                'role': 'admin',
                'full_name': 'Administrator',
                'email': '',
                'created_at': datetime.datetime.now().isoformat()
            },
            {
                'username': 'user',
                'password': 'user123',
                'role': 'user',
                'full_name': '普通用户',
                'email': 'user@welding.com',
                'created_at': datetime.datetime.now().isoformat()
            }
        ]
        
        for user_data in default_users:
            try:
                user = User(
                    username=user_data['username'],
                    password=user_data['password'],
                    role=user_data['role'],
                    full_name=user_data['full_name'],
                    email=user_data['email'],
                    created_at=user_data['created_at']
                )
                self.user_controller.create_user(user)
            except Exception as e:
                print(f"创建用户 {user_data['username']} 失败: {e}")
    
    def setup_gui(self):
        """设置GUI"""
        try:
            # 创建主窗口
            self.root = tk.Tk()
            self.root.title("焊接枪管理系统")
            
            # 设置窗口大小和位置
            width = self.settings['window_size']['width']
            height = self.settings['window_size']['height']
            self.root.geometry(f"{width}x{height}")
            
            # 设置窗口图标
            try:
                icon_path = os.path.join(current_dir, 'resources', 'icons', 'app_icon.ico')
                if os.path.exists(icon_path):
                    self.root.iconbitmap(icon_path)
            except:
                pass  # 图标加载失败不影响程序运行
            
            # 设置主题
            self.apply_theme()
            
            # 设置协议
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            # 创建菜单栏
            self.setup_menu()
            
            # 创建状态栏
            self.setup_statusbar()
            
            # 创建主窗口内容
            self.show_login_screen()
            
            return True
            
        except Exception as e:
            messagebox.showerror("GUI错误", f"界面初始化失败: {str(e)}")
            traceback.print_exc()
            return False
    
    def apply_theme(self):
        """应用主题"""
        theme = self.settings['theme']
        if theme == 'dark':
            # 深色主题
            self.root.configure(bg='#2b2b2b')
        else:
            # 浅色主题
            self.root.configure(bg='#f0f0f0')
    
    def setup_menu(self):
        """设置菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="导入数据", command=self.import_data)
        file_menu.add_command(label="导出数据", command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label="打印报表", command=self.print_report)
        file_menu.add_separator()
        file_menu.add_command(label="设置", command=self.show_settings_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.on_closing)
        
        # 编辑菜单
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="编辑", menu=edit_menu)
        edit_menu.add_command(label="添加工枪", command=self.add_gun)
        edit_menu.add_command(label="编辑工枪", command=self.edit_gun)
        edit_menu.add_command(label="删除工枪", command=self.delete_gun)
        edit_menu.add_separator()
        edit_menu.add_command(label="查找工枪", command=self.search_gun)
        
        # 视图菜单
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="视图", menu=view_menu)
        view_menu.add_command(label="仪表盘", command=lambda: self.show_view('dashboard'))
        view_menu.add_command(label="工枪列表", command=lambda: self.show_view('gun_list'))
        view_menu.add_command(label="统计分析", command=lambda: self.show_view('statistics'))
        view_menu.add_separator()
        view_menu.add_command(label="刷新", command=self.refresh_view)
        
        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="备份数据库", command=self.backup_database)
        tools_menu.add_command(label="恢复数据库", command=self.restore_database)
        tools_menu.add_separator()
        tools_menu.add_command(label="系统诊断", command=self.run_diagnostic)
        tools_menu.add_command(label="查看日志", command=self.show_logs)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="用户手册", command=self.show_manual)
        help_menu.add_command(label="关于", command=self.show_about)
        
        # 保存菜单栏引用
        self.menubar = menubar
        self.file_menu = file_menu
        self.edit_menu = edit_menu
        self.view_menu = view_menu
        self.tools_menu = tools_menu
        self.help_menu = help_menu
    
    def setup_statusbar(self):
        """设置状态栏"""
        statusbar = tk.Frame(self.root, height=20, bd=1, relief=tk.SUNKEN)
        statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 左侧状态信息
        self.status_label = tk.Label(statusbar, text="就绪", anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # 右侧用户信息
        self.user_label = tk.Label(statusbar, text="未登录", anchor=tk.E)
        self.user_label.pack(side=tk.RIGHT, padx=5)
        
        # 保存状态栏引用
        self.statusbar = statusbar
    
    def update_status(self, message):
        """更新状态栏信息"""
        if hasattr(self, 'status_label'):
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            self.status_label.config(text=f"{timestamp} - {message}")
            self.root.update_idletasks()
    
    def update_user_info(self):
        """更新用户信息显示"""
        if hasattr(self, 'user_label'):
            if self.current_user:
                role_text = "管理员" if self.is_admin else "用户"
                self.user_label.config(text=f"{self.current_user['username']} ({role_text})")
            else:
                self.user_label.config(text="未登录")
    
    def show_login_screen(self):
        """显示登录屏幕"""
        # 清除主窗口内容
        for widget in self.root.winfo_children():
            if widget not in [self.menubar, self.statusbar]:
                widget.destroy()
        
        # 创建登录框架
        login_frame = tk.Frame(self.root, padx=40, pady=40)
        login_frame.pack(expand=True)
        
        # 标题
        title_label = tk.Label(
            login_frame,
            text="焊接枪管理系统",
            font=("微软雅黑", 24, "bold"),
            fg="#2c3e50"
        )
        title_label.pack(pady=(0, 30))
        
        # 副标题
        subtitle_label = tk.Label(
            login_frame,
            text="Welding Gun Management System",
            font=("Arial", 12),
            fg="#7f8c8d"
        )
        subtitle_label.pack(pady=(0, 40))
        
        # 登录表单框架
        form_frame = tk.Frame(login_frame)
        form_frame.pack()
        
        # 用户名
        tk.Label(form_frame, text="用户名:", 
                font=("微软雅黑", 11)).grid(row=0, column=0, sticky=tk.W, pady=10)
        username_var = tk.StringVar(value="system")
        username_entry = tk.Entry(form_frame, textvariable=username_var, 
                                 font=("微软雅黑", 11), width=25)
        username_entry.grid(row=0, column=1, padx=10, pady=10)
        username_entry.focus()
        
        # 密码
        tk.Label(form_frame, text="密码:", 
                font=("微软雅黑", 11)).grid(row=1, column=0, sticky=tk.W, pady=10)
        password_var = tk.StringVar(value="manager")
        password_entry = tk.Entry(form_frame, textvariable=password_var, 
                                 font=("微软雅黑", 11), width=25, show="*")
        password_entry.grid(row=1, column=1, padx=10, pady=10)
        
        # 快速登录按钮框架
        quick_login_frame = tk.Frame(login_frame)
        quick_login_frame.pack(pady=20)
        
        tk.Label(quick_login_frame, text="快速登录:").pack(side=tk.LEFT, padx=(0, 10))
        
        # 快速登录按钮
        quick_users = [
            ("system", "manager", "系统管理员"),
            ("administrator", "", "Administrator"),
            ("user", "user123", "普通用户"),
        ]
        
        for username, password, text in quick_users:
            btn = tk.Button(
                quick_login_frame,
                text=text,
                command=lambda u=username, p=password: self.quick_login(u, p, username_var, password_var),
                bg="#3498db",
                fg="white",
                relief=tk.FLAT,
                padx=10,
                pady=5
            )
            btn.pack(side=tk.LEFT, padx=5)
        
        # 登录按钮框架
        button_frame = tk.Frame(login_frame)
        button_frame.pack(pady=30)
        
        def do_login():
            self.login(username_var.get(), password_var.get())
        
        login_btn = tk.Button(
            button_frame,
            text="登录",
            command=do_login,
            bg="#2ecc71",
            fg="white",
            font=("微软雅黑", 12, "bold"),
            relief=tk.FLAT,
            padx=30,
            pady=10,
            cursor="hand2"
        )
        login_btn.pack(side=tk.LEFT, padx=10)
        
        # 绑定回车键
        self.root.bind('<Return>', lambda event: do_login())
        
        # 记住密码复选框
        remember_var = tk.BooleanVar(value=True)
        remember_check = tk.Checkbutton(
            login_frame,
            text="记住密码",
            variable=remember_var,
            font=("微软雅黑", 10)
        )
        remember_check.pack()
    
    def quick_login(self, username, password, username_var, password_var):
        """快速登录"""
        username_var.set(username)
        password_var.set(password)
        self.login(username, password)
    
    def login(self, username, password):
        """用户登录"""
        try:
            if not username.strip():
                messagebox.showwarning("警告", "请输入用户名")
                return
            
            # 特殊处理administrator用户（无密码）
            if username == "administrator":
                user = self.user_controller.get_user_by_username(username)
                if user and user.password is None:
                    self.on_login_success(user)
                    return
            
            # 普通用户验证
            user = self.user_controller.authenticate(username, password)
            if user:
                self.on_login_success(user)
            else:
                messagebox.showerror("登录失败", "用户名或密码错误")
                
        except Exception as e:
            messagebox.showerror("登录错误", f"登录过程出错: {str(e)}")
    
    def on_login_success(self, user):
        """登录成功处理"""
        self.current_user = {
            'id': user.id,
            'username': user.username,
            'full_name': user.full_name,
            'role': user.role,
            'email': user.email
        }
        self.is_admin = (user.role == 'admin')
        self.app_state['logged_in'] = True
        
        # 更新用户信息显示
        self.update_user_info()
        self.update_status(f"欢迎, {user.full_name}!")
        
        # 显示主界面
        self.show_main_interface()
        
        # 根据用户角色启用/禁用菜单项
        self.update_menu_permissions()
    
    def show_main_interface(self):
        """显示主界面"""
        # 清除现有内容
        for widget in self.root.winfo_children():
            if widget not in [self.menubar, self.statusbar]:
                widget.destroy()
        
        # 创建主框架
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧导航栏
        nav_frame = tk.Frame(main_frame, width=200, bg="#f8f9fa", relief=tk.RAISED, bd=1)
        nav_frame.pack(side=tk.LEFT, fill=tk.Y)
        nav_frame.pack_propagate(False)
        
        # 导航标题
        nav_title = tk.Label(
            nav_frame,
            text="导航菜单",
            font=("微软雅黑", 12, "bold"),
            bg="#f8f9fa",
            pady=15
        )
        nav_title.pack(fill=tk.X)
        
        # 导航按钮
        nav_buttons = [
            ("🏠 仪表盘", "dashboard", self.show_dashboard),
            ("🔧 工枪管理", "gun_management", self.show_gun_management),
            ("👥 用户管理", "user_management", self.show_user_management),
            ("📊 统计分析", "statistics", self.show_statistics),
            ("⚙️ 系统设置", "settings", self.show_settings_dialog),
            ("📁 文件管理", "file_management", self.show_file_management),
            ("❓ 帮助", "help", self.show_help),
        ]
        
        for text, view_id, command in nav_buttons:
            # 非管理员隐藏用户管理和系统设置
            if not self.is_admin and view_id in ['user_management', 'settings']:
                continue
            
            btn = tk.Button(
                nav_frame,
                text=text,
                command=command,
                anchor=tk.W,
                bg="#f8f9fa",
                relief=tk.FLAT,
                font=("微软雅黑", 11),
                padx=20,
                pady=10
            )
            btn.pack(fill=tk.X)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#e9ecef"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#f8f9fa"))
        
        # 内容区域
        self.content_frame = tk.Frame(main_frame, bg="white")
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 默认显示仪表盘
        self.show_dashboard()
    
    def show_dashboard(self):
        """显示仪表盘"""
        # 清除内容区域
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # 仪表盘标题
        title_frame = tk.Frame(self.content_frame, bg="white", pady=20)
        title_frame.pack(fill=tk.X)
        
        tk.Label(
            title_frame,
            text="系统仪表盘",
            font=("微软雅黑", 18, "bold"),
            bg="white"
        ).pack(side=tk.LEFT, padx=20)
        
        # 刷新按钮
        refresh_btn = tk.Button(
            title_frame,
            text="刷新数据",
            command=self.refresh_dashboard,
            bg="#3498db",
            fg="white",
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        refresh_btn.pack(side=tk.RIGHT, padx=20)
        
        # 统计卡片框架
        cards_frame = tk.Frame(self.content_frame, bg="white", padx=20, pady=10)
        cards_frame.pack(fill=tk.X)
        
        try:
            # 获取统计数据
            total_guns = self.gun_controller.get_guns_count()
            active_guns = self.gun_controller.get_guns_count(status='active')
            maintenance_guns = self.gun_controller.get_guns_count(status='maintenance')
            total_users = self.user_controller.get_users_count()
            
            # 创建统计卡片
            stats = [
                ("总工枪数", total_guns, "#3498db", "把"),
                ("在用工枪", active_guns, "#2ecc71", "把"),
                ("维护中", maintenance_guns, "#e74c3c", "把"),
                ("总用户数", total_users, "#9b59b6", "人"),
            ]
            
            for i, (title, value, color, unit) in enumerate(stats):
                card = tk.Frame(cards_frame, bg=color, relief=tk.RAISED, bd=2)
                card.grid(row=0, column=i, padx=10, ipadx=20, ipady=15)
                
                tk.Label(card, text=title, bg=color, fg="white", 
                        font=("微软雅黑", 11)).pack()
                tk.Label(card, text=f"{value}{unit}", bg=color, fg="white", 
                        font=("微软雅黑", 18, "bold")).pack()
        
        except Exception as e:
            tk.Label(cards_frame, text=f"加载统计失败: {str(e)}", 
                    fg="red", bg="white").pack()
        
        # 近期活动框架
        activity_frame = tk.Frame(self.content_frame, bg="white", padx=20, pady=20)
        activity_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            activity_frame,
            text="近期活动",
            font=("微软雅黑", 14, "bold"),
            bg="white"
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # 创建活动列表
        try:
            recent_guns = self.gun_controller.get_recent_guns(limit=10)
            if recent_guns:
                for gun in recent_guns:
                    gun_info = f"{gun.name} ({gun.type}) - {gun.status}"
                    tk.Label(activity_frame, text=gun_info, 
                            bg="white", anchor=tk.W).pack(fill=tk.X, pady=2)
            else:
                tk.Label(activity_frame, text="暂无活动记录", 
                        fg="gray", bg="white").pack()
                
        except Exception as e:
            tk.Label(activity_frame, text=f"加载活动记录失败: {str(e)}", 
                    fg="red", bg="white").pack()
    
    def show_gun_management(self):
        """显示工枪管理界面"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # 工具栏
        toolbar = tk.Frame(self.content_frame, bg="#f8f9fa", pady=10)
        toolbar.pack(fill=tk.X)
        
        # 添加按钮
        add_btn = tk.Button(
            toolbar,
            text="添加工枪",
            command=self.add_gun_dialog,
            bg="#2ecc71",
            fg="white",
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        add_btn.pack(side=tk.LEFT, padx=5)
        
        # 搜索框
        search_frame = tk.Frame(toolbar, bg="#f8f9fa")
        search_frame.pack(side=tk.RIGHT, padx=5)
        
        tk.Label(search_frame, text="搜索:", bg="#f8f9fa").pack(side=tk.LEFT)
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, width=25)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        def on_search():
            self.search_guns(search_var.get())
        
        search_btn = tk.Button(
            search_frame,
            text="搜索",
            command=on_search,
            bg="#3498db",
            fg="white",
            relief=tk.FLAT
        )
        search_btn.pack(side=tk.LEFT)
        
        # 工枪列表
        self.gun_tree = ttk.Treeview(
            self.content_frame,
            columns=('id', 'name', 'type', 'model', 'status', 'last_maintenance'),
            show='headings'
        )
        
        # 设置列
        columns = [
            ('id', 'ID', 50),
            ('name', '名称', 150),
            ('type', '类型', 100),
            ('model', '型号', 120),
            ('status', '状态', 80),
            ('last_maintenance', '上次维护', 120)
        ]
        
        for col_id, heading, width in columns:
            self.gun_tree.heading(col_id, text=heading)
            self.gun_tree.column(col_id, width=width)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(self.content_frame, orient=tk.VERTICAL, 
                                 command=self.gun_tree.yview)
        self.gun_tree.configure(yscrollcommand=scrollbar.set)
        
        self.gun_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 0), pady=20)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 20), pady=20)
        
        # 绑定双击事件
        self.gun_tree.bind('<Double-1>', self.on_gun_double_click)
        
        # 右键菜单
        self.gun_context_menu = tk.Menu(self.root, tearoff=0)
        self.gun_context_menu.add_command(label="查看详情", command=self.view_gun_details)
        self.gun_context_menu.add_command(label="编辑", command=self.edit_gun_dialog)
        self.gun_context_menu.add_command(label="删除", command=self.delete_gun_dialog)
        self.gun_context_menu.add_separator()
        self.gun_context_menu.add_command(label="导出数据", command=self.export_selected_gun)
        
        self.gun_tree.bind('<Button-3>', self.show_gun_context_menu)
        
        # 加载数据
        self.load_guns()
    
    def load_guns(self, search_term=''):
        """加载工枪数据"""
        try:
            # 清空现有数据
            for item in self.gun_tree.get_children():
                self.gun_tree.delete(item)
            
            # 获取数据
            guns = self.gun_controller.search_guns(search_term)
            
            # 插入数据
            for gun in guns:
                values = (
                    gun.id,
                    gun.name,
                    gun.type,
                    gun.model or '',
                    gun.status,
                    gun.last_maintenance or ''
                )
                self.gun_tree.insert('', 'end', values=values)
            
            self.update_status(f"加载了 {len(guns)} 条工枪记录")
            
        except Exception as e:
            messagebox.showerror("加载错误", f"加载工枪数据失败: {str(e)}")
    
    def add_gun_dialog(self):
        """添加工枪对话框"""
        dialog = GunEditDialog(self.root, title="添加工枪")
        if dialog.result:
            try:
                gun_data = dialog.result
                gun = WeldingGun(**gun_data)
                success = self.gun_controller.create_gun(gun)
                if success:
                    messagebox.showinfo("成功", "工枪添加成功")
                    self.load_guns()
                else:
                    messagebox.showerror("错误", "添加工枪失败")
            except Exception as e:
                messagebox.showerror("错误", f"添加工枪时出错: {str(e)}")
    
    def on_gun_double_click(self, event):
        """工枪双击事件"""
        selection = self.gun_tree.selection()
        if selection:
            item = self.gun_tree.item(selection[0])
            gun_id = item['values'][0]
            self.view_gun_details_by_id(gun_id)
    
    def view_gun_details_by_id(self, gun_id):
        """根据ID查看工枪详情"""
        try:
            gun = self.gun_controller.get_gun_by_id(gun_id)
            if gun:
                details = f"""
名称: {gun.name}
类型: {gun.type}
型号: {gun.model or '未指定'}
序列号: {gun.serial_number or '未指定'}
状态: {gun.status}
位置: {gun.location or '未指定'}
上次维护: {gun.last_maintenance or '从未维护'}
备注: {gun.notes or '无'}
"""
                messagebox.showinfo(f"工枪详情 - {gun.name}", details)
            else:
                messagebox.showerror("错误", "工枪不存在")
        except Exception as e:
            messagebox.showerror("错误", f"获取工枪详情失败: {str(e)}")
    
    def show_gun_context_menu(self, event):
        """显示工枪右键菜单"""
        selection = self.gun_tree.identify_row(event.y)
        if selection:
            self.gun_tree.selection_set(selection)
            self.gun_context_menu.tk_popup(event.x_root, event.y_root)
    
    def edit_gun_dialog(self):
        """编辑工枪对话框"""
        selection = self.gun_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要编辑的工枪")
            return
        
        item = self.gun_tree.item(selection[0])
        gun_id = item['values'][0]
        
        try:
            gun = self.gun_controller.get_gun_by_id(gun_id)
            if gun:
                dialog = GunEditDialog(self.root, title="编辑工枪", gun=gun)
                if dialog.result:
                    updated_data = dialog.result
                    success = self.gun_controller.update_gun(gun_id, updated_data)
                    if success:
                        messagebox.showinfo("成功", "工枪更新成功")
                        self.load_guns()
                    else:
                        messagebox.showerror("错误", "更新工枪失败")
            else:
                messagebox.showerror("错误", "工枪不存在")
        except Exception as e:
            messagebox.showerror("错误", f"编辑工枪时出错: {str(e)}")
    
    def delete_gun_dialog(self):
        """删除工枪对话框"""
        selection = self.gun_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的工枪")
            return
        
        item = self.gun_tree.item(selection[0])
        gun_id = item['values'][0]
        gun_name = item['values'][1]
        
        if messagebox.askyesno("确认删除", f"确定要删除工枪 '{gun_name}' 吗？"):
            try:
                success = self.gun_controller.delete_gun(gun_id)
                if success:
                    messagebox.showinfo("成功", "工枪删除成功")
                    self.load_guns()
                else:
                    messagebox.showerror("错误", "删除工枪失败")
            except Exception as e:
                messagebox.showerror("错误", f"删除工枪时出错: {str(e)}")
    
    def search_guns(self, search_term):
        """搜索工枪"""
        self.load_guns(search_term)
        self.update_status(f"搜索: {search_term}")
    
    def show_user_management(self):
        """显示用户管理界面（仅管理员）"""
        if not self.is_admin:
            messagebox.showwarning("权限不足", "需要管理员权限")
            return
        
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # 用户管理界面代码...
        tk.Label(self.content_frame, text="用户管理界面", 
                font=("微软雅黑", 16)).pack(pady=50)
    
    def show_statistics(self):
        """显示统计分析界面"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        try:
            # 获取统计数据
            stats = self.gun_controller.get_statistics()
            
            # 创建图表框架
            fig, axes = plt.subplots(1, 2, figsize=(10, 4))
            
            # 状态分布饼图
            if stats.get('status_distribution'):
                status_data = stats['status_distribution']
                labels = list(status_data.keys())
                sizes = list(status_data.values())
                
                axes[0].pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
                axes[0].set_title('工枪状态分布')
                axes[0].axis('equal')
            
            # 类型分布柱状图
            if stats.get('type_distribution'):
                type_data = stats['type_distribution']
                types = list(type_data.keys())
                counts = list(type_data.values())
                
                axes[1].bar(types, counts)
                axes[1].set_title('工枪类型分布')
                axes[1].set_xlabel('类型')
                axes[1].set_ylabel('数量')
                axes[1].tick_params(axis='x', rotation=45)
            
            # 嵌入图表到Tkinter
            canvas = FigureCanvasTkAgg(fig, self.content_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # 添加统计表格
            table_frame = tk.Frame(self.content_frame)
            table_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
            
            # 显示主要统计数据
            tk.Label(table_frame, text="统计数据", 
                    font=("微软雅黑", 12, "bold")).pack(anchor=tk.W)
            
            stats_text = tk.Text(table_frame, height=5, width=50)
            stats_text.pack(fill=tk.X, pady=5)
            
            stats_info = f"""
总工枪数: {stats.get('total_guns', 0)}
在用工枪: {stats.get('active_guns', 0)}
维护中工枪: {stats.get('maintenance_guns', 0)}
待报废工枪: {stats.get('scrap_guns', 0)}
"""
            stats_text.insert(tk.END, stats_info)
            stats_text.config(state=tk.DISABLED)
            
        except Exception as e:
            tk.Label(self.content_frame, text=f"加载统计数据失败: {str(e)}", 
                    fg="red").pack(pady=50)
    
    def show_settings_dialog(self):
        """显示设置对话框"""
        if not self.is_admin:
            messagebox.showwarning("权限不足", "需要管理员权限")
            return
        
        dialog = SettingsDialog(self.root, self.settings)
        if dialog.result:
            self.settings.update(dialog.result)
            self.save_settings()
            self.apply_theme()
            messagebox.showinfo("设置", "设置已保存，部分设置需要重启生效")
    
    def show_file_management(self):
        """显示文件管理界面"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # 文件管理界面代码...
        tk.Label(self.content_frame, text="文件管理界面", 
                font=("微软雅黑", 16)).pack(pady=50)
    
    def show_help(self):
        """显示帮助"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        help_text = """
焊接枪管理系统 - 用户手册

主要功能：
1. 工枪管理 - 添加、编辑、删除和查询工枪信息
2. 用户管理 - 管理用户账户和权限（仅管理员）
3. 统计分析 - 查看工枪统计数据和图表
4. 数据导入导出 - 支持Excel、CSV格式

快速开始：
1. 使用快速登录按钮登录
2. 在导航菜单选择功能模块
3. 使用工具栏按钮执行操作

快捷键：
- Enter: 登录/确认
- F5: 刷新当前视图
- Ctrl+F: 搜索
- Ctrl+Q: 退出系统

技术支持：
如有问题，请联系系统管理员或查看日志文件。
"""
        
        text_widget = tk.Text(self.content_frame, wrap=tk.WORD, padx=20, pady=20)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)
    
    def import_data(self):
        """导入数据"""
        file_path = filedialog.askopenfilename(
            title="选择数据文件",
            filetypes=[
                ("Excel文件", "*.xlsx *.xls"),
                ("CSV文件", "*.csv"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            try:
                # 根据文件类型选择导入方法
                if file_path.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(file_path)
                elif file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                else:
                    messagebox.showerror("错误", "不支持的文件格式")
                    return
                
                # 导入数据到数据库
                imported = self.gun_controller.import_from_dataframe(df)
                
                messagebox.showinfo("导入成功", 
                                  f"成功导入 {imported} 条记录")
                self.load_guns()
                
            except Exception as e:
                messagebox.showerror("导入错误", f"导入数据失败: {str(e)}")
    
    def export_data(self):
        """导出数据"""
        file_path = filedialog.asksaveasfilename(
            title="保存数据文件",
            defaultextension=".xlsx",
            filetypes=[
                ("Excel文件", "*.xlsx"),
                ("CSV文件", "*.csv"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            try:
                # 获取所有工枪数据
                guns = self.gun_controller.get_all_guns()
                
                # 转换为DataFrame
                data = []
                for gun in guns:
                    data.append({
                        '名称': gun.name,
                        '类型': gun.type,
                        '型号': gun.model,
                        '序列号': gun.serial_number,
                        '状态': gun.status,
                        '位置': gun.location,
                        '上次维护': gun.last_maintenance,
                        '备注': gun.notes
                    })
                
                df = pd.DataFrame(data)
                
                # 根据文件类型保存
                if file_path.endswith('.xlsx'):
                    df.to_excel(file_path, index=False)
                elif file_path.endswith('.csv'):
                    df.to_csv(file_path, index=False, encoding='utf-8-sig')
                
                messagebox.showinfo("导出成功", 
                                  f"数据已导出到: {file_path}")
                
            except Exception as e:
                messagebox.showerror("导出错误", f"导出数据失败: {str(e)}")
    
    def print_report(self):
        """打印报表"""
        try:
            # 生成报表
            report_data = self.gun_controller.generate_report()
            
            # 显示打印对话框
            print_dialog = PrintDialog(self.root, report_data)
            
        except Exception as e:
            messagebox.showerror("打印错误", f"生成报表失败: {str(e)}")
    
    def backup_database(self):
        """备份数据库"""
        if not self.is_admin:
            messagebox.showwarning("权限不足", "需要管理员权限")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="备份数据库",
            defaultextension=".db",
            filetypes=[("数据库文件", "*.db"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                self.db.backup(file_path)
                messagebox.showinfo("备份成功", f"数据库已备份到: {file_path}")
            except Exception as e:
                messagebox.showerror("备份错误", f"备份数据库失败: {str(e)}")
    
    def restore_database(self):
        """恢复数据库"""
        if not self.is_admin:
            messagebox.showwarning("权限不足", "需要管理员权限")
            return
        
        if messagebox.askyesno("警告", "恢复数据库将覆盖当前数据，确定继续吗？"):
            file_path = filedialog.askopenfilename(
                title="选择备份文件",
                filetypes=[("数据库文件", "*.db"), ("所有文件", "*.*")]
            )
            
            if file_path:
                try:
                    self.db.restore(file_path)
                    messagebox.showinfo("恢复成功", "数据库已恢复，请重新登录")
                    self.show_login_screen()
                except Exception as e:
                    messagebox.showerror("恢复错误", f"恢复数据库失败: {str(e)}")
    
    def run_diagnostic(self):
        """运行系统诊断"""
        try:
            from diagnose import run_diagnostic
            report = run_diagnostic()
            
            # 显示诊断结果
            dialog = DiagnosticDialog(self.root, report)
            
        except Exception as e:
            messagebox.showerror("诊断错误", f"运行诊断失败: {str(e)}")
    
    def show_logs(self):
        """查看日志"""
        log_file = os.path.join(current_dir, 'logs', 'application.log')
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_content = f.read()
                
                # 显示日志对话框
                LogViewerDialog(self.root, log_content)
                
            except Exception as e:
                messagebox.showerror("日志错误", f"读取日志失败: {str(e)}")
        else:
            messagebox.showinfo("日志", "日志文件不存在")
    
    def show_manual(self):
        """显示用户手册"""
        manual_file = os.path.join(current_dir, 'docs', 'user_manual.pdf')
        if os.path.exists(manual_file):
            try:
                import webbrowser
                webbrowser.open(manual_file)
            except:
                messagebox.showinfo("用户手册", 
                                  "用户手册文件位于 docs/user_manual.pdf")
        else:
            messagebox.showinfo("用户手册", "用户手册文件不存在")
    
    def show_about(self):
        """显示关于对话框"""
        about_text = f"""
焊接枪管理系统 v1.0

功能特性：
- 工枪信息管理
- 用户权限控制
- 数据统计分析
- 导入导出功能
- 系统设置管理

系统信息：
Python版本: {sys.version}
数据库: SQLite
界面: Tkinter

© 2023 焊接枪管理系统团队
技术支持: admin@welding.com
"""
        
        messagebox.showinfo("关于", about_text)
    
    def refresh_view(self):
        """刷新当前视图"""
        current_view = self.app_state.get('current_view')
        if current_view == 'dashboard':
            self.refresh_dashboard()
        elif current_view == 'gun_management':
            self.load_guns()
        elif current_view == 'statistics':
            self.show_statistics()
    
    def refresh_dashboard(self):
        """刷新仪表盘"""
        self.show_dashboard()
        self.update_status("仪表盘已刷新")
    
    def update_menu_permissions(self):
        """根据用户权限更新菜单项"""
        # 启用/禁用编辑菜单项
        for i in range(self.edit_menu.index(tk.END) + 1):
            try:
                label = self.edit_menu.entrycget(i, 'label')
                if label in ['添加工枪', '编辑工枪', '删除工枪']:
                    if not self.is_admin:
                        self.edit_menu.entryconfig(i, state=tk.DISABLED)
                    else:
                        self.edit_menu.entryconfig(i, state=tk.NORMAL)
            except:
                pass
        
        # 启用/禁用工具菜单项
        for i in range(self.tools_menu.index(tk.END) + 1):
            try:
                label = self.tools_menu.entrycget(i, 'label')
                if label in ['备份数据库', '恢复数据库', '系统设置']:
                    if not self.is_admin:
                        self.tools_menu.entryconfig(i, state=tk.DISABLED)
                    else:
                        self.tools_menu.entryconfig(i, state=tk.NORMAL)
            except:
                pass
    
    def on_closing(self):
        """关闭应用程序"""
        if messagebox.askokcancel("退出", "确定要退出系统吗？"):
            # 保存窗口大小
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            self.settings['window_size'] = {'width': width, 'height': height}
            self.save_settings()
            
            # 关闭数据库连接
            if self.db:
                self.db.close()
            
            # 退出应用程序
            self.root.quit()
            self.root.destroy()
            sys.exit(0)
    
    def run(self):
        """运行应用程序"""
        try:
            print("启动焊接枪管理系统...")
            
            # 初始化数据库
            self.update_status("正在初始化数据库...")
            if not self.initialize_database():
                return
            
            # 设置GUI
            self.update_status("正在初始化界面...")
            if not self.setup_gui():
                return
            
            # 启动自动备份（如果启用）
            if self.settings.get('auto_save', True):
                self.start_auto_backup()
            
            self.update_status("系统准备就绪")
            
            # 启动主循环
            print("系统启动完成")
            self.root.mainloop()
            
        except Exception as e:
            messagebox.showerror("启动错误", f"应用程序启动失败: {str(e)}")
            traceback.print_exc()
    
    def start_auto_backup(self):
        """启动自动备份"""
        def backup_task():
            interval = self.settings.get('backup_interval', 3600)
            while True:
                try:
                    import time
                    time.sleep(interval)
                    
                    # 在指定时间备份
                    backup_dir = os.path.join(current_dir, 'backups')
                    os.makedirs(backup_dir, exist_ok=True)
                    
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_file = os.path.join(backup_dir, f"backup_{timestamp}.db")
                    
                    self.db.backup(backup_file)
                    
                    # 清理旧备份（保留最近5个）
                    backup_files = sorted(
                        [f for f in os.listdir(backup_dir) if f.startswith('backup_')],
                        key=lambda x: os.path.getmtime(os.path.join(backup_dir, x))
                    )
                    
                    if len(backup_files) > 5:
                        for old_file in backup_files[:-5]:
                            os.remove(os.path.join(backup_dir, old_file))
                    
                except Exception as e:
                    print(f"自动备份失败: {e}")
        
        # 在新线程中运行备份任务
        backup_thread = threading.Thread(target=backup_task, daemon=True)
        backup_thread.start()


# 对话框类（需要在主文件中定义或从模块导入）
class GunEditDialog(tk.Toplevel):
    """工枪编辑对话框"""
    def __init__(self, parent, title="工枪编辑", gun=None):
        super().__init__(parent)
        self.title(title)
        self.parent = parent
        self.gun = gun
        self.result = None
        
        self.setup_ui()
        self.center_window()
        self.grab_set()
        self.wait_window()
    
    def setup_ui(self):
        """设置UI"""
        frame = ttk.Frame(self, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 表单字段
        fields = [
            ("名称*", "name", True),
            ("类型", "type", False),
            ("型号", "model", False),
            ("序列号", "serial_number", False),
            ("状态", "status", False),
            ("位置", "location", False),
            ("上次维护", "last_maintenance", False),
            ("备注", "notes", False),
        ]
        
        self.entries = {}
        for i, (label, field, required) in enumerate(fields):
            ttk.Label(frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=5)
            
            if field == 'status':
                # 状态使用下拉框
                status_var = tk.StringVar()
                status_combo = ttk.Combobox(frame, textvariable=status_var, 
                                           values=['active', 'maintenance', 'inactive', 'scrap'])
                status_combo.grid(row=i, column=1, sticky=tk.EW, pady=5, padx=(5, 0))
                self.entries[field] = status_var
            else:
                entry = ttk.Entry(frame)
                entry.grid(row=i, column=1, sticky=tk.EW, pady=5, padx=(5, 0))
                self.entries[field] = entry
        
        # 如果传入gun对象，填充数据
        if self.gun:
            self.entries['name'].insert(0, self.gun.name)
            if 'type' in self.entries:
                if isinstance(self.entries['type'], tk.StringVar):
                    self.entries['type'].set(self.gun.type or '')
                else:
                    self.entries['type'].insert(0, self.gun.type or '')
            # ... 填充其他字段
        
        # 按钮
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="确定", 
                  command=self.on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", 
                  command=self.destroy).pack(side=tk.LEFT)
        
        # 配置网格权重
        frame.columnconfigure(1, weight=1)
    
    def center_window(self):
        """窗口居中"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = self.parent.winfo_x() + (self.parent.winfo_width() - width) // 2
        y = self.parent.winfo_y() + (self.parent.winfo_height() - height) // 2
        self.geometry(f"+{x}+{y}")
    
    def on_ok(self):
        """确定按钮处理"""
        # 验证必填字段
        if not self.entries['name'].get().strip():
            messagebox.showerror("错误", "名称是必填字段")
            return
        
        # 收集数据
        self.result = {
            'name': self.entries['name'].get().strip(),
            'type': self.get_entry_value('type'),
            'model': self.get_entry_value('model'),
            'serial_number': self.get_entry_value('serial_number'),
            'status': self.get_entry_value('status') or 'active',
            'location': self.get_entry_value('location'),
            'last_maintenance': self.get_entry_value('last_maintenance'),
            'notes': self.get_entry_value('notes'),
        }
        
        self.destroy()
    
    def get_entry_value(self, field):
        """获取输入框值"""
        entry = self.entries[field]
        if isinstance(entry, tk.StringVar):
            return entry.get().strip()
        else:
            return entry.get().strip()


class SettingsDialog(tk.Toplevel):
    """设置对话框"""
    def __init__(self, parent, settings):
        super().__init__(parent)
        self.title("系统设置")
        self.parent = parent
        self.settings = settings
        self.result = None
        
        self.setup_ui()
        self.center_window()
        self.grab_set()
        self.wait_window()
    
    def setup_ui(self):
        """设置UI"""
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 常规设置
        general_frame = ttk.Frame(notebook, padding="20")
        notebook.add(general_frame, text="常规")
        
        # 主题选择
        ttk.Label(general_frame, text="主题:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.theme_var = tk.StringVar(value=self.settings.get('theme', 'light'))
        theme_combo = ttk.Combobox(general_frame, textvariable=self.theme_var, 
                                  values=['light', 'dark'], state='readonly')
        theme_combo.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        
        # 语言选择
        ttk.Label(general_frame, text="语言:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.language_var = tk.StringVar(value=self.settings.get('language', 'zh_CN'))
        language_combo = ttk.Combobox(general_frame, textvariable=self.language_var, 
                                     values=['zh_CN', 'en_US'], state='readonly')
        language_combo.grid(row=1, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        
        # 自动保存
        self.auto_save_var = tk.BooleanVar(value=self.settings.get('auto_save', True))
        ttk.Checkbutton(general_frame, text="启用自动保存", 
                       variable=self.auto_save_var).grid(row=2, column=0, columnspan=2, 
                                                        sticky=tk.W, pady=5)
        
        # 数据设置
        data_frame = ttk.Frame(notebook, padding="20")
        notebook.add(data_frame, text="数据")
        
        # 导出格式
        ttk.Label(data_frame, text="默认导出格式:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.export_format_var = tk.StringVar(value=self.settings.get('export_format', 'excel'))
        format_combo = ttk.Combobox(data_frame, textvariable=self.export_format_var, 
                                   values=['excel', 'csv', 'pdf'], state='readonly')
        format_combo.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        
        # 备份间隔
        ttk.Label(data_frame, text="自动备份间隔(小时):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.backup_var = tk.IntVar(value=self.settings.get('backup_interval', 3600) // 3600)
        ttk.Spinbox(data_frame, from_=1, to=24, textvariable=self.backup_var, 
                   width=10).grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # 按钮
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(button_frame, text="保存", 
                  command=self.on_save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="取消", 
                  command=self.destroy).pack(side=tk.RIGHT)
        
        # 配置网格权重
        general_frame.columnconfigure(1, weight=1)
        data_frame.columnconfigure(1, weight=1)
    
    def center_window(self):
        """窗口居中"""
        self.update_idletasks()
        width = 400
        height = 300
        x = self.parent.winfo_x() + (self.parent.winfo_width() - width) // 2
        y = self.parent.winfo_y() + (self.parent.winfo_height() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def on_save(self):
        """保存设置"""
        self.result = {
            'theme': self.theme_var.get(),
            'language': self.language_var.get(),
            'auto_save': self.auto_save_var.get(),
            'export_format': self.export_format_var.get(),
            'backup_interval': self.backup_var.get() * 3600,
        }
        self.destroy()


# 其他对话框类（简化版）
class PrintDialog:
    def __init__(self, parent, data):
        pass

class DiagnosticDialog:
    def __init__(self, parent, report):
        pass

class LogViewerDialog:
    def __init__(self, parent, content):
        pass


def main():
    """主函数"""
    try:
        app = WeldingGunManager()
        app.run()
    except Exception as e:
        print(f"应用程序运行失败: {e}")
        traceback.print_exc()
        messagebox.showerror("致命错误", f"应用程序运行失败: {str(e)}")


if __name__ == "__main__":
    main()