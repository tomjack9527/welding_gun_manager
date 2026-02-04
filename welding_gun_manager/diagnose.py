# welding_gun_manager/diagnose.py
import time
import os
import sys

def diagnose_imports():
    """诊断导入问题"""
    print("诊断导入问题...")
    print("=" * 60)
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 检查关键文件是否存在
    critical_files = [
        ('views/main_window.py', '主窗口模块'),
        ('views/login_dialog.py', '登录对话框'),
        ('controllers/__init__.py', '控制器包'),
        ('models/database.py', '数据库模块'),
        ('models/entities.py', '实体类'),
        ('welding_gun.db', '数据库文件'),
    ]
    
    all_exist = True
    for file_path, description in critical_files:
        full_path = os.path.join(current_dir, file_path)
        exists = os.path.exists(full_path)
        status = "✓ 存在" if exists else "✗ 不存在"
        print(f"{description:20} {status}")
        if not exists:
            all_exist = False
    
    print("\n" + "=" * 60)
    print("测试关键模块导入...")
    print("=" * 60)
    
    # 添加项目路径
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    test_modules = [
        ('tkinter', 'GUI库'),
        ('sqlite3', '数据库库'),
        ('models.database', '数据库类'),
        ('models.entities', '实体类'),
        ('controllers.gun_controller', '工枪控制器'),
        ('views.login_dialog', '登录对话框'),
    ]
    
    for module_name, description in test_modules:
        start_time = time.time()
        try:
            if '.' in module_name:
                # 处理点号导入
                parts = module_name.split('.')
                exec(f"import {parts[0]}")
                for i in range(1, len(parts)):
                    exec(f"from {'.'.join(parts[:i])} import {parts[i]}")
            else:
                exec(f"import {module_name}")
            
            elapsed = time.time() - start_time
            print(f"{description:20} ✓ 导入成功 ({elapsed:.3f}秒)")
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"{description:20} ✗ 导入失败: {type(e).__name__} ({elapsed:.3f}秒)")
    
    return all_exist

def test_database():
    """测试数据库连接"""
    print("\n" + "=" * 60)
    print("测试数据库连接...")
    print("=" * 60)
    
    try:
        import sqlite3
        start_time = time.time()
        
        if not os.path.exists("welding_gun.db"):
            print("✗ 数据库文件不存在")
            return False
        
        conn = sqlite3.connect("welding_gun.db")
        cursor = conn.cursor()
        
        # 检查表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        elapsed = time.time() - start_time
        print(f"✓ 数据库连接成功 ({elapsed:.3f}秒)")
        print(f"  找到 {len(tables)} 个表")
        
        for table in tables:
            print(f"    - {table[0]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ 数据库连接失败: {str(e)}")
        return False

def main():
    """主诊断函数"""
    print("焊接枪管理系统 - 诊断工具")
    print("=" * 60)
    
    print("开始诊断...")
    
    # 诊断导入
    imports_ok = diagnose_imports()
    
    # 测试数据库
    db_ok = test_database()
    
    print("\n" + "=" * 60)
    print("诊断结果:")
    print("=" * 60)
    
    if imports_ok and db_ok:
        print("✓ 所有检查通过！程序应该可以正常运行。")
        print("\n建议运行: python main_fast.py (快速启动版本)")
    else:
        print("✗ 发现问题，需要修复。")
        
        if not imports_ok:
            print("  - 某些关键文件缺失或导入失败")
        
        if not db_ok:
            print("  - 数据库连接有问题")
    
    print("\n按Enter键退出...")
    input()

if __name__ == "__main__":
    main()