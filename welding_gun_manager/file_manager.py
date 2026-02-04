# file_manager.py
import tkinter as tk
from tkinter import filedialog, messagebox
import requests
import os

class FileManager:
    def __init__(self, parent_frame):
        """文件管理类 - 添加上传下载功能"""
        self.frame = tk.LabelFrame(parent_frame, text="文件管理", padx=10, pady=10)
        self.frame.pack(fill="x", padx=10, pady=5)
        
        # API 地址
        self.api_url = "http://localhost:8000"
        
        # 创建按钮
        self.create_widgets()
        
        # 初始加载文件列表
        self.refresh_files()
    
    def create_widgets(self):
        """创建界面组件"""
        # 按钮框架
        btn_frame = tk.Frame(self.frame)
        btn_frame.pack(pady=5)
        
        # 上传按钮
        self.upload_btn = tk.Button(
            btn_frame, 
            text="📤 上传文件", 
            command=self.upload_file,
            width=15,
            bg="#4CAF50",
            fg="white"
        )
        self.upload_btn.pack(side="left", padx=5)
        
        # 下载按钮
        self.download_btn = tk.Button(
            btn_frame, 
            text="📥 下载文件", 
            command=self.download_file,
            width=15,
            bg="#2196F3",
            fg="white"
        )
        self.download_btn.pack(side="left", padx=5)
        
        # 刷新按钮
        self.refresh_btn = tk.Button(
            btn_frame, 
            text="🔄 刷新列表", 
            command=self.refresh_files,
            width=15,
            bg="#FF9800",
            fg="white"
        )
        self.refresh_btn.pack(side="left", padx=5)
        
        # 文件列表框架
        list_frame = tk.Frame(self.frame)
        list_frame.pack(fill="both", expand=True, pady=10)
        
        # 列表标题
        tk.Label(list_frame, text="已上传的文件:", font=("Arial", 10, "bold")).pack(anchor="w")
        
        # 创建列表框和滚动条
        list_container = tk.Frame(list_frame)
        list_container.pack(fill="both", expand=True)
        
        # 滚动条
        scrollbar = tk.Scrollbar(list_container)
        scrollbar.pack(side="right", fill="y")
        
        # 文件列表框
        self.file_listbox = tk.Listbox(
            list_container, 
            height=8,
            yscrollcommand=scrollbar.set,
            selectmode="single"
        )
        self.file_listbox.pack(side="left", fill="both", expand=True)
        
        scrollbar.config(command=self.file_listbox.yview)
        
        # 状态标签
        self.status_label = tk.Label(
            self.frame, 
            text="就绪", 
            fg="gray",
            font=("Arial", 9)
        )
        self.status_label.pack(pady=(5, 0))
    
    def upload_file(self):
        """上传文件"""
        file_path = filedialog.askopenfilename(
            title="选择要上传的文件",
            filetypes=[
                ("所有文件", "*.*"),
                ("配置文件", "*.json *.txt *.yaml *.yml"),
                ("焊接参数", "*.csv *.xlsx *.xls"),
                ("图片文档", "*.png *.jpg *.jpeg *.pdf")
            ]
        )
        
        if not file_path:
            return
        
        try:
            self.status_label.config(text="正在上传...", fg="blue")
            self.frame.update()
            
            with open(file_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(f"{self.api_url}/api/upload", files=files)
            
            if response.status_code == 200:
                result = response.json()
                messagebox.showinfo("成功", f"文件上传成功:\n{result['filename']}")
                self.status_label.config(text="上传成功", fg="green")
                self.refresh_files()
            else:
                messagebox.showerror("错误", f"上传失败:\n{response.text}")
                self.status_label.config(text="上传失败", fg="red")
                
        except requests.exceptions.ConnectionError:
            messagebox.showerror("连接错误", "无法连接到后端服务\n请确保FastAPI正在运行")
            self.status_label.config(text="连接失败", fg="red")
        except Exception as e:
            messagebox.showerror("错误", f"上传出错:\n{str(e)}")
            self.status_label.config(text="上传错误", fg="red")
    
    def download_file(self):
        """下载选中的文件"""
        selection = self.file_listbox.curselection()
        if not selection:
            messagebox.showwarning("提示", "请先在列表中选择一个文件")
            return
        
        filename = self.file_listbox.get(selection[0])
        
        # 选择保存位置
        save_path = filedialog.asksaveasfilename(
            title="保存文件",
            initialfile=filename,
            defaultextension=".*"
        )
        
        if not save_path:
            return
        
        try:
            self.status_label.config(text="正在下载...", fg="blue")
            self.frame.update()
            
            response = requests.get(f"{self.api_url}/api/download/{filename}", stream=True)
            
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                messagebox.showinfo("成功", f"文件下载成功:\n{save_path}")
                self.status_label.config(text="下载成功", fg="green")
            else:
                messagebox.showerror("错误", f"下载失败:\n{response.text}")
                self.status_label.config(text="下载失败", fg="red")
                
        except requests.exceptions.ConnectionError:
            messagebox.showerror("连接错误", "无法连接到后端服务")
            self.status_label.config(text="连接失败", fg="red")
        except Exception as e:
            messagebox.showerror("错误", f"下载出错:\n{str(e)}")
            self.status_label.config(text="下载错误", fg="red")
    
    def refresh_files(self):
        """刷新文件列表"""
        try:
            self.status_label.config(text="正在获取文件列表...", fg="blue")
            self.frame.update()
            
            response = requests.get(f"{self.api_url}/api/files")
            
            if response.status_code == 200:
                files = response.json().get('files', [])
                
                # 清空列表框
                self.file_listbox.delete(0, tk.END)
                
                # 添加文件到列表框
                for file in files:
                    self.file_listbox.insert(tk.END, file)
                
                # 更新状态
                count = len(files)
                if count == 0:
                    self.status_label.config(text="没有文件", fg="gray")
                else:
                    self.status_label.config(text=f"找到 {count} 个文件", fg="green")
            else:
                self.status_label.config(text="获取列表失败", fg="red")
                
        except requests.exceptions.ConnectionError:
            self.status_label.config(text="无法连接到后端服务", fg="red")
            self.file_listbox.delete(0, tk.END)
            self.file_listbox.insert(tk.END, "⚠️ 请启动后端服务 (运行: python -m uvicorn main_fast:app)")
        except Exception as e:
            self.status_label.config(text=f"错误: {str(e)}", fg="red")