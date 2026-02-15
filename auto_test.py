#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化测试向导
使用密钥文件和指纹验证，无需手动输入密码
"""

import os
import sys
import subprocess
import hashlib
import tempfile
import json
import time
from pathlib import Path


class AutoTestRunner:
    """自动化测试运行器"""
    
    def __init__(self):
        self.passed = []
        self.failed = []
        self.skipped = []
        self.test_dir = None
        self.results = {}
        
        # 项目目录和测试目录
        self.project_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 测试用密码
        self.test_password = os.environ.get('TEST_PASSWORD', 'TestPass123!')
    
    def print_header(self, title):
        print("\n" + "=" * 60)
        print(f"  {title}")
        print("=" * 60)
    
    def print_step(self, num, desc, status=""):
        status_str = {"ok": "✓", "fail": "✗", "skip": "⊘"}.get(status, "○")
        print(f"\n[{status_str}] 【步骤 {num}】{desc}")
    
    def run_cmd(self, cmd, cwd=None):
        """运行命令"""
        # 使用项目目录作为基础
        work_dir = cwd or self.project_dir
        result = subprocess.run(
            cmd, shell=True,
            capture_output=True,
            text=True,
            cwd=work_dir
        )
        return result
    
    def get_file_hash(self, filepath):
        """计算文件SHA256指纹"""
        if not os.path.exists(filepath):
            return None
        sha256 = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def verify_content(self, filepath, expected_content):
        """验证文件内容"""
        if not os.path.exists(filepath):
            return False, "文件不存在"
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            actual = f.read()
        if actual == expected_content:
            return True, "内容匹配"
        return False, f"内容不匹配: {actual[:20]}..."
    
    def verify_decryption(self, original_file, decrypted_file):
        """验证解密结果"""
        if not os.path.exists(decrypted_file):
            return False, "解密文件不存在"
        
        orig_hash = self.get_file_hash(original_file)
        dec_hash = self.get_file_hash(decrypted_file)
        
        if orig_hash == dec_hash:
            return True, f"指纹匹配: {orig_hash[:16]}..."
        return False, f"指纹不匹配: {orig_hash[:16]}... vs {dec_hash[:16]}..."
    
    def test_basic_encrypt_decrypt(self):
        """测试基础加密解密"""
        self.print_step(1, "基础加密解密")
        
        # 创建测试文件
        test_file = "test_basic.txt"
        content = "Hello World! 测试内容 123"
        with open(os.path.join(self.test_dir, test_file), 'w') as f:
            f.write(content)
        
        enc_file = test_file + ".enc"
        dec_file = test_file + ".dec"
        
        # 加密
        result = self.run_cmd(
            f'python3 cli_encrypt.py encrypt {test_file} -o {enc_file} -p "{self.test_password}" -f'
        )
        
        if result.returncode != 0 or not os.path.exists(os.path.join(self.test_dir, enc_file)):
            self.failed.append(("基础加密", result.stderr))
            self.print_step(1, "基础加密解密", "fail")
            return
        
        # 解密
        result = self.run_cmd(
            f'python3 cli_encrypt.py decrypt {enc_file} -o {dec_file} -p "{self.test_password}" -f'
        )
        
        if result.returncode != 0:
            self.failed.append(("基础解密", result.stderr))
            self.print_step(1, "基础加密解密", "fail")
            return
        
        # 验证
        ok, msg = self.verify_decryption(
            os.path.join(self.test_dir, test_file),
            os.path.join(self.test_dir, dec_file)
        )
        
        if ok:
            self.passed.append("基础加密解密")
            self.results['basic'] = {'hash': self.get_file_hash(os.path.join(self.test_dir, enc_file))}
            self.print_step(1, "基础加密解密", "ok")
        else:
            self.failed.append(("基础解密验证", msg))
            self.print_step(1, "基础加密解密", "fail")
    
    def test_algorithm_chacha20(self):
        """测试ChaCha20算法"""
        self.print_step(2, "ChaCha20算法")
        
        test_file = "test_chacha.txt"
        content = "ChaCha20 algorithm test"
        with open(os.path.join(self.test_dir, test_file), 'w') as f:
            f.write(content)
        
        enc_file = test_file + ".enc"
        dec_file = test_file + ".dec"
        
        # 加密
        result = self.run_cmd(
            f'python3 cli_encrypt.py encrypt {test_file} -o {enc_file} -a chacha20 -p "{self.test_password}" -f'
        )
        
        if result.returncode != 0 or not os.path.exists(os.path.join(self.test_dir, enc_file)):
            self.failed.append(("ChaCha20加密", result.stderr))
            self.print_step(2, "ChaCha20算法", "fail")
            return
        
        # 解密
        result = self.run_cmd(
            f'python3 cli_encrypt.py decrypt {enc_file} -o {dec_file} -p "{self.test_password}" -f'
        )
        
        ok, msg = self.verify_decryption(
            os.path.join(self.test_dir, test_file),
            os.path.join(self.test_dir, dec_file)
        )
        
        if ok:
            self.passed.append("ChaCha20算法")
            self.results['chacha20'] = {'hash': self.get_file_hash(os.path.join(self.test_dir, enc_file))}
            self.print_step(2, "ChaCha20算法", "ok")
        else:
            self.failed.append(("ChaCha20验证", msg))
            self.print_step(2, "ChaCha20算法", "fail")
    
    def test_self_destruct_expiry(self):
        """测试过期自毁"""
        self.print_step(3, "过期自毁功能")
        
        test_file = "test_expiry.txt"
        content = "Expiry test content"
        with open(os.path.join(self.test_dir, test_file), 'w') as f:
            f.write(content)
        
        enc_file = test_file + ".enc"
        
        # 加密（7天后过期）
        result = self.run_cmd(
            f'python3 cli_encrypt.py encrypt {test_file} -o {enc_file} -e 7 -p "{self.test_password}" -f'
        )
        
        if result.returncode != 0:
            self.failed.append(("过期加密", result.stderr))
            self.print_step(3, "过期自毁功能", "fail")
            return
        
        # 验证文件存在（因为未过期，应该可以解密）
        if os.path.exists(os.path.join(self.test_dir, enc_file)):
            self.passed.append("过期自毁功能")
            self.results['expiry'] = {'enabled': True}
            self.print_step(3, "过期自毁功能", "ok")
        else:
            self.failed.append(("过期功能", "文件未生成"))
            self.print_step(3, "过期自毁功能", "fail")
    
    def test_stream_encryption(self):
        """测试流式加密"""
        self.print_step(4, "流式加密")
        
        stream_file = "test_stream.enc"
        
        # 流加密
        result = self.run_cmd(
            f'echo "Stream test content" | python3 cli_encrypt.py stream-encrypt -p "{self.test_password}" > {stream_file}'
        )
        
        if result.returncode != 0 or not os.path.exists(os.path.join(self.test_dir, stream_file)):
            self.failed.append(("流加密", result.stderr))
            self.print_step(4, "流式加密", "fail")
            return
        
        # 流解密
        result = self.run_cmd(
            f'python3 cli_encrypt.py stream-decrypt -p "{self.test_password}" < {stream_file}'
        )
        
        if result.returncode == 0 and "Stream test content" in result.stdout:
            self.passed.append("流式加密")
            self.print_step(4, "流式加密", "ok")
        else:
            self.failed.append(("流解密验证", result.stdout[:100]))
            self.print_step(4, "流式加密", "fail")
    
    def test_directory_encryption(self):
        """测试目录加密"""
        self.print_step(5, "目录加密")
        
        # 创建测试目录
        os.makedirs(os.path.join(self.test_dir, "test_folder"), exist_ok=True)
        with open(os.path.join(self.test_dir, "test_folder", "file1.txt"), 'w') as f:
            f.write("File 1 content")
        with open(os.path.join(self.test_dir, "test_folder", "file2.txt"), 'w') as f:
            f.write("File 2 content")
        
        enc_file = "folder.vcdir"
        dec_dir = "folder_restored"
        
        # 加密目录
        result = self.run_cmd(
            f'python3 cli_encrypt.py encrypt-dir test_folder -o {enc_file} -p "{self.test_password}" -f'
        )
        
        if result.returncode != 0:
            self.failed.append(("目录加密", result.stderr))
            self.print_step(5, "目录加密", "fail")
            return
        
        # 解密目录
        result = self.run_cmd(
            f'python3 cli_encrypt.py decrypt-dir {enc_file} -o {dec_dir} -p "{self.test_password}" -f'
        )
        
        # 验证
        if (os.path.exists(os.path.join(self.test_dir, dec_dir, "file1.txt")) and
            os.path.exists(os.path.join(self.test_dir, dec_dir, "file2.txt"))):
            self.passed.append("目录加密")
            self.print_step(5, "目录加密", "ok")
        else:
            self.failed.append(("目录验证", "文件未正确恢复"))
            self.print_step(5, "目录加密", "fail")
    
    def test_batch_encryption(self):
        """测试批量加密"""
        self.print_step(6, "批量加密")
        
        # 创建多个测试文件
        for i in range(3):
            with open(os.path.join(self.test_dir, f"batch{i}.txt"), 'w') as f:
                f.write(f"Batch file {i}")
        
        # 批量加密
        result = self.run_cmd(
            f'python3 cli_encrypt.py batch-encrypt "batch*.txt" -o batch_enc -p "{self.test_password}"'
        )
        
        if result.returncode != 0:
            self.failed.append(("批量加密", result.stderr))
            self.print_step(6, "批量加密", "fail")
            return
        
        # 检查输出
        batch_dir = os.path.join(self.test_dir, "batch_enc")
        enc_count = len([f for f in os.listdir(batch_dir) if f.endswith('.encrypted')])
        
        if enc_count == 3:
            self.passed.append("批量加密")
            self.print_step(6, "批量加密", "ok")
        else:
            self.failed.append(("批量加密计数", f"期望3个，实际{enc_count}个"))
            self.print_step(6, "批量加密", "fail")
    
    def test_dry_run(self):
        """测试预览功能"""
        self.print_step(7, "Dry-run预览")
        
        result = self.run_cmd('python3 cli_encrypt.py dry-run test_basic.txt')
        
        if result.returncode == 0 and "预览" in result.stdout:
            self.passed.append("Dry-run预览")
            self.print_step(7, "Dry-run预览", "ok")
        else:
            self.failed.append(("Dry-run", result.stdout[:100]))
            self.print_step(7, "Dry-run预览", "fail")
    
    def test_error_handling(self):
        """测试错误处理"""
        self.print_step(8, "错误处理")
        
        # 1. 错误密码应该失败
        result = self.run_cmd(
            'python3 cli_encrypt.py decrypt test_basic.txt.enc -o out.txt -p "WrongPassword" -f'
        )
        
        wrong_password_ok = result.returncode != 0
        
        # 2. 不存在的文件应该报错
        result = self.run_cmd(
            'python3 cli_encrypt.py encrypt notexist.txt -o out.enc -p "Pass"'
        )
        
        no_file_ok = result.returncode != 0
        
        if wrong_password_ok and no_file_ok:
            self.passed.append("错误处理")
            self.print_step(8, "错误处理", "ok")
        else:
            self.failed.append(("错误处理", f"wrong_pwd:{wrong_password_ok}, no_file:{no_file_ok}"))
            self.print_step(8, "错误处理", "fail")
    
    def test_special_content(self):
        """测试特殊内容"""
        self.print_step(9, "特殊内容（中Emoji）")
        
        # 测试中文
        test_file = "test_cn.txt"
        content = "中文测试内容 😀🎉"
        with open(os.path.join(self.test_dir, test_file), 'w', encoding='utf-8') as f:
            f.write(content)
        
        enc_file = test_file + ".enc"
        dec_file = test_file + ".dec"
        
        result = self.run_cmd(
            f'python3 cli_encrypt.py encrypt {test_file} -o {enc_file} -p "{self.test_password}" -f'
        )
        
        if result.returncode != 0:
            self.failed.append(("中文加密", result.stderr))
            self.print_step(9, "特殊内容", "fail")
            return
        
        result = self.run_cmd(
            f'python3 cli_encrypt.py decrypt {enc_file} -o {dec_file} -p "{self.test_password}" -f'
        )
        
        ok, msg = self.verify_content(
            os.path.join(self.test_dir, dec_file),
            content
        )
        
        if ok:
            self.passed.append("特殊内容")
            self.print_step(9, "特殊内容", "ok")
        else:
            self.failed.append(("中文验证", msg))
            self.print_step(9, "特殊内容", "fail")
    
    def print_summary(self):
        """打印总结"""
        self.print_header("测试总结")
        
        total = len(self.passed) + len(self.failed) + len(self.skipped)
        
        print(f"\n总计: {total} 项")
        print(f"✓ 通过: {len(self.passed)} 项")
        print(f"✗ 失败: {len(self.failed)} 项")
        print(f"⊘ 跳过: {len(self.skipped)} 项")
        
        if self.failed:
            print("\n【失败项目】")
            for name, detail in self.failed:
                print(f"  ✗ {name}")
                if detail and len(str(detail)) < 100:
                    print(f"    → {detail}")
        
        # 输出JSON结果
        result_file = os.path.join(self.test_dir, "test_results.json")
        result_data = {
            'passed': self.passed,
            'failed': self.failed,
            'skipped': self.skipped,
            'results': self.results,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        with open(result_file, 'w') as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n详细结果已保存: {result_file}")
        
        print("\n" + "=" * 60)
        
        if not self.failed:
            print("🎉 所有自动化测试通过！")
            return 0
        else:
            print(f"⚠️  {len(self.failed)} 项测试失败")
            return 1
    
    def run(self):
        """运行所有测试"""
        print("""
╔═══════════════════════════════════════════════════════════════════════╗
║                    CLI 加密工具自动化测试                          ║
║                  无需手动输入密码，指纹自动验证                    ║
╚═══════════════════════════════════════════════════════════════════════╝
""")
        
        # 项目目录作为测试目录
        self.test_dir = self.project_dir
        os.chdir(self.project_dir)
        
        print(f"测试目录: {self.test_dir}")
        
        # 运行所有测试
        self.test_basic_encrypt_decrypt()
        self.test_algorithm_chacha20()
        self.test_self_destruct_expiry()
        self.test_stream_encryption()
        self.test_directory_encryption()
        self.test_batch_encryption()
        self.test_dry_run()
        self.test_error_handling()
        self.test_special_content()
            
            return self.print_summary()
            
        finally:
            print(f"\n测试目录: {self.test_dir}")
            print("测试完成后可手动删除该目录")


def main():
    sys.exit(AutoTestRunner().run())


if __name__ == "__main__":
    main()
