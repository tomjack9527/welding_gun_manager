# welding_gun_manager/views/main_window_fixed.py
import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
from datetime import datetime

# 添加所有可能的路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

# 将项目根目录添加到路径
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 尝试导入必要的模块
try:
    from controllers.gun_controller import GunController
    from controllers.file_controller import FileController
    from controllers.user_controller import UserController
    from services.file_service import FileService
    from models.database import Database
    print("✓ 核心模块导入成功")
except ImportError as e:
    print(f"✗ 模块导入失败: {e}")
    
    # 尝试直接导入
    try:
        # 添加 controllers 目录
        controllers_path = os.path.join(project_root, 'controllers')
        if controllers_path not in sys.path:
            sys.path.insert(0, controllers_path)
        
        # 添加 services 目录
        services_path = os.path.join(project_root, 'services')
        if services_path not in sys.path:
            sys.path.insert(0, services_path)
        
        # 添加 models 目录
        models_path = os.path.join(project_root, 'models')
        if models_path not in sys.path:
            sys.path.insert(0, models_path)
        
        # 再次尝试导入
        from gun_controller import GunController
        from file_controller import FileController
        from user_controller import UserController
        from file_service import FileService
        from database import Database
        print("✓ 直接导入成功")
    except ImportError as e2:
        print(f"✗ 直接导入失败: {e2}")
        raise


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("焊接枪管理系统 - 正在启动...")
        self.root.geometry("1000x700")
        
        # 显示启动信息
        self.setup_loading_screen()
        
        # 延迟初始化（避免界面卡顿）
        self.root.after(100, self.initialize)
    
    def setup_loading_screen(self):
        """设置加载屏幕"""
        self.loading_frame = ttk.Frame(self.root)
        self.loading_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(self.loading_frame, text="焊接枪管理系统", 
                 font=("Arial", 18, "bold")).pack(pady=50)
        
        ttk.Label(self.loading_frame, text="正在初始化系统...", 
                 font=("Arial", 12)).pack(pady=20)
        
        self.loading_label = ttk.Label(self.loading_frame, text="")
        self.loading_label.pack(pady=10)
        
        # 进度条
        self.progress = ttk.Progressbar(self.loading_frame, mode='indeterminate', length=300)
        self.progress.pack(pady=20)
        self.progress.start()
    
    def update_loading_text(self, text):
        """更新加载文本"""
        self.loading_label.config(text=text)
        self.root.update()
    
    def initialize(self):
        """初始化系统"""
        try:
            self.update_loading_text("连接数据库...")
            
            # 初始化数据库
            self.db = Database()
            
            self.update_loading_text("初始化服务层...")
            
            # 初始化服务层
            self.file_service = FileService()
            
            self.update_loading_text("初始化控制器...")
            
            # 初始化控制器
            self.gun_controller = GunController(self.db)
            self.file_controller = FileController(self.file_service)
            self.user_controller = UserController(self.db)
            
            self.update_loading_text("用户登录...")
            
            # 用户登录
            if not self.user_login():
                self.root.destroy()
                return
            
            self.update_loading_text("设置用户界面...")
            
            # 移除加载界面
            self.loading_frame.destroy()
            
            # 设置主界面
            self.setup_main_ui()
            
            self.update_loading_text("加载初始数据...")
            
            # 加载初始数据
            self.load_initial_data()
            
            # 绑定关闭事件
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            self.progress.stop()
            
        except Exception as e:
            messagebox.showerror("初始化失败", f"系统初始化失败: {str(e)}")
            import traceback
            traceback.print_exc()
            self.root.destroy()
    
    def user_login(self):
        """用户登录"""
        try:
            # 导入登录对话框
            try:
                from views.login_dialog import LoginDialog
            except ImportError:
                # 如果导入失败，尝试其他方式
                login_dialog_path = os.path.join(os.path.dirname(__file__), 'login_dialog.py')
                if os.path.exists(login_dialog_path):
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("login_dialog", login_dialog_path)
                    login_dialog_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(login_dialog_module)
                    LoginDialog = login_dialog_module.LoginDialog
                else:
                    # 使用简单登录
                    return self.simple_login()
            
            dialog = LoginDialog(self.root)
            
            if not dialog.result:
                return False
            
            username = dialog.result['username']
            password = dialog.result['password']
            
            # 验证用户
            user = self.user_controller.login(username, password)
            if not user:
                messagebox.showerror("登录失败", "用户名或密码错误")
                return False
            
            return True
            
        except Exception as e:
            print(f"登录过程出错: {str(e)}")
            return self.simple_login()
    
    def simple_login(self):
        """简单的登录（备用）"""
        from tkinter import simpledialog
        
        username = simpledialog.askstring("登录", "请输入用户名:", 
                                         parent=self.root, initialvalue="system")
        if not username:
            return False
        
        password = None
        if username != "administrator":
            password = simpledialog.askstring("登录", "请输入密码:", 
                                            parent=self.root, show="*", initialvalue="manager")
        
        user = self.user_controller.login(username, password)
        if not user:
            messagebox.showerror("登录失败", "用户名或密码错误")
            return False
        
        return True
    
    def setup_main_ui(self):
        """设置主界面"""
        # 获取当前用户
        current_user = self.user_controller.get_current_user()
        is_admin = self.user_controller.is_admin()
        
        # 更新窗口标题
        role_text = "管理员" if is_admin else "普通用户"
        self.root.title(f"焊接枪管理系统 - {current_user.username} ({role_text})")
        
        # 创建菜单栏
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="退出", command=self.on_closing)
        
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 欢迎信息
        welcome_text = f"欢迎使用焊接枪管理系统，{current_user.username}!"
        ttk.Label(main_frame, text=welcome_text, 
                 font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # 用户信息
        info_frame = ttk.LabelFrame(main_frame, text="用户信息", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(info_frame, text=f"用户名: {current_user.username}").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Label(info_frame, text=f"角色: {role_text}").grid(row=0, column=1, sticky=tk.W, pady=5, padx=20)
        
        if is_admin:
            ttk.Label(info_frame, text="权限: 完全管理权限", 
                     font=("Arial", 10, "bold"), foreground="green").grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        else:
            ttk.Label(info_frame, text="权限: 只读权限", 
                     font=("Arial", 10), foreground="blue").grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # 功能区域
        func_frame = ttk.LabelFrame(main_frame, text="系统功能", padding="20")
        func_frame.pack(fill=tk.BOTH, expand=True)
        
        # 根据权限显示不同功能
        if is_admin:
            ttk.Button(func_frame, text="工枪管理", 
                      command=self.show_gun_management, width=20).pack(pady=10)
            ttk.Button(func_frame, text="数据导入", 
                      command=self.import_data, width=20).pack(pady=10)
            ttk.Button(func_frame, text="数据导出", 
                      command=self.export_data, width=20).pack(pady=10)
            ttk.Button(func_frame, text="备份数据库", 
                      command=self.backup_database, width=20).pack(pady=10)
        else:
            ttk.Label(func_frame, text="您当前是普通用户，只能查看数据", 
                     font=("Arial", 12)).pack(pady=20)
            ttk.Button(func_frame, text="查看工枪列表", 
                      command=self.show_gun_management, width=20).pack(pady=10)
        
        # 状态栏
        self.statusbar = ttk.Frame(self.root, relief=tk.SUNKEN, borderwidth=1)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(self.statusbar, text="就绪")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        self.time_label = ttk.Label(self.statusbar, text="")
        self.time_label.pack(side=tk.RIGHT, padx=5)
        
        # 更新时间显示
        self.update_time()
    
    def update_time(self):
        """更新时间显示"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=now)
        self.root.after(1000, self.update_time)
    
    def load_initial_data(self):
        """加载初始数据"""
        self.status_label.config(text="系统初始化完成")
    
    def show_gun_management(self):
        """显示工枪管理"""
        messagebox.showinfo("提示", "工枪管理功能开发中...")
    
    def import_data(self):
        """导入数据"""
        messagebox.showinfo("提示", "数据导入功能开发中...")
    
    def export_data(self):
        """导出数据"""
        messagebox.showinfo("提示", "数据导出功能开发中...")
    
    def backup_database(self):
        """备份数据库"""
        messagebox.showinfo("提示", "数据库备份功能开发中...")
    
    def on_closing(self):
        """关闭窗口事件"""
        if messagebox.askokcancel("退出", "确定要退出系统吗？"):
            try:
                self.db.close()
            except:
                pass
            self.root.destroy()


def main():
    """独立运行的主函数"""
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()