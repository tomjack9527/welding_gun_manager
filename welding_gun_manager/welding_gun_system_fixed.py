# welding_gun_system_fixed.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import os
import sys
import datetime

# 先只保留最基本的类，确保程序能启动
class Database:
    def __init__(self, db_path="welding_gun.db"):
        self.db_path = db_path
        self.conn = None
    
    def connect(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def initialize(self):
        try:
            if not os.path.exists(self.db_path):
                self.create_tables()
                self.create_default_data()
            return True
        except Exception as e:
            print(f"数据库初始化失败: {e}")
            return False
    
    def create_tables(self):
        conn = self.connect()
        cursor = conn.cursor()
        
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
        
        cursor.execute('''
        CREATE TABLE guns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT,
            model TEXT,
            serial_number TEXT UNIQUE,
            status TEXT NOT NULL,
            location TEXT,
            last_maintenance TEXT,
            notes TEXT,
            created_at TEXT NOT NULL
        )
        ''')
        conn.commit()
    
    def create_default_data(self):
        conn = self.connect()
        cursor = conn.cursor()
        
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
        
        guns = [
            ('GUN-001', '点焊枪', 'DW-100', 'SN001', 'active', '生产线A', '2024-01-15', '正常使用', current_time),
            ('GUN-002', '弧焊枪', 'HW-200', 'SN002', 'maintenance', '维修车间', '2023-12-20', '需要维护', current_time),
            ('GUN-003', '激光焊枪', 'LW-300', 'SN003', 'active', '实验室', '2024-02-10', '高精度', current_time),
        ]
        
        cursor.executemany('''
        INSERT INTO guns (name, type, model, serial_number, status, location, last_maintenance, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', guns)
        conn.commit()
    
    def fetch_all(self, query, params=()):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def fetch_one(self, query, params=()):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None

class SimpleWeldingGunSystem:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("焊接枪管理系统 - 简化版")
        self.root.geometry("900x600")
        
        # 数据库
        self.db = Database()
        if not self.db.initialize():
            messagebox.showerror("错误", "数据库初始化失败")
            sys.exit(1)
        
        # 当前用户
        self.current_user = None
        
        # 直接显示主界面（跳过登录用于测试）
        self.current_user = {'username': 'system', 'full_name': '系统管理员', 'role': 'admin'}
        self.show_simple_main_interface()
        
        self.root.mainloop()
    
    def show_simple_main_interface(self):
        """显示简化的主界面"""
        # 清空窗口
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # 标题
        tk.Label(self.root, text="焊接枪管理系统", 
                font=("微软雅黑", 20, "bold"), fg="#2c3e50").pack(pady=20)
        
        # 使用Notebook作为标签页
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建各个标签页
        self.create_dashboard_tab(notebook)
        self.create_gun_management_tab(notebook)
        self.create_file_management_tab(notebook)
        self.create_statistics_tab(notebook)
    
    def create_dashboard_tab(self, notebook):
        """创建仪表盘标签页"""
        frame = tk.Frame(notebook)
        notebook.add(frame, text="🏠 仪表盘")
        
        tk.Label(frame, text="系统仪表盘", 
                font=("微软雅黑", 16, "bold")).pack(pady=20)
        
        # 简单显示一些数据
        try:
            total_guns = self.db.fetch_one("SELECT COUNT(*) as count FROM guns")['count']
            tk.Label(frame, text=f"总工枪数: {total_guns} 把",
                    font=("微软雅黑", 14)).pack(pady=10)
            
            # 显示最近的工枪
            guns = self.db.fetch_all("SELECT * FROM guns ORDER BY id DESC LIMIT 5")
            tk.Label(frame, text="最近添加的工枪:", 
                    font=("微软雅黑", 12, "bold")).pack(pady=10)
            
            for gun in guns:
                gun_text = f"{gun['name']} - {gun['type']} - {gun['status']}"
                tk.Label(frame, text=gun_text, 
                        font=("微软雅黑", 10)).pack()
        except Exception as e:
            tk.Label(frame, text=f"加载数据失败: {e}").pack()
    
    def create_gun_management_tab(self, notebook):
        """创建工枪管理标签页"""
        frame = tk.Frame(notebook)
        notebook.add(frame, text="🔧 工枪管理")
        
        # 工具栏
        toolbar = tk.Frame(frame, bg="#ecf0f1", pady=10)
        toolbar.pack(fill=tk.X)
        
        tk.Button(toolbar, text="刷新数据", bg="#3498db", fg="white",
                 command=lambda: self.load_gun_table(tree)).pack(side=tk.LEFT, padx=5)
        
        # 搜索框
        search_frame = tk.Frame(toolbar, bg="#ecf0f1")
        search_frame.pack(side=tk.RIGHT, padx=5)
        
        tk.Label(search_frame, text="搜索:", bg="#ecf0f1").pack(side=tk.LEFT)
        search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=search_var, width=25).pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="搜索", bg="#2ecc71", fg="white",
                 command=lambda: self.search_guns(tree, search_var.get())).pack(side=tk.LEFT)
        
        # 表格
        table_frame = tk.Frame(frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建Treeview
        tree = ttk.Treeview(table_frame, columns=('ID', '名称', '类型', '状态'), 
                           show='headings', height=15)
        
        columns = [('ID', 60), ('名称', 150), ('类型', 120), ('状态', 100)]
        for col, width in columns:
            tree.heading(col, text=col)
            tree.column(col, width=width)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 加载数据
        self.load_gun_table(tree)
    
    def create_file_management_tab(self, notebook):
        """创建文件管理标签页"""
        frame = tk.Frame(notebook)
        notebook.add(frame, text="📁 文件管理")
        
        tk.Label(frame, text="文件管理功能", 
                font=("微软雅黑", 16, "bold")).pack(pady=20)
        
        # 按钮框架
        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="上传文件", width=15,
                 command=self.upload_file).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="下载文件", width=15,
                 command=self.download_file).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="刷新列表", width=15,
                 command=self.refresh_file_list).pack(side=tk.LEFT, padx=10)
        
        # 文件列表
        list_frame = tk.Frame(frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(list_frame, text="已上传的文件:").pack(anchor=tk.W)
        
        # 列表框
        file_listbox = tk.Listbox(list_frame, height=10)
        file_listbox.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 添加一些示例文件
        files = ["设备清单.xlsx", "操作手册.pdf", "焊接参数.csv"]
        for file in files:
            file_listbox.insert(tk.END, file)
    
    def create_statistics_tab(self, notebook):
        """创建统计分析标签页"""
        frame = tk.Frame(notebook)
        notebook.add(frame, text="📊 统计分析")
        
        tk.Label(frame, text="统计分析", 
                font=("微软雅黑", 16, "bold")).pack(pady=20)
        
        # 获取统计数据
        try:
            total = self.db.fetch_one("SELECT COUNT(*) as count FROM guns")['count']
            active = self.db.fetch_one("SELECT COUNT(*) as count FROM guns WHERE status='active'")['count']
            maintenance = self.db.fetch_one("SELECT COUNT(*) as count FROM guns WHERE status='maintenance'")['count']
            
            stats_text = f"""
总工枪数: {total} 把
在用设备: {active} 把 ({active/max(total,1)*100:.1f}%)
维护中: {maintenance} 把 ({maintenance/max(total,1)*100:.1f}%)
"""
            
            text_widget = tk.Text(frame, wrap=tk.WORD, height=10, width=50,
                                 font=("微软雅黑", 11))
            text_widget.pack(pady=20, padx=20)
            text_widget.insert(tk.END, stats_text)
            text_widget.config(state=tk.DISABLED)
            
        except Exception as e:
            tk.Label(frame, text=f"获取统计数据失败: {e}").pack()
    
    def load_gun_table(self, tree):
        """加载工枪数据到表格"""
        for item in tree.get_children():
            tree.delete(item)
        
        try:
            guns = self.db.fetch_all("SELECT * FROM guns ORDER BY name")
            for gun in guns:
                tree.insert('', 'end', values=(
                    gun['id'], 
                    gun['name'], 
                    gun['type'] or '', 
                    gun['status']
                ))
        except Exception as e:
            print(f"加载数据失败: {e}")
    
    def search_guns(self, tree, search_term):
        """搜索工枪"""
        if not search_term:
            self.load_gun_table(tree)
            return
        
        for item in tree.get_children():
            tree.delete(item)
        
        try:
            query = """
            SELECT * FROM guns 
            WHERE name LIKE ? OR type LIKE ? OR status LIKE ?
            ORDER BY name
            """
            param = f"%{search_term}%"
            guns = self.db.fetch_all(query, (param, param, param))
            
            for gun in guns:
                tree.insert('', 'end', values=(
                    gun['id'], 
                    gun['name'], 
                    gun['type'] or '', 
                    gun['status']
                ))
        except Exception as e:
            print(f"搜索失败: {e}")
    
    def upload_file(self):
        """上传文件"""
        file_path = filedialog.askopenfilename(
            title="选择要上传的文件",
            filetypes=[("所有文件", "*.*"), ("文本文件", "*.txt"), ("Excel文件", "*.xlsx")]
        )
        
        if file_path:
            filename = os.path.basename(file_path)
            messagebox.showinfo("成功", f"已选择文件: {filename}")
    
    def download_file(self):
        """下载文件"""
        messagebox.showinfo("下载", "下载文件功能")
    
    def refresh_file_list(self):
        """刷新文件列表"""
        messagebox.showinfo("刷新", "刷新文件列表")

def main():
    """主函数"""
    try:
        app = SimpleWeldingGunSystem()
    except Exception as e:
        messagebox.showerror("启动错误", f"应用程序启动失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()