#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
隐写术加密演示脚本
展示如何将加密文件伪装成普通文件
"""

import os
import sys
import tempfile
from steganography import SteganographyEncryption

def print_header(title):
    """打印标题"""
    print(f"\n{'=' * 70}")
    print(f"{title:^70}")
    print(f"{'=' * 70}\n")

def demo_basic_concept():
    """演示基本概念"""
    print_header("隐写术加密 - 基本概念")
    
    print("什么是隐写术加密？")
    print("-" * 70)
    print()
    print("普通加密：")
    print("  secret.pdf  →  [加密]  →  secret.pdf.encrypted")
    print("                              ↑")
    print("                         明显是加密文件！")
    print()
    print("隐写术加密：")
    print("  secret.pdf + cover.txt  →  [隐写加密]  →  document.txt")
    print("                                              ↑")
    print("                                    看起来像普通文本文件！")
    print()
    print("核心特点：")
    print("  ✓ 加密文件伪装成普通文件")
    print("  ✓ 可以正常打开伪装文件")
    print("  ✓ 秘密数据隐藏在文件末尾")
    print("  ✓ 难以被察觉")
    print()

def demo_file_structure():
    """演示文件结构"""
    print_header("文件结构")
    
    print("隐写加密文件的内部结构：")
    print("-" * 70)
    print()
    print("┌─────────────────────────────────────────────────────────────┐")
    print("│                    伪装文件数据                             │")
    print("│              (可以正常打开和查看)                           │")
    print("│                                                             │")
    print("│  例如：文本内容、图片数据、视频流等                         │")
    print("│                                                             │")
    print("├─────────────────────────────────────────────────────────────┤")
    print("│                  加密的秘密数据                             │")
    print("│               (隐藏在文件末尾)                              │")
    print("│                                                             │")
    print("│  使用 AES-256-GCM 加密                                      │")
    print("│  需要密码才能解密                                           │")
    print("│                                                             │")
    print("├─────────────────────────────────────────────────────────────┤")
    print("│                  元数据和标记                               │")
    print("│                (很小，难以察觉)                             │")
    print("│                                                             │")
    print("│  包含：文件名、大小、偏移量等                               │")
    print("└─────────────────────────────────────────────────────────────┘")
    print()

def demo_use_cases():
    """演示使用场景"""
    print_header("典型使用场景")
    
    scenarios = [
        {
            "title": "场景 1：隐藏敏感文档",
            "secret": "机密合同.pdf",
            "cover": "会议记录.txt",
            "output": "2024年会议记录.txt",
            "description": "将机密合同隐藏在普通的会议记录中"
        },
        {
            "title": "场景 2：伪装成图片",
            "secret": "私密照片.jpg",
            "cover": "风景.jpg",
            "output": "度假照片.jpg",
            "description": "将私密照片隐藏在风景照中"
        },
        {
            "title": "场景 3：伪装成视频",
            "secret": "重要会议.mp4",
            "cover": "旅游视频.mp4",
            "output": "假期旅游.mp4",
            "description": "将重要会议视频隐藏在旅游视频中"
        },
        {
            "title": "场景 4：伪装成日志",
            "secret": "敏感数据.xlsx",
            "cover": "系统日志.log",
            "output": "system.log",
            "description": "将敏感数据隐藏在系统日志中"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"{i}. {scenario['title']}")
        print(f"   {scenario['description']}")
        print()
        print(f"   命令：")
        print(f"   python3 cli_encrypt.py stego-encrypt \\")
        print(f"       {scenario['secret']} {scenario['cover']} \\")
        print(f"       -o {scenario['output']} -p \"密码\"")
        print()
        print(f"   结果：")
        print(f"   • 别人看到：{scenario['output']} (普通文件)")
        print(f"   • 实际包含：加密的 {scenario['secret']}")
        print()

def demo_comparison():
    """演示对比"""
    print_header("普通加密 vs 隐写术加密")
    
    print("┌────────────────┬─────────────────┬─────────────────────┐")
    print("│    特性        │   普通加密      │    隐写术加密       │")
    print("├────────────────┼─────────────────┼─────────────────────┤")
    print("│ 隐蔽性         │ ❌ 明显         │ ✅ 隐蔽             │")
    print("│ 文件后缀       │ .encrypted      │ 任意正常后缀        │")
    print("│ 可打开性       │ ❌ 无法打开     │ ✅ 可以打开         │")
    print("│ 安全性         │ ✅ AES-256      │ ✅ AES-256          │")
    print("│ 文件大小       │ 略大于原文件    │ 伪装+原文件         │")
    print("│ 适用场景       │ 一般加密        │ 需要隐蔽            │")
    print("└────────────────┴─────────────────┴─────────────────────┘")
    print()

def demo_commands():
    """演示命令"""
    print_header("常用命令")
    
    print("1. 隐写加密")
    print("-" * 70)
    print("python3 cli_encrypt.py stego-encrypt <秘密文件> <伪装文件> \\")
    print("    -o <输出文件> -p <密码>")
    print()
    print("示例：")
    print("python3 cli_encrypt.py stego-encrypt secret.pdf cover.txt \\")
    print("    -o document.txt -p \"MyPassword123\"")
    print()
    
    print("2. 隐写解密")
    print("-" * 70)
    print("python3 cli_encrypt.py stego-decrypt <隐写文件> \\")
    print("    -o <输出文件> -p <密码>")
    print()
    print("示例：")
    print("python3 cli_encrypt.py stego-decrypt document.txt \\")
    print("    -o secret.pdf -p \"MyPassword123\"")
    print()
    
    print("3. 查看文件信息")
    print("-" * 70)
    print("python3 cli_encrypt.py stego-info <文件>")
    print()
    print("示例：")
    print("python3 cli_encrypt.py stego-info document.txt")
    print()
    
    print("4. 提取伪装文件")
    print("-" * 70)
    print("python3 cli_encrypt.py stego-extract <隐写文件> -o <输出文件>")
    print()
    print("示例：")
    print("python3 cli_encrypt.py stego-extract document.txt -o cover.txt")
    print()

def demo_live_example():
    """实际演示"""
    print_header("实际演示")
    
    print("现在进行一个实际的隐写加密演示...")
    print()
    
    try:
        stego = SteganographyEncryption()
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("这是一个秘密文件的内容\n")
            f.write("包含敏感信息\n")
            f.write("需要加密保护\n")
            secret_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("这是一个普通的文本文件\n")
            f.write("看起来没有任何问题\n")
            f.write("可以正常打开和阅读\n")
            f.write("\n" * 10)
            f.write("Lorem ipsum dolor sit amet...\n" * 20)
            cover_file = f.name
        
        output_file = tempfile.mktemp(suffix='.txt')
        
        print(f"1. 创建秘密文件: {os.path.basename(secret_file)}")
        print(f"   内容: 敏感信息")
        print(f"   大小: {os.path.getsize(secret_file)} 字节")
        print()
        
        print(f"2. 创建伪装文件: {os.path.basename(cover_file)}")
        print(f"   内容: 普通文本")
        print(f"   大小: {os.path.getsize(cover_file)} 字节")
        print()
        
        print("3. 执行隐写加密...")
        result = stego.encrypt_with_cover(
            secret_file, cover_file, output_file, "DemoPassword123"
        )
        print("   ✓ 加密完成")
        print()
        
        print(f"4. 输出文件: {os.path.basename(output_file)}")
        print(f"   总大小: {result['total_size']} 字节")
        print(f"   伪装大小: {result['cover_size']} 字节")
        print(f"   加密大小: {result['encrypted_size']} 字节")
        print()
        
        print("5. 查看文件信息...")
        info = stego.get_stego_info(output_file)
        if info:
            print("   ✓ 这是一个隐写加密文件")
            print(f"   秘密文件名: {info['secret_filename']}")
            print(f"   伪装文件名: {info['cover_filename']}")
            print(f"   隐藏比例: {(info['encrypted_size']/info['total_size']*100):.1f}%")
        print()
        
        print("6. 解密测试...")
        decrypted_file = tempfile.mktemp(suffix='.txt')
        result = stego.decrypt_from_cover(output_file, decrypted_file, "DemoPassword123")
        print("   ✓ 解密成功")
        print(f"   输出文件: {os.path.basename(decrypted_file)}")
        print()
        
        # 清理
        for f in [secret_file, cover_file, output_file, decrypted_file]:
            if os.path.exists(f):
                os.remove(f)
        
        print("✓ 演示完成！")
        
    except Exception as e:
        print(f"✗ 演示失败: {e}")
        import traceback
        traceback.print_exc()

def demo_security():
    """演示安全性"""
    print_header("安全性说明")
    
    print("优势：")
    print("-" * 70)
    print("  ✓ 隐蔽性 - 文件看起来完全正常")
    print("  ✓ 双重保护 - 隐藏 + 加密")
    print("  ✓ 难以检测 - 没有明显的加密特征")
    print("  ✓ 强加密 - 使用 AES-256-GCM")
    print()
    
    print("注意事项：")
    print("-" * 70)
    print("  • 文件大小会增加（伪装文件 + 秘密文件）")
    print("  • 选择合适的伪装文件很重要")
    print("  • 伪装文件应该比秘密文件大")
    print("  • 使用强密码保护")
    print()
    
    print("最佳实践：")
    print("-" * 70)
    print("  1. 伪装文件至少是秘密文件的 2 倍大")
    print("  2. 选择常见的文件类型")
    print("  3. 使用合理的文件名")
    print("  4. 结合生物识别功能（macOS）")
    print("  5. 定期更换伪装文件")
    print()

def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("隐写术加密功能演示".center(70))
    print("Steganography Encryption Demo".center(70))
    print("=" * 70)
    
    print("\n本演示将展示如何使用隐写术加密功能")
    print("将加密文件伪装成普通文件，实现隐蔽加密")
    
    input("\n按回车开始演示...")
    
    # 1. 基本概念
    demo_basic_concept()
    input("\n按回车继续...")
    
    # 2. 文件结构
    demo_file_structure()
    input("\n按回车继续...")
    
    # 3. 使用场景
    demo_use_cases()
    input("\n按回车继续...")
    
    # 4. 对比
    demo_comparison()
    input("\n按回车继续...")
    
    # 5. 命令
    demo_commands()
    input("\n按回车继续...")
    
    # 6. 实际演示
    demo_live_example()
    input("\n按回车继续...")
    
    # 7. 安全性
    demo_security()
    
    # 总结
    print_header("演示总结")
    
    print("✓ 隐写术加密功能已集成到 CLI 加密工具")
    print("✓ 支持多种文件类型伪装")
    print("✓ 提供双重保护（隐藏 + 加密）")
    print("✓ 使用 AES-256-GCM 强加密")
    print()
    print("开始使用：")
    print("  python3 cli_encrypt.py stego-encrypt <秘密文件> <伪装文件> \\")
    print("      -o <输出文件> -p <密码>")
    print()
    print("详细文档：")
    print("  • STEGANOGRAPHY_GUIDE.md - 完整使用指南")
    print("  • README.md - 所有功能说明")
    print()
    print("=" * 70)
    print("感谢使用 CLI 加密工具！".center(70))
    print("=" * 70)
    print()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n演示被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n✗ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

