#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本 - 验证加密工具的功能
"""

import os
import sys
import tempfile
import hashlib
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crypto_core import CryptoCore


class TestColors:
    """测试输出颜色"""
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    WARNING = '\033[93m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_test(name):
    """打印测试名称"""
    print(f"\n{TestColors.BOLD}测试: {name}{TestColors.ENDC}")


def print_pass(message):
    """打印通过信息"""
    print(f"{TestColors.OKGREEN}✓ {message}{TestColors.ENDC}")


def print_fail(message):
    """打印失败信息"""
    print(f"{TestColors.FAIL}✗ {message}{TestColors.ENDC}")


def get_file_hash(filepath):
    """计算文件 SHA256 哈希"""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()


def test_password_strength():
    """测试密码强度检查"""
    print_test("密码强度检查")
    
    test_cases = [
        ("123", False, "太短"),
        ("12345678", False, "只有数字"),
        ("abcdefgh", False, "只有小写字母"),
        ("Abcd1234", True, "包含大小写和数字"),
        ("Abcd@1234", True, "包含大小写、数字和特殊字符"),
        ("MyP@ssw0rd123", True, "强密码"),
    ]
    
    passed = 0
    for password, expected_strong, description in test_cases:
        is_strong, message = CryptoCore.check_password_strength(password)
        if (is_strong == expected_strong):
            print_pass(f"{description}: {message}")
            passed += 1
        else:
            print_fail(f"{description}: 预期 {expected_strong}, 得到 {is_strong}")
    
    print(f"\n通过: {passed}/{len(test_cases)}")
    return passed == len(test_cases)


def test_encryption_decryption(kdf_type, kdf_name):
    """测试加密和解密"""
    print_test(f"加密/解密测试 - {kdf_name}")
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        test_file = f.name
        test_content = "这是测试内容\n" * 1000  # 创建较大的测试内容
        f.write(test_content)
    
    encrypted_file = test_file + '.encrypted'
    decrypted_file = test_file + '.decrypted'
    password = "TestP@ssw0rd123"
    
    try:
        # 计算原始文件哈希
        original_hash = get_file_hash(test_file)
        original_size = os.path.getsize(test_file)
        print(f"  原始文件大小: {original_size} 字节")
        print(f"  原始文件哈希: {original_hash[:16]}...")
        
        # 测试加密
        crypto = CryptoCore(kdf_type=kdf_type)
        print(f"  正在加密...")
        encrypt_info = crypto.encrypt_file(test_file, encrypted_file, password)
        
        if os.path.exists(encrypted_file):
            encrypted_size = os.path.getsize(encrypted_file)
            print_pass(f"加密成功 - 加密文件大小: {encrypted_size} 字节")
        else:
            print_fail("加密失败 - 未生成加密文件")
            return False
        
        # 测试解密
        print(f"  正在解密...")
        decrypt_info = crypto.decrypt_file(encrypted_file, decrypted_file, password)
        
        if os.path.exists(decrypted_file):
            decrypted_hash = get_file_hash(decrypted_file)
            decrypted_size = os.path.getsize(decrypted_file)
            print_pass(f"解密成功 - 解密文件大小: {decrypted_size} 字节")
            
            # 验证内容一致性
            if original_hash == decrypted_hash:
                print_pass("内容验证通过 - 原始文件和解密文件完全一致")
                return True
            else:
                print_fail("内容验证失败 - 文件内容不一致")
                return False
        else:
            print_fail("解密失败 - 未生成解密文件")
            return False
            
    except Exception as e:
        print_fail(f"测试失败: {e}")
        return False
    finally:
        # 清理临时文件
        for f in [test_file, encrypted_file, decrypted_file]:
            if os.path.exists(f):
                os.remove(f)


def test_wrong_password():
    """测试错误密码"""
    print_test("错误密码测试")
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        test_file = f.name
        f.write("测试内容")
    
    encrypted_file = test_file + '.encrypted'
    decrypted_file = test_file + '.decrypted'
    correct_password = "Correct@Pass123"
    wrong_password = "Wrong@Pass123"
    
    try:
        # 加密
        crypto = CryptoCore()
        crypto.encrypt_file(test_file, encrypted_file, correct_password)
        
        # 尝试用错误密码解密
        try:
            crypto.decrypt_file(encrypted_file, decrypted_file, wrong_password)
            print_fail("应该抛出异常但没有")
            return False
        except ValueError as e:
            if "解密失败" in str(e) or "密码错误" in str(e):
                print_pass(f"正确拒绝错误密码: {e}")
                return True
            else:
                print_fail(f"异常信息不正确: {e}")
                return False
                
    except Exception as e:
        print_fail(f"测试失败: {e}")
        return False
    finally:
        # 清理临时文件
        for f in [test_file, encrypted_file, decrypted_file]:
            if os.path.exists(f):
                os.remove(f)


def test_large_file():
    """测试大文件"""
    print_test("大文件测试 (5MB)")
    
    # 创建 5MB 测试文件
    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.bin') as f:
        test_file = f.name
        # 写入 5MB 随机数据
        for _ in range(5):
            f.write(os.urandom(1024 * 1024))
    
    encrypted_file = test_file + '.encrypted'
    decrypted_file = test_file + '.decrypted'
    password = "LargeFile@Test123"
    
    try:
        original_hash = get_file_hash(test_file)
        original_size = os.path.getsize(test_file)
        print(f"  原始文件大小: {original_size / (1024*1024):.2f} MB")
        
        # 加密
        crypto = CryptoCore()
        print(f"  正在加密...")
        crypto.encrypt_file(test_file, encrypted_file, password)
        print_pass("大文件加密成功")
        
        # 解密
        print(f"  正在解密...")
        crypto.decrypt_file(encrypted_file, decrypted_file, password)
        print_pass("大文件解密成功")
        
        # 验证
        decrypted_hash = get_file_hash(decrypted_file)
        if original_hash == decrypted_hash:
            print_pass("大文件内容验证通过")
            return True
        else:
            print_fail("大文件内容验证失败")
            return False
            
    except Exception as e:
        print_fail(f"大文件测试失败: {e}")
        return False
    finally:
        # 清理临时文件
        for f in [test_file, encrypted_file, decrypted_file]:
            if os.path.exists(f):
                os.remove(f)


def test_empty_file():
    """测试空文件"""
    print_test("空文件测试")
    
    # 创建空文件
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        test_file = f.name
    
    encrypted_file = test_file + '.encrypted'
    decrypted_file = test_file + '.decrypted'
    password = "Empty@File123"
    
    try:
        # 加密
        crypto = CryptoCore()
        crypto.encrypt_file(test_file, encrypted_file, password)
        print_pass("空文件加密成功")
        
        # 解密
        crypto.decrypt_file(encrypted_file, decrypted_file, password)
        print_pass("空文件解密成功")
        
        # 验证
        if os.path.getsize(decrypted_file) == 0:
            print_pass("空文件验证通过")
            return True
        else:
            print_fail("空文件验证失败")
            return False
            
    except Exception as e:
        print_fail(f"空文件测试失败: {e}")
        return False
    finally:
        # 清理临时文件
        for f in [test_file, encrypted_file, decrypted_file]:
            if os.path.exists(f):
                os.remove(f)


def main():
    """运行所有测试"""
    print(f"\n{TestColors.BOLD}{'='*60}")
    print("CLI 加密工具 - 测试套件")
    print(f"{'='*60}{TestColors.ENDC}\n")
    
    tests = [
        ("密码强度检查", test_password_strength),
        ("PBKDF2 加密/解密", lambda: test_encryption_decryption(
            CryptoCore.KDF_PBKDF2_SHA512, "PBKDF2-HMAC-SHA512")),
        ("错误密码测试", test_wrong_password),
        ("大文件测试", test_large_file),
        ("空文件测试", test_empty_file),
    ]
    
    # 如果 Argon2 可用，添加 Argon2 测试
    try:
        import argon2
        tests.insert(2, ("Argon2 加密/解密", lambda: test_encryption_decryption(
            CryptoCore.KDF_ARGON2ID, "Argon2id")))
    except ImportError:
        print(f"{TestColors.WARNING}⚠ Argon2 不可用，跳过 Argon2 测试{TestColors.ENDC}")
    
    # 运行测试
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print_fail(f"测试异常: {e}")
            results.append((name, False))
    
    # 打印总结
    print(f"\n{TestColors.BOLD}{'='*60}")
    print("测试总结")
    print(f"{'='*60}{TestColors.ENDC}\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{TestColors.OKGREEN}✓ 通过{TestColors.ENDC}" if result else f"{TestColors.FAIL}✗ 失败{TestColors.ENDC}"
        print(f"  {name}: {status}")
    
    print(f"\n{TestColors.BOLD}总计: {passed}/{total} 通过{TestColors.ENDC}")
    
    if passed == total:
        print(f"\n{TestColors.OKGREEN}🎉 所有测试通过！{TestColors.ENDC}\n")
        return 0
    else:
        print(f"\n{TestColors.FAIL}❌ 部分测试失败{TestColors.ENDC}\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())

