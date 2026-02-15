#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示脚本 - 展示工具的基本功能（无需安装依赖）
"""

import os

def print_banner():
    """打印横幅"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║          CLI 加密工具 - 基于 VeraCrypt 设计理念           ║
║                                                           ║
║  功能特性：                                               ║
║  ✓ AES-256-GCM 军事级加密                                ║
║  ✓ Argon2/PBKDF2 密钥派生                                ║
║  ✓ 大文件分块处理                                        ║
║  ✓ 密码强度检查                                          ║
║  ✓ 完整性验证                                            ║
║  ✓ 安全删除选项                                          ║
╚═══════════════════════════════════════════════════════════╝
""")

def print_project_structure():
    """打印项目结构"""
    print("""
项目结构：
cli-encrypt-tool/
├── crypto_core.py          # 核心加密模块 (10KB)
│   └── CryptoCore 类
│       ├── encrypt_file()      - 文件加密
│       ├── decrypt_file()      - 文件解密
│       └── check_password_strength() - 密码检查
│
├── cli_encrypt.py          # 命令行界面 (12KB)
│   └── CLIEncryptTool 类
│       ├── encrypt_command()   - 加密命令
│       ├── decrypt_command()   - 解密命令
│       └── 彩色终端输出
│
├── test_crypto.py          # 测试套件 (10KB)
│   └── 6 个测试用例
│       ├── 密码强度检查
│       ├── PBKDF2/Argon2 测试
│       ├── 错误密码检测
│       ├── 大文件测试
│       └── 空文件测试
│
├── examples.py             # 使用示例 (7KB)
│   └── 5 个交互式示例
│
├── requirements.txt        # Python 依赖
├── install.sh              # 自动安装脚本
├── README.md               # 完整文档
├── QUICKSTART.md           # 快速开始
└── PROJECT_SUMMARY.md      # 项目总结
""")

def print_usage_examples():
    """打印使用示例"""
    print("""
使用示例：

1. 基本加密
   $ python3 cli_encrypt.py encrypt document.pdf
   请输入加密密码: ********
   确认密码: ********
   ✓ 加密成功！
   输出文件: document.pdf.encrypted

2. 指定输出文件
   $ python3 cli_encrypt.py encrypt -o backup.enc document.pdf

3. 使用 Argon2（更安全）
   $ python3 cli_encrypt.py encrypt --kdf argon2 secret.txt

4. 加密后删除原文件
   $ python3 cli_encrypt.py encrypt --delete-original sensitive.doc

5. 解密文件
   $ python3 cli_encrypt.py decrypt document.pdf.encrypted
   请输入解密密码: ********
   ✓ 解密成功！
   输出文件: document.pdf

6. 解密后删除加密文件
   $ python3 cli_encrypt.py decrypt --delete-encrypted backup.enc

7. 查看帮助
   $ python3 cli_encrypt.py --help
   $ python3 cli_encrypt.py encrypt --help
""")

def print_technical_details():
    """打印技术细节"""
    print("""
技术细节：

加密算法：
  • AES-256-GCM (认证加密)
  • 256 位密钥长度
  • 12 字节 Nonce
  • 16 字节认证标签

密钥派生：
  • Argon2id: 3 次迭代, 64MB 内存, 4 线程
  • PBKDF2-HMAC-SHA512: 500,000 次迭代
  • 64 字节随机盐值

文件格式：
  [文件头 92 字节]
    - 魔数: VCCLI (5 字节)
    - 版本: 1 (1 字节)
    - KDF 类型: 1=PBKDF2, 2=Argon2 (1 字节)
    - 保留: 0 (1 字节)
    - 原始大小: (8 字节)
    - 盐值: (64 字节)
    - Nonce: (12 字节)
  
  [加密数据]
    - 分块大小: 64KB
    - 每块独立加密
    - 包含 GCM 认证标签

安全特性：
  ✓ 防暴力破解（高迭代次数）
  ✓ 防彩虹表攻击（随机盐值）
  ✓ 防篡改（GCM 认证）
  ✓ 密码强度检查
  ✓ 内存密钥清理
  ✓ 可选安全删除
""")

def print_comparison():
    """打印与 VeraCrypt 的对比"""
    print("""
与 VeraCrypt 的对比：

┌─────────────────┬──────────────────┬──────────────────┐
│     特性        │    VeraCrypt     │    本工具        │
├─────────────────┼──────────────────┼──────────────────┤
│ 用途            │ 整盘/分区加密    │ 文件加密         │
│ 加密算法        │ AES/Serpent等    │ AES-256          │
│ 加密模式        │ XTS              │ GCM              │
│ 密钥派生        │ PBKDF2/Argon2    │ PBKDF2/Argon2    │
│ 盐值大小        │ 64 字节          │ 64 字节          │
│ 挂载方式        │ 虚拟磁盘         │ 直接解密         │
│ 隐藏卷          │ 支持             │ 不支持           │
│ 平台            │ Win/Linux/macOS  │ 跨平台(Python)   │
│ 复杂度          │ 高               │ 低               │
│ 学习曲线        │ 陡峭             │ 平缓             │
└─────────────────┴──────────────────┴──────────────────┘

设计借鉴：
  • 盐值大小 (PKCS5_SALT_SIZE = 64)
  • 密钥派生算法 (PBKDF2-SHA512, Argon2)
  • 分块处理理念
  • 安全性优先原则
""")

def print_installation():
    """打印安装说明"""
    print("""
安装步骤：

1. 确保已安装 Python 3.7+
   $ python3 --version

2. 进入项目目录
   $ cd cli-encrypt-tool

3. 安装依赖（需要网络连接）
   $ pip3 install -r requirements.txt
   
   或使用自动安装脚本：
   $ ./install.sh

4. 运行测试
   $ python3 test_crypto.py

5. 查看示例
   $ python3 examples.py

6. 开始使用
   $ python3 cli_encrypt.py encrypt myfile.txt

依赖项：
  • cryptography>=41.0.0  (核心加密库)
  • argon2-cffi>=23.1.0   (Argon2 支持，可选)

注意：
  - 如果无法安装 argon2-cffi，工具会自动使用 PBKDF2
  - 首次安装可能需要编译，请耐心等待
  - macOS 用户可能需要安装 Xcode Command Line Tools
""")

def print_quick_test():
    """打印快速测试"""
    print("""
快速测试（无需安装依赖）：

# 查看项目文件
$ ls -lh

# 查看核心代码结构
$ head -50 crypto_core.py

# 查看命令行界面
$ head -50 cli_encrypt.py

# 查看完整文档
$ cat README.md

# 查看快速开始
$ cat QUICKSTART.md

# 查看项目总结
$ cat PROJECT_SUMMARY.md
""")

def main():
    """主函数"""
    print_banner()
    
    print("\n" + "="*60)
    print("欢迎使用 CLI 加密工具演示")
    print("="*60)
    
    sections = [
        ("1", "项目结构", print_project_structure),
        ("2", "使用示例", print_usage_examples),
        ("3", "技术细节", print_technical_details),
        ("4", "与 VeraCrypt 对比", print_comparison),
        ("5", "安装说明", print_installation),
        ("6", "快速测试", print_quick_test),
    ]
    
    print("\n可用章节：")
    for num, title, _ in sections:
        print(f"  {num}. {title}")
    print("  0. 显示全部")
    print("  q. 退出")
    
    while True:
        try:
            choice = input("\n请选择 (0-6, q): ").strip().lower()
            
            if choice == 'q':
                print("\n再见！")
                break
            elif choice == '0':
                for _, title, func in sections:
                    print("\n" + "="*60)
                    print(title)
                    print("="*60)
                    func()
                break
            elif choice.isdigit() and 1 <= int(choice) <= len(sections):
                _, title, func = sections[int(choice) - 1]
                print("\n" + "="*60)
                print(title)
                print("="*60)
                func()
            else:
                print("无效选择，请重试")
        except KeyboardInterrupt:
            print("\n\n操作已取消")
            break
        except Exception as e:
            print(f"\n错误: {e}")

if __name__ == '__main__':
    main()

