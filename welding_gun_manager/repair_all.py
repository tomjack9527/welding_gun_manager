# repair_all.py
import os
import sys
import subprocess

def repair_project():
    print("🔧 焊接枪管理系统修复工具")
    print("=" * 50)
    
    # 1. 修复数据库
    print("\n1️⃣ 修复数据库...")
    fix_db_code = '''
import sqlite3
import datetime

def fix_database():
    conn = sqlite3.connect("welding_gun.db")
    cursor = conn.cursor()
    
    # 检查表结构
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'full_name' not in columns:
        print("添加full_name列...")
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN full_name TEXT")
            print("✅ 添加成功")
            
            # 更新现有用户的full_name
            cursor.execute("UPDATE users SET full_name = username WHERE full_name IS NULL")
            print("✅ 更新用户数据")
        except:
            print("创建新表...")
            cursor.execute("DROP TABLE users")
            cursor.execute('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT,
                    role TEXT NOT NULL,
                    full_name TEXT,
                    email TEXT,
                    created_at TEXT NOT NULL
                )
            ''')
            
            # 重新插入默认用户
            current_time = datetime.datetime.now().isoformat()
            users = [
                ('system', 'manager', 'admin', '系统管理员', 'admin@welding.com', current_time),
                ('administrator', None, 'admin', 'Administrator', '', current_time),
                ('user', 'user123', 'user', '普通用户', 'user@welding.com', current_time)
            ]
            
            cursor.executemany('''
                INSERT INTO users (username, password, role, full_name, email, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', users)
            print("✅ 重新创建用户表")
    
    conn.commit()
    conn.close()
    print("✅ 数据库修复完成")

fix_database()
'''
    
    with open("temp_fix_db.py", "w") as f:
        f.write(fix_db_code)
    
    subprocess.call([sys.executable, "temp_fix_db.py"])
    os.remove("temp_fix_db.py")
    
    # 2. 更新user_controller.py
    print("\n2️⃣ 更新用户控制器...")
    user_controller_code = '''from models.database import Database
from models.entities import User

class UserController:
    def __init__(self, db=None):
        self.db = db or Database()
    
    def authenticate(self, username, password):
        """用户认证"""
        if username == "administrator":
            row = self.db.fetch_one(
                "SELECT * FROM users WHERE username = ? AND password IS NULL",
                (username,)
            )
        else:
            row = self.db.fetch_one(
                "SELECT * FROM users WHERE username = ? AND password = ?",
                (username, password)
            )
        
        if row:
            # 安全获取full_name
            full_name = row.get('full_name') or row['username']
            
            return User(
                id=row['id'],
                username=row['username'],
                password=row['password'],
                role=row['role'],
                full_name=full_name,
                email=row.get('email', ''),
                created_at=row['created_at']
            )
        return None
    
    def get_user_by_username(self, username):
        row = self.db.fetch_one(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )
        if row:
            full_name = row.get('full_name') or row['username']
            return User(
                id=row['id'],
                username=row['username'],
                password=row['password'],
                role=row['role'],
                full_name=full_name,
                email=row.get('email', ''),
                created_at=row['created_at']
            )
        return None
    
    def get_all_users(self):
        rows = self.db.fetch_all("SELECT * FROM users ORDER BY username")
        users = []
        for row in rows:
            full_name = row.get('full_name') or row['username']
            users.append(User(
                id=row['id'],
                username=row['username'],
                password=row['password'],
                role=row['role'],
                full_name=full_name,
                email=row.get('email', ''),
                created_at=row['created_at']
            ))
        return users
'''
    
    with open("controllers/user_controller.py", "w", encoding="utf-8") as f:
        f.write(user_controller_code)
    print("✅ 用户控制器更新完成")
    
    # 3. 创建简化的主程序
    print("\n3️⃣ 创建简化主程序...")
    main_simple_code = '''import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

# 添加路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 导入本地模块
try:
    from models.database import Database
    from models.entities import User, WeldingGun
    from controllers.gun_controller import GunController
    from controllers.user_controller import UserController
except ImportError as e:
    print(f"模块错误: {e}")
    messagebox.showerror("错误", f"模块加载失败: {e}")
    sys.exit(1)

class WeldingGunApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("焊接枪管理系统")
        self.root.geometry("900x600")
        
        # 设置样式
        self.setup_style()
        
        # 数据库
        self.db = Database()
        if not self.db.initialize():
            messagebox.showerror("错误", "数据库初始化失败")
            sys.exit(1)
        
        # 控制器
        self.gun_ctrl = GunController(self.db)
        self.user_ctrl = UserController(self.db)
        
        self.current_user = None
        self.show_login()
        self.root.mainloop()
    
    def setup_style(self):
        """设置样式"""
        style = ttk.Style()
        style.theme_use('clam')
    
    def show_login(self):
        """显示登录界面"""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        frame = tk.Frame(self.root, bg="#f0f0f0", padx=40, pady=40)
        frame.pack(expand=True, fill=tk.BOTH)
        
        # 标题
        title = tk.Label(frame, text="焊接枪管理系统", 
                        font=("微软雅黑", 24, "bold"), bg="#f0f0f0", fg="#333")
        title.pack(pady=(0, 20))
        
        subtitle = tk.Label(frame, text="Welding Gun Management System", 
                           font=("Arial", 12), bg="#f0f0f0", fg="#666")
        subtitle.pack(pady=(0, 40))
        
        # 登录表单
        form_frame = tk.Frame(frame, bg="#f0f0f0")
        form_frame.pack()
        
        tk.Label(form_frame, text="用户名:", font=("微软雅黑", 11), 
                bg="#f0f0f0").grid(row=0, column=0, sticky=tk.W, pady=10)
        self.username_var = tk.StringVar(value="system")
        tk.Entry(form_frame, textvariable=self.username_var, 
                font=("微软雅黑", 11), width=25).grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(form_frame, text="密码:", font=("微软雅黑", 11), 
                bg="#f0f0f0").grid(row=1, column=0, sticky=tk.W, pady=10)
        self.password_var = tk.StringVar(value="manager")
        tk.Entry(form_frame, textvariable=self.password_var, 
                font=("微软雅黑", 11), width=25, show="*").grid(row=1, column=1, padx=10, pady=10)
        
        # 快速登录
        quick_frame = tk.Frame(frame, bg="#f0f0f0")
        quick_frame.pack(pady=20)
        
        tk.Label(quick_frame, text="快速登录:", bg="#f0f0f0").pack(side=tk.LEFT, padx=(0, 10))
        
        users = [
            ("system", "manager", "👑 系统管理员"),
            ("administrator", "", "👨‍💼 Administrator"),
            ("user", "user123", "👤 普通用户"),
        ]
        
        for user in users:
            btn = tk.Button(quick_frame, text=user[2], bg="#3498db", fg="white",
                          command=lambda u=user[0], p=user[1]: self.quick_login(u, p))
            btn.pack(side=tk.LEFT, padx=5)
        
        # 登录按钮
        tk.Button(frame, text="登录", bg="#2ecc71", fg="white", 
                 font=("微软雅黑", 12, "bold"), padx=40, pady=8,
                 command=self.do_login).pack(pady=30)
        
        self.root.bind('<Return>', lambda e: self.do_login())
    
    def quick_login(self, username, password):
        self.username_var.set(username)
        self.password_var.set(password)
        self.do_login()
    
    def do_login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        if not username:
            messagebox.showwarning("警告", "请输入用户名")
            return
        
        user = self.user_ctrl.authenticate(username, password)
        if user:
            self.current_user = user
            self.show_main()
        else:
            messagebox.showerror("登录失败", "用户名或密码错误")
    
    def show_main(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # 导航栏
        nav_frame = tk.Frame(self.root, bg="#2c3e50", width=180)
        nav_frame.pack(side=tk.LEFT, fill=tk.Y)
        nav_frame.pack_propagate(False)
        
        tk.Label(nav_frame, text="导航菜单", font=("微软雅黑", 12, "bold"), 
                bg="#2c3e50", fg="white", pady=15).pack(fill=tk.X)
        
        buttons = [
            ("📊 仪表盘", self.show_dashboard),
            ("🔧 工枪管理", self.show_guns),
            ("📈 统计分析", self.show_stats),
            ("⚙️ 设置", self.show_settings),
            ("❓ 帮助", self.show_help),
            ("🚪 退出", self.root.quit),
        ]
        
        for text, cmd in buttons:
            btn = tk.Button(nav_frame, text=text, anchor=tk.W, bg="#34495e", 
                          fg="white", relief=tk.FLAT, font=("微软雅黑", 11), 
                          padx=20, pady=10, command=cmd)
            btn.pack(fill=tk.X, pady=2)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#4a6fa5"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#34495e"))
        
        # 内容区域
        self.content = tk.Frame(self.root, bg="white")
        self.content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 顶部信息栏
        info_frame = tk.Frame(self.content, bg="#ecf0f1", height=50)
        info_frame.pack(fill=tk.X)
        info_frame.pack_propagate(False)
        
        role = "管理员" if self.current_user.role == 'admin' else "用户"
        tk.Label(info_frame, text=f"欢迎, {self.current_user.full_name} ({role})", 
                font=("微软雅黑", 12), bg="#ecf0f1").pack(side=tk.LEFT, padx=20)
        
        self.show_dashboard()
    
    def show_dashboard(self):
        for widget in self.content.winfo_children():
            widget.destroy()
        
        tk.Label(self.content, text="系统仪表盘", font=("微软雅黑", 18, "bold"), 
                bg="white").pack(pady=20)
        
        # 显示统计信息
        try:
            stats = self.gun_ctrl.get_statistics()
            
            stats_frame = tk.Frame(self.content, bg="white", padx=20, pady=10)
            stats_frame.pack()
            
            stat_cards = [
                ("总工枪数", stats.get('total_guns', 0), "#3498db"),
                ("在用工枪", stats.get('active_guns', 0), "#2ecc71"),
                ("维护中", stats.get('maintenance_guns', 0), "#e74c3c"),
                ("闲置", stats.get('inactive_guns', 0), "#f39c12"),
            ]
            
            for i, (title, value, color) in enumerate(stat_cards):
                card = tk.Frame(stats_frame, bg=color, relief=tk.RAISED, bd=2)
                card.grid(row=0, column=i, padx=10, ipadx=20, ipady=15)
                
                tk.Label(card, text=title, bg=color, fg="white").pack()
                tk.Label(card, text=str(value), bg=color, fg="white", 
                        font=("微软雅黑", 18, "bold")).pack()
            
        except Exception as e:
            tk.Label(self.content, text=f"加载数据失败: {str(e)}", 
                    fg="red", bg="white").pack(pady=50)
    
    def show_guns(self):
        for widget in self.content.winfo_children():
            widget.destroy()
        
        # 这里可以添加工枪管理界面
        tk.Label(self.content, text="工枪管理", font=("微软雅黑", 18, "bold"), 
                bg="white").pack(pady=50)
        tk.Label(self.content, text="功能开发中...", fg="#7f8c8d", 
                bg="white").pack()
    
    def show_stats(self):
        for widget in self.content.winfo_children():
            widget.destroy()
        
        tk.Label(self.content, text="统计分析", font=("微软雅黑", 18, "bold"), 
                bg="white").pack(pady=50)
        tk.Label(self.content, text="功能开发中...", fg="#7f8c8d", 
                bg="white").pack()
    
    def show_settings(self):
        for widget in self.content.winfo_children():
            widget.destroy()
        
        tk.Label(self.content, text="系统设置", font=("微软雅黑", 18, "bold"), 
                bg="white").pack(pady=50)
        tk.Label(self.content, text="功能开发中...", fg="#7f8c8d", 
                bg="white").pack()
    
    def show_help(self):
        for widget in self.content.winfo_children():
            widget.destroy()
        
        help_text = """焊接枪管理系统 - 帮助

主要功能:
1. 仪表盘 - 查看系统概览
2. 工枪管理 - 管理焊接设备
3. 统计分析 - 查看数据报告

登录账号:
- 管理员: system / manager
- Administrator: administrator (无密码)
- 普通用户: user / user123

技术支持:
如有问题请联系管理员。"""
        
        text = tk.Text(self.content, wrap=tk.WORD, height=15, width=50, 
                      padx=20, pady=20)
        text.pack()
        text.insert(tk.END, help_text)
        text.config(state=tk.DISABLED)

if __name__ == "__main__":
    WeldingGunApp()'''
    
    with open("main_fixed.py", "w", encoding="utf-8") as f:
        f.write(main_simple_code)
    print("✅ 主程序创建完成")
    
    print("\n" + "=" * 50)
    print("🎉 修复完成！")
    print("=" * 50)
    print("\n现在可以运行以下命令：")
    print("  python main_fixed.py")
    print("\n或者如果你已经修复了原来的main.py：")
    print("  python main.py")

if __name__ == "__main__":
    repair_project()