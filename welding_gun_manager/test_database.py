# welding_gun_manager/test_database.py
import sys
import os
import sqlite3

def test_database():
    """测试数据库"""
    try:
        db_file = "welding_gun.db"
        
        if not os.path.exists(db_file):
            print(f"✗ 数据库文件不存在: {db_file}")
            return False
        
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print("=" * 50)
        print("测试数据库连接和表结构")
        print("=" * 50)
        
        # 检查表是否存在
        tables = ['users', 'welding_guns', 'presets']
        for table in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            exists = cursor.fetchone() is not None
            status = "✓ 存在" if exists else "✗ 不存在"
            print(f"表 {table}: {status}")
        
        # 检查用户数据
        print("\n" + "=" * 50)
        print("检查用户数据")
        print("=" * 50)
        
        cursor.execute("SELECT username, password, role FROM users ORDER BY id")
        users = cursor.fetchall()
        
        print(f"用户数量: {len(users)}")
        for user in users:
            password = user['password'] if user['password'] else "无密码"
            role = "管理员" if user['role'] == 'admin' else "普通用户"
            print(f"  - {user['username']}: 密码='{password}', 角色={role}")
        
        # 测试密码验证
        print("\n" + "=" * 50)
        print("测试密码验证")
        print("=" * 50)
        
        def verify_user(username, password=None):
            if password is None:
                cursor.execute(
                    "SELECT * FROM users WHERE username = ? AND password IS NULL",
                    (username,)
                )
            else:
                cursor.execute(
                    "SELECT * FROM users WHERE username = ? AND password = ?",
                    (username, password)
                )
            user = cursor.fetchone()
            return dict(user) if user else None
        
        # 测试 system 用户
        user = verify_user('system', 'manager')
        if user:
            print(f"✓ system 用户验证成功")
            print(f"  用户名: {user['username']}")
            print(f"  角色: {'管理员' if user['role'] == 'admin' else '普通用户'}")
        else:
            print(f"✗ system 用户验证失败")
        
        # 测试错误的密码
        user = verify_user('system', 'wrongpassword')
        if not user:
            print(f"✓ system 错误密码验证正确失败")
        else:
            print(f"✗ system 错误密码验证不应该成功")
        
        # 测试工枪数据
        print("\n" + "=" * 50)
        print("检查工枪数据")
        print("=" * 50)
        
        cursor.execute("SELECT COUNT(*) as count FROM welding_guns")
        gun_count = cursor.fetchone()['count']
        print(f"工枪记录数量: {gun_count}")
        
        if gun_count > 0:
            cursor.execute("SELECT model, brand, status FROM welding_guns LIMIT 3")
            guns = cursor.fetchall()
            print("示例工枪:")
            for gun in guns:
                print(f"  - {gun['model']} ({gun['brand']}) - 状态: {gun['status']}")
        
        conn.close()
        
        print("\n" + "=" * 50)
        print("数据库测试完成！")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_database()