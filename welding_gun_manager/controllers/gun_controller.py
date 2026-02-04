# controllers/gun_controller.py
from models.database import Database
from models.entities import WeldingGun
import json

class GunController:
    def __init__(self, db=None):
        self.db = db or Database()
    
    def create_gun(self, gun):
        """创build工枪"""
        try:
            self.db.execute('''
            INSERT INTO guns (name, type, model, serial_number, status, location, last_maintenance, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                gun.name, gun.type, gun.model, gun.serial_number,
                gun.status, gun.location, gun.last_maintenance,
                gun.notes, gun.created_at
            ))
            return True
        except Exception as e:
            print(f"创build工枪失败: {e}")
            return False
    
    def get_all_guns(self):
        """获取所有工枪"""
        results = self.db.fetch_all("SELECT * FROM guns ORDER BY name")
        guns = []
        for row in results:
            guns.append(WeldingGun(
                id=row['id'],
                name=row['name'],
                type=row['type'],
                model=row['model'],
                serial_number=row['serial_number'],
                status=row['status'],
                location=row['location'],
                last_maintenance=row['last_maintenance'],
                notes=row['notes'],
                created_at=row['created_at']
            ))
        return guns
    
    def get_gun_by_id(self, gun_id):
        """根据ID获取工枪"""
        row = self.db.fetch_one("SELECT * FROM guns WHERE id = ?", (gun_id,))
        if row:
            return WeldingGun(
                id=row['id'],
                name=row['name'],
                type=row['type'],
                model=row['model'],
                serial_number=row['serial_number'],
                status=row['status'],
                location=row['location'],
                last_maintenance=row['last_maintenance'],
                notes=row['notes'],
                created_at=row['created_at']
            )
        return None
    
    def update_gun(self, gun_id, gun_data):
        """更新工枪"""
        try:
            self.db.execute('''
            UPDATE guns SET
                name = ?, type = ?, model = ?, serial_number = ?,
                status = ?, location = ?, last_maintenance = ?, notes = ?
            WHERE id = ?
            ''', (
                gun_data['name'], gun_data['type'], gun_data['model'], 
                gun_data['serial_number'], gun_data['status'], gun_data['location'],
                gun_data['last_maintenance'], gun_data['notes'], gun_id
            ))
            return True
        except Exception as e:
            print(f"更新工枪失败: {e}")
            return False
    
    def delete_gun(self, gun_id):
        """删除工枪"""
        try:
            self.db.execute("DELETE FROM guns WHERE id = ?", (gun_id,))
            return True
        except Exception as e:
            print(f"删除工枪失败: {e}")
            return False
    
    def search_guns(self, search_term):
        """搜索工枪"""
        query = """
        SELECT * FROM guns 
        WHERE name LIKE ? OR type LIKE ? OR model LIKE ? OR location LIKE ?
        ORDER BY name
        """
        param = f"%{search_term}%"
        results = self.db.fetch_all(query, (param, param, param, param))
        
        guns = []
        for row in results:
            guns.append(WeldingGun(
                id=row['id'],
                name=row['name'],
                type=row['type'],
                model=row['model'],
                serial_number=row['serial_number'],
                status=row['status'],
                location=row['location'],
                last_maintenance=row['last_maintenance'],
                notes=row['notes'],
                created_at=row['created_at']
            ))
        return guns
    
    def get_statistics(self):
        """获取统计信息"""
        stats = {}
        
        # 总数
        total = self.db.fetch_one("SELECT COUNT(*) as count FROM guns")
        stats['total_guns'] = total['count'] if total else 0
        
        # 状态分布
        status_data = self.db.fetch_all(
            "SELECT status, COUNT(*) as count FROM guns GROUP BY status"
        )
        stats['status_distribution'] = {
            row['status']: row['count'] for row in status_data
        }
        
        # 类型分布
        type_data = self.db.fetch_all(
            "SELECT type, COUNT(*) as count FROM guns WHERE type IS NOT NULL GROUP BY type"
        )
        stats['type_distribution'] = {
            row['type']: row['count'] for row in type_data
        }
        
        # 各状态数量
        stats['active_guns'] = stats['status_distribution'].get('active', 0)
        stats['maintenance_guns'] = stats['status_distribution'].get('maintenance', 0)
        stats['inactive_guns'] = stats['status_distribution'].get('inactive', 0)
        stats['scrap_guns'] = stats['status_distribution'].get('scrap', 0)
        
        return stats