#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用示例脚本
演示如何使用加密工具的各种功能
"""

import os
import sys
import tempfile

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crypto_core import CryptoCore


def example_basic_encryption():
    """示例 1: 基本加密和解密"""
    print("\n" + "="*60)
    print("示例 1: 基本加密和解密")
    print("="*60)
    
    # 创建测试文件
    test_file = "example_test.txt"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("这是一个测试文件\n")
        f.write("包含一些敏感信息\n")
        f.write("需要加密保护\n")
    
    print(f"\n1. 创建测试文件: {test_file}")
    
    # 加密
    password = "MySecureP@ssw0rd"
    encrypted_file = test_file + ".encrypted"
    
    crypto = CryptoCore()
    print(f"2. 使用密码加密文件...")
    crypto.encrypt_file(test_file, encrypted_file, password)
    print(f"   ✓ 加密完成: {encrypted_file}")
    
    # 解密
    decrypted_file = "example_decrypted.txt"
    print(f"3. 解密文件...")
    crypto.decrypt_file(encrypted_file, decrypted_file, password)
    print(f"   ✓ 解密完成: {decrypted_file}")
    
    # 验证内容
    with open(decrypted_file, 'r', encoding='utf-8') as f:
        content = f.read()
    print(f"4. 验证内容:")
    print(f"   {content}")
    
    # 清理
    os.remove(test_file)
    os.remove(encrypted_file)
    os.remove(decrypted_file)
    print("5. 清理临时文件完成")


def example_different_kdf():
    """示例 2: 使用不同的密钥派生函数"""
    print("\n" + "="*60)
    print("示例 2: 使用不同的密钥派生函数")
    print("="*60)
    
    test_file = "kdf_test.txt"
    with open(test_file, 'w') as f:
        f.write("测试不同的 KDF")
    
    password = "TestKDF@123"
    
    # 使用 PBKDF2
    print("\n1. 使用 PBKDF2-HMAC-SHA512:")
    crypto_pbkdf2 = CryptoCore(kdf_type=CryptoCore.KDF_PBKDF2_SHA512)
    encrypted_pbkdf2 = "kdf_test_pbkdf2.encrypted"
    crypto_pbkdf2.encrypt_file(test_file, encrypted_pbkdf2, password)
    print(f"   ✓ 加密完成: {encrypted_pbkdf2}")
    
    # 使用 Argon2（如果可用）
    try:
        import argon2
        print("\n2. 使用 Argon2id:")
        crypto_argon2 = CryptoCore(kdf_type=CryptoCore.KDF_ARGON2ID)
        encrypted_argon2 = "kdf_test_argon2.encrypted"
        crypto_argon2.encrypt_file(test_file, encrypted_argon2, password)
        print(f"   ✓ 加密完成: {encrypted_argon2}")
        
        # 清理
        os.remove(encrypted_argon2)
    except ImportError:
        print("\n2. Argon2 不可用（需要安装 argon2-cffi）")
    
    # 清理
    os.remove(test_file)
    os.remove(encrypted_pbkdf2)
    print("\n3. 清理完成")


def example_password_strength():
    """示例 3: 密码强度检查"""
    print("\n" + "="*60)
    print("示例 3: 密码强度检查")
    print("="*60)
    
    test_passwords = [
        "123456",
        "password",
        "Password1",
        "P@ssw0rd",
        "MySecureP@ssw0rd123",
        "Tr0ub4dor&3",
    ]
    
    print("\n检查各种密码的强度:\n")
    for pwd in test_passwords:
        is_strong, message = CryptoCore.check_password_strength(pwd)
        status = "✓" if is_strong else "✗"
        print(f"{status} '{pwd}': {message}")


def example_large_file():
    """示例 4: 大文件加密"""
    print("\n" + "="*60)
    print("示例 4: 大文件加密（10MB）")
    print("="*60)
    
    # 创建 10MB 测试文件
    test_file = "large_test.bin"
    print(f"\n1. 创建 10MB 测试文件...")
    with open(test_file, 'wb') as f:
        for _ in range(10):
            f.write(os.urandom(1024 * 1024))
    print(f"   ✓ 文件创建完成: {test_file}")
    
    # 加密
    password = "LargeFile@Test"
    encrypted_file = test_file + ".encrypted"
    
    print(f"2. 加密大文件...")
    crypto = CryptoCore()
    info = crypto.encrypt_file(test_file, encrypted_file, password)
    print(f"   ✓ 加密完成")
    print(f"   - 原始大小: {info['original_size'] / (1024*1024):.2f} MB")
    print(f"   - 加密大小: {info['encrypted_size'] / (1024*1024):.2f} MB")
    
    # 解密
    decrypted_file = "large_decrypted.bin"
    print(f"3. 解密大文件...")
    crypto.decrypt_file(encrypted_file, decrypted_file, password)
    print(f"   ✓ 解密完成: {decrypted_file}")
    
    # 清理
    os.remove(test_file)
    os.remove(encrypted_file)
    os.remove(decrypted_file)
    print("4. 清理完成")


def example_api_usage():
    """示例 5: 作为 Python 库使用"""
    print("\n" + "="*60)
    print("示例 5: 作为 Python 库使用")
    print("="*60)
    
    print("\n代码示例:")
    print("""
from crypto_core import CryptoCore

# 创建加密核心实例
crypto = CryptoCore()

# 加密文件
crypto.encrypt_file(
    input_path='document.pdf',
    output_path='document.pdf.encrypted',
    password='YourSecurePassword'
)

# 解密文件
crypto.decrypt_file(
    input_path='document.pdf.encrypted',
    output_path='document.pdf',
    password='YourSecurePassword'
)

# 检查密码强度
is_strong, message = CryptoCore.check_password_strength('MyPassword')
print(f"密码强度: {message}")
    """)


def main():
    """运行所有示例"""
    print("\n" + "="*60)
    print("CLI 加密工具 - 使用示例")
    print("="*60)
    
    examples = [
        ("基本加密和解密", example_basic_encryption),
        ("不同的密钥派生函数", example_different_kdf),
        ("密码强度检查", example_password_strength),
        ("大文件加密", example_large_file),
        ("作为 Python 库使用", example_api_usage),
    ]
    
    print("\n可用示例:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    print(f"  0. 运行所有示例")
    
    try:
        choice = input("\n请选择示例 (0-5): ").strip()
        
        if choice == '0':
            for name, func in examples:
                try:
                    func()
                except Exception as e:
                    print(f"\n错误: {e}")
        elif choice.isdigit() and 1 <= int(choice) <= len(examples):
            name, func = examples[int(choice) - 1]
            func()
        else:
            print("无效选择")
            return 1
            
        print("\n" + "="*60)
        print("示例运行完成！")
        print("="*60 + "\n")
        return 0
        
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        return 0
    except Exception as e:
        print(f"\n错误: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())

