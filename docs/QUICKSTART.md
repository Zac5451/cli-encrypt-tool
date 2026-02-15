# 快速开始指南

## 5 分钟上手 CLI 加密工具

### 第一步：安装依赖

```bash
cd cli-encrypt-tool
pip3 install -r requirements.txt
```

或者使用自动安装脚本：

```bash
./install.sh
```

### 第二步：加密你的第一个文件

```bash
# 创建一个测试文件
echo "这是我的秘密信息" > secret.txt

# 加密文件（会提示输入密码）
python3 cli_encrypt.py encrypt secret.txt

# 现在你有了一个加密文件：secret.txt.encrypted
```

### 第三步：解密文件

```bash
# 解密文件（会提示输入密码）
python3 cli_encrypt.py decrypt secret.txt.encrypted

# 查看解密后的内容
cat secret.txt.decrypted
```

### 第四步：高级用法

```bash
# 使用 Argon2 密钥派生（更安全但更慢）
python3 cli_encrypt.py encrypt --kdf argon2 document.pdf

# 加密后删除原文件
python3 cli_encrypt.py encrypt --delete-original sensitive.doc

# 指定输出文件名
python3 cli_encrypt.py encrypt -o backup.encrypted important.txt

# 解密后删除加密文件
python3 cli_encrypt.py decrypt --delete-encrypted secret.txt.encrypted
```

### 常见问题

**Q: 忘记密码怎么办？**  
A: 无法恢复。这是设计如此，确保了安全性。请务必记住密码或使用密码管理器。

**Q: 可以加密文件夹吗？**  
A: 目前不支持。建议先压缩文件夹，然后加密压缩文件：
```bash
tar -czf folder.tar.gz folder/
python3 cli_encrypt.py encrypt folder.tar.gz
```

**Q: 加密文件可以在其他电脑上解密吗？**  
A: 可以！只要安装了相同的工具和依赖，使用相同的密码即可解密。

**Q: 这个工具安全吗？**  
A: 使用军事级 AES-256-GCM 加密，与 VeraCrypt 相同的密钥派生方法。但请注意：
- 妥善保管密码
- 定期备份重要数据
- 本工具仅供学习和个人使用

### 运行测试

```bash
# 运行完整测试套件
python3 test_crypto.py

# 查看使用示例
python3 examples.py
```

### 获取帮助

```bash
# 查看完整帮助
python3 cli_encrypt.py --help

# 查看加密命令帮助
python3 cli_encrypt.py encrypt --help

# 查看解密命令帮助
python3 cli_encrypt.py decrypt --help
```

### 性能提示

- 大文件（>100MB）：使用 PBKDF2（更快）
- 高安全性需求：使用 Argon2（更安全）
- 默认设置已经很安全，适合大多数场景

### 下一步

- 阅读完整文档：`README.md`
- 查看代码示例：`examples.py`
- 了解技术细节：查看 `crypto_core.py` 源码

---

**提示**：第一次使用建议先用测试文件练习，确保熟悉流程后再加密重要文件。

