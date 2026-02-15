#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键运行所有测试
自动安装依赖、运行测试、生成报告
"""

import os
import sys
import subprocess
import platform


def print_section(title):
    """打印分隔标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def check_dependencies():
    """检查并安装依赖"""
    print_section("检查依赖")
    
    required = [
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
        "hypothesis>=6.0.0",
        "pytest-timeout>=2.1.0",
    ]
    
    for package in required:
        name = package.split(">")[0].split(">=")[0]
        try:
            __import__(name.replace("-", "_"))
            print(f"✓ {name} 已安装")
        except ImportError:
            print(f"✗ {name} 未安装，正在安装...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)


def run_tests(test_file, description, extra_args=None):
    """运行测试并返回结果"""
    print_section(f"运行 {description}")
    
    if not os.path.exists(test_file):
        print(f"✗ 测试文件不存在: {test_file}")
        return False
    
    cmd = [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"]
    
    if extra_args:
        cmd.extend(extra_args)
    
    result = subprocess.run(cmd)
    return result.returncode == 0


def run_all_tests():
    """运行所有测试"""
    # 检查依赖
    check_dependencies()
    
    results = {}
    
    # 1. 单元测试
    results["单元测试"] = run_tests(
        "test_full.py",
        "完整单元测试",
        ["--timeout=60"]
    )
    
    # 2. 边界测试
    results["边界测试"] = run_tests(
        "test_boundary.py",
        "边界情况测试",
        ["--timeout=120"]
    )
    
    # 3. 属性测试
    results["属性测试"] = run_tests(
        "test_properties.py",
        "属性测试 (Hypothesis)",
        ["--hypothesis-show-statistics", "--timeout=180"]
    )
    
    # 4. 覆盖率报告
    print_section("代码覆盖率")
    subprocess.run([
        sys.executable, "-m", "pytest",
        "test_full.py", "test_boundary.py",
        "--cov=crypto_core",
        "--cov-report=term-missing",
        "--cov-report=html",
        "--cov-fail-under=70"
    ])
    
    # 打印总结
    print_section("测试总结")
    
    all_passed = True
    for name, passed in results.items():
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False
    
    print()
    
    if all_passed:
        print("🎉 所有测试通过！")
        return 0
    else:
        print("❌ 部分测试失败，请检查上述输出")
        return 1


def quick_test():
    """快速测试（不安装依赖）"""
    print_section("快速测试")
    
    # 只运行基础测试
    subprocess.run([
        sys.executable, "-m", "pytest",
        "test_full.py::TestCryptoBasic",
        "-v", "--tb=short"
    ])


def main():
    """主函数"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "quick":
            quick_test()
            return
        elif sys.argv[1] == "help":
            print("""
用法: python run_tests.py [选项]

选项:
  (无参数)     运行所有测试
  quick       快速测试（仅基础功能）
  help        显示此帮助
            """)
            return
    
    sys.exit(run_all_tests())


if __name__ == "__main__":
    main()
