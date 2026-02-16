#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化测试主控脚本
整合单元测试、集成测试、E2E测试
"""

import os
import sys
import subprocess
import time
import json
from datetime import datetime
from pathlib import Path


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'


class AutoTestRunner:
    """自动化测试运行器"""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {}
        }
        self.start_time = None
    
    def print_header(self, title):
        """打印标题"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.CYAN}  {title}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.ENDC}\n")
    
    def run_command(self, cmd, description, timeout=300):
        """运行命令并记录结果"""
        print(f"{Colors.BLUE}▶ {description}...{Colors.ENDC}")
        
        start = time.time()
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            duration = time.time() - start
            
            success = result.returncode == 0
            
            self.results['tests'][description] = {
                'success': success,
                'duration': duration,
                'returncode': result.returncode,
                'stdout': result.stdout[-500:] if len(result.stdout) > 500 else result.stdout,
                'stderr': result.stderr[-500:] if len(result.stderr) > 500 else result.stderr
            }
            
            if success:
                print(f"{Colors.GREEN}✓ {description} 完成 ({duration:.2f}s){Colors.ENDC}\n")
            else:
                print(f"{Colors.RED}✗ {description} 失败 ({duration:.2f}s){Colors.ENDC}")
                if result.stderr:
                    print(f"{Colors.YELLOW}错误信息: {result.stderr[:200]}{Colors.ENDC}\n")
            
            return success
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start
            print(f"{Colors.RED}✗ {description} 超时 ({duration:.2f}s){Colors.ENDC}\n")
            self.results['tests'][description] = {
                'success': False,
                'duration': duration,
                'error': 'timeout'
            }
            return False
        except Exception as e:
            duration = time.time() - start
            print(f"{Colors.RED}✗ {description} 异常: {e}{Colors.ENDC}\n")
            self.results['tests'][description] = {
                'success': False,
                'duration': duration,
                'error': str(e)
            }
            return False
    
    def check_dependencies(self):
        """检查依赖"""
        self.print_header("检查依赖")
        
        dependencies = [
            ('python3', 'Python 3'),
            ('pytest', 'pytest'),
        ]
        
        all_ok = True
        for cmd, name in dependencies:
            try:
                if cmd == 'pytest':
                    subprocess.run([sys.executable, '-m', 'pytest', '--version'], 
                                 capture_output=True, check=True)
                else:
                    subprocess.run([cmd, '--version'], capture_output=True, check=True)
                print(f"{Colors.GREEN}✓ {name} 已安装{Colors.ENDC}")
            except:
                print(f"{Colors.RED}✗ {name} 未安装{Colors.ENDC}")
                all_ok = False
        
        return all_ok
    
    def install_dependencies(self):
        """安装测试依赖"""
        self.print_header("安装测试依赖")
        
        packages = [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'pytest-timeout>=2.1.0',
            'hypothesis>=6.0.0'
        ]
        
        for package in packages:
            print(f"安装 {package}...")
            try:
                subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', package],
                    capture_output=True,
                    check=True
                )
                print(f"{Colors.GREEN}✓ {package} 安装成功{Colors.ENDC}")
            except:
                print(f"{Colors.YELLOW}⚠ {package} 安装失败（可能已安装）{Colors.ENDC}")
    
    def run_syntax_check(self):
        """语法检查"""
        self.print_header("代码语法检查")
        
        python_files = [
            'cli_encrypt.py',
            'crypto_core.py',
            'biometric_auth.py',
            'steganography.py',
            'file_manager.py'
        ]
        
        all_ok = True
        for file in python_files:
            if not os.path.exists(file):
                print(f"{Colors.YELLOW}⊘ {file} 不存在，跳过{Colors.ENDC}")
                continue
            
            try:
                subprocess.run(
                    [sys.executable, '-m', 'py_compile', file],
                    capture_output=True,
                    check=True
                )
                print(f"{Colors.GREEN}✓ {file} 语法正确{Colors.ENDC}")
            except:
                print(f"{Colors.RED}✗ {file} 语法错误{Colors.ENDC}")
                all_ok = False
        
        return all_ok
    
    def run_unit_tests(self):
        """运行单元测试"""
        self.print_header("单元测试")
        
        if not os.path.exists('test_full.py'):
            print(f"{Colors.YELLOW}⊘ test_full.py 不存在，跳过单元测试{Colors.ENDC}")
            return True
        
        return self.run_command(
            [sys.executable, '-m', 'pytest', 'test_full.py', '-v', '--tb=short', '--timeout=60'],
            '单元测试',
            timeout=120
        )
    
    def run_boundary_tests(self):
        """运行边界测试"""
        self.print_header("边界测试")
        
        if not os.path.exists('test_boundary.py'):
            print(f"{Colors.YELLOW}⊘ test_boundary.py 不存在，跳过边界测试{Colors.ENDC}")
            return True
        
        return self.run_command(
            [sys.executable, '-m', 'pytest', 'test_boundary.py', '-v', '--tb=short', '--timeout=120'],
            '边界测试',
            timeout=180
        )
    
    def run_e2e_tests(self):
        """运行 E2E 测试"""
        self.print_header("E2E 端到端测试")
        
        if not os.path.exists('test_e2e.py'):
            print(f"{Colors.YELLOW}⊘ test_e2e.py 不存在，跳过 E2E 测试{Colors.ENDC}")
            return True
        
        return self.run_command(
            [sys.executable, 'test_e2e.py'],
            'E2E 测试',
            timeout=300
        )
    
    def run_coverage_report(self):
        """生成覆盖率报告"""
        self.print_header("代码覆盖率分析")
        
        test_files = []
        if os.path.exists('test_full.py'):
            test_files.append('test_full.py')
        if os.path.exists('test_boundary.py'):
            test_files.append('test_boundary.py')
        
        if not test_files:
            print(f"{Colors.YELLOW}⊘ 没有测试文件，跳过覆盖率分析{Colors.ENDC}")
            return True
        
        return self.run_command(
            [sys.executable, '-m', 'pytest'] + test_files + [
                '--cov=crypto_core',
                '--cov=cli_encrypt',
                '--cov-report=term-missing',
                '--cov-report=html',
                '--cov-report=json'
            ],
            '覆盖率分析',
            timeout=180
        )
    
    def run_performance_test(self):
        """性能测试"""
        self.print_header("性能测试")
        
        print("创建测试文件...")
        test_file = 'perf_test.bin'
        
        try:
            # 创建 5MB 测试文件
            with open(test_file, 'wb') as f:
                f.write(os.urandom(5 * 1024 * 1024))
            
            # 测试加密性能
            start = time.time()
            result = subprocess.run(
                [sys.executable, 'cli_encrypt.py', 'encrypt', test_file, 
                 '-o', test_file + '.enc', '-p', 'TestPass123!'],
                capture_output=True,
                timeout=60
            )
            encrypt_time = time.time() - start
            
            if result.returncode == 0:
                print(f"{Colors.GREEN}✓ 加密 5MB 文件耗时: {encrypt_time:.2f}s{Colors.ENDC}")
                
                # 测试解密性能
                start = time.time()
                result = subprocess.run(
                    [sys.executable, 'cli_encrypt.py', 'decrypt', test_file + '.enc',
                     '-o', test_file + '.dec', '-p', 'TestPass123!'],
                    capture_output=True,
                    timeout=60
                )
                decrypt_time = time.time() - start
                
                if result.returncode == 0:
                    print(f"{Colors.GREEN}✓ 解密 5MB 文件耗时: {decrypt_time:.2f}s{Colors.ENDC}")
                    
                    self.results['performance'] = {
                        'file_size': '5MB',
                        'encrypt_time': encrypt_time,
                        'decrypt_time': decrypt_time,
                        'encrypt_speed': f"{5/encrypt_time:.2f} MB/s",
                        'decrypt_speed': f"{5/decrypt_time:.2f} MB/s"
                    }
                    
                    return True
            
            return False
            
        except Exception as e:
            print(f"{Colors.RED}✗ 性能测试失败: {e}{Colors.ENDC}")
            return False
        finally:
            # 清理测试文件
            for f in [test_file, test_file + '.enc', test_file + '.dec']:
                if os.path.exists(f):
                    os.remove(f)
    
    def save_report(self):
        """保存测试报告"""
        self.print_header("保存测试报告")
        
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            
            print(f"{Colors.GREEN}✓ 测试报告已保存: {report_file}{Colors.ENDC}")
            return True
        except Exception as e:
            print(f"{Colors.RED}✗ 保存报告失败: {e}{Colors.ENDC}")
            return False
    
    def print_summary(self):
        """打印测试总结"""
        self.print_header("测试总结")
        
        total_tests = len(self.results['tests'])
        passed_tests = sum(1 for t in self.results['tests'].values() if t.get('success'))
        failed_tests = total_tests - passed_tests
        
        total_duration = sum(t.get('duration', 0) for t in self.results['tests'].values())
        
        print(f"总测试数: {total_tests}")
        print(f"{Colors.GREEN}✓ 通过: {passed_tests}{Colors.ENDC}")
        print(f"{Colors.RED}✗ 失败: {failed_tests}{Colors.ENDC}")
        print(f"总耗时: {total_duration:.2f}s")
        
        if 'performance' in self.results:
            print(f"\n{Colors.CYAN}性能指标:{Colors.ENDC}")
            perf = self.results['performance']
            print(f"  加密速度: {perf['encrypt_speed']}")
            print(f"  解密速度: {perf['decrypt_speed']}")
        
        if failed_tests == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 所有测试通过！{Colors.ENDC}")
            return 0
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}❌ 有 {failed_tests} 个测试失败{Colors.ENDC}")
            print(f"\n{Colors.YELLOW}失败的测试:{Colors.ENDC}")
            for name, result in self.results['tests'].items():
                if not result.get('success'):
                    print(f"  {Colors.RED}✗{Colors.ENDC} {name}")
            return 1
    
    def run_all(self, quick=False):
        """运行所有测试"""
        self.start_time = time.time()
        
        print(f"\n{Colors.BOLD}{Colors.CYAN}")
        print("╔═══════════════════════════════════════════════════════════════════╗")
        print("║           CLI 加密工具 - 自动化测试套件                          ║")
        print("╚═══════════════════════════════════════════════════════════════════╝")
        print(f"{Colors.ENDC}")
        
        # 1. 检查依赖
        if not self.check_dependencies():
            print(f"\n{Colors.YELLOW}正在安装缺失的依赖...{Colors.ENDC}")
            self.install_dependencies()
        
        # 2. 语法检查
        if not self.run_syntax_check():
            print(f"\n{Colors.RED}语法检查失败，停止测试{Colors.ENDC}")
            return 1
        
        # 3. 单元测试
        self.run_unit_tests()
        
        if not quick:
            # 4. 边界测试
            self.run_boundary_tests()
            
            # 5. E2E 测试
            self.run_e2e_tests()
            
            # 6. 覆盖率报告
            self.run_coverage_report()
            
            # 7. 性能测试
            self.run_performance_test()
        
        # 8. 保存报告
        self.save_report()
        
        # 9. 打印总结
        exit_code = self.print_summary()
        
        total_time = time.time() - self.start_time
        print(f"\n总运行时间: {total_time:.2f}s\n")
        
        return exit_code


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='CLI 加密工具自动化测试')
    parser.add_argument('--quick', action='store_true', help='快速测试（仅单元测试）')
    parser.add_argument('--e2e-only', action='store_true', help='仅运行 E2E 测试')
    parser.add_argument('--coverage', action='store_true', help='仅生成覆盖率报告')
    
    args = parser.parse_args()
    
    runner = AutoTestRunner()
    
    if args.e2e_only:
        runner.run_e2e_tests()
        sys.exit(0)
    elif args.coverage:
        runner.run_coverage_report()
        sys.exit(0)
    else:
        exit_code = runner.run_all(quick=args.quick)
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
