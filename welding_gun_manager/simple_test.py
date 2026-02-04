# welding_gun_manager/simple_test.py
import tkinter as tk
import sqlite3
import os

def simple_login_test():
    """最简单的登录测试"""
    print("最简单的登录测试")
    print("=" * 50)
    
    # 检查数据库文件
    db_file = "welding_gun.db"
    if not os.path.exists(db_file):
        print(f"✗ 数据库文件不存在: {db_file}")
        return
    
    # 直接连接数据库测试
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 手动验证 system 用户
    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        ('system', 'manager')
    )
    user = cursor.fetchone()
    
    if user:
        print(f"✓ system 用户存在")
        print(f"  用户名: {user['username']}")
        print(f"  密码: {user['password']}")
        print(f"  角色: {user['role']}")
        
        # 创建简单的登录窗口测试
        root = tk.Tk()
        root.withdraw()
        
        from tkinter import simpledialog
        
        # 测试输入
        test_username = simpledialog.askstring("测试", "输入用户名:", initialvalue="system")
        if test_username == "system":
            test_password = simpledialog.askstring("测试", "输入密码:", initialvalue="manager", show="*")
            
            cursor.execute(
                "SELECT * FROM users WHERE username = ? AND password = ?",
                (test_username, test_password)
            )
            test_user = cursor.fetchone()
            
            if test_user:
                print(f"\n✓ 手动登录测试成功！")
                print(f"  用户: {test_user['username']}")
                print(f"  角色: {test_user['role']}")
            else:
                print(f"\n✗ 手动登录测试失败")
        else:
            print("\n测试取消")
        
        root.destroy()
    else:
        print(f"✗ system 用户不存在或密码错误")
    
    conn.close()

if __name__ == "__main__":
    simple_login_test()