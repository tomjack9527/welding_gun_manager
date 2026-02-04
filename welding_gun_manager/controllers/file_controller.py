# controllers/file_controller.py
import os
import json
import csv
from datetime import datetime

class FileController:
    def __init__(self):
        pass
    
    def export_to_csv(self, data, filename):
        """导出数据到CSV"""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                if data:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
            return True
        except Exception as e:
            print(f"导出CSV失败: {e}")
            return False
    
    def import_from_csv(self, filename):
        """从CSV导入数据"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return list(reader)
        except Exception as e:
            print(f"导入CSV失败: {e}")
            return []
