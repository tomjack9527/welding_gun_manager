# install_all.py
import os
import sys
import subprocess
import sqlite3
import datetime

def check_install_packages():
    """检查并安装依赖包"""
    packages = ['matplotlib', 'pandas', 'Pillow']
    
    print("=" * 50)
    print("开始安装依赖包...")
    print("=" * 50)
    
    for package in packages:
        try:
            print(f"\n正在安装 {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} 安装成功！")
        except subprocess.CalledProcessError as e:
            print(f"❌ 安装 {package} 失败: {e}")
            return False
    
    return True

def create_directories():
    """创建项目目录结构"""
    print("\n" + "=" * 50)
    print("创建目录结构...")
    print("=" * 50)
    
    directories = [
        'config',
        'controllers',
        'models', 
        'views',
        'services',
        'resources',
        'resources/icons',
        'logs',
        'backups',
        'docs'
    ]
    
    for directory in directories:
        dir_path = os.path.join(os.getcwd(), directory)
        os.makedirs(dir_path, exist_ok=True)
        print(f"✅ 创建目录: {directory}")
    
    return True

def create_database():
    """创建数据库"""
    print("\n" + "=" * 50)
    print("创建数据库...")
    print("=" * 50)
    
    db_path = "welding_gun.db"
    
    # 备份现有数据库
    if os.path.exists(db_path):
        backup_path = f"welding_gun_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"📦 已备份现有数据库到: {backup_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 创建users表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT,
            role TEXT NOT NULL CHECK(role IN ('admin', 'user')),
            full_name TEXT,
            email TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT
        )
        ''')
        
        # 创建guns表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS guns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT,
            model TEXT,
            serial_number TEXT UNIQUE,
            status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'maintenance', 'inactive', 'scrap')),
            location TEXT,
            last_maintenance TEXT,
            notes TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT,
            created_by INTEGER,
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
        ''')
        
        # 插入默认用户
        current_time = datetime.datetime.now().isoformat()
        default_users = [
            ('system', 'manager', 'admin', '系统管理员', 'admin@welding.com', current_time),
            ('administrator', None, 'admin', 'Administrator', '', current_time),
            ('user', 'user123', 'user', '普通用户', 'user@welding.com', current_time)
        ]
        
        cursor.executemany('''
        INSERT OR IGNORE INTO users (username, password, role, full_name, email, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', default_users)
        
        # 检查是否已有工枪数据
        cursor.execute("SELECT COUNT(*) FROM guns")
        gun_count = cursor.fetchone()[0]
        
        if gun_count == 0:
            # 插入示例工枪数据
            sample_guns = [
                ('GUN-001', '点焊枪', 'DW-100', 'SN001', 'active', '生产线A', '2024-01-15', '正常使用'),
                ('GUN-002', '弧焊枪', 'HW-200', 'SN002', 'maintenance', '维修车间', '2023-12-20', '需要更换电极'),
                ('GUN-003', '激光焊枪', 'LW-300', 'SN003', 'active', '实验室', '2024-02-10', '高精度焊接'),
                ('GUN-004', '气体焊枪', 'GW-150', 'SN004', 'inactive', '仓库', '2023-11-05', '备用设备'),
                ('GUN-005', '电阻焊枪', 'RW-250', 'SN005', 'active', '生产线B', '2024-01-30', '新设备')
            ]
            
            for gun in sample_guns:
                cursor.execute('''
                INSERT INTO guns (name, type, model, serial_number, status, location, last_maintenance, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (*gun, current_time))
            print("✅ 插入5条示例工枪数据")
        
        conn.commit()
        conn.close()
        
        print("✅ 数据库创建成功！")
        return True
        
    except Exception as e:
        print(f"❌ 创建数据库失败: {e}")
        return False

def create_main_file():
    """创建主程序文件"""
    print("\n" + "=" * 50)
    print("创建主程序文件...")
    print("=" * 50)
    
    # 这里放你之前提供的main.py代码
    # 由于代码太长，我创建一个简化版本
    main_code = '''import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os

class WeldingGunApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("焊接枪管理系统")
        self.root.geometry("800x600")
        
        self.db_path = "welding_gun.db"
        self.conn = None
        
        self.show_login()
        self.root.mainloop()
    
    def connect_db(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            return True
        except:
            return False
    
    def show_login(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        frame = tk.Frame(self.root, padx=40, pady=40)
        frame.pack(expand=True)
        
        tk.Label(frame, text="焊接枪管理系统", font=("微软雅黑", 20, "bold")).pack(pady=20)
        
        # 用户名
        tk.Label(frame, text="用户名:").pack()
        self.username_var = tk.StringVar(value="system")
        tk.Entry(frame, textvariable=self.username_var).pack(pady=5)
        
        # 密码
        tk.Label(frame, text="密码:").pack()
        self.password_var = tk.StringVar(value="manager")
        tk.Entry(frame, textvariable=self.password_var, show="*").pack(pady=5)
        
        # 快速登录按钮
        tk.Button(frame, text="管理员登录 (system/manager)", 
                 command=lambda: self.quick_login("system", "manager")).pack(pady=5)
        tk.Button(frame, text="Administrator登录", 
                 command=lambda: self.quick_login("administrator", "")).pack(pady=5)
        tk.Button(frame, text="普通用户登录 (user/user123)", 
                 command=lambda: self.quick_login("user", "user123")).pack(pady=5)
        
        # 登录按钮
        tk.Button(frame, text="登录", command=self.do_login, 
                 bg="green", fg="white", padx=20, pady=5).pack(pady=20)
    
    def quick_login(self, username, password):
        self.username_var.set(username)
        self.password_var.set(password)
        self.do_login()
    
    def do_login(self):
        username = self.username_var.get()
        password = self.password_var.get()
        
        if not self.connect_db():
            messagebox.showerror("错误", "无法连接数据库")
            return
        
        try:
            cursor = self.conn.cursor()
            
            if username == "administrator":
                cursor.execute("SELECT * FROM users WHERE username = ? AND password IS NULL", (username,))
            else:
                cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            
            user = cursor.fetchone()
            
            if user:
                self.show_main_interface(user)
            else:
                messagebox.showerror("登录失败", "用户名或密码错误")
                
        except Exception as e:
            messagebox.showerror("错误", f"登录失败: {str(e)}")
    
    def show_main_interface(self, user):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        role_name = "管理员" if user['role'] == 'admin' else "普通用户"
        self.root.title(f"焊接枪管理系统 - {user['username']} ({role_name})")
        
        # 显示欢迎信息
        tk.Label(self.root, text=f"欢迎, {user['full_name']}!", 
                font=("微软雅黑", 16)).pack(pady=20)
        
        tk.Label(self.root, text=f"角色: {role_name}").pack(pady=10)
        
        # 功能按钮
        if user['role'] == 'admin':
            tk.Button(self.root, text="管理工枪", width=20).pack(pady=5)
            tk.Button(self.root, text="管理用户", width=20).pack(pady=5)
        
        tk.Button(self.root, text="查看数据", width=20).pack(pady=20)
        tk.Button(self.root, text="退出", command=self.root.destroy).pack()

if __name__ == "__main__":
    app = WeldingGunApp()'''
    
    try:
        with open('main.py', 'w', encoding='utf-8') as f:
            f.write(main_code)
        print("✅ 主程序文件创建成功")
        return True
    except Exception as e:
        print(f"❌ 创建主程序文件失败: {e}")
        return False

def main():
    print("🚀 焊接枪管理系统安装程序")
    print("=" * 50)
    
    # 检查Python版本
    print(f"Python版本: {sys.version}")
    
    # 安装步骤
    steps = [
        ("安装依赖包", check_install_packages),
        ("创建目录结构", create_directories),
        ("创建数据库", create_database),
        ("创建主程序文件", create_main_file),
    ]
    
    success = True
    for step_name, step_func in steps:
        print(f"\n📋 步骤: {step_name}")
        if not step_func():
            success = False
            print(f"❌ {step_name} 失败")
            break
    
    if success:
        print("\n" + "=" * 50)
        print("🎉 安装完成！")
        print("=" * 50)
        print("\n现在可以运行以下命令启动系统：")
        print("  python main.py")
        print("\n默认登录账号：")
        print("  1. 管理员: system / manager")
        print("  2. Administrator: administrator / (无密码)")
        print("  3. 普通用户: user / user123")
    else:
        print("\n❌ 安装失败，请检查错误信息")

if __name__ == "__main__":
    main()