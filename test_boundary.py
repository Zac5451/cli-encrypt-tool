#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
边界测试清单
覆盖各种边界情况和极端输入
"""

import os
import sys
import tempfile
import pytest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crypto_core import CryptoCore


# 边界测试数据
EDGE_CASES = {
    # 极端文件大小
    "empty": b"",
    "single_byte": b"X",
    "one_kb": b"A" * 1024,
    "one_mb": b"B" * (1024 * 1024),
    
    # 特殊二进制数据
    "null_bytes": bytes(256),
    "all_bytes": bytes(range(256)),
    "alternating": bytes([i % 256 for i in range(10000)]),
    "random_binary": bytes.fromhex("deadbeef" * 1000),
    
    # 特殊字符
    "chinese": "中文测试内容😀🎉".encode("utf-8"),
    "japanese": "日本語テスト".encode("utf-8"),
    "arabic": "مرحبا بالعالم".encode("utf-8"),
    "emoji_mix": "🎉🧧🎊🎁🎄🎠🎡🌈".encode("utf-8"),
    "special_chars": "!@#$%^&*()_+-=[]{}|;':\",./<>?`~".encode("utf-8"),
    "newlines": b"line1\nline2\r\nline3\rline4\n",
    "tabs": b"col1\tcol2\tcol3\t",
    
    # 路径边界
    "long_filename": "a" * 200 + ".txt",
    "unicode_filename": "文件_📁_测试.txt",
    "path_traversal": "../../../etc/passwd",
    "spaces_in_name": "file with spaces.txt",
    "dots.in.name": "file.with.dots.txt",
    
    # 压缩友好的数据
    "repeated_chars": b"AAAAAAA" * 10000,
    "compressible": b"1234567890" * 10000,
}


class TestEdgeCases:
    """边界情况测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        self.tmp_dir = tmp_path
        self.created_files = []
        yield
        for f in self.created_files:
            if os.path.exists(f):
                try:
                    if os.path.isdir(f):
                        import shutil
                        shutil.rmtree(f)
                    else:
                        os.remove(f)
                except:
                    pass
    
    def _create_file(self, name, content):
        """创建测试文件"""
        path = str(self.tmp_dir / name)
        with open(path, 'wb') as f:
            f.write(content)
        self.created_files.append(path)
        return path
    
    def _test_encrypt_decrypt(self, data, name):
        """测试加解密"""
        input_file = self._create_file(name, data)
        output_file = input_file + ".enc"
        decrypt_file = input_file + ".dec"
        
        crypto = CryptoCore()
        
        # 加密
        crypto.encrypt_file(input_file, output_file, "TestPass123!")
        
        # 解密
        crypto.decrypt_file(output_file, decrypt_file, "TestPass123!")
        
        # 验证
        with open(decrypt_file, 'rb') as f:
            decrypted = f.read()
        
        assert decrypted == data, f"Failed for: {name}"
    
    def test_empty_data(self):
        """测试：空数据"""
        self._test_encrypt_decrypt(b"", "empty.txt")
    
    def test_single_byte(self):
        """测试：单字节"""
        self._test_encrypt_decrypt(b"X", "single.txt")
    
    def test_null_bytes(self):
        """测试：全空字节"""
        self._test_encrypt_decrypt(bytes(256), "null_bytes.bin")
    
    def test_all_byte_values(self):
        """测试：所有字节值 (0-255)"""
        self._test_encrypt_decrypt(bytes(range(256)), "all_bytes.bin")
    
    def test_chinese_content(self):
        """测试：中文内容"""
        self._test_encrypt_decrypt("中文测试😀".encode("utf-8"), "chinese.txt")
    
    def test_emoji_content(self):
        """测试：Emoji内容"""
        self._test_encrypt_decrypt("🎉🎊🎁🎄".encode("utf-8"), "emoji.txt")
    
    def test_japanese_content(self):
        """测试：日文内容"""
        self._test_encrypt_decrypt("日本語テスト".encode("utf-8"), "japanese.txt")
    
    def test_arabic_content(self):
        """测试：阿拉伯文内容"""
        self._test_encrypt_decrypt("مرحبا".encode("utf-8"), "arabic.txt")
    
    def test_special_characters(self):
        """测试：特殊字符"""
        self._test_encrypt_decrypt(b"!@#$%^&*()_+-=[]{}|;':\",./<>?", "special.txt")
    
    def test_newlines(self):
        """测试：换行符"""
        self._test_encrypt_decrypt(b"line1\nline2\r\nline3", "newlines.txt")
    
    def test_repeated_data(self):
        """测试：重复数据（压缩友好）"""
        self._test_encrypt_decrypt(b"A" * 100000, "repeated.txt")
    
    def test_mixed_content(self):
        """测试：混合内容"""
        content = b"Text with \x00 null and Chinese and emoji"
        self._test_encrypt_decrypt(content, "mixed.txt")
    
    def test_binary_executable(self):
        """测试：类二进制可执行数据"""
        # 模拟 ELF 头
        elf_header = bytes([0x7f, 0x45, 0x4c, 0x46]) + bytes(range(256))
        self._test_encrypt_decrypt(elf_header, "elf_header.bin")
    
    def test_image_header(self):
        """测试：图片头数据"""
        # PNG 头
        png_header = bytes([0x89, 0x50, 0x4e, 0x47]) + bytes(range(100))
        self._test_encrypt_decrypt(png_header, "png_header.bin")
    
    def test_max_file_size(self):
        """测试：大文件 (10MB)"""
        large_data = b"X" * (10 * 1024 * 1024)
        self._test_encrypt_decrypt(large_data, "large_file.bin")


class TestBoundaryConditions:
    """边界条件测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        self.tmp_dir = tmp_path
        yield
    
    def test_password_boundary(self):
        """测试：密码边界"""
        test_file = str(self.tmp_dir / "test.txt")
        
        # 最小有效密码
        with open(test_file, 'w') as f:
            f.write("test")
        
        crypto = CryptoCore()
        
        # 8字符密码
        crypto.encrypt_file(test_file, test_file + ".enc", "12345678")
        
        # 128字符密码
        crypto.encrypt_file(test_file, test_file + "2.enc", "A" * 128)
        
        # Unicode密码
        crypto.encrypt_file(test_file, test_file + "3.enc", "中文密码")
        
        os.remove(test_file)
        os.remove(test_file + ".enc")
        os.remove(test_file + "2.enc")
        os.remove(test_file + "3.enc")
    
    def test_concurrent_encryption(self):
        """测试：并发加密同一文件"""
        import threading
        
        test_file = str(self.tmp_dir / "test.txt")
        with open(test_file, 'w') as f:
            f.write("concurrent test")
        
        results = []
        
        def encrypt_with_password(password):
            output = test_file + f".{password}.enc"
            crypto = CryptoCore()
            try:
                crypto.encrypt_file(test_file, output, password)
                results.append(("success", password))
            except Exception as e:
                results.append(("error", str(e)))
        
        threads = [
            threading.Thread(target=encrypt_with_password, args=(f"pass{i}",))
            for i in range(5)
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # 所有加密应该成功
        assert len([r for r in results if r[0] == "success"]) == 5
    
    def test_rapid_encrypt_decrypt(self):
        """测试：快速连续加解密"""
        test_file = str(self.tmp_dir / "test.txt")
        with open(test_file, 'w') as f:
            f.write("rapid test")
        
        crypto = CryptoCore()
        
        # 连续加密解密10次
        for i in range(10):
            enc_file = test_file + f".enc{i}"
            dec_file = test_file + f".dec{i}"
            
            crypto.encrypt_file(test_file, enc_file, "Pass123!")
            crypto.decrypt_file(enc_file, dec_file, "Pass123!")
        
        # 清理
        for i in range(10):
            os.remove(test_file + f".enc{i}")
            os.remove(test_file + f".dec{i}")
    
    def test_memory_limit_handling(self):
        """测试：内存限制处理"""
        # 测试分块加密
        test_file = str(self.tmp_dir / "test.txt")
        data = b"X" * (5 * 1024 * 1024)  # 5MB
        with open(test_file, 'wb') as f:
            f.write(data)
        
        crypto = CryptoCore()
        
        # 加密和解密应该成功
        enc_file = test_file + ".enc"
        dec_file = test_file + ".dec"
        
        crypto.encrypt_file(test_file, enc_file, "Pass123!")
        crypto.decrypt_file(enc_file, dec_file, "Pass123!")
        
        with open(dec_file, 'rb') as f:
            assert f.read() == data
        
        os.remove(test_file)
        os.remove(enc_file)
        os.remove(dec_file)


class TestErrorHandling:
    """错误处理测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        self.tmp_dir = tmp_path
        yield
    
    def test_invalid_file_handle(self):
        """测试：无效文件处理"""
        crypto = CryptoCore()
        
        # 不存在的文件
        with pytest.raises(FileNotFoundError):
            crypto.encrypt_file("/nonexistent/file.txt", "out.enc", "pass")
    
    def test_invalid_magic_number(self):
        """测试：无效魔数"""
        enc_file = str(self.tmp_dir / "invalid.enc")
        
        # 写入无效魔数
        with open(enc_file, 'wb') as f:
            f.write(b"INVALID")
            f.write(b"\x00" * 100)
        
        crypto = CryptoCore()
        
        with pytest.raises(ValueError, match="不是有效的加密文件"):
            crypto.decrypt_file(enc_file, "out.txt", "pass")
    
    def test_truncated_file(self):
        """测试：截断的文件"""
        enc_file = str(self.tmp_dir / "truncated.enc")
        
        # 写入有效的头但数据不完整
        crypto = CryptoCore()
        test_file = str(self.tmp_dir / "test.txt")
        with open(test_file, 'w') as f:
            f.write("test")
        
        crypto.encrypt_file(test_file, enc_file, "pass")
        
        # 截断文件
        with open(enc_file, 'r+b') as f:
            f.truncate(os.path.getsize(enc_file) // 2)
        
        crypto = CryptoCore()
        
        with pytest.raises(Exception):
            crypto.decrypt_file(enc_file, "out.txt", "pass")
    
    def test_wrong_kdf_type(self):
        """测试：错误的KDF类型"""
        # 跳过：CryptoCore 从文件头读取 KDF 类型，所以会使用正确的 KDF
        pytest.skip("KDF type is read from file header during decryption")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
