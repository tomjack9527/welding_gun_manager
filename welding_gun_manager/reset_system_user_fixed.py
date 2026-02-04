# welding_gun_manager/reset_system_user_fixed.py
import sys
import os
import sqlite3
from datetime import datetime

def create_database_from_scratch():
    """从零开始创建数据库"""
    try:
        db_file = "welding_gun.db"
        
        print("=" * 50)
        print("从零开始创建焊接枪管理系统数据库")
        print("=" * 50)
        
        # 如果数据库文件已存在，先备份
        if os.path.exists(db_file):
            backup_file = f"{db_file}.backup"
            import shutil
            shutil.copy2(db_file, backup_file)
            print(f"✓ 备份旧数据库到: {backup_file}")
        
        # 删除旧数据库文件
        if os.path.exists(db_file):
            os.remove(db_file)
            print("✓ 删除旧的数据库文件")
        
        # 创建新的数据库连接
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print("\n创建数据表...")
        
        # 1. 创建用户表
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✓ 创建 users 表")
        
        # 2. 创建工枪表
        cursor.execute('''
            CREATE TABLE welding_guns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model TEXT NOT NULL,
                brand TEXT NOT NULL,
                serial_number TEXT,
                status TEXT DEFAULT '正常',
                production_date TEXT,
                purchase_date TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✓ 创建 welding_guns 表")
        
        # 3. 创建预设表
        cursor.execute('''
            CREATE TABLE presets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                gun_type TEXT NOT NULL,
                parameters TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✓ 创建 presets 表")
        
        conn.commit()
        
        print("\n创建默认用户...")
        print("-" * 30)
        
        # 创建 system 用户（管理员，密码：manager）
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ('system', 'manager', 'admin')
        )
        print("✓ 创建 system 用户")
        print("  用户名: system")
        print("  密码: manager")
        print("  角色: 管理员")
        
        # 创建 administrator 用户（无密码，管理员）
        cursor.execute(
            "INSERT INTO users (username, role) VALUES (?, ?)",
            ('administrator', 'admin')
        )
        print("✓ 创建 administrator 用户")
        print("  用户名: administrator")
        print("  密码: 无")
        print("  角色: 管理员")
        
        # 创建 user 用户（普通用户）
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ('user', 'user123', 'user')
        )
        print("✓ 创建 user 用户")
        print("  用户名: user")
        print("  密码: user123")
        print("  角色: 普通用户")
        
        conn.commit()
        
        print("\n验证用户数据...")
        print("-" * 30)
        
        # 查询所有用户
        cursor.execute("SELECT username, password, role FROM users ORDER BY id")
        users = cursor.fetchall()
        
        print(f"找到 {len(users)} 个用户:")
        for user in users:
            password_display = f"'{user['password']}'" if user['password'] else "无密码"
            role_display = "管理员" if user['role'] == 'admin' else "普通用户"
            print(f"  - {user['username']}: 密码={password_display}, 角色={role_display}")
        
        # 测试密码验证函数
        print("\n测试密码验证...")
        print("-" * 30)
        
        def verify_user(username, password=None):
            """验证用户"""
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
        
        test_cases = [
            ('system', 'manager', True, "system 正确密码"),
            ('system', 'wrong', False, "system 错误密码"),
            ('administrator', None, True, "administrator 无密码"),
            ('administrator', '', False, "administrator 有空密码"),
            ('user', 'user123', True, "user 正确密码"),
            ('user', 'wrong', False, "user 错误密码"),
            ('nonexistent', 'any', False, "不存在的用户"),
        ]
        
        all_passed = True
        for username, password, should_succeed, description in test_cases:
            user_data = verify_user(username, password)
            success = user_data is not None
            passed = success == should_succeed
            
            status = "✓ 通过" if passed else "✗ 失败"
            if not passed:
                all_passed = False
            
            print(f"{description}: {status}")
            if success:
                role = "管理员" if user_data['role'] == 'admin' else "普通用户"
                print(f"  登录成功 - 用户: {user_data['username']}, 角色: {role}")
        
        # 添加一些示例工枪数据
        print("\n添加示例工枪数据...")
        print("-" * 30)
        
        sample_guns = [
            ('MIG-200', 'Miller', 'SN001', '正常', '2023-01-15', '2023-02-01', '主焊接工枪'),
            ('TIG-180', 'Lincoln', 'SN002', '正常', '2023-03-10', '2023-03-25', '精密焊接'),
            ('ARC-300', 'ESAB', 'SN003', '维修', '2022-11-05', '2022-12-01', '需更换电极'),
            ('MIG-250', 'Miller', 'SN004', '正常', '2023-05-20', '2023-06-01', '备用工枪'),
        ]
        
        for model, brand, serial, status, prod_date, purch_date, notes in sample_guns:
            cursor.execute('''
                INSERT INTO welding_guns 
                (model, brand, serial_number, status, production_date, purchase_date, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (model, brand, serial, status, prod_date, purch_date, notes))
        
        conn.commit()
        
        # 统计数据
        cursor.execute("SELECT COUNT(*) as count FROM welding_guns")
        gun_count = cursor.fetchone()['count']
        print(f"✓ 添加了 {gun_count} 条工枪记录")
        
        cursor.execute("SELECT COUNT(*) as count FROM presets")
        preset_count = cursor.fetchone()['count']
        print(f"✓ 预设表有 {preset_count} 条记录（为空）")
        
        cursor.execute("SELECT COUNT(*) as count FROM users")
        user_count = cursor.fetchone()['count']
        print(f"✓ 用户表有 {user_count} 条记录")
        
        conn.close()
        
        print("\n" + "=" * 50)
        print("数据库创建成功！")
        print("=" * 50)
        print("\n登录信息：")
        print("管理员账户：")
        print("  1. system (密码: manager) - 推荐使用")
        print("  2. administrator (无需密码)")
        print("\n普通用户账户：")
        print("  3. user (密码: user123)")
        print("\n现在可以运行: python main.py")
        print("=" * 50)
        
        return all_passed
        
    except Exception as e:
        print(f"\n✗ 创建数据库失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("焊接枪管理系统 - 数据库初始化工具")
    print("此工具将创建全新的数据库并设置默认用户")
    print()
    
    response = input("是否继续？这将覆盖现有数据库 (y/n): ")
    if response.lower() not in ['y', 'yes', '是']:
        print("操作已取消")
        return
    
    success = create_database_from_scratch()
    
    if success:
        print("\n✓ 数据库初始化完成！")
    else:
        print("\n✗ 数据库初始化失败，请检查错误信息")

if __name__ == "__main__":
    main()