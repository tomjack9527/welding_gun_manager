# welding_gun_manager/views/user_dialog.py
import tkinter as tk
from tkinter import ttk


class UserDialog:
    """用户管理对话框"""
    
    def __init__(self, parent, user_controller, mode='view'):
        self.parent = parent
        self.user_controller = user_controller
        self.mode = mode
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("用户管理" if mode == 'view' else "添加用户")
        self.dialog.geometry("600x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        
        # 居中显示
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
        
        if mode == 'view':
            self.load_users()
        
        self.dialog.wait_window()
    
    def setup_ui(self):
        """设置对话框UI"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        if self.mode == 'view':
            # 用户列表模式
            columns = ("ID", "用户名", "角色", "创建时间")
            self.user_tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=15)
            
            for col in columns:
                self.user_tree.heading(col, text=col)
                self.user_tree.column(col, width=100)
            
            scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.user_tree.yview)
            self.user_tree.configure(yscrollcommand=scrollbar.set)
            
            self.user_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # 按钮框架
            btn_frame = ttk.Frame(self.dialog)
            btn_frame.pack(fill=tk.X, padx=10, pady=10)
            
            ttk.Button(btn_frame, text="关闭", command=self.dialog.destroy).pack(side=tk.RIGHT)
            
        else:
            # 添加用户模式
            form_frame = ttk.Frame(main_frame)
            form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # 用户名
            ttk.Label(form_frame, text="用户名:").grid(row=0, column=0, sticky=tk.W, pady=10)
            self.username_var = tk.StringVar()
            ttk.Entry(form_frame, textvariable=self.username_var, width=30).grid(
                row=0, column=1, sticky=tk.W, pady=10)
            
            # 密码
            ttk.Label(form_frame, text="密码:").grid(row=1, column=0, sticky=tk.W, pady=10)
            self.password_var = tk.StringVar()
            ttk.Entry(form_frame, textvariable=self.password_var, show="*", width=30).grid(
                row=1, column=1, sticky=tk.W, pady=10)
            
            # 确认密码
            ttk.Label(form_frame, text="确认密码:").grid(row=2, column=0, sticky=tk.W, pady=10)
            self.confirm_password_var = tk.StringVar()
            ttk.Entry(form_frame, textvariable=self.confirm_password_var, show="*", width=30).grid(
                row=2, column=1, sticky=tk.W, pady=10)
            
            # 角色
            ttk.Label(form_frame, text="角色:").grid(row=3, column=0, sticky=tk.W, pady=10)
            self.role_var = tk.StringVar(value="user")
            role_combo = ttk.Combobox(form_frame, textvariable=self.role_var, 
                                     values=["user", "admin"], width=28, state="readonly")
            role_combo.grid(row=3, column=1, sticky=tk.W, pady=10)
            
            # 按钮框架
            btn_frame = ttk.Frame(form_frame)
            btn_frame.grid(row=4, column=0, columnspan=2, pady=20)
            
            ttk.Button(btn_frame, text="添加", command=self.add_user).pack(side=tk.LEFT, padx=10)
            ttk.Button(btn_frame, text="取消", command=self.dialog.destroy).pack(side=tk.LEFT)
    
    def load_users(self):
        """加载用户列表"""
        users = self.user_controller.get_all_users()
        for user in users:
            self.user_tree.insert('', 'end', values=(
                user.id,
                user.username,
                "管理员" if user.role == "admin" else "普通用户",
                user.created_at.strftime("%Y-%m-%d %H:%M:%S") if hasattr(user.created_at, 'strftime') else user.created_at
            ))
    
    def add_user(self):
        """添加用户"""
        username = self.username_var.get().strip()
        password = self.password_var.get()
        confirm_password = self.confirm_password_var.get()
        role = self.role_var.get()
        
        if not username:
            tk.messagebox.showwarning("警告", "用户名不能为空")
            return
        
        if not password:
            tk.messagebox.showwarning("警告", "密码不能为空")
            return
        
        if password != confirm_password:
            tk.messagebox.showwarning("警告", "两次输入的密码不一致")
            return
        
        try:
            self.user_controller.add_user({
                'username': username,
                'password': password,
                'role': role
            })
            tk.messagebox.showinfo("成功", "用户添加成功")
            self.dialog.destroy()
        except Exception as e:
            tk.messagebox.showerror("错误", f"添加用户失败: {str(e)}")