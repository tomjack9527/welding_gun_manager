#!/usr/bin/env python3
"""
项目打包器 - 将Python项目转换为可分享的文本文件
"""

import os
import sys
import base64
import json
import zlib
import hashlib
from datetime import datetime
from pathlib import Path

class ProjectPacker:
    """项目打包器"""
    
    def __init__(self, project_root="."):
        self.project_root = Path(project_root).resolve()
        self.ignore_patterns = [
            "__pycache__",
            ".pyc",
            ".pyo",
            ".pyd",
            ".so",
            ".db",
            ".db-journal",
            ".log",
            ".tmp",
            ".temp",
            "*.zip",
            "*.7z",
            "*.rar",
            "uploaded_guns",  # 排除上传的文件
            "backups",        # 排除备份文件
            "venv",           # 排除虚拟环境
            ".git",           # 排除git目录
            ".vscode",
            ".idea",
            "node_modules",
        ]
        
        self.code_extensions = [
            '.py', '.txt', '.md', '.json', '.xml', '.yml', '.yaml',
            '.ini', '.cfg', '.conf', '.html', '.css', '.js'
        ]
        
    def should_include(self, filepath):
        """判断文件是否应该包含"""
        # 转换为相对路径
        try:
            rel_path = filepath.relative_to(self.project_root)
        except ValueError:
            return False
            
        # 检查忽略模式
        for pattern in self.ignore_patterns:
            if pattern.startswith('*'):
                if str(rel_path).endswith(pattern[1:]):
                    return False
            elif pattern in str(rel_path):
                return False
                
        # 检查文件扩展名
        if filepath.suffix.lower() in self.code_extensions:
            return True
            
        return False
    
    def read_file_safely(self, filepath):
        """安全读取文件内容"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return content
        except Exception as e:
            return f"# 读取文件失败: {str(e)}"
    
    def generate_project_report(self):
        """生成项目结构报告"""
        report = []
        
        # 项目统计
        code_files = []
        total_lines = 0
        total_size = 0
        
        for root, dirs, files in os.walk(self.project_root):
            root_path = Path(root)
            
            # 过滤目录
            dirs[:] = [d for d in dirs if not any(pattern in d for pattern in self.ignore_patterns)]
            
            for file in files:
                filepath = root_path / file
                if self.should_include(filepath):
                    try:
                        content = self.read_file_safely(filepath)
                        lines = content.count('\n') + 1
                        size = filepath.stat().st_size
                        
                        code_files.append({
                            'path': str(filepath.relative_to(self.project_root)),
                            'lines': lines,
                            'size': size,
                            'content': content
                        })
                        
                        total_lines += lines
                        total_size += size
                    except:
                        continue
        
        # 生成报告头
        report.append("=" * 80)
        report.append(f"项目打包报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 80)
        report.append("")
        report.append(f"项目根目录: {self.project_root}")
        report.append(f"文件数量: {len(code_files)}")
        report.append(f"代码行数: {total_lines}")
        report.append(f"总大小: {total_size / 1024:.1f} KB")
        report.append("")
        report.append("目录结构:")
        report.append("-" * 40)
        
        # 生成目录树
        for code_file in sorted(code_files, key=lambda x: x['path']):
            indent = "  " * code_file['path'].count(os.sep)
            report.append(f"{indent}📄 {code_file['path']} ({code_file['lines']}行, {code_file['size']}字节)")
        
        report.append("")
        report.append("文件内容:")
        report.append("=" * 80)
        
        # 添加文件内容
        for i, code_file in enumerate(code_files, 1):
            report.append(f"\n{'=' * 80}")
            report.append(f"文件 {i}/{len(code_files)}: {code_file['path']}")
            report.append(f"大小: {code_file['size']}字节 | 行数: {code_file['lines']}")
            report.append(f"{'=' * 80}\n")
            report.append(code_file['content'])
        
        return "\n".join(report), code_files
    
    def compress_report(self, report_text):
        """压缩报告文本"""
        # 先压缩再Base64编码
        compressed = zlib.compress(report_text.encode('utf-8'), level=9)
        encoded = base64.b64encode(compressed).decode('ascii')
        
        # 计算校验和
        checksum = hashlib.md5(report_text.encode('utf-8')).hexdigest()
        
        return {
            'compressed': encoded,
            'checksum': checksum,
            'original_size': len(report_text),
            'compressed_size': len(encoded)
        }
    
    def save_report(self, output_file="project_report.txt"):
        """保存报告到文件"""
        report_text, _ = self.generate_project_report()
        
        print(f"生成报告中...")
        print(f"原始大小: {len(report_text)} 字节")
        
        # 如果文件太大，分割
        max_size = 100 * 1024  # 100KB
        if len(report_text) > max_size:
            print("文件较大，进行分割...")
            return self.save_split_report(report_text, output_file)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        print(f"报告已保存到: {output_file}")
        print(f"文件大小: {os.path.getsize(output_file) / 1024:.1f} KB")
        return output_file
    
    def save_split_report(self, report_text, output_file="project_report"):
        """保存分割的报告"""
        max_chunk = 80 * 1024  # 80KB 每个分块
        
        parts = []
        for i in range(0, len(report_text), max_chunk):
            chunk = report_text[i:i + max_chunk]
            part_num = len(parts) + 1
            part_file = f"{output_file}_part{part_num:02d}.txt"
            
            # 添加分块信息头
            header = f"项目分块 {part_num}/{len(report_text)//max_chunk + 1}\n"
            header += f"总大小: {len(report_text)} 字节\n"
            header += f"本块: {len(chunk)} 字节\n"
            header += "=" * 60 + "\n\n"
            
            with open(part_file, 'w', encoding='utf-8') as f:
                f.write(header + chunk)
            
            parts.append(part_file)
            print(f"创建分块 {part_num}: {part_file} ({len(chunk)/1024:.1f} KB)")
        
        # 创建索引文件
        index_file = f"{output_file}_index.txt"
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(f"项目分块索引\n")
            f.write(f"生成时间: {datetime.now()}\n")
            f.write(f"总大小: {len(report_text)} 字节\n")
            f.write(f"分块数量: {len(parts)}\n")
            f.write("=" * 60 + "\n\n")
            for part in parts:
                f.write(f"{part}\n")
        
        print(f"索引文件: {index_file}")
        print(f"请上传所有分块文件")
        return parts

def main():
    """主函数"""
    print("🏭 焊枪管理系统 - 项目打包工具")
    print("=" * 50)
    
    # 自动检测项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir
    
    packer = ProjectPacker(project_root)
    
    # 打包选项
    print("\n选择打包选项:")
    print("1. 生成完整代码报告")
    print("2. 只生成核心文件")
    print("3. 压缩打包（Base64）")
    print("4. 分析项目结构")
    
    choice = input("\n请选择 (1-4, 默认1): ").strip() or "1"
    
    if choice == "1":
        output_file = packer.save_report("welding_gun_project_full.txt")
        print(f"\n✅ 完整报告已生成: {output_file}")
        
    elif choice == "2":
        # 只打包核心文件
        core_files = packer.save_core_files("welding_gun_project_core.txt")
        print(f"\n✅ 核心文件报告已生成")
        
    elif choice == "3":
        # 压缩打包
        compressed = packer.compress_and_save("welding_gun_project_compressed.txt")
        print(f"\n✅ 压缩报告已生成")
        
    elif choice == "4":
        # 分析项目结构
        packer.analyze_project()
        
    else:
        print("无效选择")

if __name__ == "__main__":
    main()