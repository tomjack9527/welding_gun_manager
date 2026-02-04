# views/login_window.py
import tkinter as tk
from tkinter import ttk, messagebox

class LoginWindow:
    """用户登录窗口（支持切换用户）"""
    VALID_USERS = {
        "administrator": {"password": None, "role": "readonly", "desc": "只读用户"},
        "system": {"password": "manager", "role": "admin", "desc": "管理员"}
    }
    
    def __init__(self, parent, on_success_callback):
        self.parent = parent
        self.on_success = on_success_callback
        self.window = tk.Toplevel(parent)
        self.window.title("用户登录")
        self.window.geometry("320x180")
        self.window.transient(parent)
        self.window.grab_set()  # 模态窗口
        self.window.resizable(False, False)
        
        # 用户ID
        ttk.Label(self.window, text="用户ID:").grid(row=0, column=0, padx=15, pady=10, sticky='e')
        self.user_id_var = tk.StringVar(value="administrator")
        user_entry = ttk.Entry(self.window, textvariable=self.user_id_var, width=25)
        user_entry.grid(row=0, column=1, pady=10, sticky='w')
        
        # 密码（administrator留空即可）
        ttk.Label(self.window, text="密码:").grid(row=1, column=0, padx=15, pady=5, sticky='e')
        self.pw_var = tk.StringVar()
        pw_entry = ttk.Entry(self.window, textvariable=self.pw_var, show="*", width=25)
        pw_entry.grid(row=1, column=1, pady=5, sticky='w')
        pw_entry.bind('<Return>', lambda e: self._attempt_login())
        
        # 提示标签
        tip = ttk.Label(
            self.window, 
            text="• administrator 无需密码\n• system 密码: manager",
            font=("Arial", 8), foreground="gray"
        )
        tip.grid(row=2, column=0, columnspan=2, pady=(5,10))
        
        # 按钮区
        btn_frame = ttk.Frame(self.window)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=5)
        ttk.Button(btn_frame, text="登录", command=self._attempt_login, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=self.window.destroy, width=10).pack(side=tk.LEFT, padx=5)
        
        # 聚焦密码框（ID已默认填好）
        pw_entry.focus_set()
    
    def _attempt_login(self):
        uid = self.user_id_var.get().strip()
        pwd = self.pw_var.get()
        
        if uid not in self.VALID_USERS:
            messagebox.showerror("错误", "无效的用户ID！", parent=self.window)
            return
        
        user_cfg = self.VALID_USERS[uid]
        # administrator 无密码，system 需验证密码
        if user_cfg["password"] is None or pwd == user_cfg["password"]:
            self.on_success(uid, user_cfg["role"], user_cfg["desc"])
            self.window.destroy()
        else:
            messagebox.showerror("错误", "密码错误！", parent=self.window)
            self.pw_var.set("")