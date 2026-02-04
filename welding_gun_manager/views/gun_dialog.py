# welding_gun_manager/views/gun_dialog.py
import tkinter as tk
from tkinter import ttk
from datetime import datetime


class GunDialog:
    def __init__(self, parent, title="工枪信息", gun=None):
        self.parent = parent
        self.gun = gun
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        
        # 居中显示
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
        
        # 如果是编辑模式，填充数据
        if gun:
            self.fill_data()
        
        self.dialog.wait_window()
    
    def setup_ui(self):
        """设置对话框UI"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 型号
        ttk.Label(main_frame, text="型号*:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.model_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.model_var, width=30).grid(
            row=0, column=1, sticky=tk.W, pady=5, padx=5)
        
        # 品牌
        ttk.Label(main_frame, text="品牌*:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.brand_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.brand_var, width=30).grid(
            row=1, column=1, sticky=tk.W, pady=5, padx=5)
        
        # 序列号
        ttk.Label(main_frame, text="序列号:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.serial_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.serial_var, width=30).grid(
            row=2, column=1, sticky=tk.W, pady=5, padx=5)
        
        # 状态
        ttk.Label(main_frame, text="状态:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.status_var = tk.StringVar(value="正常")
        status_combo = ttk.Combobox(main_frame, textvariable=self.status_var, 
                                   values=["正常", "维修", "停用", "报废"], width=27)
        status_combo.grid(row=3, column=1, sticky=tk.W, pady=5, padx=5)
        
        # 生产日期
        ttk.Label(main_frame, text="生产日期:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.production_date_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.production_date_var, width=30).grid(
            row=4, column=1, sticky=tk.W, pady=5, padx=5)
        
        # 购买日期
        ttk.Label(main_frame, text="购买日期:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.purchase_date_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.purchase_date_var, width=30).grid(
            row=5, column=1, sticky=tk.W, pady=5, padx=5)
        
        # 备注
        ttk.Label(main_frame, text="备注:").grid(row=6, column=0, sticky=tk.NW, pady=5)
        self.notes_text = tk.Text(main_frame, width=30, height=5)
        self.notes_text.grid(row=6, column=1, sticky=tk.W, pady=5, padx=5)
        
        # 按钮框架
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="确定", command=self.on_ok).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="取消", command=self.on_cancel).pack(side=tk.LEFT, padx=10)
        
        # 绑定回车键
        self.dialog.bind('<Return>', lambda e: self.on_ok())
        self.dialog.bind('<Escape>', lambda e: self.on_cancel())
        
        # 设置焦点
        self.model_var.trace_add('write', self.validate_form)
        self.brand_var.trace_add('write', self.validate_form)
    
    def fill_data(self):
        """填充现有数据"""
        if self.gun:
            self.model_var.set(self.gun.model or "")
            self.brand_var.set(self.gun.brand or "")
            self.serial_var.set(self.gun.serial_number or "")
            self.status_var.set(self.gun.status or "正常")
            self.production_date_var.set(self.gun.production_date or "")
            self.purchase_date_var.set(self.gun.purchase_date or "")
            self.notes_text.delete(1.0, tk.END)
            self.notes_text.insert(1.0, self.gun.notes or "")
    
    def validate_form(self, *args):
        """验证表单"""
        return bool(self.model_var.get().strip() and self.brand_var.get().strip())
    
    def on_ok(self):
        """确定按钮"""
        if not self.validate_form():
            tk.messagebox.showwarning("警告", "型号和品牌不能为空")
            return
        
        self.result = {
            'model': self.model_var.get().strip(),
            'brand': self.brand_var.get().strip(),
            'serial_number': self.serial_var.get().strip(),
            'status': self.status_var.get(),
            'production_date': self.production_date_var.get().strip(),
            'purchase_date': self.purchase_date_var.get().strip(),
            'notes': self.notes_text.get(1.0, tk.END).strip(),
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        self.dialog.destroy()
    
    def on_cancel(self):
        """取消按钮"""
        self.result = None
        self.dialog.destroy()