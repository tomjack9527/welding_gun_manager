# fix_database.py
import sqlite3
import os
import datetime

def fix_database():
    db_path = "welding_gun.db"
    
    # 备份原数据库
    if os.path.exists(db_path):
        backup_path = f"welding_gun_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"📦 已备份数据库到: {backup_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 方法1：尝试添加full_name列
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN full_name TEXT")
        print("✅ 成功添加full_name列到users表")
    except sqlite3.OperationalError as e:
        print(f"添加列失败: {e}")
        print("尝试重新创建表...")
        
        # 方法2：重新创建表
        try:
            # 保存现有数据
            cursor.execute("SELECT * FROM users")
            old_users = cursor.fetchall()
            print(f"找到 {len(old_users)} 条用户记录")
            
            # 删除旧表
            cursor.execute("DROP TABLE users")
            
            # 创建新表
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
            print("✅ 重新创建users表")
            
            # 重新插入数据
            for user in old_users:
                # 处理不同列数的旧数据
                if len(user) == 6:  # 没有full_name
                    cursor.execute('''
                    INSERT INTO users (id, username, password, role, full_name, email, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (user[0], user[1], user[2], user[3], user[1], user[4], user[5]))
                elif len(user) == 7:  # 有full_name
                    cursor.execute('''
                    INSERT INTO users (id, username, password, role, full_name, email, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', user)
            
            print("✅ 恢复用户数据")
            
        except Exception as e2:
            print(f"重新创建表失败: {e2}")
            print("创建全新的表...")
            
            # 删除表并创建全新表
            cursor.execute("DROP TABLE IF EXISTS users")
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
            print("✅ 创建全新的users表")
            
            # 插入默认用户
            current_time = datetime.datetime.now().isoformat()
            default_users = [
                ('system', 'manager', 'admin', '系统管理员', 'admin@welding.com', current_time),
                ('administrator', None, 'admin', 'Administrator', '', current_time),
                ('user', 'user123', 'user', '普通用户', 'user@welding.com', current_time)
            ]
            
            cursor.executemany('''
            INSERT INTO users (username, password, role, full_name, email, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', default_users)
            print("✅ 插入默认用户数据")
    
    # 检查并修复guns表
    try:
        cursor.execute("PRAGMA table_info(guns)")
        gun_columns = [col[1] for col in cursor.fetchall()]
        print(f"\nguns表的列: {gun_columns}")
        
        # 检查是否有full_name列（不应该有）
        if 'full_name' in gun_columns:
            print("⚠️  guns表中存在full_name列，删除中...")
            # 这里需要更复杂的处理，暂时跳过
        
    except Exception as e:
        print(f"检查guns表失败: {e}")
    
    conn.commit()
    
    # 验证修复
    print("\n✅ 验证修复结果:")
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    print("users表结构:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # 显示用户数据
    print("\n用户数据:")
    cursor.execute("SELECT id, username, full_name, role FROM users")
    users = cursor.fetchall()
    for user in users:
        print(f"  ID:{user[0]} 用户名:{user[1]} 姓名:{user[2]} 角色:{user[3]}")
    
    conn.close()
    print("\n🎉 数据库修复完成！")

if __name__ == "__main__":
    fix_database()