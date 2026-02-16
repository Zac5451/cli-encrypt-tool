#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E2E 端到端测试套件
模拟真实用户场景，测试完整的命令行工具功能
"""

import os
import sys
import subprocess
import tempfile
import shutil
import time
import json
from pathlib import Path
from typing import List, Dict, Tuple


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'


class E2ETestRunner:
    """E2E 测试运行器"""
    
    def __init__(self):
        self.test_dir = None
        self.cli_path = "cli_encrypt.py"
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.test_results = []
    
    def setup(self):
        """设置测试环境"""
        self.test_dir = tempfile.mkdtemp(prefix="e2e_test_")
        print(f"{Colors.CYAN}测试目录: {self.test_dir}{Colors.ENDC}\n")
    
    def teardown(self):
        """清理测试环境"""
        if self.test_dir and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def run_cli(self, args: List[str], input_text: str = None, timeout: int = 30) -> Tuple[int, str, str]:
        """
        运行 CLI 命令
        
        Returns:
            (returncode, stdout, stderr)
        """
        cmd = [sys.executable, self.cli_path] + args
        
        try:
            result = subprocess.run(
                cmd,
                input=input_text.encode() if input_text else None,
                capture_output=True,
                timeout=timeout,
                cwd=os.getcwd()
            )
            return result.returncode, result.stdout.decode('utf-8', errors='ignore'), result.stderr.decode('utf-8', errors='ignore')
        except subprocess.TimeoutExpired:
            return -1, "", "命令超时"
        except Exception as e:
            return -1, "", str(e)
    
    def create_test_file(self, filename: str, content: str = None, size: int = None) -> str:
        """创建测试文件"""
        filepath = os.path.join(self.test_dir, filename)
        
        if size:
            # 创建指定大小的文件
            with open(filepath, 'wb') as f:
                f.write(os.urandom(size))
        else:
            # 创建文本文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content or "Test content")
        
        return filepath
    
    def assert_file_exists(self, filepath: str) -> bool:
        """断言文件存在"""
        return os.path.exists(filepath)
    
    def assert_file_content(self, filepath: str, expected: str) -> bool:
        """断言文件内容"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read() == expected
        except:
            return False
    
    def log_test(self, name: str, passed: bool, message: str = ""):
        """记录测试结果"""
        if passed:
            self.passed += 1
            status = f"{Colors.GREEN}✓ PASS{Colors.ENDC}"
        else:
            self.failed += 1
            status = f"{Colors.RED}✗ FAIL{Colors.ENDC}"
        
        self.test_results.append({
            'name': name,
            'passed': passed,
            'message': message
        })
        
        print(f"{status} {name}")
        if message and not passed:
            print(f"  {Colors.YELLOW}→ {message}{Colors.ENDC}")
    
    def skip_test(self, name: str, reason: str):
        """跳过测试"""
        self.skipped += 1
        self.test_results.append({
            'name': name,
            'passed': None,
            'message': reason
        })
        print(f"{Colors.YELLOW}⊘ SKIP{Colors.ENDC} {name}")
        print(f"  {Colors.YELLOW}→ {reason}{Colors.ENDC}")
    
    # ==================== 测试用例 ====================
    
    def test_basic_encrypt_decrypt(self):
        """测试：基本加密解密流程"""
        test_file = self.create_test_file("test1.txt", "Hello World!")
        encrypted_file = test_file + ".encrypted"
        decrypted_file = test_file + ".decrypted"
        
        # 加密
        returncode, stdout, stderr = self.run_cli([
            'encrypt', test_file,
            '-o', encrypted_file,
            '-p', 'TestPassword123!'
        ])
        
        if returncode != 0:
            self.log_test("基本加密", False, f"加密失败: {stderr}")
            return
        
        if not self.assert_file_exists(encrypted_file):
            self.log_test("基本加密", False, "加密文件未生成")
            return
        
        self.log_test("基本加密", True)
        
        # 解密
        returncode, stdout, stderr = self.run_cli([
            'decrypt', encrypted_file,
            '-o', decrypted_file,
            '-p', 'TestPassword123!'
        ])
        
        if returncode != 0:
            self.log_test("基本解密", False, f"解密失败: {stderr}")
            return
        
        if not self.assert_file_content(decrypted_file, "Hello World!"):
            self.log_test("基本解密", False, "解密内容不匹配")
            return
        
        self.log_test("基本解密", True)
    
    def test_wrong_password(self):
        """测试：错误密码应该失败"""
        test_file = self.create_test_file("test2.txt", "Secret")
        encrypted_file = test_file + ".encrypted"
        
        # 加密
        self.run_cli(['encrypt', test_file, '-o', encrypted_file, '-p', 'CorrectPass'])
        
        # 用错误密码解密
        returncode, stdout, stderr = self.run_cli([
            'decrypt', encrypted_file,
            '-o', test_file + ".dec",
            '-p', 'WrongPass'
        ])
        
        # 应该失败
        passed = returncode != 0
        self.log_test("错误密码拒绝", passed, "错误密码应该被拒绝" if not passed else "")
    
    def test_chinese_content(self):
        """测试：中文内容加密解密"""
        content = "这是中文测试内容！包含特殊字符：@#￥%……&*（）"
        test_file = self.create_test_file("test_cn.txt", content)
        encrypted_file = test_file + ".encrypted"
        decrypted_file = test_file + ".decrypted"
        
        # 加密
        returncode, _, _ = self.run_cli([
            'encrypt', test_file, '-o', encrypted_file, '-p', '中文密码123'
        ])
        
        if returncode != 0:
            self.log_test("中文内容加密", False, "加密失败")
            return
        
        # 解密
        returncode, _, _ = self.run_cli([
            'decrypt', encrypted_file, '-o', decrypted_file, '-p', '中文密码123'
        ])
        
        passed = returncode == 0 and self.assert_file_content(decrypted_file, content)
        self.log_test("中文内容加密解密", passed)
    
    def test_empty_file(self):
        """测试：空文件处理"""
        test_file = self.create_test_file("empty.txt", "")
        encrypted_file = test_file + ".encrypted"
        decrypted_file = test_file + ".decrypted"
        
        returncode, _, _ = self.run_cli([
            'encrypt', test_file, '-o', encrypted_file, '-p', 'Pass123'
        ])
        
        if returncode != 0:
            self.log_test("空文件加密", False, "空文件加密失败")
            return
        
        returncode, _, _ = self.run_cli([
            'decrypt', encrypted_file, '-o', decrypted_file, '-p', 'Pass123'
        ])
        
        passed = returncode == 0 and os.path.getsize(decrypted_file) == 0
        self.log_test("空文件加密解密", passed)
    
    def test_large_file(self):
        """测试：大文件加密（10MB）"""
        test_file = self.create_test_file("large.bin", size=10*1024*1024)
        encrypted_file = test_file + ".encrypted"
        decrypted_file = test_file + ".decrypted"
        
        # 读取原始内容
        with open(test_file, 'rb') as f:
            original_content = f.read()
        
        # 加密
        returncode, _, _ = self.run_cli([
            'encrypt', test_file, '-o', encrypted_file, '-p', 'Pass123'
        ], timeout=60)
        
        if returncode != 0:
            self.log_test("大文件加密", False, "加密失败")
            return
        
        # 解密
        returncode, _, _ = self.run_cli([
            'decrypt', encrypted_file, '-o', decrypted_file, '-p', 'Pass123'
        ], timeout=60)
        
        if returncode != 0:
            self.log_test("大文件解密", False, "解密失败")
            return
        
        # 验证内容
        with open(decrypted_file, 'rb') as f:
            decrypted_content = f.read()
        
        passed = original_content == decrypted_content
        self.log_test("大文件加密解密", passed)
    
    def test_different_algorithms(self):
        """测试：不同加密算法"""
        algorithms = ['aes256', 'chacha20']
        
        for algo in algorithms:
            test_file = self.create_test_file(f"test_{algo}.txt", f"Test {algo}")
            encrypted_file = test_file + ".encrypted"
            decrypted_file = test_file + ".decrypted"
            
            # 加密
            returncode, _, _ = self.run_cli([
                'encrypt', test_file,
                '-o', encrypted_file,
                '-p', 'Pass123',
                '-a', algo
            ])
            
            if returncode != 0:
                self.log_test(f"算法 {algo} 加密", False, "加密失败")
                continue
            
            # 解密
            returncode, _, _ = self.run_cli([
                'decrypt', encrypted_file,
                '-o', decrypted_file,
                '-p', 'Pass123'
            ])
            
            passed = returncode == 0 and self.assert_file_content(decrypted_file, f"Test {algo}")
            self.log_test(f"算法 {algo} 加密解密", passed)
    
    def test_stream_encryption(self):
        """测试：流式加密"""
        input_data = "Stream test data\n" * 100
        
        # 流式加密
        returncode, encrypted_output, _ = self.run_cli([
            'stream-encrypt', '-p', 'Pass123'
        ], input_text=input_data)
        
        if returncode != 0:
            self.log_test("流式加密", False, "加密失败")
            return
        
        # 流式解密
        returncode, decrypted_output, _ = self.run_cli([
            'stream-decrypt', '-p', 'Pass123'
        ], input_text=encrypted_output)
        
        passed = returncode == 0 and decrypted_output == input_data
        self.log_test("流式加密解密", passed)
    
    def test_force_overwrite(self):
        """测试：强制覆盖已存在文件"""
        test_file = self.create_test_file("test_overwrite.txt", "Original")
        encrypted_file = test_file + ".encrypted"
        
        # 第一次加密
        self.run_cli(['encrypt', test_file, '-o', encrypted_file, '-p', 'Pass123'])
        
        # 修改原文件
        with open(test_file, 'w') as f:
            f.write("Modified")
        
        # 第二次加密（强制覆盖）
        returncode, _, _ = self.run_cli([
            'encrypt', test_file,
            '-o', encrypted_file,
            '-p', 'Pass123',
            '-f'  # 强制覆盖
        ])
        
        passed = returncode == 0
        self.log_test("强制覆盖文件", passed)
    
    def test_delete_original(self):
        """测试：加密后删除原文件"""
        test_file = self.create_test_file("test_delete.txt", "Delete me")
        encrypted_file = test_file + ".encrypted"
        
        returncode, _, _ = self.run_cli([
            'encrypt', test_file,
            '-o', encrypted_file,
            '-p', 'Pass123',
            '-d'  # 删除原文件
        ])
        
        passed = returncode == 0 and not os.path.exists(test_file) and os.path.exists(encrypted_file)
        self.log_test("加密后删除原文件", passed)
    
    def test_help_command(self):
        """测试：帮助命令"""
        returncode, stdout, _ = self.run_cli(['--help'])
        
        passed = returncode == 0 and 'encrypt' in stdout and 'decrypt' in stdout
        self.log_test("帮助命令", passed)
    
    def test_nonexistent_file(self):
        """测试：不存在的文件"""
        returncode, _, stderr = self.run_cli([
            'encrypt', '/nonexistent/file.txt',
            '-p', 'Pass123'
        ])
        
        # 应该失败
        passed = returncode != 0
        self.log_test("不存在文件处理", passed)
    
    def test_special_characters_in_filename(self):
        """测试：文件名包含特殊字符"""
        test_file = self.create_test_file("test 文件 (1).txt", "Special chars")
        encrypted_file = test_file + ".encrypted"
        decrypted_file = test_file + ".decrypted"
        
        returncode, _, _ = self.run_cli([
            'encrypt', test_file, '-o', encrypted_file, '-p', 'Pass123'
        ])
        
        if returncode != 0:
            self.log_test("特殊字符文件名", False, "加密失败")
            return
        
        returncode, _, _ = self.run_cli([
            'decrypt', encrypted_file, '-o', decrypted_file, '-p', 'Pass123'
        ])
        
        passed = returncode == 0 and self.assert_file_content(decrypted_file, "Special chars")
        self.log_test("特殊字符文件名", passed)
    
    def test_dry_run(self):
        """测试：预览模式"""
        test_file = self.create_test_file("test_dryrun.txt", "Dry run test")
        
        returncode, stdout, _ = self.run_cli([
            'dry-run', test_file
        ])
        
        # 预览不应该创建加密文件
        encrypted_file = test_file + ".encrypted"
        passed = returncode == 0 and not os.path.exists(encrypted_file) and "预览" in stdout
        self.log_test("预览模式", passed)
    
    def test_batch_encrypt(self):
        """测试：批量加密"""
        # 创建多个文件
        files = []
        for i in range(3):
            f = self.create_test_file(f"batch_{i}.txt", f"Content {i}")
            files.append(f)
        
        # 批量加密
        pattern = os.path.join(self.test_dir, "batch_*.txt")
        output_dir = os.path.join(self.test_dir, "encrypted")
        
        returncode, stdout, _ = self.run_cli([
            'batch-encrypt', pattern,
            '-o', output_dir,
            '-p', 'Pass123'
        ])
        
        if returncode != 0:
            self.log_test("批量加密", False, "批量加密失败")
            return
        
        # 检查是否生成了加密文件
        encrypted_count = len([f for f in os.listdir(output_dir) if f.endswith('.encrypted')])
        passed = encrypted_count == 3
        self.log_test("批量加密", passed, f"生成了 {encrypted_count}/3 个加密文件")
    
    def test_verbose_mode(self):
        """测试：详细输出模式"""
        test_file = self.create_test_file("test_verbose.txt", "Verbose test")
        encrypted_file = test_file + ".encrypted"
        
        returncode, stdout, _ = self.run_cli([
            '-v',  # 详细模式
            'encrypt', test_file,
            '-o', encrypted_file,
            '-p', 'Pass123'
        ])
        
        # 详细模式应该有更多输出
        passed = returncode == 0 and len(stdout) > 100
        self.log_test("详细输出模式", passed)
    
    def test_concurrent_operations(self):
        """测试：并发操作（多线程）"""
        test_file = self.create_test_file("test_threads.txt", "Thread test" * 1000)
        encrypted_file = test_file + ".encrypted"
        
        returncode, _, _ = self.run_cli([
            'encrypt', test_file,
            '-o', encrypted_file,
            '-p', 'Pass123',
            '-t', '4'  # 4个线程
        ])
        
        passed = returncode == 0 and os.path.exists(encrypted_file)
        self.log_test("多线程加密", passed)
    
    def test_password_strength_check(self):
        """测试：密码强度检查（通过 Python API）"""
        from crypto_core import CryptoCore
        
        weak_passwords = ["123", "abc", "password"]
        strong_passwords = ["StrongPass123!", "Secure@2024", "MyP@ssw0rd"]
        
        all_passed = True
        
        for pwd in weak_passwords:
            is_strong, _ = CryptoCore.check_password_strength(pwd)
            if is_strong:
                all_passed = False
                break
        
        for pwd in strong_passwords:
            is_strong, _ = CryptoCore.check_password_strength(pwd)
            if not is_strong:
                all_passed = False
                break
        
        self.log_test("密码强度检查", all_passed)
    
    def test_file_integrity(self):
        """测试：文件完整性验证"""
        test_file = self.create_test_file("test_integrity.txt", "Integrity test")
        encrypted_file = test_file + ".encrypted"
        
        # 加密
        self.run_cli(['encrypt', test_file, '-o', encrypted_file, '-p', 'Pass123'])
        
        # 损坏加密文件
        with open(encrypted_file, 'r+b') as f:
            f.seek(100)
            f.write(b'\x00' * 10)
        
        # 尝试解密损坏的文件
        returncode, _, _ = self.run_cli([
            'decrypt', encrypted_file,
            '-o', test_file + ".dec",
            '-p', 'Pass123'
        ])
        
        # 应该失败
        passed = returncode != 0
        self.log_test("文件完整性验证", passed, "损坏的文件应该被检测到" if not passed else "")
    
    def test_emoji_content(self):
        """测试：Emoji 内容"""
        content = "🎉 Hello 🌍 World! 🎊 测试 Emoji 😀"
        test_file = self.create_test_file("test_emoji.txt", content)
        encrypted_file = test_file + ".encrypted"
        decrypted_file = test_file + ".decrypted"
        
        self.run_cli(['encrypt', test_file, '-o', encrypted_file, '-p', 'Pass123'])
        self.run_cli(['decrypt', encrypted_file, '-o', decrypted_file, '-p', 'Pass123'])
        
        passed = self.assert_file_content(decrypted_file, content)
        self.log_test("Emoji 内容处理", passed)
    
    # ==================== 运行所有测试 ====================
    
    def run_all_tests(self):
        """运行所有测试"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.CYAN}  CLI 加密工具 E2E 测试套件{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.ENDC}\n")
        
        self.setup()
        
        try:
            # 基础功能测试
            print(f"\n{Colors.BOLD}📋 基础功能测试{Colors.ENDC}")
            print("-" * 60)
            self.test_basic_encrypt_decrypt()
            self.test_wrong_password()
            self.test_help_command()
            self.test_nonexistent_file()
            
            # 内容类型测试
            print(f"\n{Colors.BOLD}📝 内容类型测试{Colors.ENDC}")
            print("-" * 60)
            self.test_chinese_content()
            self.test_empty_file()
            self.test_emoji_content()
            self.test_large_file()
            
            # 算法测试
            print(f"\n{Colors.BOLD}🔐 加密算法测试{Colors.ENDC}")
            print("-" * 60)
            self.test_different_algorithms()
            self.test_stream_encryption()
            
            # 高级功能测试
            print(f"\n{Colors.BOLD}⚙️  高级功能测试{Colors.ENDC}")
            print("-" * 60)
            self.test_force_overwrite()
            self.test_delete_original()
            self.test_dry_run()
            self.test_batch_encrypt()
            self.test_verbose_mode()
            self.test_concurrent_operations()
            
            # 边界情况测试
            print(f"\n{Colors.BOLD}🔍 边界情况测试{Colors.ENDC}")
            print("-" * 60)
            self.test_special_characters_in_filename()
            self.test_password_strength_check()
            self.test_file_integrity()
            
        finally:
            self.teardown()
        
        # 打印总结
        self.print_summary()
    
    def print_summary(self):
        """打印测试总结"""
        total = self.passed + self.failed + self.skipped
        
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.CYAN}  测试总结{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.ENDC}\n")
        
        print(f"总计: {total} 个测试")
        print(f"{Colors.GREEN}✓ 通过: {self.passed}{Colors.ENDC}")
        print(f"{Colors.RED}✗ 失败: {self.failed}{Colors.ENDC}")
        print(f"{Colors.YELLOW}⊘ 跳过: {self.skipped}{Colors.ENDC}")
        
        if self.failed > 0:
            print(f"\n{Colors.RED}{Colors.BOLD}失败的测试：{Colors.ENDC}")
            for result in self.test_results:
                if result['passed'] is False:
                    print(f"  {Colors.RED}✗{Colors.ENDC} {result['name']}")
                    if result['message']:
                        print(f"    {Colors.YELLOW}→ {result['message']}{Colors.ENDC}")
        
        # 计算通过率
        if total > 0:
            pass_rate = (self.passed / total) * 100
            print(f"\n通过率: {pass_rate:.1f}%")
            
            if pass_rate == 100:
                print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 所有测试通过！{Colors.ENDC}")
            elif pass_rate >= 80:
                print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  大部分测试通过，但仍有改进空间{Colors.ENDC}")
            else:
                print(f"\n{Colors.RED}{Colors.BOLD}❌ 测试失败率较高，需要修复{Colors.ENDC}")
        
        print()
        
        # 返回退出码
        return 0 if self.failed == 0 else 1


def main():
    """主函数"""
    runner = E2ETestRunner()
    exit_code = runner.run_all_tests()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

