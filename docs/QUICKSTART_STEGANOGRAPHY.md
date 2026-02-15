# 隐写术加密 - 5分钟快速入门

## 什么是隐写术加密？

将加密文件**伪装成普通文件**，让别人无法察觉这是一个加密文件。

```
普通加密：secret.pdf → secret.pdf.encrypted  ❌ 明显是加密文件
隐写加密：secret.pdf + cover.txt → document.txt  ✅ 看起来像普通文本
```

## 快速开始

### 步骤 1：隐写加密

```bash
python3 cli_encrypt.py stego-encrypt secret.pdf cover.txt -o document.txt -p "密码"
```

**结果**：
- `document.txt` 看起来像普通文本文件
- 可以用文本编辑器打开
- 但实际包含加密的 `secret.pdf`

### 步骤 2：隐写解密

```bash
python3 cli_encrypt.py stego-decrypt document.txt -o secret.pdf -p "密码"
```

**结果**：
- 从 `document.txt` 中解密出 `secret.pdf`
- 需要正确的密码

### 步骤 3：查看信息

```bash
python3 cli_encrypt.py stego-info document.txt
```

**输出**：
```
✓ 这是一个隐写加密文件
文件信息：
  总大小: 1.5 MB
  伪装文件大小: 500 KB
  加密数据大小: 1.0 MB
  秘密文件名: secret.pdf
  隐藏比例: 66.7%
```

## 实用场景

### 场景 1：隐藏敏感文档

```bash
python3 cli_encrypt.py stego-encrypt 机密合同.pdf 会议记录.txt \
    -o 会议记录.txt -p "密码"
```

别人看到：普通会议记录  
实际包含：加密的机密合同

### 场景 2：伪装成图片

```bash
python3 cli_encrypt.py stego-encrypt 私密照片.jpg 风景.jpg \
    -o 度假照片.jpg -p "密码"
```

别人看到：普通风景照片（可以正常打开）  
实际包含：加密的私密照片

### 场景 3：伪装成视频

```bash
python3 cli_encrypt.py stego-encrypt 重要会议.mp4 电影.mp4 \
    -o 周末电影.mp4 -p "密码"
```

别人看到：普通电影（可以正常播放）  
实际包含：加密的会议视频

## 核心优势

| 特性 | 说明 |
|------|------|
| 🎭 完美伪装 | 文件看起来完全正常 |
| 🔒 双重保护 | 隐藏 + AES-256 加密 |
| 📁 保持功能 | 伪装文件仍可正常打开 |
| 🔍 难以检测 | 没有明显的加密特征 |

## 支持的文件类型

- **文本**：.txt, .log, .md, .json, .xml
- **图片**：.jpg, .png, .gif, .bmp
- **视频**：.mp4, .avi, .mov, .mkv
- **音频**：.mp3, .wav, .flac, .aac
- **文档**：.pdf, .doc, .docx, .xls
- **压缩**：.zip, .rar, .7z, .tar

## 最佳实践

1. **伪装文件要够大**
   - 伪装文件至少是秘密文件的 2 倍大
   - 这样文件大小增加不明显

2. **选择常见类型**
   - 使用常见的文件类型
   - 避免引起怀疑

3. **合理命名**
   - 使用普通的文件名
   - 不要用 `encrypted_xxx` 之类的名字

4. **结合生物识别**（macOS）
   - 加密时保存密码到钥匙串
   - 解密时使用 Touch ID/Face ID

## 常见问题

**Q: 伪装文件会被修改吗？**  
A: 不会。伪装文件的内容保持不变，秘密数据添加在文件末尾。

**Q: 别人能发现这是加密文件吗？**  
A: 很难。文件看起来完全正常，可以正常打开。只有使用 `stego-info` 命令才能检测。

**Q: 安全吗？**  
A: 非常安全。使用 AES-256-GCM 加密，即使被发现是隐写文件，仍需要密码才能解密。

**Q: 文件会变多大？**  
A: 输出文件 = 伪装文件 + 加密数据 + 少量元数据（约几十字节）

## 完整示例

```bash
# 1. 准备文件
echo "这是秘密内容" > secret.txt
echo "这是普通内容" > cover.txt

# 2. 隐写加密
python3 cli_encrypt.py stego-encrypt secret.txt cover.txt \
    -o output.txt -p "MyPassword123"

# 3. 验证伪装（应该显示 cover.txt 的内容）
cat output.txt

# 4. 查看信息
python3 cli_encrypt.py stego-info output.txt

# 5. 解密
python3 cli_encrypt.py stego-decrypt output.txt \
    -o decrypted.txt -p "MyPassword123"

# 6. 验证（应该显示 secret.txt 的内容）
cat decrypted.txt
```

## 查看演示

```bash
# 运行完整演示
python3 demo_steganography.py
```

## 详细文档

- [STEGANOGRAPHY_GUIDE.md](STEGANOGRAPHY_GUIDE.md) - 完整使用指南
- [README.md](README.md) - 所有功能说明

---

**开始使用隐写术加密，享受隐蔽的安全保护！** 🎭🔒

