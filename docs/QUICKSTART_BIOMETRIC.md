# 生物识别功能快速入门

## 5 分钟上手指南

### 第 1 步：安装依赖

```bash
pip install keyring
```

### 第 2 步：加密文件并保存密码

```bash
python3 cli_encrypt.py encrypt myfile.pdf
```

**交互过程**：
```
请输入加密密码: ********
确认密码: ********

是否保存密码以便下次使用生物识别验证？(y/N): y
✓ 密码已安全保存到系统钥匙串
✓ 加密成功！
```

### 第 3 步：使用生物识别解密

```bash
python3 cli_encrypt.py decrypt myfile.pdf.encrypted
```

**交互过程**：
```
检测到已保存的密码凭证
是否使用生物识别验证？(Y/n): [按回车]

🔐 正在从钥匙串获取密码（可能需要生物识别验证）...
[系统弹出 Touch ID 提示 - 按下指纹或看向摄像头]
✓ 生物识别验证成功
✓ 解密成功！
```

## 就这么简单！

从此无需记忆和输入复杂密码，只需：
1. 👆 按下 Touch ID
2. 👀 或看向摄像头（Face ID）
3. ✅ 完成！

## 常见问题

**Q: 我的设备支持吗？**  
A: 需要 macOS 系统，且设备支持 Touch ID 或 Face ID。

**Q: 安全吗？**  
A: 非常安全！密码存储在 macOS 系统钥匙串中，与 Safari 密码使用相同的安全机制。

**Q: 如果不想用生物识别呢？**  
A: 可以随时选择手动输入密码，两种方式都支持。

**Q: 密码存在哪里？**  
A: 存储在 macOS 系统钥匙串中，可以在"钥匙串访问"应用中查看和管理。

## 测试功能

运行测试脚本验证功能：

```bash
python3 test_biometric.py
```

## 查看演示

运行演示脚本了解更多：

```bash
python3 demo_biometric.py
```

## 详细文档

- [完整使用指南](BIOMETRIC_AUTH_GUIDE.md)
- [README](README.md)

---

**享受无密码的加密体验！** 🎉

