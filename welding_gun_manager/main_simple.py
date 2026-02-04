# main.py
import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

# 添加当前目录到路径
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
    print(f"模块导入错误: {e}")
    print("正在创建必要模块...")
    # 这里可以动态创建模块，但为了简化，我们先提示
    messagebox.showerror("错误", "缺少必要模块，请确保所有文件都存在")
    sys.exit(1)

class WeldingGunManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("焊接枪管理系统")
        self.root.geometry("1000x700")
        
        # 初始化数据库
        self.db = Database()
        if not self.db.initialize():
            messagebox.showerror("错误", "数据库初始化失败")
            sys.exit(1)
        
        # 创建控制器
        self.gun_controller = GunController(self.db)
        self.user_controller = UserController(self.db)
        
        # 当前用户
        self.current_user = None
        
        # 运行应用
        self.show_login()
        self.root.mainloop()
    
    def show_login(self):
        """显示登录界面"""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        frame = tk.Frame(self.root, padx=40, pady=40)
        frame.pack(expand=True)
        
        # 标题
        tk.Label(frame, text="焊接枪管理系统", 
                font=("微软雅黑", 24, "bold"), fg="#2c3e50").pack(pady=(0, 20))
        
        tk.Label(frame, text="Welding Gun Management System", 
                font=("Arial", 12), fg="#7f8c8d").pack(pady=(0, 40))
        
        # 登录表单
        form_frame = tk.Frame(frame)
        form_frame.pack()
        
        tk.Label(form_frame, text="用户名:", 
                font=("微软雅黑", 11)).grid(row=0, column=0, sticky=tk.W, pady=10)
        self.username_var = tk.StringVar(value="system")
        tk.Entry(form_frame, textvariable=self.username_var, 
                font=("微软雅黑", 11), width=25).grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(form_frame, text="密码:", 
                font=("微软雅黑", 11)).grid(row=1, column=0, sticky=tk.W, pady=10)
        self.password_var = tk.StringVar(value="manager")
        tk.Entry(form_frame, textvariable=self.password_var, 
                font=("微软雅黑", 11), width=25, show="*").grid(row=1, column=1, padx=10, pady=10)
        
        # 快速登录按钮
        quick_frame = tk.Frame(frame)
        quick_frame.pack(pady=20)
        
        tk.Label(quick_frame, text="快速登录:").pack(side=tk.LEFT, padx=(0, 10))
        
        users = [
            ("system", "manager", "系统管理员"),
            ("administrator", "", "Administrator"),
            ("user", "user123", "普通用户"),
        ]
        
        for username, password, text in users:
            btn = tk.Button(quick_frame, text=text, bg="#3498db", fg="white",
                           command=lambda u=username, p=password: self.quick_login(u, p))
            btn.pack(side=tk.LEFT, padx=5)
        
        # 登录按钮
        tk.Button(frame, text="登录", bg="#2ecc71", fg="white", 
                 font=("微软雅黑", 12, "bold"), padx=30, pady=10,
                 command=self.do_login).pack(pady=30)
        
        # 绑定回车键
        self.root.bind('<Return>', lambda event: self.do_login())
    
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
        
        # 验证登录
        user = self.user_controller.authenticate(username, password)
        if user:
            self.current_user = user
            self.show_main_interface()
        else:
            messagebox.showerror("登录失败", "用户名或密码错误")
    
    def show_main_interface(self):
        """显示主界面"""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        role_name = "管理员" if self.current_user.role == 'admin' else "普通用户"
        self.root.title(f"焊接枪管理系统 - {self.current_user.username} ({role_name})")
        
        # 创建主框架
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧导航栏
        nav_frame = tk.Frame(main_frame, width=180, bg="#f8f9fa", relief=tk.RAISED, bd=1)
        nav_frame.pack(side=tk.LEFT, fill=tk.Y)
        nav_frame.pack_propagate(False)
        
        # 导航标题
        tk.Label(nav_frame, text="导航菜单", font=("微软雅黑", 12, "bold"), 
                bg="#f8f9fa", pady=15).pack(fill=tk.X)
        
        # 导航按钮
        buttons = [
            ("🏠 仪表盘", self.show_dashboard),
            ("🔧 工枪管理", self.show_guns),
            ("📊 统计分析", self.show_statistics),
            ("⚙️ 系统设置", self.show_settings),
            ("❓ 帮助", self.show_help),
            ("🚪 退出", self.root.destroy),
        ]
        
        for text, command in buttons:
            btn = tk.Button(nav_frame, text=text, anchor=tk.W, bg="#f8f9fa", 
                           relief=tk.FLAT, font=("微软雅黑", 11), padx=20, pady=10,
                           command=command)
            btn.pack(fill=tk.X)
            
            # 鼠标悬停效果
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#e9ecef"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#f8f9fa"))
        
        # 内容区域
        self.content_frame = tk.Frame(main_frame, bg="white")
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 显示欢迎信息
        self.show_dashboard()
    
    def show_dashboard(self):
        """显示仪表盘"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # 标题
        tk.Label(self.content_frame, text="系统仪表盘", 
                font=("微软雅黑", 18, "bold"), bg="white").pack(pady=20)
        
        # 获取统计数据
        try:
            stats = self.gun_controller.get_statistics()
            
            # 统计卡片
            cards_frame = tk.Frame(self.content_frame, bg="white", padx=20, pady=10)
            cards_frame.pack(fill=tk.X)
            
            stats_data = [
                ("总工枪数", stats.get('total_guns', 0), "#3498db", "把"),
                ("在用工枪", stats.get('active_guns', 0), "#2ecc71", "把"),
                ("维护中", stats.get('maintenance_guns', 0), "#e74c3c", "把"),
                ("总用户数", 3, "#9b59b6", "人"),  # 固定3个用户
            ]
            
            for i, (title, value, color, unit) in enumerate(stats_data):
                card = tk.Frame(cards_frame, bg=color, relief=tk.RAISED, bd=2)
                card.grid(row=0, column=i, padx=10, ipadx=15, ipady=10)
                
                tk.Label(card, text=title, bg=color, fg="white", 
                        font=("微软雅黑", 11)).pack()
                tk.Label(card, text=f"{value}{unit}", bg=color, fg="white", 
                        font=("微软雅黑", 16, "bold")).pack()
            
            # 最近工枪
            tk.Label(self.content_frame, text="最近工枪", 
                    font=("微软雅黑", 14, "bold"), bg="white").pack(
                    anchor=tk.W, padx=20, pady=(20, 10))
            
            list_frame = tk.Frame(self.content_frame, bg="white", padx=20)
            list_frame.pack(fill=tk.X)
            
            guns = self.gun_controller.get_all_guns()
            if guns:
                for gun in guns[:5]:  # 只显示前5个
                    gun_text = f"{gun.name} - {gun.type or '未分类'} - {gun.status}"
                    tk.Label(list_frame, text=gun_text, bg="white", 
                            anchor=tk.W).pack(fill=tk.X, pady=2)
            else:
                tk.Label(list_frame, text="暂无工枪数据", fg="gray", 
                        bg="white").pack()
            
        except Exception as e:
            tk.Label(self.content_frame, text=f"加载数据失败: {str(e)}", 
                    fg="red", bg="white").pack(pady=50)
    
    def show_guns(self):
        """显示工枪管理"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # 工具栏
        toolbar = tk.Frame(self.content_frame, bg="#f8f9fa", pady=10)
        toolbar.pack(fill=tk.X)
        
        # 刷新按钮
        tk.Button(toolbar, text="刷新", bg="#3498db", fg="white",
                 command=self.load_guns_table).pack(side=tk.LEFT, padx=5)
        
        # 搜索框
        search_frame = tk.Frame(toolbar, bg="#f8f9fa")
        search_frame.pack(side=tk.RIGHT, padx=5)
        
        tk.Label(search_frame, text="搜索:", bg="#f8f9fa").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.search_var, width=25).pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="搜索", bg="#3498db", fg="white",
                 command=self.search_guns).pack(side=tk.LEFT)
        
        # 表格框架
        table_frame = tk.Frame(self.content_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建表格
        columns = ['ID', '名称', '类型', '型号', '状态', '位置']
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 加载数据
        self.load_guns_table()
    
    def load_guns_table(self):
        """加载工枪数据到表格"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            guns = self.gun_controller.get_all_guns()
            for gun in guns:
                self.tree.insert('', 'end', values=(
                    gun.id, gun.name, gun.type or '', gun.model or '', 
                    gun.status, gun.location or ''
                ))
        except Exception as e:
            print(f"加载工枪数据失败: {e}")
            messagebox.showerror("错误", f"加载数据失败: {str(e)}")
    
    def search_guns(self):
        """搜索工枪"""
        search_term = self.search_var.get()
        if not search_term:
            self.load_guns_table()
            return
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            guns = self.gun_controller.search_guns(search_term)
            for gun in guns:
                self.tree.insert('', 'end', values=(
                    gun.id, gun.name, gun.type or '', gun.model or '', 
                    gun.status, gun.location or ''
                ))
        except Exception as e:
            print(f"搜索工枪失败: {e}")
    
    def show_statistics(self):
        """显示统计分析"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        tk.Label(self.content_frame, text="统计分析", 
                font=("微软雅黑", 18, "bold"), bg="white").pack(pady=20)
        
        try:
            stats = self.gun_controller.get_statistics()
            
            # 创建文本显示
            text_widget = tk.Text(self.content_frame, wrap=tk.WORD, height=15, 
                                 width=60, padx=20, pady=20)
            text_widget.pack()
            
            stats_text = f"""
工枪统计信息:
============
总工枪数: {stats.get('total_guns', 0)} 把

状态分布:
--------"""
            
            for status, count in stats.get('status_distribution', {}).items():
                status_zh = {
                    'active': '在用',
                    'maintenance': '维护',
                    'inactive': '闲置',
                    'scrap': '报废'
                }.get(status, status)
                stats_text += f"\n  {status_zh}: {count} 把"
            
            stats_text += "\n\n类型分布:"
            stats_text += "\n--------"
            for gun_type, count in stats.get('type_distribution', {}).items():
                stats_text += f"\n  {gun_type}: {count} 把"
            
            text_widget.insert(tk.END, stats_text)
            text_widget.config(state=tk.DISABLED)
            
        except Exception as e:
            tk.Label(self.content_frame, text=f"加载统计失败: {str(e)}", 
                    fg="red", bg="white").pack(pady=50)
    
    def show_settings(self):
        """显示系统设置"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        tk.Label(self.content_frame, text="系统设置", 
                font=("微软雅黑", 18, "bold"), bg="white").pack(pady=20)
        
        # 简单的设置选项
        settings_frame = tk.Frame(self.content_frame, bg="white", padx=30)
        settings_frame.pack()
        
        tk.Label(settings_frame, text="功能开发中...", 
                font=("微软雅黑", 14), fg="#7f8c8d", bg="white").pack(pady=50)
    
    def show_help(self):
        """显示帮助"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        help_text = """
焊接枪管理系统 - 使用帮助

主要功能:
1. 工枪管理 - 查看和管理所有焊接枪设备
2. 统计分析 - 查看工枪状态和类型分布
3. 系统设置 - 配置系统参数

快速开始:
- 使用快速登录按钮快速进入系统
- 左侧导航菜单选择功能
- 仪表盘查看系统概览
- 工枪管理查看设备详情

登录账号:
- 管理员: system / manager
- Administrator: administrator / (无密码)
- 普通用户: user / user123

技术支持:
如有问题，请联系系统管理员。
"""
        
        text_widget = tk.Text(self.content_frame, wrap=tk.WORD, padx=20, pady=20, height=20)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)

def main():
    """主函数"""
    try:
        app = WeldingGunManager()
    except Exception as e:
        messagebox.showerror("启动错误", f"应用程序启动失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()