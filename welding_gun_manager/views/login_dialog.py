# views/login_dialog.py
import tkinter as tk
from tkinter import ttk

class LoginDialog:
    def __init__(self, parent):
        self.parent = parent
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("登录")
        self.dialog.geometry("300x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        self.dialog.wait_window()
    
    def setup_ui(self):
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="用户登录").pack(pady=10)
        
        ttk.Label(frame, text="用户名:").pack(anchor=tk.W)
        self.username_var = tk.StringVar(value="system")
        ttk.Entry(frame, textvariable=self.username_var).pack(fill=tk.X, pady=5)
        
        ttk.Label(frame, text="密码:").pack(anchor=tk.W, pady=(10, 0))
        self.password_var = tk.StringVar(value="manager")
        ttk.Entry(frame, textvariable=self.password_var, show="*").pack(fill=tk.X, pady=5)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="登录", 
                  command=self.on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", 
                  command=self.dialog.destroy).pack(side=tk.LEFT)
    
    def on_ok(self):
        self.result = {
            'username': self.username_var.get(),
            'password': self.password_var.get()
        }
        self.dialog.destroy()