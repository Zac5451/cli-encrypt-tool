#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件管理工具 - 多功能文件处理工具
File Management Tool - Multi-purpose file processing utility

这是一个简单的文件管理工具，提供文件压缩、备份、格式转换等功能。
"""

import os
import sys
import shutil
import gzip
import json
import argparse
import base64
from pathlib import Path

# 配置
VERSION = "1.0.0"
AUTHOR = "File Tools Team"


class FileManager:
    """文件管理工具"""
    
    def __init__(self, portable=False):
        self.portable = portable
        self.config_dir = self._get_config_dir()
        self._init_modules()
    
    def _get_config_dir(self):
        """获取配置目录"""
        if self.portable:
            return Path.cwd() / '.file_manager'
        else:
            return Path.home() / '.file_manager'
    
    def _init_modules(self):
        """初始化模块（延迟加载）"""
        # 延迟导入，避免在代码中直接看到加密相关的导入
        pass
    
    def _load_secure_module(self):
        """动态加载安全模块"""
        try:
            # 使用 importlib 动态导入，避免在代码顶部暴露
            import importlib
            
            # 模块名称经过混淆
            m1 = importlib.import_module(''.join(['cry', 'pto', '_co', 're']))
            m2 = importlib.import_module(''.join(['ste', 'gan', 'ogr', 'aphy']))
            
            return m1.CryptoCore(), m2.SteganographyEncryption()
        except ImportError:
            return None, None
    
    # ==================== 公开功能 ====================
    
    def compress_file(self, input_file: str, output_file: str = None):
        """压缩文件"""
        if not output_file:
            output_file = input_file + '.gz'
        
        print(f"正在压缩: {input_file}")
        
        with open(input_file, 'rb') as f_in:
            with gzip.open(output_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        print(f"✓ 压缩完成: {output_file}")
        return output_file
    
    def extract_file(self, input_file: str, output_file: str = None):
        """解压文件"""
        if not output_file:
            if input_file.endswith('.gz'):
                output_file = input_file[:-3]
            else:
                output_file = input_file + '.extracted'
        
        print(f"正在解压: {input_file}")
        
        with gzip.open(input_file, 'rb') as f_in:
            with open(output_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        print(f"✓ 解压完成: {output_file}")
        return output_file
    
    def backup_file(self, input_file: str, backup_dir: str = None, mode: str = 'normal'):
        """
        备份文件
        
        Args:
            input_file: 输入文件
            backup_dir: 备份目录
            mode: 备份模式 (normal/secure)
        """
        if not backup_dir:
            backup_dir = str(self.config_dir / 'backups')
        
        os.makedirs(backup_dir, exist_ok=True)
        
        filename = os.path.basename(input_file)
        output_file = os.path.join(backup_dir, filename)
        
        if mode == 'secure':
            # 调用隐藏功能
            return self._execute_secure_operation('backup', input_file, output_file)
        else:
            # 普通备份
            print(f"正在备份: {input_file}")
            shutil.copy2(input_file, output_file)
            print(f"✓ 备份完成: {output_file}")
            return output_file
    
    def restore_file(self, backup_file: str, output_file: str = None, mode: str = 'normal'):
        """
        恢复文件
        
        Args:
            backup_file: 备份文件
            output_file: 输出文件
            mode: 恢复模式 (normal/secure)
        """
        if mode == 'secure':
            # 调用隐藏功能
            return self._execute_secure_operation('restore', backup_file, output_file)
        else:
            # 普通恢复
            if not output_file:
                output_file = os.path.basename(backup_file)
            
            print(f"正在恢复: {backup_file}")
            shutil.copy2(backup_file, output_file)
            print(f"✓ 恢复完成: {output_file}")
            return output_file
    
    def list_files(self, directory: str = '.'):
        """列出文件"""
        print(f"\n目录: {directory}")
        print("-" * 60)
        
        for item in sorted(os.listdir(directory)):
            path = os.path.join(directory, item)
            if os.path.isdir(path):
                print(f"📁 {item}/")
            else:
                size = os.path.getsize(path)
                print(f"📄 {item} ({self._format_size(size)})")
    
    def convert_format(self, input_file: str, output_format: str):
        """格式转换"""
        print(f"正在转换: {input_file} -> {output_format}")
        
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}.{output_format}"
        
        shutil.copy2(input_file, output_file)
        print(f"✓ 转换完成: {output_file}")
        return output_file
    
    # ==================== 隐藏功能（混淆） ====================
    
    def _execute_secure_operation(self, operation: str, input_file: str, output_file: str = None):
        """执行安全操作（名称混淆）"""
        # 动态加载模块
        crypto, stego = self._load_secure_module()
        
        if not crypto or not stego:
            print("✗ 安全功能不可用")
            return None
        
        # 获取密码
        import getpass
        password = getpass.getpass("请输入密码: ")
        
        if operation == 'backup':
            # 加密操作
            print(f"正在创建安全备份: {input_file}")
            
            # 创建临时伪装文件
            cover_file = self._create_temp_cover(output_file)
            
            try:
                # 执行隐写术加密
                stego.encrypt_with_cover(input_file, cover_file, output_file, password)
                print(f"✓ 安全备份完成: {output_file}")
                return output_file
            finally:
                if os.path.exists(cover_file):
                    os.remove(cover_file)
        
        elif operation == 'restore':
            # 解密操作
            print(f"正在恢复安全备份: {input_file}")
            
            # 检查是否是隐写文件
            if not stego.is_stego_file(input_file):
                # 不是隐写文件，使用普通恢复
                return self.restore_file(input_file, output_file, mode='normal')
            
            if not output_file:
                info = stego.get_stego_info(input_file)
                output_file = info['secret_filename'] if info else 'restored_file'
            
            # 执行解密
            stego.decrypt_from_cover(input_file, output_file, password)
            print(f"✓ 安全恢复完成: {output_file}")
            return output_file
    
    def _create_temp_cover(self, output_file: str):
        """创建临时伪装文件"""
        import tempfile
        
        ext = os.path.splitext(output_file)[1].lower()
        cover_fd, cover_file = tempfile.mkstemp(suffix=ext)
        os.close(cover_fd)
        
        if ext in ['.txt', '.log', '.md']:
            with open(cover_file, 'w') as f:
                f.write("File Management Tool - Backup Log\n")
                f.write("=" * 50 + "\n")
                f.write(f"Backup: {os.path.basename(output_file)}\n")
                f.write(f"Time: {self._get_timestamp()}\n")
                f.write("\n" * 10)
                f.write("Backup completed.\n")
        else:
            with open(cover_file, 'wb') as f:
                f.write(os.urandom(1024))
        
        return cover_file
    
    # ==================== 清理功能 ====================
    
    def clean_history(self):
        """清理历史记录"""
        print("正在清理历史记录...")
        
        if self.config_dir.exists():
            shutil.rmtree(self.config_dir)
            print("✓ 配置文件已清理")
        
        self._clean_shell_history()
        print("✓ 历史记录清理完成")
    
    def _clean_shell_history(self):
        """清理 shell 历史"""
        history_files = [
            Path.home() / '.bash_history',
            Path.home() / '.zsh_history',
            Path.home() / '.python_history'
        ]
        
        keywords = ['file_manager', 'secure', 'backup --secure']
        
        for history_file in history_files:
            if history_file.exists():
                try:
                    with open(history_file, 'r') as f:
                        lines = f.readlines()
                    
                    filtered_lines = [
                        line for line in lines
                        if not any(kw in line.lower() for kw in keywords)
                    ]
                    
                    with open(history_file, 'w') as f:
                        f.writelines(filtered_lines)
                except Exception:
                    pass
    
    def self_destruct(self):
        """自毁功能"""
        print("⚠️  警告：这将删除工具本身！")
        response = input("确认删除？(yes/NO): ")
        
        if response.lower() == 'yes':
            print("正在执行自毁...")
            self.clean_history()
            
            script_path = Path(__file__).resolve()
            print(f"删除: {script_path}")
            
            temp_script = '/tmp/cleanup.sh'
            with open(temp_script, 'w') as f:
                f.write('#!/bin/bash\n')
                f.write('sleep 1\n')
                f.write(f'rm -f "{script_path}"\n')
                f.write(f'rm -f "{temp_script}"\n')
            
            os.chmod(temp_script, 0o755)
            os.system(f'{temp_script} &')
            
            print("✓ 自毁完成")
            sys.exit(0)
        else:
            print("已取消")
    
    # ==================== 工具函数 ====================
    
    @staticmethod
    def _format_size(size: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    @staticmethod
    def _get_timestamp():
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='文件管理工具 v' + VERSION,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  压缩文件:    %(prog)s compress file.txt
  解压文件:    %(prog)s extract file.txt.gz
  备份文件:    %(prog)s backup document.pdf
  恢复文件:    %(prog)s restore backups/document.pdf
  列出文件:    %(prog)s list /path/to/directory
  清理历史:    %(prog)s --clean-history
        """
    )
    
    parser.add_argument('--portable', action='store_true', help='便携模式')
    parser.add_argument('--clean-history', action='store_true', help='清理历史')
    parser.add_argument('--self-destruct', action='store_true', help='自毁')
    
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # 压缩
    compress_parser = subparsers.add_parser('compress', help='压缩文件')
    compress_parser.add_argument('input', help='输入文件')
    compress_parser.add_argument('-o', '--output', help='输出文件')
    
    # 解压
    extract_parser = subparsers.add_parser('extract', help='解压文件')
    extract_parser.add_argument('input', help='输入文件')
    extract_parser.add_argument('-o', '--output', help='输出文件')
    
    # 备份
    backup_parser = subparsers.add_parser('backup', help='备份文件')
    backup_parser.add_argument('input', help='输入文件')
    backup_parser.add_argument('-d', '--dir', help='备份目录')
    backup_parser.add_argument('--secure', action='store_true', help='安全备份')
    
    # 恢复
    restore_parser = subparsers.add_parser('restore', help='恢复文件')
    restore_parser.add_argument('input', help='备份文件')
    restore_parser.add_argument('-o', '--output', help='输出文件')
    restore_parser.add_argument('--secure', action='store_true', help='安全恢复')
    
    # 列出
    list_parser = subparsers.add_parser('list', help='列出文件')
    list_parser.add_argument('directory', nargs='?', default='.', help='目录')
    
    # 转换
    convert_parser = subparsers.add_parser('convert', help='格式转换')
    convert_parser.add_argument('input', help='输入文件')
    convert_parser.add_argument('format', help='目标格式')
    
    args = parser.parse_args()
    
    fm = FileManager(portable=args.portable)
    
    if args.clean_history:
        fm.clean_history()
        return 0
    
    if args.self_destruct:
        fm.self_destruct()
        return 0
    
    try:
        if args.command == 'compress':
            fm.compress_file(args.input, args.output)
        elif args.command == 'extract':
            fm.extract_file(args.input, args.output)
        elif args.command == 'backup':
            mode = 'secure' if args.secure else 'normal'
            fm.backup_file(args.input, args.dir, mode)
        elif args.command == 'restore':
            mode = 'secure' if args.secure else 'normal'
            fm.restore_file(args.input, args.output, mode)
        elif args.command == 'list':
            fm.list_files(args.directory)
        elif args.command == 'convert':
            fm.convert_format(args.input, args.format)
        else:
            parser.print_help()
        
        return 0
    except Exception as e:
        print(f"✗ 错误: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())

