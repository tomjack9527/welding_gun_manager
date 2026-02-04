# welding_gun_manager/main_fast.py
import tkinter as tk
from tkinter import ttk 
import os
import sys
import threading
import time
import shutil
import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from typing import List

app = FastAPI()

# 添加上传目录
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """上传文件"""
    try:
        # 生成唯一文件名，避免冲突
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"
        
        file_location = os.path.join(UPLOAD_DIR, unique_filename)
        
        # 保存文件
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return {
            "message": "文件上传成功",
            "original_filename": file.filename,
            "saved_filename": unique_filename,
            "file_path": file_location
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """下载文件"""
    file_location = os.path.join(UPLOAD_DIR, filename)
    
    if not os.path.exists(file_location):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(
        path=file_location,
        filename=filename,
        media_type='application/octet-stream'
    )

@app.get("/api/files")
async def list_files():
    """获取文件列表"""
    if not os.path.exists(UPLOAD_DIR):
        return {"files": []}
    
    files = os.listdir(UPLOAD_DIR)
    return {"files": files}

class FastApp:
    """快速启动的应用程序"""
    
    def __init__(self):
        self.root = None
        self.initialized = False
        
    def start(self):
        """启动应用程序"""
        print("快速启动焊接枪管理系统...")
        
        # 创建根窗口但不立即显示
        self.root = tk.Tk()
        self.root.withdraw()  # 先隐藏
        
        # 设置标题
        self.root.title("焊接枪管理系统")
        
        # 在后台线程中初始化
        print("在后台初始化系统...")
        init_thread = threading.Thread(target=self.initialize_background)
        init_thread.daemon = True
        init_thread.start()
        
        # 显示加载窗口
        self.show_loading_window()
        
        # 启动主循环
        self.root.mainloop()
    
    def show_loading_window(self):
        """显示加载窗口"""
        self.loading_window = tk.Toplevel(self.root)
        self.loading_window.title("正在启动...")
        self.loading_window.geometry("300x150")
        
        # 居中显示
        self.loading_window.update_idletasks()
        x = (self.loading_window.winfo_screenwidth() - 300) // 2
        y = (self.loading_window.winfo_screenheight() - 150) // 2
        self.loading_window.geometry(f"+{x}+{y}")
        
        # 禁止调整大小和关闭
        self.loading_window.resizable(False, False)
        self.loading_window.protocol("WM_DELETE_WINDOW", lambda: None)
        
        # 加载内容
        tk.Label(self.loading_window, text="焊接枪管理系统", 
                font=("Arial", 14, "bold")).pack(pady=20)
        
        tk.Label(self.loading_window, text="正在初始化，请稍候...").pack()
        
        # 进度条
        self.progress = ttk.Progressbar(self.loading_window, mode='indeterminate', length=200)
        self.progress.pack(pady=20)
        self.progress.start()
        
        # 检查初始化的定时器
        self.check_initialization()
    
    def check_initialization(self):
        """检查初始化是否完成"""
        if self.initialized:
            # 初始化完成，关闭加载窗口，显示主窗口
            self.progress.stop()
            self.loading_window.destroy()
            self.show_main_window()
        else:
            # 继续检查
            self.root.after(100, self.check_initialization)
    
    def initialize_background(self):
        """在后台初始化"""
        try:
            # 添加路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)
            
            # 延迟导入，避免启动时加载所有模块
            time.sleep(0.5)  # 模拟初始化时间
            
            # 检查数据库
            if not os.path.exists("welding_gun.db"):
                print("警告: 数据库文件不存在")
                # 在UI线程中显示错误
                self.root.after(0, self.show_db_error)
                return
            
            # 标记初始化完成
            self.initialized = True
            
        except Exception as e:
            print(f"初始化失败: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # 在UI线程中显示错误
            self.root.after(0, lambda: self.show_error(str(e)))
    
    def show_db_error(self):
        """显示数据库错误"""
        self.progress.stop()
        self.loading_window.destroy()
        
        from tkinter import messagebox
        messagebox.showerror("错误", "数据库文件不存在！\n\n请先运行: python reset_system_user_fixed.py")
        self.root.destroy()
    
    def show_error(self, error_msg):
        """显示错误"""
        self.progress.stop()
        self.loading_window.destroy()
        
        from tkinter import messagebox
        messagebox.showerror("初始化失败", f"系统初始化失败:\n\n{error_msg}")
        self.root.destroy()
    
    def show_main_window(self):
        """显示主窗口"""
        try:
            # 现在导入主窗口模块
            from views.main_window_fixed import MainWindow
            
            # 显示主窗口
            self.root.deiconify()  # 显示隐藏的窗口
            
            # 创建主窗口实例
            app = MainWindow(self.root)
            
            print("✓ 应用程序启动成功")
            
        except ImportError as e:
            # 如果导入失败，使用简化版本
            print(f"导入失败，使用简化界面: {e}")
            self.show_simple_interface()
    
    def show_simple_interface(self):
        """显示简化界面"""
        self.root.deiconify()
        self.root.title("焊接枪管理系统 - 简化版")
        self.root.geometry("600x400")
        
        # 创建简化界面
        frame = tk.Frame(self.root, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="焊接枪管理系统", 
                font=("Arial", 18, "bold")).pack(pady=20)
        
        tk.Label(frame, text="简化界面模式", 
                font=("Arial", 12)).pack(pady=10)
        
        # 直接登录按钮
        tk.Button(frame, text="使用 system 登录 (密码: manager)", 
                 command=self.login_as_system, width=30).pack(pady=10)
        
        tk.Button(frame, text="使用 administrator 登录 (无密码)", 
                 command=self.login_as_admin, width=30).pack(pady=10)
        
        tk.Button(frame, text="退出", 
                 command=self.root.destroy, width=20).pack(pady=20)
    
    def login_as_system(self):
        """以system用户登录"""
        self.show_gun_management('system')
    
    def login_as_admin(self):
        """以administrator用户登录"""
        self.show_gun_management('administrator')
    
    def show_gun_management(self, username):
        """显示工枪管理界面"""
        # 清除当前界面
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # 创建工枪管理界面
        self.root.title(f"焊接枪管理系统 - {username}")
        
        # 添加一些简单的功能
        frame = tk.Frame(self.root, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text=f"欢迎, {username}!", 
                font=("Arial", 16, "bold")).pack(pady=20)
        
        if username == 'system':
            tk.Label(frame, text="管理员权限", fg="green").pack()
            tk.Button(frame, text="添加工枪", width=20).pack(pady=5)
            tk.Button(frame, text="编辑工枪", width=20).pack(pady=5)
            tk.Button(frame, text="删除工枪", width=20).pack(pady=5)
        else:
            tk.Label(frame, text="管理员权限 (无密码)", fg="blue").pack()
            tk.Button(frame, text="添加工枪", width=20).pack(pady=5)
            tk.Button(frame, text="编辑工枪", width=20).pack(pady=5)
        
        tk.Button(frame, text="查看工枪列表", width=20).pack(pady=20)
        tk.Button(frame, text="返回登录", 
                 command=self.show_simple_interface, width=15).pack()


def main():
    """主函数"""
    app = FastApp()
    app.start()

if __name__ == "__main__":
    main()