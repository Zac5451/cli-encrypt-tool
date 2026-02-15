#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生物识别功能演示脚本
展示如何使用 Touch ID/Face ID 进行文件加密和解密
"""

import os
import sys
import tempfile
from cli_encrypt import CLIEncryptTool, Colors
from biometric_auth import BiometricAuth

def print_header(title):
    """打印标题"""
    print(f"\n{Colors.OKCYAN}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{title:^60}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}{'=' * 60}{Colors.ENDC}\n")

def demo_biometric_check():
    """演示：检查生物识别是否可用"""
    print_header("步骤 1: 检查生物识别可用性")
    
    if BiometricAuth.is_available():
        print(f"{Colors.OKGREEN}✓ 生物识别可用{Colors.ENDC}")
        print(f"  您的设备支持 Touch ID 或 Face ID")
        return True
    else:
        print(f"{Colors.FAIL}✗ 生物识别不可用{Colors.ENDC}")
        print(f"  原因可能是：")
        print(f"  - 不是 macOS 系统")
        print(f"  - 设备不支持 Touch ID/Face ID")
        print(f"  - 未在系统设置中配置生物识别")
        return False

def demo_encrypt_with_save():
    """演示：加密文件并保存密码"""
    print_header("步骤 2: 加密文件并保存密码到钥匙串")
    
    # 创建临时测试文件
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("这是一个测试文件的内容\n")
        f.write("包含一些敏感信息\n")
        f.write("需要加密保护\n")
        test_file = f.name
    
    print(f"创建测试文件: {test_file}")
    print(f"\n{Colors.WARNING}提示：{Colors.ENDC}")
    print(f"  1. 请输入一个测试密码（例如：Test123!）")
    print(f"  2. 确认密码")
    print(f"  3. 当询问是否保存密码时，输入 'y'")
    print(f"\n按回车继续...")
    input()
    
    # 模拟加密命令
    print(f"\n{Colors.OKBLUE}执行命令：{Colors.ENDC}")
    print(f"  python3 cli_encrypt.py encrypt {test_file}")
    print(f"\n{Colors.WARNING}（实际演示中，这里会调用加密功能）{Colors.ENDC}")
    
    return test_file

def demo_decrypt_with_biometric(test_file):
    """演示：使用生物识别解密文件"""
    print_header("步骤 3: 使用生物识别解密文件")
    
    encrypted_file = test_file + '.encrypted'
    
    print(f"加密文件: {encrypted_file}")
    print(f"\n{Colors.WARNING}提示：{Colors.ENDC}")
    print(f"  1. 系统会检测到已保存的密码")
    print(f"  2. 询问是否使用生物识别验证")
    print(f"  3. 按回车或输入 'y' 确认")
    print(f"  4. 系统会弹出 Touch ID/Face ID 验证提示")
    print(f"  5. 验证成功后自动解密文件")
    print(f"\n按回车继续...")
    input()
    
    print(f"\n{Colors.OKBLUE}执行命令：{Colors.ENDC}")
    print(f"  python3 cli_encrypt.py decrypt {encrypted_file}")
    print(f"\n{Colors.WARNING}（实际演示中，这里会调用解密功能）{Colors.ENDC}")

def demo_advantages():
    """演示：生物识别的优势"""
    print_header("生物识别验证的优势")
    
    advantages = [
        ("🚀 便捷性", "无需记忆和输入复杂密码"),
        ("🔒 安全性", "密码存储在系统钥匙串，硬件级加密"),
        ("⚡ 快速", "指纹或面部识别只需1-2秒"),
        ("🔐 隔离", "每个文件独立存储密码凭证"),
        ("🛡️ 保护", "生物识别数据从不离开设备"),
        ("✨ 无缝", "与 macOS 系统完美集成"),
    ]
    
    for emoji_title, description in advantages:
        print(f"{Colors.OKGREEN}{emoji_title}{Colors.ENDC}")
        print(f"  {description}\n")

def demo_use_cases():
    """演示：使用场景"""
    print_header("典型使用场景")
    
    use_cases = [
        {
            "title": "个人文档加密",
            "description": "加密个人敏感文档，使用 Touch ID 快速访问",
            "example": "python3 cli_encrypt.py encrypt 身份证.pdf"
        },
        {
            "title": "工作文件保护",
            "description": "保护工作相关的机密文件",
            "example": "python3 cli_encrypt.py encrypt 合同.docx"
        },
        {
            "title": "批量加密",
            "description": "批量加密多个文件，统一使用生物识别管理",
            "example": "python3 cli_encrypt.py batch-encrypt '*.pdf' -o encrypted/"
        },
        {
            "title": "临时文件",
            "description": "加密临时下载的敏感文件",
            "example": "python3 cli_encrypt.py encrypt download.zip -e 7"
        }
    ]
    
    for i, case in enumerate(use_cases, 1):
        print(f"{Colors.BOLD}{i}. {case['title']}{Colors.ENDC}")
        print(f"   {case['description']}")
        print(f"   {Colors.OKCYAN}示例: {case['example']}{Colors.ENDC}\n")

def demo_comparison():
    """演示：传统方式 vs 生物识别"""
    print_header("传统密码 vs 生物识别对比")
    
    print(f"{Colors.BOLD}传统密码方式：{Colors.ENDC}")
    print(f"  1. 输入密码（可能需要查找密码管理器）")
    print(f"  2. 输入时可能被偷窥")
    print(f"  3. 容易输错，需要重新输入")
    print(f"  4. 复杂密码难以记忆")
    print(f"  {Colors.WARNING}⏱️  平均耗时：10-30秒{Colors.ENDC}\n")
    
    print(f"{Colors.BOLD}生物识别方式：{Colors.ENDC}")
    print(f"  1. 按下 Touch ID 或看向摄像头")
    print(f"  2. 验证成功，自动解密")
    print(f"  {Colors.OKGREEN}⚡ 平均耗时：1-2秒{Colors.ENDC}\n")
    
    print(f"{Colors.OKGREEN}效率提升：{Colors.ENDC}")
    print(f"  • 速度提升 5-15 倍")
    print(f"  • 无需记忆密码")
    print(f"  • 零输入错误")
    print(f"  • 更好的用户体验")

def main():
    """主演示函数"""
    print(f"\n{Colors.BOLD}{Colors.OKCYAN}")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "生物识别加密功能演示" + " " * 10 + "║")
    print("║" + " " * 8 + "Touch ID / Face ID 支持" + " " * 8 + "║")
    print("╚" + "=" * 58 + "╝")
    print(f"{Colors.ENDC}")
    
    print(f"\n{Colors.WARNING}本演示将展示如何使用生物识别功能进行文件加密和解密{Colors.ENDC}")
    print(f"\n按回车开始演示...")
    input()
    
    # 步骤 1: 检查可用性
    if not demo_biometric_check():
        print(f"\n{Colors.FAIL}无法继续演示，因为生物识别不可用{Colors.ENDC}")
        print(f"\n如果您在 macOS 上，请确保：")
        print(f"  1. 设备支持 Touch ID 或 Face ID")
        print(f"  2. 在系统偏好设置中已设置生物识别")
        print(f"  3. 已安装 keyring 库: pip install keyring")
        return
    
    input(f"\n按回车继续...")
    
    # 步骤 2: 加密演示
    test_file = demo_encrypt_with_save()
    
    input(f"\n按回车继续...")
    
    # 步骤 3: 解密演示
    demo_decrypt_with_biometric(test_file)
    
    input(f"\n按回车继续...")
    
    # 优势说明
    demo_advantages()
    
    input(f"\n按回车继续...")
    
    # 使用场景
    demo_use_cases()
    
    input(f"\n按回车继续...")
    
    # 对比说明
    demo_comparison()
    
    # 总结
    print_header("演示总结")
    
    print(f"{Colors.OKGREEN}✓ 生物识别功能已集成到 CLI 加密工具{Colors.ENDC}")
    print(f"{Colors.OKGREEN}✓ 支持 Touch ID 和 Face ID{Colors.ENDC}")
    print(f"{Colors.OKGREEN}✓ 密码安全存储在系统钥匙串{Colors.ENDC}")
    print(f"{Colors.OKGREEN}✓ 无缝集成，自动检测{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}开始使用：{Colors.ENDC}")
    print(f"  1. 加密文件: python3 cli_encrypt.py encrypt <文件>")
    print(f"  2. 选择保存密码到钥匙串")
    print(f"  3. 解密时使用生物识别验证")
    
    print(f"\n{Colors.BOLD}详细文档：{Colors.ENDC}")
    print(f"  • README.md - 完整使用说明")
    print(f"  • BIOMETRIC_AUTH_GUIDE.md - 生物识别详细指南")
    
    print(f"\n{Colors.OKCYAN}感谢使用 CLI 加密工具！{Colors.ENDC}\n")
    
    # 清理
    if os.path.exists(test_file):
        os.remove(test_file)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}演示被用户中断{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n{Colors.FAIL}演示过程中发生错误: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

