#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动测试向导
引导用户逐步测试每个功能，检测"看起来实现了但实际没实现"的bug
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path


class ManualTestRunner:
    """手动测试运行器"""
    
    def __init__(self):
        self.passed = []
        self.failed = []
        self.test_dir = None
    
    def print_header(self, title):
        print("\n" + "=" * 60)
        print(f"  {title}")
        print("=" * 60)
    
    def print_step(self, num, desc):
        print(f"\n【步骤 {num}】{desc}")
    
    def run_command(self, cmd, check_output=False):
        """运行命令并返回结果"""
        result = subprocess.run(
            cmd, shell=True,
            capture_output=True,
            text=True
        )
        if check_output:
            return result.returncode, result.stdout, result.stderr
        return result.returncode == 0
    
    def test_interactive_mode(self):
        """测试交互模式"""
        self.print_header("测试交互模式")
        
        # 创建测试文件
        test_file = os.path.join(self.test_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("interactive test")
        
        print("\n⚠️  交互模式需要手动测试，请按以下步骤操作：")
        print(f"""
1. 运行命令: python3 cli_encrypt.py interactive

2. 输入以下命令测试:
   enc {test_file}
   (输入密码: TestPass123!)
   (确认密码: TestPass123!)
   
3. 验证加密文件是否生成:
   ls -la {test_file}.encrypted

4. 测试解密:
   dec {test_file}.encrypted
   (输入密码: TestPass123!)

5. 验证解密内容:
   cat {test_file}.encrypted.decrypted

6. 退出:
   exit
""")
        
        input("按回车键继续...")
        
        # 检查文件是否存在
        enc_file = test_file + ".encrypted"
        if os.path.exists(enc_file):
            print("✓ 交互模式加密功能正常")
            self.passed.append("交互模式-加密")
        else:
            print("✗ 交互模式加密功能异常")
            self.failed.append("交互模式-加密")
    
    def test_all_commands(self):
        """测试所有命令"""
        self.print_header("测试所有命令行功能")
        
        test_file = os.path.join(self.test_dir, "test_data.txt")
        with open(test_file, 'w') as f:
            f.write("test content for all commands")
        
        commands = [
            # 1. 基础加密解密
            ("基础加密", f"python3 cli_encrypt.py encrypt {test_file} -o {test_file}.enc -p 'TestPass123!' -f"),
            ("基础解密", f"python3 cli_encrypt.py decrypt {test_file}.enc -o {test_file}.dec -p 'TestPass123!' -f"),
            
            # 2. 不同算法
            ("ChaCha20算法", f"python3 cli_encrypt.py encrypt {test_file} -o {test_file}.chacha -a chacha20 -p 'TestPass123!' -f"),
            
            # 3. 自毁功能
            ("过期时间", f"python3 cli_encrypt.py encrypt {test_file} -o {test_file}.exp -e 7 -p 'TestPass123!' -f"),
            ("最大解密次数", f"python3 cli_encrypt.py encrypt {test_file} -o {test_file}.max -m 2 -p 'TestPass123!' -f"),
            
            # 4. 流式加密
            ("流式加密", f"echo 'stream test' | python3 cli_encrypt.py stream-encrypt -p 'TestPass123!' > {test_file}.stream"),
            
            # 5. 目录加密
            ("目录加密", f"mkdir -p {self.test_dir}/test_folder && echo 'folder test' > {self.test_dir}/test_folder/file.txt && python3 cli_encrypt.py encrypt-dir {self.test_dir}/test_folder -o {self.test_dir}/folder.vcdir -p 'TestPass123!' -f"),
            
            # 6. 批量加密
            ("批量加密", f"touch {self.test_dir}/a.txt {self.test_dir}/b.txt && python3 cli_encrypt.py batch-encrypt '{self.test_dir}/*.txt' -o {self.test_dir}/batch_out -p 'TestPass123!'"),
            
            # 7. 预览
            ("Dry-run预览", f"python3 cli_encrypt.py dry-run {test_file}"),
        ]
        
        for name, cmd in commands:
            self.print_step(commands.index((name, cmd)) + 1, name)
            print(f"执行: {cmd}")
            
            success, stdout, stderr = self.run_command(cmd, check_output=True)
            
            if success:
                print(f"✓ {name} - 命令执行成功")
                self.passed.append(name)
            else:
                print(f"✗ {name} - 命令执行失败")
                print(f"  错误: {stderr[:200]}")
                self.failed.append(name)
    
    def test_error_handling(self):
        """测试错误处理"""
        self.print_header("测试错误处理")
        
        test_file = os.path.join(self.test_dir, "error_test.txt")
        with open(test_file, 'w') as f:
            f.write("error test")
        
        # 1. 错误密码
        print("\n【测试】错误密码应该失败")
        cmd = f"python3 cli_encrypt.py encrypt {test_file} -o {test_file}.enc -p 'CorrectPass' -f"
        self.run_command(cmd)
        
        # 用错误密码解密
        cmd = f"python3 cli_encrypt.py decrypt {test_file}.enc -o {test_file}.wrong -p 'WrongPass' -f"
        success, stdout, stderr = self.run_command(cmd, check_output=True)
        
        if not success and ("失败" in stdout or "失败" in stderr or "错误" in stdout or "错误" in stderr):
            print("✓ 错误密码正确被拒绝")
            self.passed.append("错误密码处理")
        else:
            print("✗ 错误密码处理异常")
            self.failed.append("错误密码处理")
        
        # 2. 不存在的文件
        print("\n【测试】不存在的文件")
        cmd = "python3 cli_encrypt.py encrypt /nonexistent/file.txt -o out.enc -p 'Pass'"
        success, stdout, stderr = self.run_command(cmd, check_output=True)
        
        if not success:
            print("✓ 不存在的文件正确报错")
            self.passed.append("不存在文件处理")
        else:
            print("✗ 不存在的文件处理异常")
            self.failed.append("不存在文件处理")
    
    def check_file_outputs(self):
        """检查文件输出"""
        self.print_header("检查文件输出")
        
        expected_files = [
            "test_data.txt.enc",
            "test_data.txt.dec",
            "test_data.txt.chacha",
            "test_data.txt.exp",
            "test_data.txt.max",
            "folder.vcdir",
        ]
        
        print("\n检查以下文件是否生成:")
        for f in expected_files:
            path = os.path.join(self.test_dir, f)
            if os.path.exists(path):
                size = os.path.getsize(path)
                print(f"  ✓ {f} ({size} bytes)")
                self.passed.append(f"文件生成-{f}")
            else:
                print(f"  ✗ {f} (未找到)")
                self.failed.append(f"文件生成-{f}")
        
        # 检查解密内容
        dec_file = os.path.join(self.test_dir, "test_data.txt.dec")
        if os.path.exists(dec_file):
            with open(dec_file) as f:
                content = f.read()
            if content == "test content for all commands":
                print("✓ 解密内容正确")
                self.passed.append("解密内容")
            else:
                print(f"✗ 解密内容错误: {content}")
                self.failed.append("解密内容")
    
    def print_summary(self):
        """打印测试总结"""
        self.print_header("测试总结")
        
        print(f"\n✓ 通过: {len(self.passed)} 项")
        print(f"✗ 失败: {len(self.failed)} 项")
        
        if self.failed:
            print("\n失败的测试:")
            for f in self.failed:
                print(f"  - {f}")
        
        print("\n" + "=" * 60)
        
        if not self.failed:
            print("🎉 所有手动测试通过！")
            return 0
        else:
            print("⚠️  部分测试失败，请检查！")
            return 1
    
    def run(self):
        """运行所有测试"""
        # 获取项目根目录
        project_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(project_dir)
        
        # 创建临时测试目录
        self.test_dir = tempfile.mkdtemp(prefix="crypto_test_")
        print(f"测试目录: {self.test_dir}")
        
        try:
            # 运行各项测试
            self.test_all_commands()
            self.test_error_handling()
            self.check_file_outputs()
            self.test_interactive_mode()
            
            return self.print_summary()
            
        finally:
            # 清理
            print(f"\n测试目录: {self.test_dir}")
            print("测试完成后可手动删除该目录")


def main():
    print("""
╔═══════════════════════════════════════════════════════════════════════╗
║                    CLI 加密工具手动测试向导                          ║
║                                                                       ║
║  本测试将逐步引导您测试每个功能，检测"看起来实现了但实际没实现"的bug  ║
╚═══════════════════════════════════════════════════════════════════════╝
""")
    
    runner = ManualTestRunner()
    sys.exit(runner.run())


if __name__ == "__main__":
    main()
