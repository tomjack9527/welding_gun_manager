# welding_gun_manager/setup.py
import subprocess
import sys
import os

def install_packages():
    """安装必要的Python包"""
    packages = [
        'pandas>=1.5.0',
        'openpyxl>=3.0.0'
    ]
    
    print("正在安装必要的依赖包...")
    
    for package in packages:
        print(f"正在安装 {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"{package} 安装成功")
        except subprocess.CalledProcessError as e:
            print(f"{package} 安装失败: {e}")
            print("请手动安装: pip install pandas openpyxl")
    
    print("\n依赖包安装完成！")

def create_directories():
    """创建必要的目录"""
    directories = [
        'data',
        'backups',
        'resources/images',
        'resources/documents',
        'logs'
    ]
    
    print("正在创建目录结构...")
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"创建目录: {directory}")
    
    print("目录结构创建完成！")

def main():
    """主安装函数"""
    print("=" * 50)
    print("焊接枪管理系统 - 安装程序")
    print("=" * 50)
    
    # 创建目录
    create_directories()
    
    # 询问是否安装包
    response = input("\n是否安装必要的Python包？(y/n): ")
    if response.lower() in ['y', 'yes', '是']:
        install_packages()
    else:
        print("跳过包安装，请确保已安装必要的依赖")
        print("需要安装: pandas, openpyxl")
        print("命令: pip install pandas openpyxl")
    
    print("\n" + "=" * 50)
    print("安装完成！")
    print("现在可以运行: python main.py")
    print("=" * 50)

if __name__ == "__main__":
    main()