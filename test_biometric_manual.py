#!/usr/bin/env python3
"""测试生物识别功能"""

import subprocess
import sys

# 测试加密（交互式输入密码）
print("=== 测试 1: 加密文件（交互式输入密码）===\n")
print("请按照提示操作：")
print("1. 输入密码：TestPass123!")
print("2. 确认密码：TestPass123!")
print("3. 是否保存密码：y")
print()

result = subprocess.run([
    sys.executable, 'cli_encrypt.py', 
    'encrypt', 'bio_test.txt',
    '-o', 'bio_test.txt.enc'
])

if result.returncode == 0:
    print("\n✓ 加密成功！")
    print("\n=== 测试 2: 解密文件（应该弹出指纹识别）===\n")
    
    result = subprocess.run([
        sys.executable, 'cli_encrypt.py',
        'decrypt', 'bio_test.txt.enc',
        '-o', 'bio_test.txt.dec'
    ])
    
    if result.returncode == 0:
        print("\n✓ 解密成功！")
    else:
        print("\n✗ 解密失败")
else:
    print("\n✗ 加密失败")

