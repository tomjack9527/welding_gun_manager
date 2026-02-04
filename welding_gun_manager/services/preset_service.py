# services/preset_service.py
class PresetService:
    def __init__(self):
        pass
    
    def validate_preset(self, preset_data):
        """验证预设数据"""
        required = ['name', 'gun_type']
        for field in required:
            if not preset_data.get(field):
                return False, f"缺少必填字段: {field}"
        return True, "验证通过"
