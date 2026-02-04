# welding_gun_manager/views/login_dialog_simple.py
import tkinter as tk
from tkinter import ttk

class SimpleLoginDialog:
    """简化登录对话框"""
    
    def __init__(self, parent):
        self.parent = parent
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("用户登录")
        self.dialog.geometry("300x250")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 居中
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 300) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 250) // 2
        self.dialog.geometry(f"+{x}+{y}")
        
        self.setup_ui()
        self.dialog.wait_window()
    
    def setup_ui(self):
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="用户登录", 
                 font=("Arial", 12, "bold")).pack(pady=(0, 15))
        
        # 快速登录按钮
        users = [
            ("system", "manager", "System 管理员"),
            ("administrator", "", "Administrator (无密码)"),
            ("user", "user123", "普通用户"),
        ]
        
        for username, password, description in users:
            btn = ttk.Button(frame, text=description, 
                           command=lambda u=username, p=password: self.quick_login(u, p),
                           width=25)
            btn.pack(pady=5)
        
        ttk.Separator(frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # 手动登录
        ttk.Label(frame, text="或手动输入:").pack(anchor=tk.W, pady=(0, 5))
        
        user_frame = ttk.Frame(frame)
        user_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(user_frame, text="用户:").grid(row=0, column=0, sticky=tk.W)
        self.user_var = tk.StringVar(value="system")
        ttk.Entry(user_frame, textvariable=self.user_var, width=20).grid(row=0, column=1, padx=5)
        
        ttk.Label(user_frame, text="密码:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.pass_var = tk.StringVar(value="manager")
        ttk.Entry(user_frame, textvariable=self.pass_var, show="*", width=20).grid(row=1, column=1, padx=5, pady=5)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="登录", 
                  command=self.manual_login).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="取消", 
                  command=self.dialog.destroy).pack(side=tk.LEFT)
    
    def quick_login(self, username, password):
        """快速登录"""
        self.result = {
            'username': username,
            'password': password if password else None
        }
        self.dialog.destroy()
    
    def manual_login(self):
        """手动登录"""
        username = self.user_var.get().strip()
        password = self.pass_var.get().strip()
        
        if not username:
            tk.messagebox.showwarning("警告", "请输入用户名")
            return
        
        self.result = {
            'username': username,
            'password': password if password else None
        }
        self.dialog.destroy()