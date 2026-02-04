
# models/database.py
import sqlite3
import os

class Database:
    def __init__(self, db_path="welding_gun.db"):
        self.db_path = db_path
        self.conn = None
    
    def connect(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def initialize(self):
        try:
            if not os.path.exists(self.db_path):
                self.create_tables()
                self.create_default_data()
            return True
        except Exception as e:
            print(f"数据库初始化失败: {e}")
            return False
    
    def create_tables(self):
        conn = self.connect()
        cursor = conn.cursor()
        
        # 删除旧表（如果存在）
        cursor.execute("DROP TABLE IF EXISTS guns")
        cursor.execute("DROP TABLE IF EXISTS users")
        
        # 创建新表（简化版）
        cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT,
            role TEXT NOT NULL,
            full_name TEXT,
            email TEXT,
            created_at TEXT NOT NULL
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE guns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT,
            model TEXT,
            serial_number TEXT UNIQUE,
            status TEXT NOT NULL,
            location TEXT,
            last_maintenance TEXT,
            notes TEXT,
            created_at TEXT NOT NULL
        )
        ''')
        
        conn.commit()
        print("数据库表创建成功")
    
    def create_default_data(self):
        conn = self.connect()
        cursor = conn.cursor()
        
        import datetime
        
        # 插入默认用户
        current_time = datetime.datetime.now().isoformat()
        users = [
            ('system', 'manager', 'admin', '系统管理员', 'admin@welding.com', current_time),
            ('administrator', None, 'admin', 'Administrator', '', current_time),
            ('user', 'user123', 'user', '普通用户', 'user@welding.com', current_time)
        ]
        
        cursor.executemany('''
        INSERT INTO users (username, password, role, full_name, email, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', users)
        
        # 插入示例工枪
        guns = [
            ('GUN-001', '点焊枪', 'DW-100', 'SN001', 'active', '生产线A', '2024-01-15', '正常使用', current_time),
            ('GUN-002', '弧焊枪', 'HW-200', 'SN002', 'maintenance', '维修车间', '2023-12-20', '需要维护', current_time),
            ('GUN-003', '激光焊枪', 'LW-300', 'SN003', 'active', '实验室', '2024-02-10', '高精度', current_time),
        ]
        
        cursor.executemany('''
        INSERT INTO guns (name, type, model, serial_number, status, location, last_maintenance, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', guns)
        
        conn.commit()
        print("默认数据创建成功")
    
    def execute(self, query, params=()):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor
    
    def fetch_all(self, query, params=()):
        cursor = self.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def fetch_one(self, query, params=()):
        cursor = self.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None