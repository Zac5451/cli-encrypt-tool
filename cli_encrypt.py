#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级命令行加密工具
支持多算法、自毁文件、流式加密、交互模式等
"""

import os
import sys
import getpass
import argparse
import glob as glob_module
import configparser
from pathlib import Path
from typing import Optional, Callable
from io import BytesIO

from crypto_core import CryptoCore, BruteForceProtection
from biometric_auth import BiometricAuth, BiometricPasswordManager
from steganography import SteganographyEncryption

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False


DEFAULT_CONFIG = """[encryption]
algorithm = aes256
kdf = argon2
threads = 4
signature = false

[security]
hide_metadata = true
brute_force_protection = true

[defaults]
compress = true
"""


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


class CLIEncryptTool:
    """高级命令行加密工具"""
    
    def __init__(self, verbose: bool = False, config_file: Optional[str] = None):
        self.crypto = None
        self.verbose = verbose
        self._progress_bar = None
        self.config = self._load_config(config_file)
        self.biometric_manager = BiometricPasswordManager()
        self.stego = SteganographyEncryption()
    
    def _load_config(self, config_file: Optional[str]) -> configparser.ConfigParser:
        """加载配置文件"""
        config = configparser.ConfigParser()
        config.read_string(DEFAULT_CONFIG)
        
        if config_file and os.path.exists(config_file):
            config.read(config_file)
        else:
            user_config = os.path.expanduser('~/.cli-encryptrc')
            if os.path.exists(user_config):
                config.read(user_config)
        
        return config
    
    def log(self, message: str):
        """输出详细日志"""
        if self.verbose:
            print(f"{Colors.OKCYAN}[VERBOSE] {message}{Colors.ENDC}")
    
    def print_banner(self):
        banner = f"""
{Colors.OKCYAN}{Colors.BOLD}
╔═══════════════════════════════════════════════════════════════════════╗
║                    CLI 高级加密工具 v2.0                             ║
║              支持多算法 | 自毁文件 | 流式加密 | 交互模式             ║
╚═══════════════════════════════════════════════════════════════════════╝
{Colors.ENDC}
"""
        print(banner)
    
    def encrypt_command(self, args):
        """加密命令"""
        input_file = args.input
        output_file = args.output
        
        if not os.path.exists(input_file):
            print(f"{Colors.FAIL}✗ 错误：输入文件不存在: {input_file}{Colors.ENDC}")
            return 1
        
        if not output_file:
            output_file = input_file + '.encrypted'
        
        if os.path.exists(output_file) and not args.force:
            print(f"{Colors.WARNING}⚠ 警告：输出文件已存在: {output_file}{Colors.ENDC}")
            response = input("是否覆盖？(y/N): ")
            if response.lower() != 'y':
                print("操作已取消")
                return 0
        
        password = self._get_password_for_encryption(args.password, input_file)
        if not password:
            return 1
        
        kdf_type = self._select_kdf(args.kdf)
        algorithm = self._select_algorithm(args.algorithm)
        
        try:
            self.crypto = CryptoCore(
                kdf_type=kdf_type,
                algorithm=algorithm,
                threads=args.threads,
                enable_signature=args.sign
            )
            
            print(f"\n{Colors.OKBLUE}📁 输入文件: {input_file}{Colors.ENDC}")
            print(f"{Colors.OKBLUE}📁 输出文件: {output_file}{Colors.ENDC}")
            print(f"{Colors.OKBLUE}🔐 加密算法: {self.crypto._get_algorithm_name()}{Colors.ENDC}")
            print(f"{Colors.OKBLUE}🔑 密钥派生: {self._get_kdf_name(kdf_type)}{Colors.ENDC}")
            print(f"{Colors.OKBLUE}⚙️  线程数: {args.threads}{Colors.ENDC}")
            
            if args.expiry:
                print(f"{Colors.WARNING}⏰ 过期时间: {args.expiry} 天{Colors.ENDC}")
            if args.max_decrypts:
                print(f"{Colors.WARNING}🔢 最大解密次数: {args.max_decrypts}{Colors.ENDC}")
            if args.hide_metadata is False:
                print(f"{Colors.WARNING}🔓 元数据: 可见{Colors.ENDC}")
            
            print(f"\n{Colors.WARNING}⏳ 正在加密...{Colors.ENDC}")
            
            progress_callback = self._create_progress_callback()
            
            info = self.crypto.encrypt_file(
                input_file, output_file, password,
                expiry_days=args.expiry,
                max_decrypts=args.max_decrypts,
                hide_metadata=args.hide_metadata,
                progress_callback=progress_callback
            )
            
            print(f"\n{Colors.OKGREEN}✓ 加密成功！{Colors.ENDC}")
            print(f"\n{Colors.OKCYAN}加密信息：{Colors.ENDC}")
            print(f"  原始大小: {self._format_size(info['original_size'])}")
            print(f"  加密大小: {self._format_size(info['encrypted_size'])}")
            print(f"  加密算法: {info['algorithm']}")
            print(f"  元数据隐藏: {'是' if info.get('metadata_hidden') else '否'}")
            
            if args.delete_original:
                self._secure_delete(input_file)
                print(f"{Colors.OKGREEN}✓ 原文件已安全删除{Colors.ENDC}")
            
            return 0
            
        except Exception as e:
            print(f"{Colors.FAIL}✗ 加密失败: {e}{Colors.ENDC}")
            if os.path.exists(output_file):
                os.remove(output_file)
            return 1
    
    def decrypt_command(self, args):
        """解密命令"""
        input_file = args.input
        output_file = args.output
        
        if not os.path.exists(input_file):
            print(f"{Colors.FAIL}✗ 错误：输入文件不存在: {input_file}{Colors.ENDC}")
            return 1
        
        if not output_file:
            if input_file.endswith('.encrypted'):
                output_file = input_file[:-10]
            else:
                output_file = input_file + '.decrypted'
        
        if os.path.exists(output_file) and not args.force:
            print(f"{Colors.WARNING}⚠ 警告：输出文件已存在: {output_file}{Colors.ENDC}")
            response = input("是否覆盖？(y/N): ")
            if response.lower() != 'y':
                print("操作已取消")
                return 0
        
        password = self._get_password_for_decryption(args.password, input_file)
        if not password:
            return 1
        
        try:
            self.crypto = CryptoCore()
            
            print(f"\n{Colors.OKBLUE}📁 输入文件: {input_file}{Colors.ENDC}")
            print(f"{Colors.OKBLUE}📁 输出文件: {output_file}{Colors.ENDC}")
            
            progress_callback = self._create_progress_callback()
            print(f"\n{Colors.WARNING}⏳ 正在解密...{Colors.ENDC}")
            
            info = self.crypto.decrypt_file(input_file, output_file, password, progress_callback)
            
            print(f"\n{Colors.OKGREEN}✓ 解密成功！{Colors.ENDC}")
            print(f"\n{Colors.OKCYAN}解密信息：{Colors.ENDC}")
            print(f"  原始大小: {self._format_size(info['original_size'])}")
            print(f"  解密大小: {self._format_size(info['decrypted_size'])}")
            print(f"  加密算法: {info['algorithm']}")
            
            if info.get('remaining_decrypts') is not None:
                print(f"  剩余解密次数: {info['remaining_decrypts']}")
            
            if args.delete_encrypted:
                os.remove(input_file)
                print(f"{Colors.OKGREEN}✓ 加密文件已删除{Colors.ENDC}")
            
            return 0
            
        except Exception as e:
            print(f"{Colors.FAIL}✗ 解密失败: {e}{Colors.ENDC}")
            if os.path.exists(output_file):
                os.remove(output_file)
            return 1
    
    def stream_encrypt_command(self, args):
        """流式加密命令"""
        password = self._get_password_for_encryption(args.password)
        if not password:
            return 1
        
        try:
            algorithm = self._select_algorithm(args.algorithm)
            self.crypto = CryptoCore(algorithm=algorithm, threads=args.threads)
            
            print(f"{Colors.OKBLUE}🔐 加密算法: {self.crypto._get_algorithm_name()}{Colors.ENDC}")
            print(f"{Colors.OKGREEN}开始输入数据（Ctrl+D 结束）:{Colors.ENDC}\n")
            
            total = 0
            def progress(bytes_read):
                nonlocal total
                total = bytes_read
                if self.verbose:
                    print(f"\r已读取: {self._format_size(total)}", end='')
            
            result = self.crypto.encrypt_stream(
                sys.stdin.buffer,
                sys.stdout.buffer,
                password,
                progress_callback=progress if self.verbose else None
            )
            
            print(f"\n\n{Colors.OKGREEN}✓ 流加密完成 ({self._format_size(result['original_size'])}){Colors.ENDC}")
            return 0
            
        except Exception as e:
            print(f"\n{Colors.FAIL}✗ 流加密失败: {e}{Colors.ENDC}")
            return 1
    
    def stream_decrypt_command(self, args):
        """流式解密命令"""
        password = self._get_password_for_decryption(args.password)
        if not password:
            return 1
        
        try:
            self.crypto = CryptoCore()
            
            total = 0
            def progress(bytes_read):
                nonlocal total
                total = bytes_read
                if self.verbose:
                    print(f"\r已解密: {self._format_size(total)}", end='')
            
            result = self.crypto.decrypt_stream(
                sys.stdin.buffer,
                sys.stdout.buffer,
                password,
                progress_callback=progress if self.verbose else None
            )
            
            print(f"\n\n{Colors.OKGREEN}✓ 流解密完成 ({self._format_size(result['decrypted_size'])}){Colors.ENDC}")
            return 0
            
        except Exception as e:
            print(f"\n{Colors.FAIL}✗ 流解密失败: {e}{Colors.ENDC}")
            return 1
    
    def encrypt_directory_command(self, args):
        """加密目录命令"""
        input_dir = args.input
        output_file = args.output
        
        if not os.path.isdir(input_dir):
            print(f"{Colors.FAIL}✗ 错误：输入路径不是目录: {input_dir}{Colors.ENDC}")
            return 1
        
        if not output_file:
            output_file = os.path.basename(input_dir.rstrip('/')) + '.vcdir'
        
        if os.path.exists(output_file) and not args.force:
            print(f"{Colors.WARNING}⚠ 警告：输出文件已存在: {output_file}{Colors.ENDC}")
            response = input("是否覆盖？(y/N): ")
            if response.lower() != 'y':
                print("操作已取消")
                return 0
        
        password = self._get_password_for_encryption(args.password)
        if not password:
            return 1
        
        kdf_type = self._select_kdf(args.kdf)
        
        try:
            self.crypto = CryptoCore(kdf_type=kdf_type)
            
            print(f"\n{Colors.OKBLUE}📁 输入目录: {input_dir}{Colors.ENDC}")
            print(f"{Colors.OKBLUE}📁 输出文件: {output_file}{Colors.ENDC}")
            
            progress_callback = self._create_progress_callback()
            print(f"\n{Colors.WARNING}⏳ 正在加密目录...{Colors.ENDC}")
            
            info = self.crypto.encrypt_directory(
                input_dir, output_file, password,
                progress_callback=progress_callback,
                compress=not args.no_compress,
                expiry_days=args.expiry,
                max_decrypts=args.max_decrypts
            )
            
            print(f"\n{Colors.OKGREEN}✓ 目录加密成功！{Colors.ENDC}")
            print(f"\n{Colors.OKCYAN}加密信息：{Colors.ENDC}")
            print(f"  文件数量: {info['file_count']}")
            print(f"  原始大小: {self._format_size(info['original_size'])}")
            print(f"  加密大小: {self._format_size(info['encrypted_size'])}")
            
            if args.delete_original:
                import shutil
                shutil.rmtree(input_dir)
                print(f"{Colors.OKGREEN}✓ 原目录已删除{Colors.ENDC}")
            
            return 0
            
        except Exception as e:
            print(f"{Colors.FAIL}✗ 目录加密失败: {e}{Colors.ENDC}")
            if os.path.exists(output_file):
                os.remove(output_file)
            return 1
    
    def decrypt_directory_command(self, args):
        """解密目录命令"""
        input_file = args.input
        output_dir = args.output
        
        if not os.path.exists(input_file):
            print(f"{Colors.FAIL}✗ 错误：输入文件不存在: {input_file}{Colors.ENDC}")
            return 1
        
        if not output_dir:
            basename = os.path.basename(input_file)
            if basename.endswith('.vcdir'):
                output_dir = basename[:-6]
            else:
                output_dir = basename + '.dir'
        
        if os.path.exists(output_dir) and not args.force:
            print(f"{Colors.WARNING}⚠ 警告：输出目录已存在: {output_dir}{Colors.ENDC}")
            response = input("是否覆盖？(y/N): ")
            if response.lower() != 'y':
                print("操作已取消")
                return 0
        
        password = self._get_password_for_decryption(args.password)
        if not password:
            return 1
        
        try:
            self.crypto = CryptoCore()
            
            print(f"\n{Colors.OKBLUE}📁 输入文件: {input_file}{Colors.ENDC}")
            print(f"{Colors.OKBLUE}📁 输出目录: {output_dir}{Colors.ENDC}")
            
            progress_callback = self._create_progress_callback()
            print(f"\n{Colors.WARNING}⏳ 正在解密目录...{Colors.ENDC}")
            
            info = self.crypto.decrypt_directory(
                input_file, output_dir, password,
                progress_callback=progress_callback
            )
            
            print(f"\n{Colors.OKGREEN}✓ 目录解密成功！{Colors.ENDC}")
            print(f"\n{Colors.OKCYAN}解密信息：{Colors.ENDC}")
            print(f"  输出目录: {info['output_dir']}")
            print(f"  解密大小: {self._format_size(info['decrypted_size'])}")
            
            if args.delete_encrypted:
                os.remove(input_file)
                print(f"{Colors.OKGREEN}✓ 加密文件已删除{Colors.ENDC}")
            
            return 0
            
        except Exception as e:
            print(f"{Colors.FAIL}✗ 目录解密失败: {e}{Colors.ENDC}")
            return 1
    
    def batch_encrypt_command(self, args):
        """批量加密命令"""
        pattern = args.pattern
        output_dir = args.output
        
        files = glob_module.glob(pattern)
        if not files:
            print(f"{Colors.FAIL}✗ 错误：没有找到匹配的文件: {pattern}{Colors.ENDC}")
            return 1
        
        password = self._get_password_for_encryption(args.password)
        if not password:
            return 1
        
        kdf_type = self._select_kdf(args.kdf)
        
        try:
            self.crypto = CryptoCore(kdf_type=kdf_type, threads=args.threads)
            
            print(f"\n{Colors.OKBLUE}📋 找到 {len(files)} 个文件待加密{Colors.ENDC}")
            print(f"{Colors.OKBLUE}📁 输出目录: {output_dir}{Colors.ENDC}")
            
            def progress_callback(current: int, total: int, filename: str):
                if TQDM_AVAILABLE:
                    if self._progress_bar:
                        self._progress_bar.set_description(filename[:20])
                        self._progress_bar.update(1)
            
            if TQDM_AVAILABLE:
                with tqdm(total=len(files), desc="加密进度", unit="file") as pbar:
                    self._progress_bar = pbar
                    results = self.crypto.encrypt_files_batch(
                        files, output_dir, password,
                        progress_callback=progress_callback
                    )
            else:
                results = self.crypto.encrypt_files_batch(
                    files, output_dir, password,
                    progress_callback=progress_callback
                )
            
            success_count = sum(1 for r in results if r['success'])
            print(f"\n{Colors.OKGREEN}✓ 批量加密完成！成功: {success_count}/{len(files)}{Colors.ENDC}")
            
            for r in results:
                if not r['success']:
                    print(f"{Colors.FAIL}✗ {r['file']}: {r.get('error', '未知错误')}{Colors.ENDC}")
            
            return 0
            
        except Exception as e:
            print(f"{Colors.FAIL}✗ 批量加密失败: {e}{Colors.ENDC}")
            return 1
    
    def batch_decrypt_command(self, args):
        """批量解密命令"""
        pattern = args.pattern
        output_dir = args.output
        
        files = glob_module.glob(pattern)
        if not files:
            print(f"{Colors.FAIL}✗ 错误：没有找到匹配的文件: {pattern}{Colors.ENDC}")
            return 1
        
        password = self._get_password_for_decryption(args.password)
        if not password:
            return 1
        
        try:
            self.crypto = CryptoCore()
            
            print(f"\n{Colors.OKBLUE}📋 找到 {len(files)} 个文件待解密{Colors.ENDC}")
            print(f"{Colors.OKBLUE}📁 输出目录: {output_dir}{Colors.ENDC}")
            
            def progress_callback(current: int, total: int, filename: str):
                if TQDM_AVAILABLE:
                    if self._progress_bar:
                        self._progress_bar.set_description(filename[:20])
                        self._progress_bar.update(1)
            
            if TQDM_AVAILABLE:
                with tqdm(total=len(files), desc="解密进度", unit="file") as pbar:
                    self._progress_bar = pbar
                    results = self.crypto.decrypt_files_batch(
                        files, output_dir, password,
                        progress_callback=progress_callback
                    )
            else:
                results = self.crypto.decrypt_files_batch(
                    files, output_dir, password,
                    progress_callback=progress_callback
                )
            
            success_count = sum(1 for r in results if r['success'])
            print(f"\n{Colors.OKGREEN}✓ 批量解密完成！成功: {success_count}/{len(files)}{Colors.ENDC}")
            
            for r in results:
                if not r['success']:
                    print(f"{Colors.FAIL}✗ {r['file']}: {r.get('error', '未知错误')}{Colors.ENDC}")
            
            return 0
            
        except Exception as e:
            print(f"{Colors.FAIL}✗ 批量解密失败: {e}{Colors.ENDC}")
            return 1
    
    def stego_encrypt_command(self, args):
        """隐写术加密命令"""
        secret_file = args.secret
        cover_file = args.cover
        output_file = args.output
        
        if not os.path.exists(secret_file):
            print(f"{Colors.FAIL}✗ 错误：秘密文件不存在: {secret_file}{Colors.ENDC}")
            return 1
        
        if not os.path.exists(cover_file):
            print(f"{Colors.FAIL}✗ 错误：伪装文件不存在: {cover_file}{Colors.ENDC}")
            return 1
        
        if not output_file:
            # 使用伪装文件的扩展名
            cover_ext = os.path.splitext(cover_file)[1]
            output_file = os.path.splitext(secret_file)[0] + '_hidden' + cover_ext
        
        password = self._get_password_for_encryption(args.password, secret_file)
        if not password:
            return 1
        
        try:
            print(f"\n{Colors.OKBLUE}🎭 隐写术加密{Colors.ENDC}")
            print(f"{Colors.OKBLUE}📁 秘密文件: {secret_file}{Colors.ENDC}")
            print(f"{Colors.OKBLUE}🎨 伪装文件: {cover_file}{Colors.ENDC}")
            print(f"{Colors.OKBLUE}📁 输出文件: {output_file}{Colors.ENDC}")
            
            print(f"\n{Colors.WARNING}⏳ 正在加密并隐藏...{Colors.ENDC}")
            
            result = self.stego.encrypt_with_cover(
                secret_file, cover_file, output_file, password
            )
            
            print(f"\n{Colors.OKGREEN}✓ 隐写加密成功！{Colors.ENDC}")
            print(f"\n{Colors.OKCYAN}加密信息：{Colors.ENDC}")
            print(f"  秘密文件: {result['secret_file']}")
            print(f"  伪装文件: {result['cover_file']} ({result['cover_type']})")
            print(f"  伪装大小: {self._format_size(result['cover_size'])}")
            print(f"  加密大小: {self._format_size(result['encrypted_size'])}")
            print(f"  总大小: {self._format_size(result['total_size'])}")
            print(f"\n{Colors.WARNING}💡 提示：输出文件看起来像普通的 {result['cover_type']} 文件{Colors.ENDC}")
            
            return 0
            
        except Exception as e:
            print(f"{Colors.FAIL}✗ 隐写加密失败: {e}{Colors.ENDC}")
            return 1
    
    def stego_decrypt_command(self, args):
        """隐写术解密命令"""
        input_file = args.input
        output_file = args.output
        
        if not os.path.exists(input_file):
            print(f"{Colors.FAIL}✗ 错误：输入文件不存在: {input_file}{Colors.ENDC}")
            return 1
        
        # 检查是否是隐写文件
        if not self.stego.is_stego_file(input_file):
            print(f"{Colors.FAIL}✗ 错误：这不是一个有效的隐写加密文件{Colors.ENDC}")
            return 1
        
        # 获取文件信息
        info = self.stego.get_stego_info(input_file)
        if info:
            print(f"\n{Colors.OKCYAN}📋 隐写文件信息：{Colors.ENDC}")
            print(f"  原始秘密文件名: {info['secret_filename']}")
            print(f"  伪装文件类型: {info['cover_type']}")
            print(f"  总大小: {self._format_size(info['total_size'])}")
        
        if not output_file:
            output_file = info['secret_filename'] if info else 'decrypted_file'
        
        password = self._get_password_for_decryption(args.password, input_file)
        if not password:
            return 1
        
        try:
            print(f"\n{Colors.WARNING}⏳ 正在解密隐藏数据...{Colors.ENDC}")
            
            result = self.stego.decrypt_from_cover(input_file, output_file, password)
            
            print(f"\n{Colors.OKGREEN}✓ 隐写解密成功！{Colors.ENDC}")
            print(f"\n{Colors.OKCYAN}解密信息：{Colors.ENDC}")
            print(f"  输出文件: {result['output_file']}")
            print(f"  原始文件名: {result['original_secret_name']}")
            print(f"  解密大小: {self._format_size(result['decrypted_size'])}")
            
            return 0
            
        except Exception as e:
            print(f"{Colors.FAIL}✗ 隐写解密失败: {e}{Colors.ENDC}")
            return 1
    
    def stego_extract_command(self, args):
        """提取伪装文件命令"""
        input_file = args.input
        output_file = args.output
        
        if not os.path.exists(input_file):
            print(f"{Colors.FAIL}✗ 错误：输入文件不存在: {input_file}{Colors.ENDC}")
            return 1
        
        if not self.stego.is_stego_file(input_file):
            print(f"{Colors.FAIL}✗ 错误：这不是一个有效的隐写加密文件{Colors.ENDC}")
            return 1
        
        info = self.stego.get_stego_info(input_file)
        if not output_file and info:
            output_file = info['cover_filename']
        
        try:
            result = self.stego.extract_cover(input_file, output_file)
            
            print(f"\n{Colors.OKGREEN}✓ 伪装文件提取成功！{Colors.ENDC}")
            print(f"  输出文件: {result['cover_file']}")
            print(f"  文件大小: {self._format_size(result['cover_size'])}")
            print(f"\n{Colors.WARNING}💡 提示：这是伪装文件，秘密数据仍在原文件中{Colors.ENDC}")
            
            return 0
            
        except Exception as e:
            print(f"{Colors.FAIL}✗ 提取失败: {e}{Colors.ENDC}")
            return 1
    
    def stego_info_command(self, args):
        """查看隐写文件信息命令"""
        input_file = args.input
        
        if not os.path.exists(input_file):
            print(f"{Colors.FAIL}✗ 错误：文件不存在: {input_file}{Colors.ENDC}")
            return 1
        
        if not self.stego.is_stego_file(input_file):
            print(f"{Colors.WARNING}这不是一个隐写加密文件{Colors.ENDC}")
            return 0
        
        info = self.stego.get_stego_info(input_file)
        if info:
            print(f"\n{Colors.OKGREEN}✓ 这是一个隐写加密文件{Colors.ENDC}")
            print(f"\n{Colors.OKCYAN}文件信息：{Colors.ENDC}")
            print(f"  总大小: {self._format_size(info['total_size'])}")
            print(f"  伪装文件大小: {self._format_size(info['cover_size'])}")
            print(f"  加密数据大小: {self._format_size(info['encrypted_size'])}")
            print(f"  秘密文件名: {info['secret_filename']}")
            print(f"  伪装文件名: {info['cover_filename']}")
            print(f"  伪装类型: {info['cover_type']}")
            
            # 计算隐藏比例
            hide_ratio = (info['encrypted_size'] / info['total_size']) * 100
            print(f"  隐藏比例: {hide_ratio:.1f}%")
        
        return 0
    
    def dry_run_command(self, args):
        """预览加密效果"""
        input_file = args.input
        
        if not os.path.exists(input_file):
            print(f"{Colors.FAIL}✗ 错误：输入文件不存在: {input_file}{Colors.ENDC}")
            return 1
        
        file_size = os.path.getsize(input_file)
        
        print(f"\n{Colors.OKCYAN}📋 加密预览信息：{Colors.ENDC}")
        print(f"  输入文件: {input_file}")
        print(f"  文件大小: {self._format_size(file_size)}")
        print(f"  预计加密后大小: ~{self._format_size(int(file_size * 1.1) + 200)}")
        print(f"  算法: {args.algorithm or 'aes256'}")
        print(f"  KDF: {args.kdf or 'argon2'}")
        print(f"  线程数: {args.threads or 4}")
        
        if args.expiry:
            print(f"  过期时间: {args.expiry} 天")
        if args.max_decrypts:
            print(f"  最大解密次数: {args.max_decrypts}")
        
        print(f"\n{Colors.WARNING}这只是预览，不会实际执行加密{Colors.ENDC}")
        return 0
    
    def interactive_mode(self):
        """交互式Shell模式"""
        print(f"\n{Colors.OKGREEN}=== CLI 加密工具交互模式 ==={Colors.ENDC}")
        print("输入命令执行操作，输入 'help' 查看帮助，'exit' 退出\n")
        
        while True:
            try:
                cmd = input(f"{Colors.OKBLUE}encrypt>{Colors.ENDC} ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n退出")
                break
            
            if not cmd:
                continue
            
            if cmd in ['exit', 'quit', 'q']:
                print("再见！")
                break
            
            if cmd == 'help':
                self._print_help()
                continue
            
            if cmd == 'status':
                print(f"{Colors.OKCYAN}当前配置：{Colors.ENDC}")
                print(f"  算法: {self.config.get('encryption', 'algorithm')}")
                print(f"  KDF: {self.config.get('encryption', 'kdf')}")
                print(f"  线程: {self.config.get('encryption', 'threads')}")
                continue
            
            parts = cmd.split()
            if len(parts) < 2:
                print(f"{Colors.FAIL}命令格式错误{Colors.ENDC}")
                continue
            
            action = parts[0]
            path = parts[1]
            
            if action == 'enc':
                if not os.path.exists(path):
                    print(f"{Colors.FAIL}文件不存在: {path}{Colors.ENDC}")
                    continue
                output_path = path + '.encrypted'
                password = self._get_password_for_encryption(None)
                if not password:
                    continue
                try:
                    self.crypto = CryptoCore()
                    self.crypto.encrypt_file(path, output_path, password)
                    print(f"{Colors.OKGREEN}✓ 加密成功: {output_path}{Colors.ENDC}")
                except Exception as e:
                    print(f"{Colors.FAIL}✗ 加密失败: {e}{Colors.ENDC}")
            
            elif action == 'dec':
                if not os.path.exists(path):
                    print(f"{Colors.FAIL}文件不存在: {path}{Colors.ENDC}")
                    continue
                if path.endswith('.encrypted'):
                    output_path = path[:-10]
                else:
                    output_path = path + '.decrypted'
                password = self._get_password_for_decryption(None)
                if not password:
                    continue
                try:
                    self.crypto = CryptoCore()
                    self.crypto.decrypt_file(path, output_path, password)
                    print(f"{Colors.OKGREEN}✓ 解密成功: {output_path}{Colors.ENDC}")
                except Exception as e:
                    print(f"{Colors.FAIL}✗ 解密失败: {e}{Colors.ENDC}")
            
            else:
                print(f"{Colors.FAIL}未知命令: {action}{Colors.ENDC}")
    
    def _print_help(self):
        """打印交互模式帮助"""
        print(f"""
{Colors.OKCYAN}可用命令：{Colors.ENDC}
  enc <file>   加密文件
  dec <file>  解密文件
  status       显示当前配置
  help         显示帮助
  exit         退出
""")
    
    def _get_password_for_encryption(self, password_arg: Optional[str], filepath: Optional[str] = None) -> Optional[str]:
        """获取加密密码"""
        if password_arg:
            return password_arg
        
        print(f"\n{Colors.BOLD}请输入加密密码：{Colors.ENDC}")
        password = getpass.getpass("密码: ")
        
        is_strong, message = CryptoCore.check_password_strength(password)
        print(f"{Colors.OKCYAN}{message}{Colors.ENDC}")
        
        if not is_strong:
            response = input(f"{Colors.WARNING}密码强度不足，是否继续？(y/N): {Colors.ENDC}")
            if response.lower() != 'y':
                return None
        
        password_confirm = getpass.getpass("确认密码: ")
        if password != password_confirm:
            print(f"{Colors.FAIL}✗ 两次输入的密码不一致{Colors.ENDC}")
            return None
        
        # 询问是否保存密码用于生物识别
        if filepath and BiometricAuth.is_available():
            response = input(f"\n{Colors.OKCYAN}是否保存密码以便下次使用生物识别验证？(y/N): {Colors.ENDC}")
            if response.lower() == 'y':
                if self.biometric_manager.save_password_for_file(filepath, password):
                    print(f"{Colors.OKGREEN}✓ 密码已安全保存到系统钥匙串{Colors.ENDC}")
        
        return password
    
    def _get_password_for_decryption(self, password_arg: Optional[str], filepath: Optional[str] = None) -> Optional[str]:
        """获取解密密码"""
        if password_arg:
            return password_arg
        
        # 检查是否可以使用生物识别
        if filepath and BiometricAuth.is_available():
            if self.biometric_manager.has_saved_password(filepath):
                print(f"\n{Colors.OKCYAN}检测到已保存的密码凭证{Colors.ENDC}")
                response = input(f"是否使用生物识别验证？(Y/n): ")
                
                if response.lower() != 'n':
                    password_hash = self.biometric_manager.get_password_for_file(
                        filepath, 
                        f"解密文件: {os.path.basename(filepath)}"
                    )
                    
                    if password_hash:
                        # 使用保存的密码哈希
                        # 注意：这里需要返回原始密码，但我们只存储了哈希
                        # 所以我们需要修改存储策略
                        return password_hash
                    else:
                        print(f"{Colors.WARNING}生物识别验证失败，请手动输入密码{Colors.ENDC}")
        
        print(f"\n{Colors.BOLD}请输入解密密码：{Colors.ENDC}")
        return getpass.getpass("密码: ")
    
    def _select_kdf(self, kdf_arg: Optional[str]) -> int:
        """选择密钥派生函数"""
        if kdf_arg:
            if kdf_arg.lower() == 'argon2':
                return CryptoCore.KDF_ARGON2ID
            elif kdf_arg.lower() == 'pbkdf2':
                return CryptoCore.KDF_PBKDF2_SHA512
        
        try:
            from argon2 import PasswordHasher
            return CryptoCore.KDF_ARGON2ID
        except ImportError:
            return CryptoCore.KDF_PBKDF2_SHA512
    
    def _select_algorithm(self, algo_arg: Optional[str]) -> int:
        """选择加密算法"""
        algo_map = {
            'aes256': CryptoCore.ALGORITHM_AES_256_GCM,
            'chacha20': CryptoCore.ALGORITHM_CHACHA20_POLY1305,
            'cascade': CryptoCore.ALGORITHM_CASCADE_AES_SERPENT
        }
        
        if algo_arg and algo_arg.lower() in algo_map:
            return algo_map[algo_arg.lower()]
        
        return CryptoCore.ALGORITHM_AES_256_GCM
    
    def _get_kdf_name(self, kdf_type: int) -> str:
        """获取 KDF 名称"""
        if kdf_type == CryptoCore.KDF_ARGON2ID:
            return "Argon2id"
        elif kdf_type == CryptoCore.KDF_PBKDF2_SHA512:
            return "PBKDF2-HMAC-SHA512"
        return "Unknown"
    
    def _format_size(self, size: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"
    
    def _secure_delete(self, filepath: str):
        """安全删除文件"""
        try:
            file_size = os.path.getsize(filepath)
            with open(filepath, 'wb') as f:
                f.write(os.urandom(file_size))
            os.remove(filepath)
        except Exception as e:
            print(f"{Colors.WARNING}⚠ 警告：安全删除失败: {e}{Colors.ENDC}")
            try:
                os.remove(filepath)
            except Exception:
                pass
    
    def _create_progress_callback(self) -> Optional[Callable[[float, str], None]]:
        """创建进度回调函数"""
        if not TQDM_AVAILABLE:
            return None
        
        def callback(progress: float, status: str):
            if self._progress_bar is None:
                self._progress_bar = tqdm(total=100, desc="进度", unit="%")
            self._progress_bar.n = int(progress * 100)
            self._progress_bar.set_postfix_str(status)
            self._progress_bar.refresh()
            if progress >= 1.0:
                self._progress_bar.close()
                self._progress_bar = None
        
        return callback


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='CLI 高级加密工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  加密文件:
    %(prog)s encrypt document.pdf -p "密码"
    %(prog)s encrypt doc.pdf --algorithm chacha20 --expiry 7
    %(prog)s encrypt file.pdf --max-decrypts 3 --sign
  
  流式加密:
    %(prog)s stream-encrypt -p "密码" < input.txt > output.enc
    %(prog)s stream-decrypt -p "密码" < output.enc > result.txt
  
  交互模式:
    %(prog)s interactive
        """
    )
    
    parser.add_argument('-v', '--verbose', action='store_true', help='显示详细日志')
    parser.add_argument('-c', '--config', help='配置文件路径')
    
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # 加密命令
    encrypt_parser = subparsers.add_parser('encrypt', help='加密文件')
    encrypt_parser.add_argument('input', help='输入文件路径')
    encrypt_parser.add_argument('-o', '--output', help='输出文件路径')
    encrypt_parser.add_argument('-p', '--password', help='加密密码')
    encrypt_parser.add_argument('-k', '--kdf', choices=['pbkdf2', 'argon2'], help='密钥派生函数')
    encrypt_parser.add_argument('-a', '--algorithm', choices=['aes256', 'chacha20', 'cascade'],
                               help='加密算法 (aes256/chacha20/cascade)')
    encrypt_parser.add_argument('-t', '--threads', type=int, default=1, help='线程数')
    encrypt_parser.add_argument('-f', '--force', action='store_true', help='强制覆盖')
    encrypt_parser.add_argument('-d', '--delete-original', action='store_true', help='加密后删除原文件')
    encrypt_parser.add_argument('-e', '--expiry', type=int, help='过期天数')
    encrypt_parser.add_argument('-m', '--max-decrypts', type=int, help='最大解密次数')
    encrypt_parser.add_argument('--no-hide-metadata', dest='hide_metadata', action='store_false', default=True,
                               help='显示元数据')
    encrypt_parser.add_argument('-s', '--sign', action='store_true', help='启用数字签名')
    
    # 解密命令
    decrypt_parser = subparsers.add_parser('decrypt', help='解密文件')
    decrypt_parser.add_argument('input', help='加密文件路径')
    decrypt_parser.add_argument('-o', '--output', help='输出文件路径')
    decrypt_parser.add_argument('-p', '--password', help='解密密码')
    decrypt_parser.add_argument('-f', '--force', action='store_true', help='强制覆盖')
    decrypt_parser.add_argument('-d', '--delete-encrypted', action='store_true', help='解密后删除加密文件')
    
    # 流加密命令
    stream_encrypt_parser = subparsers.add_parser('stream-encrypt', help='流式加密 (stdin->stdout)')
    stream_encrypt_parser.add_argument('-p', '--password', help='加密密码')
    stream_encrypt_parser.add_argument('-a', '--algorithm', choices=['aes256', 'chacha20'], help='加密算法')
    stream_encrypt_parser.add_argument('-t', '--threads', type=int, default=1, help='线程数')
    
    # 流解密命令
    stream_decrypt_parser = subparsers.add_parser('stream-decrypt', help='流式解密 (stdin->stdout)')
    stream_decrypt_parser.add_argument('-p', '--password', help='解密密码')
    
    # 目录加密命令
    encrypt_dir_parser = subparsers.add_parser('encrypt-dir', help='加密目录')
    encrypt_dir_parser.add_argument('input', help='输入目录路径')
    encrypt_dir_parser.add_argument('-o', '--output', help='输出文件路径')
    encrypt_dir_parser.add_argument('-p', '--password', help='加密密码')
    encrypt_dir_parser.add_argument('-k', '--kdf', choices=['pbkdf2', 'argon2'], help='密钥派生函数')
    encrypt_dir_parser.add_argument('-f', '--force', action='store_true', help='强制覆盖')
    encrypt_dir_parser.add_argument('-d', '--delete-original', action='store_true', help='加密后删除原目录')
    encrypt_dir_parser.add_argument('--no-compress', action='store_true', help='不压缩')
    encrypt_dir_parser.add_argument('-e', '--expiry', type=int, help='过期天数')
    encrypt_dir_parser.add_argument('-m', '--max-decrypts', type=int, help='最大解密次数')
    
    # 目录解密命令
    decrypt_dir_parser = subparsers.add_parser('decrypt-dir', help='解密目录')
    decrypt_dir_parser.add_argument('input', help='加密文件路径')
    decrypt_dir_parser.add_argument('-o', '--output', help='输出目录路径')
    decrypt_dir_parser.add_argument('-p', '--password', help='解密密码')
    decrypt_dir_parser.add_argument('-f', '--force', action='store_true', help='强制覆盖')
    decrypt_dir_parser.add_argument('-d', '--delete-encrypted', action='store_true', help='解密后删除加密文件')
    
    # 批量加密命令
    batch_encrypt_parser = subparsers.add_parser('batch-encrypt', help='批量加密')
    batch_encrypt_parser.add_argument('pattern', help='文件匹配模式')
    batch_encrypt_parser.add_argument('-o', '--output', default='.', help='输出目录')
    batch_encrypt_parser.add_argument('-p', '--password', help='加密密码')
    batch_encrypt_parser.add_argument('-k', '--kdf', choices=['pbkdf2', 'argon2'], help='密钥派生函数')
    batch_encrypt_parser.add_argument('-t', '--threads', type=int, default=1, help='线程数')
    
    # 批量解密命令
    batch_decrypt_parser = subparsers.add_parser('batch-decrypt', help='批量解密')
    batch_decrypt_parser.add_argument('pattern', help='加密文件匹配模式')
    batch_decrypt_parser.add_argument('-o', '--output', default='.', help='输出目录')
    batch_decrypt_parser.add_argument('-p', '--password', help='解密密码')
    
    # 预览命令
    dryrun_parser = subparsers.add_parser('dry-run', help='预览加密效果')
    dryrun_parser.add_argument('input', help='输入文件路径')
    dryrun_parser.add_argument('-k', '--kdf', choices=['pbkdf2', 'argon2'], help='密钥派生函数')
    dryrun_parser.add_argument('-a', '--algorithm', choices=['aes256', 'chacha20', 'cascade'], help='加密算法')
    dryrun_parser.add_argument('-t', '--threads', type=int, default=4, help='线程数')
    dryrun_parser.add_argument('-e', '--expiry', type=int, help='过期天数')
    dryrun_parser.add_argument('-m', '--max-decrypts', type=int, help='最大解密次数')
    
    # 交互模式
    subparsers.add_parser('interactive', help='交互式Shell模式')
    
    # 隐写术加密命令
    stego_encrypt_parser = subparsers.add_parser('stego-encrypt', help='隐写术加密（伪装成普通文件）')
    stego_encrypt_parser.add_argument('secret', help='要加密的秘密文件')
    stego_encrypt_parser.add_argument('cover', help='用作伪装的普通文件')
    stego_encrypt_parser.add_argument('-o', '--output', help='输出文件路径')
    stego_encrypt_parser.add_argument('-p', '--password', help='加密密码')
    
    # 隐写术解密命令
    stego_decrypt_parser = subparsers.add_parser('stego-decrypt', help='隐写术解密')
    stego_decrypt_parser.add_argument('input', help='隐写加密文件')
    stego_decrypt_parser.add_argument('-o', '--output', help='输出文件路径')
    stego_decrypt_parser.add_argument('-p', '--password', help='解密密码')
    
    # 提取伪装文件命令
    stego_extract_parser = subparsers.add_parser('stego-extract', help='提取伪装文件（不解密）')
    stego_extract_parser.add_argument('input', help='隐写加密文件')
    stego_extract_parser.add_argument('-o', '--output', help='输出文件路径')
    
    # 查看隐写文件信息
    stego_info_parser = subparsers.add_parser('stego-info', help='查看隐写文件信息')
    stego_info_parser.add_argument('input', help='文件路径')
    
    args = parser.parse_args()
    
    tool = CLIEncryptTool(verbose=args.verbose, config_file=args.config)
    
    if args.command == 'encrypt':
        tool.print_banner()
        sys.exit(tool.encrypt_command(args))
    elif args.command == 'decrypt':
        tool.print_banner()
        sys.exit(tool.decrypt_command(args))
    elif args.command == 'stream-encrypt':
        sys.exit(tool.stream_encrypt_command(args))
    elif args.command == 'stream-decrypt':
        sys.exit(tool.stream_decrypt_command(args))
    elif args.command == 'encrypt-dir':
        tool.print_banner()
        sys.exit(tool.encrypt_directory_command(args))
    elif args.command == 'decrypt-dir':
        tool.print_banner()
        sys.exit(tool.decrypt_directory_command(args))
    elif args.command == 'batch-encrypt':
        tool.print_banner()
        sys.exit(tool.batch_encrypt_command(args))
    elif args.command == 'batch-decrypt':
        tool.print_banner()
        sys.exit(tool.batch_decrypt_command(args))
    elif args.command == 'dry-run':
        sys.exit(tool.dry_run_command(args))
    elif args.command == 'interactive':
        tool.interactive_mode()
        sys.exit(0)
    elif args.command == 'stego-encrypt':
        tool.print_banner()
        sys.exit(tool.stego_encrypt_command(args))
    elif args.command == 'stego-decrypt':
        tool.print_banner()
        sys.exit(tool.stego_decrypt_command(args))
    elif args.command == 'stego-extract':
        tool.print_banner()
        sys.exit(tool.stego_extract_command(args))
    elif args.command == 'stego-info':
        sys.exit(tool.stego_info_command(args))
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == '__main__':
    main()
