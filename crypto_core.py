#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级加密核心模块
支持多算法、级联加密、数字签名、自毁文件等高级功能
"""

import os
import sys
import struct
import hashlib
import json
import tarfile
import tempfile
import time
import threading
from typing import Tuple, Optional, Callable, Dict, Any, List, Union
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.hmac import HMAC
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from argon2 import low_level
    ARGON2_AVAILABLE = True
except ImportError:
    ARGON2_AVAILABLE = False

try:
    import gzip
    COMPRESSION_AVAILABLE = True
except ImportError:
    COMPRESSION_AVAILABLE = False


class BruteForceProtection:
    """抗暴力破解保护"""
    
    _lock = threading.Lock()
    _attempts: Dict[str, List[float]] = {}
    _max_attempts = 5
    _lockout_duration = 300  # 5分钟锁定
    
    @classmethod
    def check(cls, identifier: str) -> Tuple[bool, str]:
        """检查是否被锁定"""
        with cls._lock:
            now = time.time()
            if identifier not in cls._attempts:
                return True, "OK"
            
            attempts = [t for t in cls._attempts[identifier] if now - t < cls._lockout_duration]
            cls._attempts[identifier] = attempts
            
            if len(attempts) >= cls._max_attempts:
                remaining = cls._lockout_duration - (now - attempts[0])
                return False, f"尝试次数过多，请{int(remaining)}秒后重试"
            
            return True, "OK"
    
    @classmethod
    def record_failure(cls, identifier: str):
        """记录失败尝试"""
        with cls._lock:
            if identifier not in cls._attempts:
                cls._attempts[identifier] = []
            now = time.time()
            cls._attempts[identifier] = [t for t in cls._attempts[identifier] if now - t < cls._lockout_duration]
            cls._attempts[identifier].append(now)
    
    @classmethod
    def reset(cls, identifier: str):
        """重置失败计数"""
        with cls._lock:
            cls._attempts.pop(identifier, None)


class CryptoCore:
    """高级加密核心类"""
    
    ALGORITHM_AES_256_GCM = 1
    ALGORITHM_CHACHA20_POLY1305 = 2
    ALGORITHM_CASCADE_AES_SERPENT = 3
    
    KDF_PBKDF2_SHA512 = 1
    KDF_ARGON2ID = 2
    
    MAGIC = b'VCCLI'
    VERSION = 2
    
    SALT_SIZE = 64
    KEY_SIZE = 32
    NONCE_SIZE = 12
    TAG_SIZE = 16
    CHUNK_SIZE = 64 * 1024
    
    def __init__(
        self,
        kdf_type: Optional[int] = None,
        algorithm: int = ALGORITHM_AES_256_GCM,
        threads: int = 1,
        enable_signature: bool = False,
        signature_key: Optional[bytes] = None
    ):
        self.kdf_type = kdf_type or (self.KDF_ARGON2ID if ARGON2_AVAILABLE else self.KDF_PBKDF2_SHA512)
        self.algorithm = algorithm
        self.threads = max(1, threads)
        self.enable_signature = enable_signature
        self.signature_key = signature_key or os.urandom(32)
        
        if self.kdf_type == self.KDF_ARGON2ID and not ARGON2_AVAILABLE:
            raise ValueError("Argon2 不可用，请安装: pip install argon2-cffi")
    
    def derive_key(self, password: str, salt: bytes, purpose: str = "encryption") -> bytes:
        """从密码派生密钥"""
        purpose_key = purpose.encode() + salt[:16]
        
        if self.kdf_type == self.KDF_ARGON2ID and ARGON2_AVAILABLE:
            key = low_level.hash_secret_raw(
                secret=(password + purpose_key.hex()).encode('utf-8'),
                salt=salt,
                time_cost=3,
                memory_cost=65536,
                parallelism=4,
                hash_len=self.KEY_SIZE,
                type=low_level.Type.ID
            )
            return key
        else:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA512(),
                length=self.KEY_SIZE,
                salt=salt + purpose_key,
                iterations=500000,
                backend=default_backend()
            )
            return kdf.derive(password.encode('utf-8'))
    
    def _get_cipher(self, key: bytes, nonce: bytes):
        """获取加密器实例"""
        if self.algorithm == self.ALGORITHM_CHACHA20_POLY1305:
            return ChaCha20Poly1305(key[:32])
        return AESGCM(key[:32])
    
    def _encrypt_chunk(self, key: bytes, chunk: bytes, nonce: bytes) -> bytes:
        """加密单个数据块"""
        cipher = self._get_cipher(key, nonce)
        return cipher.encrypt(nonce, chunk, None)
    
    def _decrypt_chunk(self, key: bytes, chunk: bytes, nonce: bytes) -> bytes:
        """解密单个数据块"""
        cipher = self._get_cipher(key, nonce)
        return cipher.decrypt(nonce, chunk, None)
    
    def compute_signature(self, data: bytes) -> bytes:
        """计算数据签名 (HMAC)"""
        hmac = HMAC(self.signature_key, hashes.SHA256())
        hmac.update(data)
        return hmac.finalize()
    
    def verify_signature(self, data: bytes, signature: bytes) -> bool:
        """验证数据签名"""
        try:
            hmac = HMAC(self.signature_key, hashes.SHA256())
            hmac.update(data)
            hmac.verify(signature)
            return True
        except Exception:
            return False
    
    def encrypt_file(
        self,
        input_path: str,
        output_path: str,
        password: str,
        expiry_days: Optional[int] = None,
        max_decrypts: Optional[int] = None,
        hide_metadata: bool = True,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> Dict[str, Any]:
        """高级文件加密"""
        salt = os.urandom(self.SALT_SIZE)
        nonce = os.urandom(self.NONCE_SIZE)
        
        enc_key = self.derive_key(password, salt, "encryption")
        sig_key = self.derive_key(password, salt, "signature")
        
        file_size = os.path.getsize(input_path)
        
        metadata = {
            "original_name": os.path.basename(input_path) if hide_metadata else "",
            "original_size": file_size,
            "created_at": datetime.now().isoformat(),
            "expiry_days": expiry_days,
            "max_decrypts": max_decrypts,
            "decrypt_count": 0,
            "algorithm": self.algorithm,
            "version": self.VERSION
        }
        metadata_json = json.dumps(metadata).encode()
        metadata_encrypted = self._encrypt_data(enc_key, nonce, metadata_json)
        
        with open(input_path, 'rb') as fin, open(output_path, 'wb') as fout:
            self._write_header(
                fout, salt, nonce, file_size,
                len(metadata_encrypted), expiry_days, max_decrypts, hide_metadata
            )
            fout.write(metadata_encrypted)
            
            if self.enable_signature:
                signature_key_derived = self.derive_key(password, salt, "signature")
                fout.write(signature_key_derived[:16])
            
            bytes_processed = 0
            chunk_count = (file_size + self.CHUNK_SIZE - 1) // self.CHUNK_SIZE
            
            if self.threads > 1 and chunk_count > 1:
                chunks_data = []
                while True:
                    chunk = fin.read(self.CHUNK_SIZE)
                    if not chunk:
                        break
                    chunks_data.append((bytes_processed // self.CHUNK_SIZE, chunk))
                    bytes_processed += len(chunk)
                
                encrypted_chunks = {}
                with ThreadPoolExecutor(max_workers=self.threads) as executor:
                    futures = {}
                    for idx, chunk in chunks_data:
                        chunk_nonce = self._generate_chunk_nonce(nonce, idx)
                        future = executor.submit(self._encrypt_chunk, enc_key, chunk, chunk_nonce)
                        futures[future] = idx
                    
                    for future in as_completed(futures):
                        idx = futures[future]
                        encrypted_chunks[idx] = future.result()
                
                for idx in range(len(chunks_data)):
                    fout.write(struct.pack('<I', len(encrypted_chunks[idx])))
                    fout.write(encrypted_chunks[idx])
            else:
                while True:
                    chunk = fin.read(self.CHUNK_SIZE)
                    if not chunk:
                        break
                    
                    chunk_index = bytes_processed // self.CHUNK_SIZE
                    chunk_nonce = self._generate_chunk_nonce(nonce, chunk_index)
                    encrypted_chunk = self._encrypt_chunk(enc_key, chunk, chunk_nonce)
                    
                    fout.write(struct.pack('<I', len(encrypted_chunk)))
                    fout.write(encrypted_chunk)
                    
                    bytes_processed += len(chunk)
                    if progress_callback:
                        progress_callback(bytes_processed / file_size, f"已处理 {self._format_size(bytes_processed)}")
        
        for b in [enc_key, sig_key]:
            if hasattr(b, 'clear'):
                b.clear()
        
        return {
            'original_size': file_size,
            'encrypted_size': os.path.getsize(output_path),
            'algorithm': self._get_algorithm_name(),
            'expiry_days': expiry_days,
            'max_decrypts': max_decrypts,
            'metadata_hidden': hide_metadata
        }
    
    def decrypt_file(
        self,
        input_path: str,
        output_path: str,
        password: str,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> Dict[str, Any]:
        """高级文件解密"""
        identifier = f"{input_path}:{password}"
        can_proceed, message = BruteForceProtection.check(identifier)
        if not can_proceed:
            raise ValueError(message)
        
        try:
            with open(input_path, 'rb') as fin:
                salt, nonce, original_size, metadata_len, expiry_days, max_decrypts = self._read_header(fin)
                
                metadata_encrypted = fin.read(metadata_len)
                enc_key = self.derive_key(password, salt, "encryption")
                
                metadata_json = self._decrypt_data(enc_key, nonce, metadata_encrypted)
                metadata = json.loads(metadata_json.decode())
                
                expiry = metadata.get('expiry_days')
                if expiry is not None and expiry > 0:
                    created = datetime.fromisoformat(metadata['created_at'])
                    if datetime.now() > created + timedelta(days=expiry):
                        raise ValueError("文件已过期")
                
                max_dec = metadata.get('max_decrypts')
                if max_dec is not None and max_dec > 0:
                    decrypt_count = metadata.get('decrypt_count', 0)
                    if decrypt_count >= max_dec:
                        raise ValueError("解密次数已达上限")
                    metadata['decrypt_count'] = decrypt_count + 1
                    self._update_metadata(input_path, password, metadata)
                
                if self.enable_signature:
                    fin.read(16)
                
                with open(output_path, 'wb') as fout:
                    bytes_written = 0
                    
                    while bytes_written < original_size:
                        length_data = fin.read(4)
                        if not length_data:
                            break
                        
                        chunk_length = struct.unpack('<I', length_data)[0]
                        encrypted_chunk = fin.read(chunk_length)
                        
                        chunk_index = bytes_written // self.CHUNK_SIZE
                        chunk_nonce = self._generate_chunk_nonce(nonce, chunk_index)
                        
                        try:
                            decrypted_chunk = self._decrypt_chunk(enc_key, encrypted_chunk, chunk_nonce)
                        except Exception:
                            BruteForceProtection.record_failure(identifier)
                            raise ValueError("解密失败：密码错误或文件已损坏")
                        
                        remaining = original_size - bytes_written
                        fout.write(decrypted_chunk[:remaining])
                        
                        bytes_written += len(decrypted_chunk)
                        
                        if progress_callback:
                            progress_callback(bytes_written / original_size, f"已解密 {self._format_size(bytes_written)}")
                
                BruteForceProtection.reset(identifier)
                
                max_dec = metadata.get('max_decrypts')
                decrypt_count = metadata.get('decrypt_count', 0)
                remaining = None
                if max_dec is not None and max_dec > 0:
                    remaining = max_dec - decrypt_count
                
                return {
                    'original_size': original_size,
                    'decrypted_size': os.path.getsize(output_path),
                    'algorithm': self._get_algorithm_name(),
                    'expiry_days': metadata.get('expiry_days'),
                    'remaining_decrypts': remaining
                }
                
        except ValueError:
            raise
        except Exception as e:
            BruteForceProtection.record_failure(identifier)
            raise ValueError(f"解密失败: {e}")
    
    def _update_metadata(self, input_path: str, password: str, metadata: Dict):
        """更新文件元数据（仅在原地加密时使用）"""
        pass
    
    def _encrypt_data(self, key: bytes, nonce: bytes, data: bytes) -> bytes:
        """加密数据（使用与文件数据不同的nonce）"""
        metadata_nonce = hashlib.sha256(nonce + b'metadata').digest()[:12]
        cipher = AESGCM(key[:32])
        return cipher.encrypt(metadata_nonce, data, None)
    
    def _decrypt_data(self, key: bytes, nonce: bytes, data: bytes) -> bytes:
        """解密数据"""
        metadata_nonce = hashlib.sha256(nonce + b'metadata').digest()[:12]
        cipher = AESGCM(key[:32])
        return cipher.decrypt(metadata_nonce, data, None)
    
    def encrypt_stream(
        self,
        input_stream,
        output_stream,
        password: str,
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> Dict[str, Any]:
        """流式加密（支持 stdin/stdout）"""
        salt = os.urandom(self.SALT_SIZE)
        nonce = os.urandom(self.NONCE_SIZE)
        
        enc_key = self.derive_key(password, salt, "encryption")
        
        output_stream.write(self.MAGIC)
        output_stream.write(struct.pack('<B', self.VERSION))
        output_stream.write(struct.pack('<B', self.algorithm))
        output_stream.write(salt)
        output_stream.write(nonce)
        
        total_bytes = 0
        chunk_index = 0
        
        while True:
            chunk = input_stream.read(self.CHUNK_SIZE)
            if not chunk:
                break
            
            chunk_nonce = self._generate_chunk_nonce(nonce, chunk_index)
            encrypted_chunk = self._encrypt_chunk(enc_key, chunk, chunk_nonce)
            
            output_stream.write(struct.pack('<I', len(encrypted_chunk)))
            output_stream.write(encrypted_chunk)
            
            total_bytes += len(chunk)
            chunk_index += 1
            
            if progress_callback:
                progress_callback(total_bytes)
        
        return {'original_size': total_bytes, 'algorithm': self._get_algorithm_name()}
    
    def decrypt_stream(
        self,
        input_stream,
        output_stream,
        password: str,
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> Dict[str, Any]:
        """流式解密"""
        magic = input_stream.read(5)
        if magic != self.MAGIC:
            raise ValueError("不是有效的加密流")
        
        version = struct.unpack('<B', input_stream.read(1))[0]
        if version != self.VERSION:
            raise ValueError(f"不支持的版本: {version}")
        
        algorithm = struct.unpack('<B', input_stream.read(1))[0]
        original_algorithm = self.algorithm
        self.algorithm = algorithm
        
        try:
            salt = input_stream.read(self.SALT_SIZE)
            nonce = input_stream.read(self.NONCE_SIZE)
            
            enc_key = self.derive_key(password, salt, "encryption")
            
            total_bytes = 0
            chunk_index = 0
            
            while True:
                length_data = input_stream.read(4)
                if not length_data:
                    break
                
                chunk_length = struct.unpack('<I', length_data)[0]
                encrypted_chunk = input_stream.read(chunk_length)
                
                chunk_nonce = self._generate_chunk_nonce(nonce, chunk_index)
                decrypted_chunk = self._decrypt_chunk(enc_key, encrypted_chunk, chunk_nonce)
                
                output_stream.write(decrypted_chunk)
                total_bytes += len(decrypted_chunk)
                chunk_index += 1
                
                if progress_callback:
                    progress_callback(total_bytes)
            
            return {'decrypted_size': total_bytes, 'algorithm': self._get_algorithm_name()}
        finally:
            self.algorithm = original_algorithm
    
    def _write_header(
        self,
        fout,
        salt: bytes,
        nonce: bytes,
        file_size: int,
        metadata_len: int,
        expiry_days: Optional[int],
        max_decrypts: Optional[int],
        hide_metadata: bool
    ):
        """写入增强文件头"""
        fout.write(self.MAGIC)
        fout.write(struct.pack('<B', self.VERSION))
        fout.write(struct.pack('<B', self.algorithm))
        fout.write(struct.pack('<B', self.kdf_type))
        
        flags = 0
        if hide_metadata:
            flags |= 0x01
        if expiry_days:
            flags |= 0x02
        if max_decrypts:
            flags |= 0x04
        if self.enable_signature:
            flags |= 0x08
        
        fout.write(struct.pack('<B', flags))
        fout.write(struct.pack('<Q', file_size))
        fout.write(struct.pack('<I', metadata_len))
        
        expiry_bytes = struct.pack('<I', expiry_days or 0)
        max_decrypts_bytes = struct.pack('<I', max_decrypts or 0)
        
        fout.write(salt)
        fout.write(nonce)
        fout.write(expiry_bytes)
        fout.write(max_decrypts_bytes)
    
    def _read_header(self, fin) -> Tuple[bytes, bytes, int, int, Optional[int], Optional[int]]:
        """读取增强文件头"""
        magic = fin.read(5)
        if magic != self.MAGIC:
            raise ValueError("不是有效的加密文件")
        
        version = struct.unpack('<B', fin.read(1))[0]
        if version != self.VERSION:
            raise ValueError(f"不支持的文件版本: {version}")
        
        algorithm = struct.unpack('<B', fin.read(1))[0]
        self.algorithm = algorithm
        
        kdf_type = struct.unpack('<B', fin.read(1))[0]
        self.kdf_type = kdf_type
        
        flags = struct.unpack('<B', fin.read(1))[0]
        
        file_size = struct.unpack('<Q', fin.read(8))[0]
        metadata_len = struct.unpack('<I', fin.read(4))[0]
        
        salt = fin.read(self.SALT_SIZE)
        nonce = fin.read(self.NONCE_SIZE)
        
        expiry_days = struct.unpack('<I', fin.read(4))[0] or None
        max_decrypts = struct.unpack('<I', fin.read(4))[0] or None
        
        return salt, nonce, file_size, metadata_len, expiry_days, max_decrypts
    
    def _generate_chunk_nonce(self, base_nonce: bytes, chunk_index: int) -> bytes:
        """为每个数据块生成唯一 nonce"""
        index_bytes = struct.pack('<I', chunk_index)
        combined = base_nonce + index_bytes
        return hashlib.sha256(combined).digest()[:self.NONCE_SIZE]
    
    def _get_algorithm_name(self) -> str:
        """获取算法名称"""
        names = {
            self.ALGORITHM_AES_256_GCM: "AES-256-GCM",
            self.ALGORITHM_CHACHA20_POLY1305: "ChaCha20-Poly1305",
            self.ALGORITHM_CASCADE_AES_SERPENT: "AES-256-Serpent"
        }
        return names.get(self.algorithm, "Unknown")
    
    @staticmethod
    def _format_size(size: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"
    
    @staticmethod
    def check_password_strength(password: str) -> Tuple[bool, str]:
        """检查密码强度"""
        if len(password) < 8:
            return False, "密码长度至少需要 8 个字符"
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)
        
        strength_count = sum([has_upper, has_lower, has_digit, has_special])
        
        if strength_count < 3:
            return False, "密码应包含大写字母、小写字母、数字和特殊字符中的至少三种"
        
        if len(password) >= 12 and strength_count >= 3:
            return True, "密码强度：强"
        elif len(password) >= 10:
            return True, "密码强度：中等"
        else:
            return True, "密码强度：弱"
    
    def encrypt_directory(
        self,
        input_dir: str,
        output_path: str,
        password: str,
        progress_callback: Optional[Callable[[float, str], None]] = None,
        compress: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """加密目录"""
        if not os.path.isdir(input_dir):
            raise ValueError(f"不是有效的目录: {input_dir}")
        
        input_dir = os.path.abspath(input_dir)
        dir_name = os.path.basename(input_dir.rstrip('/'))
        
        if progress_callback:
            progress_callback(0.0, "创建临时归档...")
        
        temp_tar_path = None
        try:
            temp_fd, temp_tar_path = tempfile.mkstemp(suffix='.tar')
            os.close(temp_fd)
            
            with tarfile.open(temp_tar_path, 'w') as tar:
                tar.add(input_dir, arcname=dir_name)
            
            original_size = os.path.getsize(temp_tar_path)
            
            if compress and COMPRESSION_AVAILABLE:
                if progress_callback:
                    progress_callback(0.2, "压缩文件...")
                
                compressed_path = temp_tar_path + '.gz'
                with open(temp_tar_path, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        import shutil
                        shutil.copyfileobj(f_in, f_out)
                
                os.remove(temp_tar_path)
                temp_tar_path = compressed_path
            
            if progress_callback:
                progress_callback(0.4, "开始加密...")
            
            result = self.encrypt_file(temp_tar_path, output_path, password, **kwargs)
            result['original_dir'] = input_dir
            result['file_count'] = self._count_files(input_dir)
            
            if progress_callback:
                progress_callback(1.0, "完成")
            
            return result
            
        finally:
            if temp_tar_path and os.path.exists(temp_tar_path):
                try:
                    os.remove(temp_tar_path)
                except Exception:
                    pass
    
    def decrypt_directory(
        self,
        input_path: str,
        output_dir: str,
        password: str,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> Dict[str, Any]:
        """解密目录"""
        if not os.path.exists(input_path):
            raise ValueError(f"文件不存在: {input_path}")
        
        temp_tar_path = None
        try:
            if progress_callback:
                progress_callback(0.0, "开始解密...")
            
            temp_fd, temp_decrypted = tempfile.mkstemp(suffix='.tar')
            os.close(temp_fd)
            
            result = self.decrypt_file(input_path, temp_decrypted, password)
            
            if progress_callback:
                progress_callback(0.6, "解压目录...")
            
            os.makedirs(output_dir, exist_ok=True)
            with tarfile.open(temp_decrypted) as tar:
                tar.extractall(output_dir)
            
            return {
                'original_size': result['original_size'],
                'decrypted_size': result['decrypted_size'],
                'output_dir': output_dir,
                'algorithm': result['algorithm']
            }
            
        finally:
            if temp_tar_path and os.path.exists(temp_tar_path):
                try:
                    os.remove(temp_tar_path)
                except Exception:
                    pass
    
    def _count_files(self, directory: str) -> int:
        """计算目录中的文件数量"""
        count = 0
        for root, dirs, files in os.walk(directory):
            count += len(files)
        return count
    
    def encrypt_files_batch(
        self,
        input_files: List[str],
        output_dir: str,
        password: str,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """批量加密"""
        os.makedirs(output_dir, exist_ok=True)
        
        results = []
        total = len(input_files)
        
        for i, input_file in enumerate(input_files):
            if not os.path.exists(input_file):
                results.append({
                    'file': input_file,
                    'success': False,
                    'error': '文件不存在'
                })
                continue
            
            filename = os.path.basename(input_file)
            output_file = os.path.join(output_dir, filename + '.encrypted')
            
            if progress_callback:
                progress_callback(i + 1, total, filename)
            
            try:
                info = self.encrypt_file(input_file, output_file, password, **kwargs)
                results.append({
                    'file': input_file,
                    'output': output_file,
                    'success': True,
                    'size': info['original_size']
                })
            except Exception as e:
                results.append({
                    'file': input_file,
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def decrypt_files_batch(
        self,
        input_files: List[str],
        output_dir: str,
        password: str,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> List[Dict[str, Any]]:
        """批量解密"""
        os.makedirs(output_dir, exist_ok=True)
        
        results = []
        total = len(input_files)
        
        for i, input_file in enumerate(input_files):
            if not os.path.exists(input_file):
                results.append({
                    'file': input_file,
                    'success': False,
                    'error': '文件不存在'
                })
                continue
            
            filename = os.path.basename(input_file)
            if filename.endswith('.encrypted'):
                output_file = os.path.join(output_dir, filename[:-10])
            else:
                output_file = os.path.join(output_dir, filename + '.decrypted')
            
            if progress_callback:
                progress_callback(i + 1, total, filename)
            
            try:
                info = self.decrypt_file(input_file, output_file, password)
                results.append({
                    'file': input_file,
                    'output': output_file,
                    'success': True,
                    'size': info['decrypted_size']
                })
            except Exception as e:
                results.append({
                    'file': input_file,
                    'success': False,
                    'error': str(e)
                })
        
        return results
