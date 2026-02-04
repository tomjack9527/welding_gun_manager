# controllers/preset_controller.py
from models.database import Database
import json

class PresetController:
    def __init__(self, db=None):
        self.db = db or Database()
    
    def get_all_presets(self):
        """获取所有预设"""
        return self.db.fetch_all("SELECT * FROM presets ORDER BY name")
    
    def get_preset_by_id(self, preset_id):
        """根据ID获取预设"""
        return self.db.fetch_one("SELECT * FROM presets WHERE id = ?", (preset_id,))
    
    def create_preset(self, name, gun_type, parameters=None, description=None):
        """创建预设"""
        try:
            params_json = json.dumps(parameters or {})
            self.db.execute('''
            INSERT INTO presets (name, gun_type, parameters, description, created_at)
            VALUES (?, ?, ?, ?, datetime('now'))
            ''', (name, gun_type, params_json, description))
            return True
        except Exception as e:
            print(f"创建预设失败: {e}")
            return False
