# file_operations.py
import os
import zipfile
import shutil
from datetime import datetime
import json

class GunFileManager:
    """焊枪文件管理器"""
    
    def __init__(self, base_dir="uploaded_guns"):
        self.base_dir = base_dir
        self.ensure_directory_exists()
    
    def ensure_directory_exists(self):
        """确保基础目录存在"""
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
    
    def create_gun_folder(self, gun_info):
        """
        创建焊枪文件夹结构
        
        Args:
            gun_info: 包含焊枪信息的字典
            
        Returns:
            str: 创建的文件夹路径
        """
        # 生成文件夹名称：焊枪名称_当前时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_name = f"{gun_info['name']}_{timestamp}"
        folder_path = os.path.join(self.base_dir, folder_name)
        
        # 创建主文件夹
        os.makedirs(folder_path)
        
        # 创建子文件夹结构
        subfolders = ['3d_models', '2d_drawings', 'images', 'signature_drawings', 'dwg_files']
        for subfolder in subfolders:
            os.makedirs(os.path.join(folder_path, subfolder))
        
        # 保存焊枪信息到JSON文件
        info_file = os.path.join(folder_path, 'gun_info.json')
        gun_info['created_at'] = datetime.now().isoformat()
        gun_info['folder_name'] = folder_name
        
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(gun_info, f, ensure_ascii=False, indent=2)
        
        return folder_path
    
    def save_file_to_folder(self, folder_path, file_path, file_type):
        """
        保存文件到对应的文件夹
        
        Args:
            folder_path: 焊枪文件夹路径
            file_path: 要保存的文件路径
            file_type: 文件类型（3d, 2d, image, signature, dwg）
            
        Returns:
            str: 保存后的文件路径
        """
        # 映射文件类型到子文件夹
        type_to_folder = {
            '3d': '3d_models',
            '2d': '2d_drawings',
            'image': 'images',
            'signature': 'signature_drawings',
            'dwg': 'dwg_files'
        }
        
        if file_type not in type_to_folder:
            raise ValueError(f"不支持的文件类型: {file_type}")
        
        # 获取原始文件名
        original_filename = os.path.basename(file_path)
        
        # 目标路径
        target_folder = os.path.join(folder_path, type_to_folder[file_type])
        target_path = os.path.join(target_folder, original_filename)
        
        # 如果文件已存在，添加时间戳
        if os.path.exists(target_path):
            timestamp = datetime.now().strftime("%H%M%S")
            name, ext = os.path.splitext(original_filename)
            new_filename = f"{name}_{timestamp}{ext}"
            target_path = os.path.join(target_folder, new_filename)
        
        # 复制文件
        shutil.copy2(file_path, target_path)
        
        # 更新信息文件
        self.update_file_info(folder_path, file_type, os.path.basename(target_path))
        
        return target_path
    
    def update_file_info(self, folder_path, file_type, filename):
        """更新信息文件中的文件列表"""
        info_file = os.path.join(folder_path, 'gun_info.json')
        
        if os.path.exists(info_file):
            with open(info_file, 'r', encoding='utf-8') as f:
                info = json.load(f)
            
            # 初始化文件列表
            if 'files' not in info:
                info['files'] = {}
            
            if file_type not in info['files']:
                info['files'][file_type] = []
            
            # 添加文件
            if filename not in info['files'][file_type]:
                info['files'][file_type].append(filename)
                info['updated_at'] = datetime.now().isoformat()
                
                # 保存更新
                with open(info_file, 'w', encoding='utf-8') as f:
                    json.dump(info, f, ensure_ascii=False, indent=2)
    
    def create_zip_file(self, folder_path):
        """
        将焊枪文件夹压缩为ZIP文件
        
        Args:
            folder_path: 焊枪文件夹路径
            
        Returns:
            str: 创建的ZIP文件路径
        """
        zip_filename = os.path.basename(folder_path) + '.zip'
        zip_path = os.path.join(self.base_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, folder_path)
                    zipf.write(file_path, arcname)
        
        return zip_path
    
    def get_all_guns(self):
        """获取所有焊枪信息"""
        guns = []
        
        if not os.path.exists(self.base_dir):
            return guns
        
        for item in os.listdir(self.base_dir):
            item_path = os.path.join(self.base_dir, item)
            
            if os.path.isdir(item_path):
                info_file = os.path.join(item_path, 'gun_info.json')
                
                if os.path.exists(info_file):
                    try:
                        with open(info_file, 'r', encoding='utf-8') as f:
                            gun_info = json.load(f)
                        
                        # 添加文件夹路径
                        gun_info['folder_path'] = item_path
                        gun_info['zip_file'] = os.path.join(self.base_dir, item + '.zip')
                        
                        # 检查是否有ZIP文件
                        gun_info['has_zip'] = os.path.exists(gun_info['zip_file'])
                        
                        guns.append(gun_info)
                    except:
                        continue
        
        # 按创建时间排序
        guns.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return guns
    
    def get_gun_by_name(self, gun_name):
        """根据焊枪名称获取焊枪信息"""
        guns = self.get_all_guns()
        
        for gun in guns:
            if gun['name'] == gun_name:
                return gun
        
        return None
    
    def delete_gun(self, gun_name):
        """删除焊枪及其文件"""
        gun = self.get_gun_by_name(gun_name)
        
        if gun:
            # 删除文件夹
            if 'folder_path' in gun and os.path.exists(gun['folder_path']):
                shutil.rmtree(gun['folder_path'])
            
            # 删除ZIP文件
            if 'zip_file' in gun and os.path.exists(gun['zip_file']):
                os.remove(gun['zip_file'])
            
            return True
        
        return False