# 生物识别功能使用说明

## ❓ 为什么没有弹出指纹识别对话框？

### 原因分析

生物识别功能需要**两个步骤**才能工作：

#### 步骤 1：首次加密时保存密码（必须）

当你**第一次加密文件**时，需要：
1. ❌ **不要使用 `-p` 参数**
2. ✅ **交互式输入密码**
3. ✅ **选择保存密码到钥匙串**

#### 步骤 2：解密时使用指纹

只有在步骤 1 完成后，解密时才会：
1. 检测到已保存的密码
2. 自动弹出 Touch ID/Face ID 对话框
3. 验证成功后自动解密

---

## ✅ 正确的使用方法

### 第一次加密（保存密码）

```bash
# ❌ 错误：使用 -p 参数
python3 cli_encrypt.py encrypt document.pdf -p "MyPassword"
# 这样不会询问是否保存密码！

# ✅ 正确：不使用 -p 参数
python3 cli_encrypt.py encrypt document.pdf
```

**交互过程：**
```
请输入加密密码：
密码: ********（输入密码）
密码应包含大写字母、小写字母、数字和特殊字符中的至少三种

确认密码: ********（再次输入）

💡 是否保存密码到钥匙串？下次解密时可直接使用 Touch ID/Face ID (y/N): y
✓ 密码已安全保存，下次解密时将自动使用生物识别验证

📁 输入文件: document.pdf
📁 输出文件: document.pdf.encrypted
🔐 加密算法: AES-256-GCM
...
✓ 加密成功！
```

### 第二次解密（使用指纹）

```bash
python3 cli_encrypt.py decrypt document.pdf.encrypted
```

**这时会弹出：**
```
🔐 检测到已保存的密码凭证，使用生物识别验证...
🔐 正在从钥匙串获取密码（可能需要生物识别验证）...
```

**macOS 会弹出系统对话框：**
- 💬 "cli-encrypt-tool 想要访问钥匙串中的密钥"
- 👆 **请按 Touch ID 或看向摄像头（Face ID）**

验证成功后：
```
✓ 生物识别验证成功

📁 输入文件: document.pdf.encrypted
📁 输出文件: document.pdf
⏳ 正在解密...
✓ 解密成功！
```

---

## 🧪 完整测试步骤

### 1. 准备测试文件

```bash
cd /Users/xucan/Projects/cli-encrypt-tool
echo "这是测试内容" > test_bio.txt
```

### 2. 加密并保存密码

```bash
python3 cli_encrypt.py encrypt test_bio.txt
```

**按照提示操作：**
1. 输入密码：`TestPass123!`
2. 确认密码：`TestPass123!`
3. 是否保存密码：输入 `y` 并回车

### 3. 解密（触发指纹识别）

```bash
python3 cli_encrypt.py decrypt test_bio.txt.encrypted
```

**此时应该：**
- ✅ 显示"检测到已保存的密码凭证"
- ✅ 弹出 macOS 系统对话框
- ✅ 要求 Touch ID 或 Face ID 验证
- ✅ 验证成功后自动解密

---

## 🔍 故障排查

### 问题 1：没有询问是否保存密码

**原因：** 使用了 `-p` 参数直接提供密码

**解决：** 不要使用 `-p` 参数，让程序交互式询问密码

### 问题 2：解密时没有弹出指纹识别

**可能原因：**

1. **首次加密时没有保存密码**
   - 检查：加密时是否看到"是否保存密码到钥匙串？"的提示
   - 解决：重新加密，这次选择 `y` 保存密码

2. **keyring 模块未安装**
   ```bash
   pip3 install keyring
   ```

3. **文件路径或属性改变**
   - 密码是基于文件路径和属性保存的
   - 如果文件被移动或重命名，需要重新保存密码

4. **macOS 钥匙串权限问题**
   - 打开"钥匙串访问"应用
   - 搜索 "cli-encrypt-tool"
   - 确保有对应的条目

### 问题 3：生物识别不可用

**检查：**
```bash
python3 -c "from biometric_auth import BiometricAuth; print('可用:', BiometricAuth.is_available())"
```

**如果显示 `False`：**
- 确保你在 macOS 上
- 确保设备有 Touch ID 或 Face ID
- 确保已在系统设置中启用生物识别

---

## 📝 工作原理

### 密码存储

1. 加密时，如果选择保存密码：
   - 生成文件唯一标识：`SHA256(文件路径:inode:大小)`
   - 将密码存储到 macOS 系统钥匙串
   - 钥匙串条目名称：`cli-encrypt-tool`

### 密码获取

2. 解密时，如果检测到已保存的密码：
   - 计算文件标识
   - 尝试从钥匙串获取密码
   - **macOS 自动触发 Touch ID/Face ID 验证**
   - 验证成功后返回密码

### 安全性

- ✅ 密码存储在系统钥匙串，受系统级加密保护
- ✅ 只有通过生物识别才能访问
- ✅ 每个文件的密码独立存储
- ✅ 不会同步到其他设备

---

## 💡 使用建议

### 日常使用

```bash
# 第一次加密文件
python3 cli_encrypt.py encrypt important.pdf
# 输入密码，选择 y 保存

# 以后每次解密
python3 cli_encrypt.py decrypt important.pdf.encrypted
# 按指纹即可，无需输入密码
```

### 临时文件（不保存密码）

```bash
# 使用 -p 参数
python3 cli_encrypt.py encrypt temp.txt -p "TempPassword"

# 或者交互式输入，但选择 n 不保存
python3 cli_encrypt.py encrypt temp.txt
# 输入密码，选择 n 不保存
```

### 批量文件（共享密码）

```bash
# 第一个文件：保存密码
python3 cli_encrypt.py encrypt file1.txt
# 选择 y 保存

# 其他文件：也保存密码
python3 cli_encrypt.py encrypt file2.txt
# 使用相同密码，选择 y 保存

# 解密时都可以用指纹
python3 cli_encrypt.py decrypt file1.txt.encrypted
python3 cli_encrypt.py decrypt file2.txt.encrypted
```

---

## 🎯 总结

**要使用生物识别功能，记住：**

1. ✅ **加密时不要用 `-p` 参数**
2. ✅ **交互式输入密码**
3. ✅ **选择 `y` 保存密码**
4. ✅ **解密时会自动弹出指纹识别**

**如果还是不行：**
1. 检查 keyring 是否安装
2. 检查是否在 macOS 上
3. 查看钥匙串访问应用中是否有保存的条目
4. 尝试删除旧条目重新保存

---

**创建时间**: 2024-02-15  
**适用版本**: CLI 加密工具 v2.0

