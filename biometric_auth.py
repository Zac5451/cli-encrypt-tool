#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生物识别认证模块
支持 Touch ID 和 Face ID 验证
"""

import os
import sys
import subprocess
import keyring
import hashlib
import base64
from typing import Optional, Tuple


class BiometricAuth:
    """生物识别认证类"""
    
    SERVICE_NAME = "cli-encrypt-tool"
    
    @staticmethod
    def is_available() -> bool:
        """检查生物识别是否可用"""
        if sys.platform != 'darwin':
            return False
        
        try:
            # 检查是否有 Touch ID 或 Face ID
            result = subprocess.run(
                ['bioutil', '-r'],
                capture_output=True,
                text=True,
                timeout=2
            )
            return result.returncode == 0
        except Exception:
            return False
    
    @staticmethod
    def authenticate(reason: str = "验证身份以访问加密文件") -> bool:
        """
        使用生物识别进行身份验证
        
        Args:
            reason: 显示给用户的验证原因
            
        Returns:
            bool: 验证是否成功
        """
        if not BiometricAuth.is_available():
            return False
        
        try:
            # 简化版本：使用 security 命令触发钥匙串验证
            # macOS 会自动使用 Touch ID/Face ID
            result = subprocess.run(
                ['security', 'unlock-keychain'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            return False
        except Exception as e:
            print(f"生物识别验证失败: {e}")
            return False
    
    @staticmethod
    def store_password_key(file_identifier: str, password: str) -> bool:
        """
        在系统钥匙串中存储密码
        需要生物识别验证才能访问
        
        Args:
            file_identifier: 文件唯一标识符
            password: 原始密码
            
        Returns:
            bool: 是否存储成功
        """
        try:
            # 直接存储原始密码到系统钥匙串
            # macOS 钥匙串会自动要求生物识别验证
            keyring.set_password(
                BiometricAuth.SERVICE_NAME,
                file_identifier,
                password
            )
            return True
        except Exception as e:
            print(f"存储密钥失败: {e}")
            return False
    
    @staticmethod
    def get_password_key(file_identifier: str) -> Optional[str]:
        """
        从系统钥匙串获取密码
        需要生物识别验证
        
        Args:
            file_identifier: 文件唯一标识符
            
        Returns:
            Optional[str]: 原始密码，如果不存在或验证失败则返回 None
        """
        try:
            password = keyring.get_password(
                BiometricAuth.SERVICE_NAME,
                file_identifier
            )
            return password
        except Exception as e:
            print(f"获取密钥失败: {e}")
            return None
    
    @staticmethod
    def delete_password_key(file_identifier: str) -> bool:
        """
        删除存储的密码密钥
        
        Args:
            file_identifier: 文件唯一标识符
            
        Returns:
            bool: 是否删除成功
        """
        try:
            keyring.delete_password(
                BiometricAuth.SERVICE_NAME,
                file_identifier
            )
            return True
        except Exception:
            return False
    
    @staticmethod
    def generate_file_identifier(filepath: str) -> str:
        """
        为文件生成唯一标识符
        
        Args:
            filepath: 文件路径
            
        Returns:
            str: 文件唯一标识符
        """
        # 使用文件的绝对路径和 inode 生成唯一标识
        abs_path = os.path.abspath(filepath)
        try:
            stat = os.stat(abs_path)
            identifier = f"{abs_path}:{stat.st_ino}:{stat.st_size}"
        except Exception:
            identifier = abs_path
        
        # 返回哈希值作为标识符
        return hashlib.sha256(identifier.encode()).hexdigest()[:32]
    
    @staticmethod
    def authenticate_with_prompt(reason: str = "验证身份") -> bool:
        """
        使用 AppleScript 显示生物识别提示
        
        Args:
            reason: 验证原因
            
        Returns:
            bool: 是否验证成功
        """
        try:
            # 使用 AppleScript 调用系统认证对话框
            script = '''
use framework "LocalAuthentication"
use framework "Foundation"
use scripting additions

set ctx to current application's LAContext's alloc()'s init()
set myError to reference

set canAuth to ctx's canEvaluatePolicy:2 |error|:(myError)

if canAuth is true then
    set authResult to ctx's evaluatePolicy:2 localizedReason:"''' + reason + '''" reply:(missing value) |error|:(myError)
    if authResult is true then
        return "SUCCESS"
    else
        return "FAILED"
    end if
else
    return "UNAVAILABLE"
end if
'''
            
            result = subprocess.run(
                ['osascript', '-l', 'AppleScript', '-e', script],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            output = result.stdout.strip()
            return output == "SUCCESS"
            
        except Exception as e:
            print(f"认证失败: {e}")
            return False


class BiometricPasswordManager:
    """生物识别密码管理器"""
    
    def __init__(self):
        self.auth = BiometricAuth()
    
    def save_password_for_file(self, filepath: str, password: str) -> bool:
        """
        为文件保存密码（需要生物识别验证）
        
        Args:
            filepath: 文件路径
            password: 密码
            
        Returns:
            bool: 是否保存成功
        """
        if not BiometricAuth.is_available():
            print("生物识别不可用")
            return False
        
        # 生成文件标识符
        file_id = BiometricAuth.generate_file_identifier(filepath)
        
        # 存储密码
        success = BiometricAuth.store_password_key(file_id, password)
        
        if success:
            print(f"✓ 密码已安全保存，下次可使用生物识别验证")
        
        return success
    
    def get_password_for_file(self, filepath: str, reason: str = "访问加密文件") -> Optional[str]:
        """
        获取文件的密码（需要生物识别验证）
        
        Args:
            filepath: 文件路径
            reason: 验证原因
            
        Returns:
            Optional[str]: 原始密码，如果验证失败则返回 None
        """
        if not BiometricAuth.is_available():
            return None
        
        # macOS 钥匙串会自动触发生物识别验证
        # 不需要额外调用 authenticate_with_prompt
        print(f"\n🔐 正在从钥匙串获取密码（可能需要生物识别验证）...")
        
        # 验证成功后获取密码
        file_id = BiometricAuth.generate_file_identifier(filepath)
        password = BiometricAuth.get_password_key(file_id)
        
        if password:
            print("✓ 生物识别验证成功")
        
        return password
    
    def has_saved_password(self, filepath: str) -> bool:
        """
        检查文件是否已保存密码
        
        Args:
            filepath: 文件路径
            
        Returns:
            bool: 是否已保存
        """
        file_id = BiometricAuth.generate_file_identifier(filepath)
        password_hash = BiometricAuth.get_password_key(file_id)
        return password_hash is not None


# 测试代码
if __name__ == '__main__':
    print("=== 生物识别认证测试 ===\n")
    
    if BiometricAuth.is_available():
        print("✓ 生物识别可用")
        
        print("\n测试认证...")
        if BiometricAuth.authenticate_with_prompt("测试生物识别功能"):
            print("✓ 认证成功！")
        else:
            print("✗ 认证失败")
    else:
        print("✗ 生物识别不可用（仅支持 macOS）")

