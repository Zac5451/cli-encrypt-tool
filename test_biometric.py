#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生物识别功能测试脚本
"""

import os
import sys
import tempfile
from biometric_auth import BiometricAuth, BiometricPasswordManager

def test_biometric_availability():
    """测试生物识别是否可用"""
    print("=" * 60)
    print("测试 1: 检查生物识别可用性")
    print("=" * 60)
    
    if BiometricAuth.is_available():
        print("✓ 生物识别可用（Touch ID 或 Face ID）")
        return True
    else:
        print("✗ 生物识别不可用")
        print("  原因可能是：")
        print("  - 不是 macOS 系统")
        print("  - 设备不支持 Touch ID/Face ID")
        print("  - 未设置生物识别")
        return False

def test_password_storage():
    """测试密码存储和检索"""
    print("\n" + "=" * 60)
    print("测试 2: 密码存储和检索")
    print("=" * 60)
    
    manager = BiometricPasswordManager()
    
    # 创建临时测试文件
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("测试文件内容")
        test_file = f.name
    
    try:
        test_password = "TestPassword123!"
        
        print(f"\n测试文件: {test_file}")
        print(f"测试密码: {test_password}")
        
        # 保存密码
        print("\n正在保存密码到钥匙串...")
        if manager.save_password_for_file(test_file, test_password):
            print("✓ 密码保存成功")
        else:
            print("✗ 密码保存失败")
            return False
        
        # 检查是否已保存
        print("\n检查密码是否已保存...")
        if manager.has_saved_password(test_file):
            print("✓ 检测到已保存的密码")
        else:
            print("✗ 未检测到已保存的密码")
            return False
        
        # 获取密码（需要生物识别）
        print("\n尝试获取密码（需要生物识别验证）...")
        retrieved_password = manager.get_password_for_file(test_file, "测试生物识别功能")
        
        if retrieved_password:
            if retrieved_password == test_password:
                print("✓ 密码检索成功且匹配")
                return True
            else:
                print("✗ 密码检索成功但不匹配")
                print(f"  期望: {test_password}")
                print(f"  实际: {retrieved_password}")
                return False
        else:
            print("✗ 密码检索失败（可能是生物识别验证失败）")
            return False
            
    finally:
        # 清理
        if os.path.exists(test_file):
            os.remove(test_file)
        
        # 删除测试密码
        file_id = BiometricAuth.generate_file_identifier(test_file)
        BiometricAuth.delete_password_key(file_id)

def test_file_identifier():
    """测试文件标识符生成"""
    print("\n" + "=" * 60)
    print("测试 3: 文件标识符生成")
    print("=" * 60)
    
    # 创建测试文件
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("测试内容")
        test_file = f.name
    
    try:
        identifier1 = BiometricAuth.generate_file_identifier(test_file)
        identifier2 = BiometricAuth.generate_file_identifier(test_file)
        
        print(f"\n文件: {test_file}")
        print(f"标识符 1: {identifier1}")
        print(f"标识符 2: {identifier2}")
        
        if identifier1 == identifier2:
            print("✓ 相同文件生成相同标识符")
        else:
            print("✗ 相同文件生成不同标识符")
            return False
        
        # 修改文件内容
        with open(test_file, 'a') as f:
            f.write("\n更多内容")
        
        identifier3 = BiometricAuth.generate_file_identifier(test_file)
        print(f"标识符 3 (修改后): {identifier3}")
        
        if identifier3 != identifier1:
            print("✓ 文件修改后标识符改变")
        else:
            print("⚠ 文件修改后标识符未改变（可能是预期行为）")
        
        return True
        
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)

def main():
    """主测试函数"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "生物识别功能测试" + " " * 15 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    results = []
    
    # 测试 1: 可用性
    results.append(("生物识别可用性", test_biometric_availability()))
    
    if not results[0][1]:
        print("\n⚠ 生物识别不可用，跳过后续测试")
        print("\n如果您在 macOS 上，请确保：")
        print("  1. 设备支持 Touch ID 或 Face ID")
        print("  2. 已在系统偏好设置中设置生物识别")
        print("  3. 已安装 keyring 库: pip install keyring")
        return
    
    # 测试 2: 密码存储
    results.append(("密码存储和检索", test_password_storage()))
    
    # 测试 3: 文件标识符
    results.append(("文件标识符生成", test_file_identifier()))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！生物识别功能正常工作。")
    else:
        print("\n⚠ 部分测试失败，请检查配置。")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

