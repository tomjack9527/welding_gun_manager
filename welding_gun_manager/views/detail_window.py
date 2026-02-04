# views/detail_window.py
"""
详情/编辑窗口视图
用于添加或编辑单个焊枪的详细信息。
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

class DetailWindow:
    """
    用于添加或编辑焊枪详情的窗口。
    """
    def __init__(self, window, controller, gun_data, mode='add', presets=None):
        self.window = window
        self.controller = controller
        self.gun_data = gun_data # 这是一个 WeldingGun 对象或空对象
        self.mode = mode # 'add' or 'edit'
        self.presets = presets or {} # 预设选项字典

        # UI 控件的变量
        self.vars = {}
        self.file_vars = {
            'image_path': tk.StringVar(),
            'step_stp_path': tk.StringVar(),
            'jt_path': tk.StringVar(),
            'pdf_dwg_path': tk.StringVar(),
        }
        
        # 设置窗口属性
        self.window.title(f"{'添加' if mode == 'add' else '编辑'}焊枪详情")
        self.window.geometry("800x700") # 可根据需要调整大小
        self.window.transient() # 设置为临时窗口
        self.window.grab_set() # 模态窗口

        self.setup_ui()
        self.populate_form()

    def setup_ui(self):
        """设置详情窗口的用户界面。"""
        # 主容器框架
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- 表单字段区域 ---
        form_frame = ttk.LabelFrame(main_frame, text="基本信息", padding="10")
        form_frame.pack(fill=tk.X, pady=(0, 10))

        fields = [
            ('name', '名称*', 0),
            ('brand', '品牌*', 1),
            ('gun_type', '焊枪类型*', 2),
            ('line', '线体*', 3),
            ('area', '区域*', 4),
            ('robot_number', '机器人号*', 5),
            ('motor_brand', '电机品牌*', 6),
            ('gun_number', '焊枪编号*', 7),
            ('throat_depth', '喉深 (mm)', 8),
            ('throat_width', '喉宽 (mm)', 9),
            ('max_travel', '最大行程 (mm)', 10),
            ('max_pressure', '最大压力 (N)', 11),
            ('electrode_cap_spec', '电极帽规格', 12),
            ('electrode_cap_size', '电极帽尺寸 (mm)', 13),
            ('static_arm_height', '静态臂高 (mm)', 14),
            ('dynamic_arm_height', '动态臂高 (mm)', 15),
            ('dynamic_tip_angle', '动态尖角 (°)', 16),
            ('static_tip_angle', '静态尖角 (°)', 17),
        ]

        # 动态创建标签和输入控件
        for field_attr, label_text, row in fields:
            ttk.Label(form_frame, text=label_text).grid(row=row, column=0, sticky=tk.W, padx=(0, 10), pady=2)

            # 确定控件类型
            if field_attr in ['brand', 'gun_type', 'line', 'area', 'motor_brand']: # 使用预设的下拉菜单
                preset_key_map = {
                    'brand': 'manufacturers',
                    'gun_type': 'gun_types',
                    'line': 'lines',
                    'area': 'areas',
                    'motor_brand': 'motor_brands',
                }
                preset_key = preset_key_map.get(field_attr)
                preset_options = self.presets.get(preset_key, []) if self.presets else []
                
                var = tk.StringVar()
                combo = ttk.Combobox(form_frame, textvariable=var, values=preset_options, state="readonly", width=30)
                combo.grid(row=row, column=1, sticky=tk.EW, padx=(0, 10), pady=2)
                self.vars[field_attr] = var
            elif field_attr in ['name', 'robot_number', 'gun_number', 'electrode_cap_spec']:
                var = tk.StringVar()
                entry = ttk.Entry(form_frame, textvariable=var, width=32)
                entry.grid(row=row, column=1, sticky=tk.EW, padx=(0, 10), pady=2)
                self.vars[field_attr] = var
            elif field_attr in ['throat_depth', 'throat_width', 'max_travel', 'max_pressure', 'electrode_cap_size', 'static_arm_height', 'dynamic_arm_height', 'dynamic_tip_angle', 'static_tip_angle']:
                var = tk.DoubleVar()
                entry = ttk.Entry(form_frame, textvariable=var, width=32)
                entry.grid(row=row, column=1, sticky=tk.EW, padx=(0, 10), pady=2)
                self.vars[field_attr] = var
            else: # 未知字段，跳过
                continue

        # 配置列权重，使输入框能随窗口伸缩
        form_frame.columnconfigure(1, weight=1)

        # --- 文件上传区域 ---
        file_frame = ttk.LabelFrame(main_frame, text="文件上传", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 10))

        file_fields = [
            ('image_path', '图片', ('.jpg', '.jpeg', '.png', '.gif')),
            ('step_stp_path', 'STEP/STP 模型', ('.step', '.stp')),
            ('jt_path', 'JT 模型', ('.jt',)),
            ('pdf_dwg_path', 'PDF/DWG 文档', ('.pdf', '.dwg')),
        ]

        for i, (field, label, exts) in enumerate(file_fields):
            ttk.Label(file_frame, text=f"{label}:").grid(row=i, column=0, sticky=tk.W, padx=(0, 10), pady=2)
            
            entry = ttk.Entry(file_frame, textvariable=self.file_vars[field], state='readonly', width=40) # 只读显示路径
            entry.grid(row=i, column=1, sticky=tk.EW, padx=(0, 5), pady=2)
            
            btn = ttk.Button(file_frame, text="浏览...", command=lambda f=field, e=exts: self.browse_file(f, e))
            btn.grid(row=i, column=2, sticky=tk.W, pady=2)

        file_frame.columnconfigure(1, weight=1) # 使路径显示 Entry 伸缩

        # --- 备注区域 ---
        notes_frame = ttk.LabelFrame(main_frame, text="备注", padding="10")
        notes_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.notes_text = tk.Text(notes_frame, height=4, wrap=tk.WORD)
        notes_scrollbar = ttk.Scrollbar(notes_frame, orient=tk.VERTICAL, command=self.notes_text.yview)
        self.notes_text.configure(yscrollcommand=notes_scrollbar.set)
        
        self.notes_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        notes_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # --- 按钮区域 ---
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="保存", command=self.save_data).pack(side=tk.RIGHT, padx=(0, 5))
        ttk.Button(button_frame, text="取消", command=self.window.destroy).pack(side=tk.RIGHT)

    def populate_form(self):
        """将 gun_data 对象中的数据填充到表单控件中。"""
        for attr_name, var in self.vars.items():
            value = getattr(self.gun_data, attr_name, "")
            if isinstance(var, tk.DoubleVar) and (value is None or value == ""):
                 var.set(0.0) # 对于数值类型，如果数据库中为空，则设为0.0
            else:
                var.set(value)

        # 填充文件路径变量
        for attr_name, var in self.file_vars.items():
            value = getattr(self.gun_data, attr_name, "")
            var.set(value)

        # 填充备注
        self.notes_text.delete(1.0, tk.END) # 清空
        self.notes_text.insert(1.0, getattr(self.gun_data, 'notes', ""))

    def browse_file(self, field_name, extensions):
        """打开文件浏览器，让用户选择文件，并更新对应变量。"""
        file_path = filedialog.askopenfilename(
            title=f"选择{field_name.replace('_', ' ').title()}文件",
            filetypes=[("支持的文件", " ".join(extensions)), ("所有文件", "*.*")]
        )
        if file_path:
            # 将选中的文件路径存储到对应的 StringVar 中
            # 注意：这里存储的是用户选择的原始路径，将在保存时由控制器处理
            self.file_vars[field_name].set(file_path)

    def save_data(self):
        """从表单收集数据并保存到数据库。"""
        try:
            # 从 UI 控件收集数据
            data_dict = {}
            for attr_name, var in self.vars.items():
                value = var.get()
                # 特殊处理：如果数值字段在UI上为空字符串，则存为 None 或 0
                if isinstance(var, tk.DoubleVar) and value == 0.0:
                    # 如果用户清空了数值框，默认 DoubleVar.get() 可能是 0.0
                    # 我们需要检查 Entry 的实际内容
                    entry_widget = None
                    for widget in self.window.winfo_children()[0].winfo_children()[0].winfo_children():
                        if hasattr(widget, 'textvariable') and widget.textvariable == str(var):
                            entry_widget = widget
                            break
                    if entry_widget and entry_widget.get() == "":
                         value = None
                
                data_dict[attr_name] = value

            # 添加文件路径
            for attr_name, var in self.file_vars.items():
                data_dict[attr_name] = var.get() # 获取的是用户选择的原始路径或空字符串

            # 添加备注
            data_dict['notes'] = self.notes_text.get(1.0, tk.END).strip()

            # 调用控制器进行保存
            success = False
            if self.mode == 'add':
                success = self.controller.add_new_gun(data_dict)
                message = "新增焊枪成功！" if success else "新增焊枪失败，请检查数据。"
            elif self.mode == 'edit':
                # 在编辑模式下，必须包含 ID
                data_dict['id'] = self.gun_data.id
                success = self.controller.update_existing_gun(self.gun_data.id, data_dict)
                message = "更新焊枪信息成功！" if success else "更新焊枪信息失败，请检查数据。"
            
            if success:
                messagebox.showinfo("成功", message)
                self.window.destroy() # 关闭当前窗口
                # 可以在这里触发主窗口刷新，例如通过回调函数
                # if hasattr(self.controller, 'notify_detail_saved'):
                #     self.controller.notify_detail_saved()
            else:
                messagebox.showerror("错误", message)

        except ValueError as e:
            # 捕获 DoubleVar 转换错误等
            messagebox.showerror("输入错误", f"数据格式不正确，请检查数值字段。\n错误详情: {e}")
        except Exception as e:
            messagebox.showerror("错误", f"保存过程中发生未知错误: {e}")

# --- 示例用法 ---
# if __name__ == "__main__":
#     # 这个窗口通常由 MainWindow 打开，所以不单独运行
#     pass