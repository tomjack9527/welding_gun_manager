# 保存为 main_enhanced.py
import tkinter as tk
from tkinter import ttk, messagebox
import os
import sqlite3

class WeldingGunManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("焊接枪管理系统")
        self.root.geometry("900x700")
        
        # 当前用户
        self.current_user = None
        
        # 样式
        self.setup_styles()
        
    def setup_styles(self):
        """设置样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 自定义样式
        style.configure('Title.TLabel', font=('Arial', 18, 'bold'))
        style.configure('Heading.TLabel', font=('Arial', 12, 'bold'))
        
    def run(self):
        """运行应用程序"""
        self.show_login()
        self.root.mainloop()
    
    def show_login(self):
        """显示登录界面"""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        frame = ttk.Frame(self.root, padding="40")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        ttk.Label(frame, text="焊接枪管理系统", 
                 style='Title.TLabel').pack(pady=(0, 30))
        
        # 登录表单
        form_frame = ttk.Frame(frame)
        form_frame.pack(pady=20)
        
        ttk.Label(form_frame, text="用户名:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.username_var = tk.StringVar(value="system")
        ttk.Entry(form_frame, textvariable=self.username_var, width=25).grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(form_frame, text="密码:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar(value="manager")
        ttk.Entry(form_frame, textvariable=self.password_var, show="*", width=25).grid(row=1, column=1, pady=5, padx=5)
        
        # 快速用户按钮
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)
        
        users = [
            ("system", "manager", "System 管理员"),
            ("administrator", "", "Administrator"),
            ("user", "user123", "普通用户"),
        ]
        
        for username, password, desc in users:
            ttk.Button(button_frame, text=desc,
                      command=lambda u=username, p=password: self.quick_login(u, p),
                      width=20).pack(side=tk.LEFT, padx=5)
        
        # 登录按钮
        ttk.Button(frame, text="登录", command=self.do_login, 
                  width=20).pack(pady=20)
    
    def quick_login(self, username, password):
        """快速登录"""
        self.username_var.set(username)
        self.password_var.set(password)
        self.do_login()
    
    def do_login(self):
        """执行登录"""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        if not username:
            messagebox.showwarning("警告", "请输入用户名")
            return
        
        try:
            conn = sqlite3.connect("welding_gun.db")
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if username == "administrator":
                cursor.execute(
                    "SELECT * FROM users WHERE username = ? AND password IS NULL",
                    (username,)
                )
            else:
                cursor.execute(
                    "SELECT * FROM users WHERE username = ? AND password = ?",
                    (username, password)
                )
            
            user = cursor.fetchone()
            conn.close()
            
            if not user:
                messagebox.showerror("登录失败", "用户名或密码错误")
                return
            
            self.current_user = dict(user)
            self.show_main_menu()
            
        except Exception as e:
            messagebox.showerror("错误", f"登录失败: {str(e)}")
    
    def show_main_menu(self):
        """显示主菜单"""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        role_name = "管理员" if self.current_user['role'] == 'admin' else "普通用户"
        self.root.title(f"焊接枪管理系统 - {self.current_user['username']} ({role_name})")
        
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 顶部信息栏
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(info_frame, text=f"欢迎, {self.current_user['username']}!", 
                 style='Title.TLabel').pack(side=tk.LEFT)
        
        ttk.Label(info_frame, text=f"角色: {role_name}").pack(side=tk.RIGHT)
        
        # 功能按钮区
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧功能列
        left_frame = ttk.Frame(button_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        ttk.Label(left_frame, text="主要功能", style='Heading.TLabel').pack(pady=(0, 10))
        
        functions = [
            ("工枪管理", self.show_gun_management),
            ("用户管理", self.show_user_management),
            ("数据统计", self.show_statistics),
            ("系统设置", self.show_settings),
        ]
        
        for text, command in functions:
            if command in [self.show_user_management, self.show_settings] and self.current_user['role'] != 'admin':
                continue  # 非管理员跳过某些功能
            ttk.Button(left_frame, text=text, command=command, 
                      width=20).pack(pady=5)
        
        # 右侧快速操作
        right_frame = ttk.Frame(button_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        ttk.Label(right_frame, text="快速操作", style='Heading.TLabel').pack(pady=(0, 10))
        
        ttk.Button(right_frame, text="查看所有工枪", 
                  command=self.show_all_guns).pack(pady=5)
        ttk.Button(right_frame, text="添加新工枪", 
                  command=self.add_new_gun).pack(pady=5)
        ttk.Button(right_frame, text="生成报表", 
                  command=self.generate_report).pack(pady=5)
        
        # 底部按钮
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(bottom_frame, text="退出系统", 
                  command=self.root.destroy).pack(side=tk.RIGHT)
        ttk.Button(bottom_frame, text="重新登录", 
                  command=self.show_login).pack(side=tk.RIGHT, padx=5)
    
    def show_gun_management(self):
        """显示工枪管理界面"""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # 返回按钮
        ttk.Button(self.root, text="返回主菜单", 
                  command=self.show_main_menu).pack(anchor=tk.NW, padx=10, pady=10)
        
        # 标题
        ttk.Label(self.root, text="工枪管理", 
                 style='Title.TLabel').pack(pady=20)
        
        # 搜索框
        search_frame = ttk.Frame(self.root)
        search_frame.pack(pady=10)
        
        ttk.Label(search_frame, text="搜索:").pack(side=tk.LEFT)
        search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=search_var, width=30).pack(side=tk.LEFT, padx=5)
        
        def search_guns():
            search_term = search_var.get()
            # 实际搜索功能
            messagebox.showinfo("搜索", f"搜索: {search_term}")
        
        ttk.Button(search_frame, text="搜索", 
                  command=search_guns).pack(side=tk.LEFT)
        
        # 显示工枪列表
        try:
            conn = sqlite3.connect("welding_gun.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM guns")
            guns = cursor.fetchall()
            conn.close()
            
            # 创建表格
            tree_frame = ttk.Frame(self.root)
            tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            tree = ttk.Treeview(tree_frame, columns=('ID', '名称', '类型', '状态'), show='headings')
            tree.heading('ID', text='ID')
            tree.heading('名称', text='名称')
            tree.heading('类型', text='类型')
            tree.heading('状态', text='状态')
            
            for gun in guns:
                tree.insert('', 'end', values=gun[:4])
            
            tree.pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            ttk.Label(self.root, text=f"加载失败: {str(e)}", 
                     foreground='red').pack()
    
    # 其他功能方法（简化版）
    def show_user_management(self):
        messagebox.showinfo("用户管理", "用户管理功能")
        self.show_main_menu()
    
    def show_statistics(self):
        messagebox.showinfo("数据统计", "数据统计功能")
        self.show_main_menu()
    
    def show_settings(self):
        messagebox.showinfo("系统设置", "系统设置功能")
        self.show_main_menu()
    
    def show_all_guns(self):
        messagebox.showinfo("所有工枪", "显示所有工枪")
    
    def add_new_gun(self):
        messagebox.showinfo("添加工枪", "添加新工枪")
    
    def generate_report(self):
        messagebox.showinfo("生成报表", "生成报表")

if __name__ == "__main__":
    app = WeldingGunManager()
    app.run()