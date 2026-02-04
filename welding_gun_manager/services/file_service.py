# services/file_service.py
class FileService:
    def __init__(self):
        pass
    
    def validate_file(self, filepath):
        """验证文件"""
        return os.path.exists(filepath)
    
    def get_file_info(self, filepath):
        """获取文件信息"""
        if os.path.exists(filepath):
            stats = os.stat(filepath)
            return {
                'size': stats.st_size,
                'modified': datetime.fromtimestamp(stats.st_mtime),
                'created': datetime.fromtimestamp(stats.st_ctime)
            }
        return None
