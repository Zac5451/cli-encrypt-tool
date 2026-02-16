# 生物识别功能使用指南（macOS 专用）

## 功能说明

本加密工具支持在 macOS 上使用 Touch ID 或 Face ID 进行生物识别验证，让你无需每次都输入密码即可解密文件。

## 工作流程

### 1. 首次加密文件

当你加密文件时，工具会询问是否保存密码到系统钥匙串：

```bash
python3 cli_encrypt.py encrypt document.pdf -p "YourPassword123!"
```

加密完成后会提示：

```
💡 是否保存密码到钥匙串？下次解密时可直接使用 Touch ID/Face ID (y/N): 
```

输入 `y` 后，密码会被安全地保存到 macOS 系统钥匙串中。

### 2. 使用生物识别解密

下次解密同一个文件时，工具会自动检测到已保存的密码：

```bash
python3 cli_encrypt.py decrypt document.pdf.encrypted
```

你会看到：

```
🔐 检测到已保存的密码凭证，使用生物识别验证...
🔐 正在从钥匙串获取密码（可能需要生物识别验证）...
```

此时：
- **MacBook Pro/Air with Touch ID**: 将手指放在 Touch ID 传感器上
- **MacBook with Face ID**: 看向摄像头进行面部识别

验证成功后会显示：

```
✓ 生物识别验证成功
```

然后自动开始解密，无需输入密码！

### 3. 生物识别失败时

如果生物识别验证失败或取消，工具会询问：

```
⚠ 生物识别验证失败或已取消
是否手动输入密码？(Y/n): 
```

- 输入 `y` 或直接回车：手动输入密码
- 输入 `n`：取消解密操作

## 安全性说明

1. **密码存储位置**：密码存储在 macOS 系统钥匙串中，受系统级加密保护
2. **访问控制**：只有通过生物识别验证才能获取密码
3. **文件关联**：每个文件的密码独立存储，基于文件路径和属性生成唯一标识
4. **跨设备**：密码不会同步到其他设备，仅在当前 Mac 上有效

## 命令行选项

### 加密时跳过生物识别保存

如果不想保存密码，直接在提示时输入 `n`：

```bash
python3 cli_encrypt.py encrypt file.txt -p "password"
# 提示时输入 n
```

### 解密时强制输入密码

使用 `-p` 参数直接提供密码，跳过生物识别：

```bash
python3 cli_encrypt.py decrypt file.txt.encrypted -p "password"
```

## 检查生物识别是否可用

运行测试脚本：

```bash
python3 biometric_auth.py
```

输出示例：

```
=== 生物识别认证测试 ===

✓ 生物识别可用

测试认证...
✓ 认证成功！
```

## 常见问题

### Q: 为什么没有提示使用生物识别？

A: 可能的原因：
1. 不是 macOS 系统
2. 首次加密时没有选择保存密码
3. keyring 模块未安装（运行 `pip3 install keyring`）
4. 文件路径或属性已改变

### Q: 如何删除已保存的密码？

A: 打开"钥匙串访问"应用，搜索 "cli-encrypt-tool"，删除对应的条目。

### Q: 生物识别验证失败怎么办？

A: 
1. 确保手指干净（Touch ID）或光线充足（Face ID）
2. 重试几次
3. 选择手动输入密码
4. 在系统设置中重新设置生物识别

### Q: 可以在其他电脑上使用生物识别吗？

A: 不可以。密码保存在本地钥匙串中，不会同步。需要在每台电脑上重新保存。

## 示例场景

### 场景 1：日常文档加密

```bash
# 第一次加密
python3 cli_encrypt.py encrypt report.pdf -p "SecurePass123!"
# 提示时输入 y 保存密码

# 以后每次解密只需：
python3 cli_encrypt.py decrypt report.pdf.encrypted
# 按指纹即可，无需输入密码
```

### 场景 2：批量文件加密

```bash
# 加密多个文件，使用相同密码
python3 cli_encrypt.py encrypt file1.txt -p "Pass123!"
python3 cli_encrypt.py encrypt file2.txt -p "Pass123!"
python3 cli_encrypt.py encrypt file3.txt -p "Pass123!"

# 每次都选择 y 保存密码

# 解密时都可以使用生物识别
python3 cli_encrypt.py decrypt file1.txt.encrypted
python3 cli_encrypt.py decrypt file2.txt.encrypted
python3 cli_encrypt.py decrypt file3.txt.encrypted
```

### 场景 3：临时文件（不保存密码）

```bash
# 加密临时文件
python3 cli_encrypt.py encrypt temp.txt -p "TempPass"
# 提示时输入 n，不保存密码

# 解密时需要手动输入密码
python3 cli_encrypt.py decrypt temp.txt.encrypted
# 输入密码
```

## 技术细节

- **密钥派生**：使用 Argon2id 或 PBKDF2-HMAC-SHA512
- **加密算法**：AES-256-GCM（默认）
- **文件标识**：SHA256(文件路径:inode:大小)
- **钥匙串服务**：使用 Python keyring 库
- **生物识别**：通过 macOS 系统钥匙串自动触发

## 注意事项

⚠️ **重要**：
1. 如果文件被移动或重命名，生物识别可能无法识别（因为文件标识改变）
2. 建议定期备份重要文件的密码
3. 生物识别仅为便利功能，请确保密码本身足够强壮
4. 系统钥匙串密码丢失会导致无法使用生物识别（但可以手动输入密码）

## 更新日志

- **v2.0**: 添加生物识别支持
  - 自动检测已保存密码
  - 直接使用 Touch ID/Face ID 解密
  - 优化用户体验，减少交互步骤

