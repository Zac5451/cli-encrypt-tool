#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
隐写术加密模块
将加密文件伪装成普通文件，实现隐蔽加密
"""

import os
import struct
import hashlib
import mimetypes
from typing import Optional, Tuple
from crypto_core import CryptoCore


class SteganographyEncryption:
    """隐写术加密类 - 将加密数据隐藏在普通文件中"""
    
    # 魔数标记（隐藏在文件末尾）
    MAGIC_MARKER = b'STEG'
    VERSION = 1
    
    # 支持的伪装文件类型
    COVER_TYPES = {
        'text': ['.txt', '.log', '.md', '.json', '.xml', '.csv'],
        'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
        'video': ['.mp4', '.avi', '.mov', '.mkv', '.flv'],
        'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg'],
        'document': ['.pdf', '.doc', '.docx', '.xls', '.xlsx'],
        'archive': ['.zip', '.rar', '.7z', '.tar', '.gz']
    }
    
    def __init__(self):
        self.crypto = CryptoCore()
    
    def encrypt_with_cover(
        self,
        secret_file: str,
        cover_file: str,
        output_file: str,
        password: str,
        keep_cover_functional: bool = True
    ) -> dict:
        """
        使用伪装文件加密
        
        Args:
            secret_file: 要加密的秘密文件
            cover_file: 用作伪装的普通文件
            output_file: 输出文件路径
            password: 加密密码
            keep_cover_functional: 是否保持伪装文件可用
            
        Returns:
            dict: 加密信息
        """
        # 1. 加密秘密文件到临时文件
        import tempfile
        temp_encrypted = tempfile.mktemp(suffix='.enc')
        
        try:
            # 加密秘密文件
            self.crypto.encrypt_file(secret_file, temp_encrypted, password)
            
            # 读取加密数据
            with open(temp_encrypted, 'rb') as f:
                encrypted_data = f.read()
            
            # 读取伪装文件
            with open(cover_file, 'rb') as f:
                cover_data = f.read()
            
            # 构建隐写文件
            with open(output_file, 'wb') as f:
                # 1. 写入伪装文件数据
                f.write(cover_data)
                
                # 2. 写入分隔符和元数据
                separator_offset = len(cover_data)
                
                # 3. 写入加密数据
                f.write(encrypted_data)
                
                # 4. 写入尾部标记
                footer = self._create_footer(
                    separator_offset,
                    len(encrypted_data),
                    os.path.basename(secret_file),
                    os.path.basename(cover_file)
                )
                f.write(footer)
            
            # 如果需要保持伪装文件可用，复制文件属性
            if keep_cover_functional:
                self._preserve_file_attributes(cover_file, output_file)
            
            return {
                'secret_file': secret_file,
                'cover_file': cover_file,
                'output_file': output_file,
                'cover_size': len(cover_data),
                'encrypted_size': len(encrypted_data),
                'total_size': os.path.getsize(output_file),
                'cover_type': self._detect_file_type(cover_file)
            }
            
        finally:
            if os.path.exists(temp_encrypted):
                os.remove(temp_encrypted)
    
    def decrypt_from_cover(
        self,
        stego_file: str,
        output_file: str,
        password: str
    ) -> dict:
        """
        从伪装文件中解密
        
        Args:
            stego_file: 包含隐藏数据的文件
            output_file: 输出文件路径
            password: 解密密码
            
        Returns:
            dict: 解密信息
        """
        import tempfile
        
        # 1. 读取文件并解析尾部标记
        with open(stego_file, 'rb') as f:
            # 读取整个文件
            file_data = f.read()
            file_size = len(file_data)
            
            # 查找魔数标记
            footer_start = self._find_footer(file_data)
            if footer_start == -1:
                raise ValueError("这不是一个有效的隐写加密文件")
            
            # 解析尾部信息
            footer_data = file_data[footer_start:]
            metadata = self._parse_footer(footer_data)
            
            # 提取加密数据
            encrypted_start = metadata['separator_offset']
            encrypted_end = footer_start
            encrypted_data = file_data[encrypted_start:encrypted_end]
        
        # 2. 解密数据
        temp_encrypted = tempfile.mktemp(suffix='.enc')
        temp_decrypted = tempfile.mktemp()
        
        try:
            # 写入临时加密文件
            with open(temp_encrypted, 'wb') as f:
                f.write(encrypted_data)
            
            # 解密
            self.crypto.decrypt_file(temp_encrypted, temp_decrypted, password)
            
            # 移动到目标位置
            import shutil
            shutil.move(temp_decrypted, output_file)
            
            return {
                'stego_file': stego_file,
                'output_file': output_file,
                'original_secret_name': metadata['secret_filename'],
                'original_cover_name': metadata['cover_filename'],
                'decrypted_size': os.path.getsize(output_file)
            }
            
        finally:
            for tmp in [temp_encrypted, temp_decrypted]:
                if os.path.exists(tmp):
                    os.remove(tmp)
    
    def extract_cover(self, stego_file: str, output_file: str) -> dict:
        """
        提取伪装文件（不解密秘密数据）
        
        Args:
            stego_file: 包含隐藏数据的文件
            output_file: 输出的伪装文件路径
            
        Returns:
            dict: 提取信息
        """
        with open(stego_file, 'rb') as f:
            file_data = f.read()
            
            # 查找尾部标记
            footer_start = self._find_footer(file_data)
            if footer_start == -1:
                raise ValueError("这不是一个有效的隐写加密文件")
            
            # 解析元数据
            footer_data = file_data[footer_start:]
            metadata = self._parse_footer(footer_data)
            
            # 提取伪装文件数据
            cover_data = file_data[:metadata['separator_offset']]
        
        # 写入伪装文件
        with open(output_file, 'wb') as f:
            f.write(cover_data)
        
        return {
            'stego_file': stego_file,
            'cover_file': output_file,
            'cover_size': len(cover_data),
            'cover_filename': metadata['cover_filename']
        }
    
    def is_stego_file(self, filepath: str) -> bool:
        """
        检查文件是否是隐写加密文件
        
        Args:
            filepath: 文件路径
            
        Returns:
            bool: 是否是隐写文件
        """
        try:
            with open(filepath, 'rb') as f:
                file_data = f.read()
                return self._find_footer(file_data) != -1
        except Exception:
            return False
    
    def get_stego_info(self, filepath: str) -> Optional[dict]:
        """
        获取隐写文件信息（不解密）
        
        Args:
            filepath: 文件路径
            
        Returns:
            Optional[dict]: 文件信息
        """
        try:
            with open(filepath, 'rb') as f:
                file_data = f.read()
                footer_start = self._find_footer(file_data)
                
                if footer_start == -1:
                    return None
                
                footer_data = file_data[footer_start:]
                metadata = self._parse_footer(footer_data)
                
                return {
                    'is_stego': True,
                    'total_size': len(file_data),
                    'cover_size': metadata['separator_offset'],
                    'encrypted_size': metadata['encrypted_size'],
                    'secret_filename': metadata['secret_filename'],
                    'cover_filename': metadata['cover_filename'],
                    'cover_type': self._detect_file_type(filepath)
                }
        except Exception:
            return None
    
    def create_dummy_cover(self, cover_type: str, output_file: str, size_kb: int = 10) -> str:
        """
        创建虚拟伪装文件
        
        Args:
            cover_type: 文件类型 (text/image/video等)
            output_file: 输出文件路径
            size_kb: 文件大小（KB）
            
        Returns:
            str: 创建的文件路径
        """
        if cover_type == 'text':
            # 创建文本文件
            content = self._generate_dummy_text(size_kb * 1024)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
        
        elif cover_type == 'image':
            # 创建简单的图片（需要 PIL）
            try:
                from PIL import Image
                import random
                
                # 创建随机噪点图片
                width, height = 800, 600
                img = Image.new('RGB', (width, height))
                pixels = img.load()
                
                for i in range(width):
                    for j in range(height):
                        pixels[i, j] = (
                            random.randint(0, 255),
                            random.randint(0, 255),
                            random.randint(0, 255)
                        )
                
                img.save(output_file)
            except ImportError:
                raise ValueError("需要安装 Pillow: pip install Pillow")
        
        elif cover_type == 'binary':
            # 创建二进制文件
            with open(output_file, 'wb') as f:
                f.write(os.urandom(size_kb * 1024))
        
        else:
            raise ValueError(f"不支持的类型: {cover_type}")
        
        return output_file
    
    def _create_footer(
        self,
        separator_offset: int,
        encrypted_size: int,
        secret_filename: str,
        cover_filename: str
    ) -> bytes:
        """创建尾部标记"""
        # 编码文件名
        secret_name_bytes = secret_filename.encode('utf-8')
        cover_name_bytes = cover_filename.encode('utf-8')
        
        footer = b''
        footer += struct.pack('<I', separator_offset)  # 分隔符偏移
        footer += struct.pack('<I', encrypted_size)    # 加密数据大小
        footer += struct.pack('<H', len(secret_name_bytes))  # 秘密文件名长度
        footer += secret_name_bytes                    # 秘密文件名
        footer += struct.pack('<H', len(cover_name_bytes))   # 伪装文件名长度
        footer += cover_name_bytes                     # 伪装文件名
        footer += struct.pack('<B', self.VERSION)      # 版本号
        footer += self.MAGIC_MARKER                    # 魔数
        
        return footer
    
    def _find_footer(self, data: bytes) -> int:
        """查找尾部标记位置"""
        # 从文件末尾向前查找魔数
        marker_pos = data.rfind(self.MAGIC_MARKER)
        if marker_pos == -1:
            return -1
        
        # 验证版本号
        if marker_pos < 1:
            return -1
        
        version = data[marker_pos - 1]
        if version != self.VERSION:
            return -1
        
        # 计算尾部起始位置
        # 需要向前读取以找到完整的尾部
        # 最小尾部大小：4+4+2+2+1+4 = 17字节
        min_footer_size = 17
        
        if marker_pos < min_footer_size:
            return -1
        
        # 尝试解析以找到真正的起始位置
        try:
            # 从魔数位置向前读取
            pos = marker_pos - 1  # 跳过版本号
            
            # 读取伪装文件名长度
            pos -= 2
            cover_name_len = struct.unpack('<H', data[pos:pos+2])[0]
            
            # 读取伪装文件名
            pos -= cover_name_len
            
            # 读取秘密文件名长度
            pos -= 2
            secret_name_len = struct.unpack('<H', data[pos:pos+2])[0]
            
            # 读取秘密文件名
            pos -= secret_name_len
            
            # 读取加密数据大小和分隔符偏移
            pos -= 8
            
            return pos
            
        except Exception:
            return -1
    
    def _parse_footer(self, footer_data: bytes) -> dict:
        """解析尾部标记"""
        pos = 0
        
        # 读取分隔符偏移
        separator_offset = struct.unpack('<I', footer_data[pos:pos+4])[0]
        pos += 4
        
        # 读取加密数据大小
        encrypted_size = struct.unpack('<I', footer_data[pos:pos+4])[0]
        pos += 4
        
        # 读取秘密文件名
        secret_name_len = struct.unpack('<H', footer_data[pos:pos+2])[0]
        pos += 2
        secret_filename = footer_data[pos:pos+secret_name_len].decode('utf-8')
        pos += secret_name_len
        
        # 读取伪装文件名
        cover_name_len = struct.unpack('<H', footer_data[pos:pos+2])[0]
        pos += 2
        cover_filename = footer_data[pos:pos+cover_name_len].decode('utf-8')
        
        return {
            'separator_offset': separator_offset,
            'encrypted_size': encrypted_size,
            'secret_filename': secret_filename,
            'cover_filename': cover_filename
        }
    
    def _detect_file_type(self, filepath: str) -> str:
        """检测文件类型"""
        ext = os.path.splitext(filepath)[1].lower()
        
        for type_name, extensions in self.COVER_TYPES.items():
            if ext in extensions:
                return type_name
        
        return 'unknown'
    
    def _preserve_file_attributes(self, source: str, target: str):
        """保留文件属性"""
        try:
            stat = os.stat(source)
            os.utime(target, (stat.st_atime, stat.st_mtime))
        except Exception:
            pass
    
    def _generate_dummy_text(self, size: int) -> str:
        """生成虚拟文本内容"""
        lorem = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. 
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum.
Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia.

"""
        
        # 重复文本直到达到目标大小
        content = ""
        while len(content.encode('utf-8')) < size:
            content += lorem
        
        return content[:size]


# 命令行接口
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='隐写术加密工具')
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # 加密命令
    encrypt_parser = subparsers.add_parser('encrypt', help='隐写加密')
    encrypt_parser.add_argument('secret', help='要加密的秘密文件')
    encrypt_parser.add_argument('cover', help='伪装文件')
    encrypt_parser.add_argument('-o', '--output', required=True, help='输出文件')
    encrypt_parser.add_argument('-p', '--password', required=True, help='密码')
    
    # 解密命令
    decrypt_parser = subparsers.add_parser('decrypt', help='隐写解密')
    decrypt_parser.add_argument('input', help='隐写文件')
    decrypt_parser.add_argument('-o', '--output', required=True, help='输出文件')
    decrypt_parser.add_argument('-p', '--password', required=True, help='密码')
    
    # 提取伪装文件
    extract_parser = subparsers.add_parser('extract-cover', help='提取伪装文件')
    extract_parser.add_argument('input', help='隐写文件')
    extract_parser.add_argument('-o', '--output', required=True, help='输出文件')
    
    # 检查文件
    info_parser = subparsers.add_parser('info', help='查看文件信息')
    info_parser.add_argument('file', help='文件路径')
    
    args = parser.parse_args()
    
    stego = SteganographyEncryption()
    
    if args.command == 'encrypt':
        result = stego.encrypt_with_cover(
            args.secret, args.cover, args.output, args.password
        )
        print(f"✓ 隐写加密成功")
        print(f"  秘密文件: {result['secret_file']}")
        print(f"  伪装文件: {result['cover_file']}")
        print(f"  输出文件: {result['output_file']}")
        print(f"  总大小: {result['total_size']} 字节")
    
    elif args.command == 'decrypt':
        result = stego.decrypt_from_cover(args.input, args.output, args.password)
        print(f"✓ 隐写解密成功")
        print(f"  输出文件: {result['output_file']}")
        print(f"  原始文件名: {result['original_secret_name']}")
    
    elif args.command == 'extract-cover':
        result = stego.extract_cover(args.input, args.output)
        print(f"✓ 伪装文件提取成功")
        print(f"  输出文件: {result['cover_file']}")
    
    elif args.command == 'info':
        info = stego.get_stego_info(args.file)
        if info:
            print(f"✓ 这是一个隐写加密文件")
            print(f"  总大小: {info['total_size']} 字节")
            print(f"  伪装文件大小: {info['cover_size']} 字节")
            print(f"  加密数据大小: {info['encrypted_size']} 字节")
            print(f"  秘密文件名: {info['secret_filename']}")
            print(f"  伪装文件名: {info['cover_filename']}")
        else:
            print("✗ 这不是隐写加密文件")

