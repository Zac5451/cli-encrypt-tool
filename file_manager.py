#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件管理工具 - 多功能文件处理工具
File Management Tool - Multi-purpose file processing utility

功能包括：
- 文件压缩和解压
- 文件备份和恢复
- 格式转换
- 安全功能（可选）
"""

import os
import sys
import shutil
import gzip
import json
import argparse
from pathlib import Path

# 导入核心功能（隐藏导入）
try:
    from crypto_core import CryptoCore
    from steganography import SteganographyEncryption
    from biometric_auth import BiometricPasswordManager
    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False


class FileManager:
    """多功能文件管理工具"""
    
    def __init__(self, portable=False):
        self.portable = portable
        self.config_dir = self._get_config_dir()
        
        if SECURITY_AVAILABLE:
            self.crypto = CryptoCore()
            self.stego = SteganographyEncryption()
            self.biometric = BiometricPasswordManager()
    
    def _get_config_dir(self):
        """获取配置目录"""
        if self.portable:
            # 便携模式：使用当前目录
            return Path.cwd() / '.file_manager'
        else:
            # 标准模式：使用用户目录
            return Path.home() / '.file_manager'
    
    # ==================== 真实功能（掩护） ====================
    
    def compress_file(self, input_file: str, output_file: str = None):
        """压缩文件（真实功能）"""
        if not output_file:
            output_file = input_file + '.gz'
        
        print(f"正在压缩: {input_file}")
        
        with open(input_file, 'rb') as f_in:
            with gzip.open(output_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        print(f"✓ 压缩完成: {output_file}")
        return output_file
    
    def extract_file(self, input_file: str, output_file: str = None):
        """解压文件（真实功能）"""
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
    
    def backup_file(self, input_file: str, backup_dir: str = None, secure: bool = False):
        """
        备份文件（真实功能 + 隐藏的加密功能）
        
        Args:
            input_file: 输入文件
            backup_dir: 备份目录
            secure: 是否使用安全备份（隐藏的加密功能）
        """
        if not backup_dir:
            backup_dir = str(self.config_dir / 'backups')
        
        os.makedirs(backup_dir, exist_ok=True)
        
        filename = os.path.basename(input_file)
        output_file = os.path.join(backup_dir, filename)
        
        if secure and SECURITY_AVAILABLE:
            # 隐藏的加密功能
            return self._secure_backup(input_file, output_file)
        else:
            # 普通备份
            print(f"正在备份: {input_file}")
            shutil.copy2(input_file, output_file)
            print(f"✓ 备份完成: {output_file}")
            return output_file
    
    def restore_file(self, backup_file: str, output_file: str = None, secure: bool = False):
        """
        恢复文件（真实功能 + 隐藏的解密功能）
        
        Args:
            backup_file: 备份文件
            output_file: 输出文件
            secure: 是否使用安全恢复（隐藏的解密功能）
        """
        if secure and SECURITY_AVAILABLE:
            # 隐藏的解密功能
            return self._secure_restore(backup_file, output_file)
        else:
            # 普通恢复
            if not output_file:
                output_file = os.path.basename(backup_file)
            
            print(f"正在恢复: {backup_file}")
            shutil.copy2(backup_file, output_file)
            print(f"✓ 恢复完成: {output_file}")
            return output_file
    
    def list_files(self, directory: str = '.'):
        """列出文件（真实功能）"""
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
        """格式转换（真实功能 - 简单实现）"""
        print(f"正在转换: {input_file} -> {output_format}")
        
        # 简单的格式转换（可以扩展）
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}.{output_format}"
        
        shutil.copy2(input_file, output_file)
        print(f"✓ 转换完成: {output_file}")
        return output_file
    
    # ==================== 隐藏的安全功能 ====================
    
    def _secure_backup(self, input_file: str, output_file: str):
        """安全备份（隐藏的加密功能）"""
        if not SECURITY_AVAILABLE:
            raise ValueError("安全功能不可用")
        
        print(f"正在创建安全备份: {input_file}")
        
        # 获取密码
        password = self._get_password("secure")
        
        # 创建伪装文件
        cover_file = self._create_cover_file(output_file)
        
        # 隐写术加密
        self.stego.encrypt_with_cover(
            input_file, cover_file, output_file, password
        )
        
        # 清理临时文件
        if os.path.exists(cover_file):
            os.remove(cover_file)
        
        print(f"✓ 安全备份完成: {output_file}")
        return output_file
    
    def _secure_restore(self, backup_file: str, output_file: str):
        """安全恢复（隐藏的解密功能）"""
        if not SECURITY_AVAILABLE:
            raise ValueError("安全功能不可用")
        
        print(f"正在恢复安全备份: {backup_file}")
        
        # 检查是否是隐写文件
        if not self.stego.is_stego_file(backup_file):
            # 不是隐写文件，使用普通恢复
            return self.restore_file(backup_file, output_file, secure=False)
        
        # 获取密码
        password = self._get_password("secure")
        
        if not output_file:
            info = self.stego.get_stego_info(backup_file)
            output_file = info['secret_filename'] if info else 'restored_file'
        
        # 解密
        self.stego.decrypt_from_cover(backup_file, output_file, password)
        
        print(f"✓ 安全恢复完成: {output_file}")
        return output_file
    
    def _create_cover_file(self, output_file: str):
        """创建伪装文件"""
        import tempfile
        
        # 根据输出文件类型创建合适的伪装文件
        ext = os.path.splitext(output_file)[1].lower()
        
        cover_fd, cover_file = tempfile.mkstemp(suffix=ext)
        os.close(cover_fd)
        
        if ext in ['.txt', '.log', '.md']:
            # 创建文本伪装
            with open(cover_file, 'w') as f:
                f.write("File Management Tool - Backup Log\n")
                f.write("=" * 50 + "\n")
                f.write(f"Backup created: {os.path.basename(output_file)}\n")
                f.write(f"Timestamp: {self._get_timestamp()}\n")
                f.write("\n" * 10)
                f.write("Backup completed successfully.\n")
        else:
            # 创建二进制伪装
            with open(cover_file, 'wb') as f:
                f.write(os.urandom(1024))
        
        return cover_file
    
    def _get_password(self, mode: str):
        """获取密码（支持生物识别）"""
        import getpass
        
        # 尝试使用生物识别
        if hasattr(self, 'biometric'):
            # 这里可以集成生物识别
            pass
        
        # 手动输入密码
        return getpass.getpass("请输入密码: ")
    
    # ==================== 清理功能 ====================
    
    def clean_history(self):
        """清理使用历史"""
        print("正在清理历史记录...")
        
        # 清理配置目录
        if self.config_dir.exists():
            shutil.rmtree(self.config_dir)
            print("✓ 配置文件已清理")
        
        # 清理 shell 历史中的相关命令
        self._clean_shell_history()
        
        print("✓ 历史记录清理完成")
    
    def _clean_shell_history(self):
        """清理 shell 历史"""
        history_files = [
            Path.home() / '.bash_history',
            Path.home() / '.zsh_history',
            Path.home() / '.python_history'
        ]
        
        for history_file in history_files:
            if history_file.exists():
                try:
                    # 读取历史
                    with open(history_file, 'r') as f:
                        lines = f.readlines()
                    
                    # 过滤掉包含敏感关键词的行
                    keywords = ['file_manager', 'secure', 'stego', 'encrypt']
                    filtered_lines = [
                        line for line in lines
                        if not any(kw in line.lower() for kw in keywords)
                    ]
                    
                    # 写回
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
            
            # 清理历史
            self.clean_history()
            
            # 删除自身
            script_path = Path(__file__).resolve()
            print(f"删除: {script_path}")
            
            # 创建一个临时脚本来删除自身
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
        description='文件管理工具 - 多功能文件处理',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  压缩文件:
    %(prog)s compress file.txt
  
  解压文件:
    %(prog)s extract file.txt.gz
  
  备份文件:
    %(prog)s backup document.pdf
  
  恢复文件:
    %(prog)s restore backups/document.pdf
  
  列出文件:
    %(prog)s list /path/to/directory
  
  清理历史:
    %(prog)s --clean-history
        """
    )
    
    parser.add_argument('--portable', action='store_true', help='便携模式（不在系统留下痕迹）')
    parser.add_argument('--clean-history', action='store_true', help='清理使用历史')
    parser.add_argument('--self-destruct', action='store_true', help='自毁（删除工具本身）')
    
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # 压缩命令
    compress_parser = subparsers.add_parser('compress', help='压缩文件')
    compress_parser.add_argument('input', help='输入文件')
    compress_parser.add_argument('-o', '--output', help='输出文件')
    
    # 解压命令
    extract_parser = subparsers.add_parser('extract', help='解压文件')
    extract_parser.add_argument('input', help='输入文件')
    extract_parser.add_argument('-o', '--output', help='输出文件')
    
    # 备份命令
    backup_parser = subparsers.add_parser('backup', help='备份文件')
    backup_parser.add_argument('input', help='输入文件')
    backup_parser.add_argument('-d', '--dir', help='备份目录')
    backup_parser.add_argument('--secure', action='store_true', help='安全备份（加密）')
    
    # 恢复命令
    restore_parser = subparsers.add_parser('restore', help='恢复文件')
    restore_parser.add_argument('input', help='备份文件')
    restore_parser.add_argument('-o', '--output', help='输出文件')
    restore_parser.add_argument('--secure', action='store_true', help='安全恢复（解密）')
    
    # 列出文件命令
    list_parser = subparsers.add_parser('list', help='列出文件')
    list_parser.add_argument('directory', nargs='?', default='.', help='目录路径')
    
    # 格式转换命令
    convert_parser = subparsers.add_parser('convert', help='格式转换')
    convert_parser.add_argument('input', help='输入文件')
    convert_parser.add_argument('format', help='目标格式')
    
    args = parser.parse_args()
    
    # 创建文件管理器
    fm = FileManager(portable=args.portable)
    
    # 处理全局选项
    if args.clean_history:
        fm.clean_history()
        return 0
    
    if args.self_destruct:
        fm.self_destruct()
        return 0
    
    # 处理命令
    try:
        if args.command == 'compress':
            fm.compress_file(args.input, args.output)
        
        elif args.command == 'extract':
            fm.extract_file(args.input, args.output)
        
        elif args.command == 'backup':
            fm.backup_file(args.input, args.dir, args.secure)
        
        elif args.command == 'restore':
            fm.restore_file(args.input, args.output, args.secure)
        
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

