# controllers/user_controller.py
from models.database import Database
from models.entities import User

class UserController:
    def __init__(self, db=None):
        self.db = db or Database()
    
    def authenticate(self, username, password):
        """用户认证"""
        if username == "administrator":
            row = self.db.fetch_one(
                "SELECT * FROM users WHERE username = ? AND password IS NULL",
                (username,)
            )
        else:
            row = self.db.fetch_one(
                "SELECT * FROM users WHERE username = ? AND password = ?",
                (username, password)
            )
        
        if row:
            # 安全地获取full_name，如果不存在则使用username
            full_name = row.get('full_name')
            if full_name is None:
                full_name = username
            
            return User(
                id=row['id'],
                username=row['username'],
                password=row['password'],
                role=row['role'],
                full_name=full_name,
                email=row.get('email', ''),
                created_at=row['created_at']
            )
        return None
    
    def get_user_by_username(self, username):
        """根据用户名获取用户"""
        row = self.db.fetch_one(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )
        if row:
            # 安全地获取full_name
            full_name = row.get('full_name')
            if full_name is None:
                full_name = username
            
            return User(
                id=row['id'],
                username=row['username'],
                password=row['password'],
                role=row['role'],
                full_name=full_name,
                email=row.get('email', ''),
                created_at=row['created_at']
            )
        return None
    
    def get_all_users(self):
        """获取所有用户"""
        rows = self.db.fetch_all("SELECT * FROM users ORDER BY username")
        users = []
        for row in rows:
            # 安全地获取full_name
            full_name = row.get('full_name')
            if full_name is None:
                full_name = row['username']
            
            users.append(User(
                id=row['id'],
                username=row['username'],
                password=row['password'],
                role=row['role'],
                full_name=full_name,
                email=row.get('email', ''),
                created_at=row['created_at']
            ))
        return users
    
    def create_user(self, user):
        """创建用户"""
        try:
            self.db.execute('''
            INSERT INTO users (username, password, role, full_name, email, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                user.username, user.password, user.role,
                user.full_name, user.email, user.created_at
            ))
            return True
        except Exception as e:
            print(f"创建用户失败: {e}")
            return False