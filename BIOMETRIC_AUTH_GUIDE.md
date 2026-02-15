# 生物识别认证使用指南

## 功能概述

CLI 加密工具现在支持使用 **Touch ID** 或 **Face ID** 进行生物识别验证，无需每次手动输入密码。

## 系统要求

- **操作系统**: macOS（支持 Touch ID 或 Face ID 的设备）
- **Python 依赖**: `keyring` 库

## 安装依赖

```bash
pip install keyring
```

或者使用项目的 requirements.txt：

```bash
pip install -r requirements.txt
```

## 工作原理

1. **首次加密文件时**：输入密码后，系统会询问是否保存密码到钥匙串
2. **密码存储**：密码被安全地存储在 macOS 系统钥匙串中
3. **后续解密**：系统会检测到已保存的密码，提示使用生物识别验证
4. **生物识别验证**：使用 Touch ID 或 Face ID 验证身份后，自动获取密码进行解密

## 使用示例

### 1. 加密文件并保存密码

```bash
./cli_encrypt.py encrypt document.pdf
```

**操作流程**：
1. 输入加密密码
2. 确认密码
3. 系统询问："是否保存密码以便下次使用生物识别验证？(y/N)"
4. 输入 `y` 确认保存

### 2. 使用生物识别解密文件

```bash
./cli_encrypt.py decrypt document.pdf.encrypted
```

**操作流程**：
1. 系统检测到已保存的密码凭证
2. 提示："是否使用生物识别验证？(Y/n)"
3. 按回车或输入 `y`
4. 系统弹出 Touch ID/Face ID 验证提示
5. 验证成功后自动解密文件

### 3. 手动输入密码（不使用生物识别）

如果不想使用生物识别，在提示时输入 `n`：

```bash
./cli_encrypt.py decrypt document.pdf.encrypted
# 提示：是否使用生物识别验证？(Y/n)
# 输入: n
# 然后手动输入密码
```

## 安全性说明

### 密码存储安全

- 密码存储在 **macOS 系统钥匙串**中，这是 Apple 提供的安全存储机制
- 钥匙串数据经过硬件级加密保护
- 只有通过生物识别验证才能访问存储的密码

### 生物识别安全

- 使用 Apple 的 **LocalAuthentication** 框架
- 生物识别数据（指纹/面部）从不离开设备的安全区域
- 支持 Touch ID 和 Face ID 的所有安全特性

### 文件标识符

- 每个文件使用唯一标识符（基于路径、inode、大小）
- 即使文件名相同，不同文件也有不同的密码凭证
- 文件移动或重命名后需要重新保存密码

## 管理已保存的密码

### 查看已保存的密码

可以通过 macOS 的"钥匙串访问"应用查看：

1. 打开"钥匙串访问"（Keychain Access）
2. 搜索 `cli-encrypt-tool`
3. 可以看到所有已保存的文件密码凭证

### 删除已保存的密码

在"钥匙串访问"中：
1. 找到对应的密码项
2. 右键点击 → 删除

或者使用命令行：

```bash
security delete-generic-password -s "cli-encrypt-tool" -a "<文件标识符>"
```

## 命令行参数

生物识别功能与现有的所有命令兼容：

```bash
# 加密文件
./cli_encrypt.py encrypt file.txt -a chacha20

# 解密文件（自动检测生物识别）
./cli_encrypt.py decrypt file.txt.encrypted

# 批量加密
./cli_encrypt.py batch-encrypt "*.pdf" -o encrypted/

# 批量解密
./cli_encrypt.py batch-decrypt "encrypted/*.encrypted" -o decrypted/
```

## 故障排除

### 问题：提示"生物识别不可用"

**原因**：
- 不是 macOS 系统
- 设备不支持 Touch ID/Face ID
- 未安装 `keyring` 库

**解决方案**：
```bash
pip install keyring
```

### 问题：生物识别验证失败

**可能原因**：
- Touch ID/Face ID 未设置
- 系统设置中禁用了生物识别
- 钥匙串被锁定

**解决方案**：
1. 检查"系统偏好设置" → "Touch ID" 或 "Face ID"
2. 确保至少添加了一个指纹或面部
3. 尝试解锁钥匙串：`security unlock-keychain`

### 问题：找不到已保存的密码

**可能原因**：
- 文件被移动或重命名
- 文件大小发生变化
- 密码凭证被删除

**解决方案**：
- 手动输入密码解密
- 重新加密文件并保存新的密码凭证

## 最佳实践

1. **首次使用**：加密重要文件时选择保存密码
2. **定期备份**：虽然密码存储在钥匙串中，但建议记住原始密码
3. **多设备使用**：每台设备需要单独保存密码凭证
4. **敏感文件**：对于极度敏感的文件，可以选择不保存密码，每次手动输入

## 技术细节

### 文件标识符生成

```python
identifier = SHA256(filepath + inode + filesize)[:32]
```

### 钥匙串服务名称

```
服务名称: cli-encrypt-tool
账户名称: <文件标识符>
```

### 生物识别验证流程

1. 应用请求访问钥匙串项
2. macOS 自动触发生物识别提示
3. 用户完成 Touch ID/Face ID 验证
4. 系统返回存储的密码
5. 应用使用密码解密文件

## 示例脚本

### 批量加密并保存密码

```bash
#!/bin/bash
# 加密目录中的所有 PDF 文件

for file in *.pdf; do
    echo "加密: $file"
    ./cli_encrypt.py encrypt "$file" --delete-original
    # 在提示时输入密码并选择保存
done
```

### 自动化解密（使用生物识别）

```bash
#!/bin/bash
# 解密所有加密文件（自动使用生物识别）

for file in *.encrypted; do
    echo "解密: $file"
    # 系统会自动使用生物识别验证
    ./cli_encrypt.py decrypt "$file" --delete-encrypted
done
```

## 常见问题

**Q: 生物识别是否比密码更安全？**  
A: 生物识别提供了便利性，但密码仍然是加密的基础。生物识别只是用于访问存储的密码，文件本身仍然使用强密码加密。

**Q: 如果我的 Touch ID 被禁用了怎么办？**  
A: 可以随时选择手动输入密码，不影响文件的解密。

**Q: 密码存储在哪里？**  
A: 存储在 macOS 系统钥匙串中，与 Safari 密码、Wi-Fi 密码等使用相同的安全机制。

**Q: 可以在多台 Mac 上使用吗？**  
A: 可以，但每台 Mac 需要单独保存密码凭证。钥匙串不会自动同步加密工具的密码。

**Q: 支持 Windows 或 Linux 吗？**  
A: 目前仅支持 macOS。Windows 和 Linux 可以继续使用传统的密码输入方式。

## 更新日志

### v2.1 (2026-02-14)
- ✨ 新增 Touch ID/Face ID 生物识别支持
- 🔐 集成 macOS 系统钥匙串
- 🚀 自动检测已保存的密码凭证
- 📝 添加生物识别使用指南

