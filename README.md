# CLI 高级加密工具 v2.2

基于 VeraCrypt 设计理念的命令行文件加密工具，支持多算法、自毁文件、流式加密、**生物识别验证**、**隐写术加密**等高级功能。

## 功能特性

- ✅ **多算法支持**：AES-256-GCM、ChaCha20-Poly1305
- ✅ **密钥派生**：Argon2id、PBKDF2-HMAC-SHA512
- ✅ **生物识别验证**：Touch ID / Face ID 支持（macOS）
- ✅ **隐写术加密**：将加密文件伪装成普通文件 🆕
- ✅ **自毁文件**：支持过期时间、最大解密次数限制
- ✅ **流式加密**：支持 stdin/stdout 管道操作
- ✅ **抗暴力破解**：连续错误后自动锁定
- ✅ **元数据隐藏**：文件名、大小等被加密存储
- ✅ **多线程加速**：支持多线程并行加密
- ✅ **大文件支持**：分块处理，内存占用恒定
- ✅ **目录加密**：支持整个目录打包加密
- ✅ **批量处理**：支持通配符批量操作
- ✅ **进度显示**：tqdm 进度条
- ✅ **交互模式**：支持交互式 Shell

## 安装

```bash
pip install -r requirements.txt
```

依赖：
- cryptography >= 41.0.0
- argon2-cffi >= 23.1.0
- tqdm >= 4.65.0
- keyring >= 24.0.0 (生物识别功能)

## 快速开始

### 基本加密/解密

```bash
# 加密文件
python3 cli_encrypt.py encrypt document.pdf -p "YourPassword123!"

# 解密文件
python3 cli_encrypt.py decrypt document.pdf.encrypted -p "YourPassword123!"
```

### 🆕 使用生物识别验证（macOS）

```bash
# 加密文件并保存密码到钥匙串
python3 cli_encrypt.py encrypt document.pdf
# 输入密码后，选择 'y' 保存到钥匙串

# 使用 Touch ID/Face ID 解密
python3 cli_encrypt.py decrypt document.pdf.encrypted
# 系统会自动提示使用生物识别验证，无需手动输入密码！
```

**详细说明**：查看 [生物识别认证使用指南](BIOMETRIC_AUTH_GUIDE.md)

### 🆕 隐写术加密（伪装成普通文件）

```bash
# 将秘密文件隐藏在普通文件中
python3 cli_encrypt.py stego-encrypt secret.pdf cover.txt -o document.txt -p "密码"
# document.txt 看起来像普通文本文件，但实际包含加密的 secret.pdf

# 解密隐藏的文件
python3 cli_encrypt.py stego-decrypt document.txt -o secret.pdf -p "密码"

# 查看隐写文件信息
python3 cli_encrypt.py stego-info document.txt
```

**详细说明**：查看 [隐写术加密使用指南](STEGANOGRAPHY_GUIDE.md)

## 命令详解

### 1. 加密文件 (encrypt)

```bash
python3 cli_encrypt.py encrypt <input> [options]

选项:
  -o, --output PATH        输出文件路径
  -p, --password PASSWORD 加密密码
  -k, --kdf {pbkdf2,argon2}  密钥派生函数
  -a, --algorithm {aes256,chacha20,cascade}  加密算法
  -t, --threads N         线程数 (默认: 1)
  -f, --force             强制覆盖
  -d, --delete-original  加密后删除原文件
  -e, --expiry DAYS      过期天数 (自毁功能)
  -m, --max-decrypts N   最大解密次数 (自毁功能)
  --no-hide-metadata     显示元数据
  -s, --sign             启用数字签名
```

示例：
```bash
# 使用 ChaCha20 算法，7天后过期
python3 cli_encrypt.py encrypt file.pdf -a chacha20 -e 7 -p "密码"

# 最多解密3次
python3 cli_encrypt.py encrypt file.pdf -m 3 -p "密码"

# 多线程加密大文件
python3 cli_encrypt.py encrypt bigfile.iso -t 8 -p "密码"
```

### 2. 解密文件 (decrypt)

```bash
python3 cli_encrypt.py decrypt <input> [options]

选项:
  -o, --output PATH       输出文件路径
  -p, --password PASSWORD 解密密码
  -f, --force             强制覆盖
  -d, --delete-encrypted  解密后删除加密文件
```

### 3. 流式加密 (stream-encrypt)

支持管道操作，适合处理 stdin 输入或输出到 stdout：

```bash
# 流式加密
echo "Hello World" | python3 cli_encrypt.py stream-encrypt -p "密码" > file.enc

# 流式解密
python3 cli_encrypt.py stream-decrypt -p "密码" < file.enc

# 加密整个文件
cat secret.txt | python3 cli_encrypt.py stream-encrypt -p "密码" -a chacha20 > secret.enc
```

### 4. 目录加密 (encrypt-dir)

将整个目录打包并加密：

```bash
python3 cli_encrypt.py encrypt-dir myfolder -o backup.vcdir -p "密码"

# 带压缩和过期时间
python3 cli_encrypt.py encrypt-dir project/ -e 30 -p "密码"
```

### 5. 目录解密 (decrypt-dir)

```bash
python3 cli_encrypt.py decrypt-dir backup.vcdir -o restored_folder -p "密码"
```

### 6. 批量加密 (batch-encrypt)

支持通配符批量处理：

```bash
# 加密当前目录下所有 PDF
python3 cli_encrypt.py batch-encrypt "*.pdf" -o encrypted/ -p "密码"

# 加密多个指定文件
python3 cli_encrypt.py batch-encrypt "file1.txt file2.txt" -p "密码"
```

### 7. 批量解密 (batch-decrypt)

```bash
python3 cli_encrypt.py batch-decrypt "*.encrypted" -o decrypted/ -p "密码"
```

### 8. 预览模式 (dry-run)

预览加密效果，不实际执行：

```bash
python3 cli_encrypt.py dry-run largefile.iso

# 输出示例:
# 📋 加密预览信息：
#   输入文件: largefile.iso
#   文件大小: 1.50 GB
#   预计加密后大小: ~1.65 GB
#   算法: aes256
#   KDF: argon2
#   线程数: 4
```

### 9. 交互模式 (interactive)

交互式 Shell 模式：

```bash
$ python3 cli_encrypt.py interactive

=== CLI 加密工具交互模式 ===

encrypt> enc myfile.txt   # 加密
encrypt> dec myfile.enc   # 解密
encrypt> status           # 查看配置
encrypt> help             # 帮助
encrypt> exit             # 退出
```

### 10. 隐写术加密 (stego-encrypt) 🆕

将加密文件伪装成普通文件：

```bash
# 基本用法
python3 cli_encrypt.py stego-encrypt secret.pdf cover.txt -o document.txt -p "密码"

# 伪装成图片
python3 cli_encrypt.py stego-encrypt private.jpg landscape.jpg -o vacation.jpg -p "密码"

# 伪装成视频
python3 cli_encrypt.py stego-encrypt meeting.mp4 movie.mp4 -o video.mp4 -p "密码"
```

### 11. 隐写术解密 (stego-decrypt) 🆕

从伪装文件中解密：

```bash
python3 cli_encrypt.py stego-decrypt document.txt -o secret.pdf -p "密码"
```

### 12. 查看隐写文件信息 (stego-info) 🆕

检查文件是否包含隐藏数据：

```bash
python3 cli_encrypt.py stego-info document.txt

# 输出示例:
# ✓ 这是一个隐写加密文件
# 文件信息：
#   总大小: 1.5 MB
#   伪装文件大小: 500 KB
#   加密数据大小: 1.0 MB
#   秘密文件名: secret.pdf
#   隐藏比例: 66.7%
```

### 13. 提取伪装文件 (stego-extract) 🆕

只提取伪装文件，不解密秘密数据：

```bash
python3 cli_encrypt.py stego-extract document.txt -o cover.txt
```

## 高级功能

### 🆕 生物识别验证（Touch ID / Face ID）

**仅支持 macOS 系统**

无需每次手动输入密码，使用指纹或面部识别即可解密文件。

**工作流程**：
1. 首次加密文件时，输入密码后选择保存到系统钥匙串
2. 密码被安全存储在 macOS 钥匙串中（硬件级加密）
3. 后续解密时，系统自动检测已保存的密码
4. 使用 Touch ID 或 Face ID 验证身份后自动解密

**示例**：
```bash
# 加密并保存密码
$ python3 cli_encrypt.py encrypt secret.pdf
请输入加密密码: ********
确认密码: ********
是否保存密码以便下次使用生物识别验证？(y/N): y
✓ 密码已安全保存到系统钥匙串

# 使用生物识别解密
$ python3 cli_encrypt.py decrypt secret.pdf.encrypted
检测到已保存的密码凭证
是否使用生物识别验证？(Y/n): 
🔐 正在从钥匙串获取密码（可能需要生物识别验证）...
[系统弹出 Touch ID 提示]
✓ 生物识别验证成功
✓ 解密成功！
```

**安全性**：
- 密码存储在系统钥匙串，与 Safari 密码使用相同的安全机制
- 钥匙串数据经过硬件级加密
- 只有通过生物识别验证才能访问
- 生物识别数据从不离开设备的安全区域

**管理已保存的密码**：
```bash
# 查看已保存的密码
打开"钥匙串访问"应用 → 搜索 "cli-encrypt-tool"

# 删除已保存的密码
在钥匙串访问中右键删除对应项
```

**详细文档**：[BIOMETRIC_AUTH_GUIDE.md](BIOMETRIC_AUTH_GUIDE.md)

### 🆕 隐写术加密

将加密文件伪装成普通文件，实现隐蔽加密。

**工作原理**：
```
普通加密：secret.pdf → secret.pdf.encrypted (明显是加密文件)
隐写加密：secret.pdf + cover.txt → document.txt (看起来像普通文本)
```

**使用场景**：
1. **隐藏敏感文档**
```bash
python3 cli_encrypt.py stego-encrypt 机密合同.pdf 会议记录.txt -o 会议记录.txt -p "密码"
# 看起来是普通会议记录，实际包含加密的机密合同
```

2. **伪装成图片**
```bash
python3 cli_encrypt.py stego-encrypt 私密照片.jpg 风景.jpg -o 度假照片.jpg -p "密码"
# 可以正常打开查看风景照，但包含加密的私密照片
```

3. **伪装成视频**
```bash
python3 cli_encrypt.py stego-encrypt 重要会议.mp4 电影.mp4 -o 周末电影.mp4 -p "密码"
# 可以正常播放电影，但包含加密的会议视频
```

**优势**：
- 🎭 完美伪装 - 文件看起来完全正常
- 🔒 双重保护 - 隐藏 + 加密
- 📁 保持功能 - 伪装文件仍可正常打开
- 🔍 难以检测 - 没有明显的加密特征

**详细文档**：[STEGANOGRAPHY_GUIDE.md](STEGANOGRAPHY_GUIDE.md)

### 自毁文件

支持两种自毁方式：

1. **时间过期**
```bash
python3 cli_encrypt.py encrypt secret.pdf -e 7 -p "密码"
# 7天后文件自动过期，无法解密
```

2. **次数限制**
```bash
python3 cli_encrypt.py encrypt secret.pdf -m 3 -p "密码"
# 只能解密3次，第3次后失效
```

### 加密算法

| 算法 | 说明 | 适用场景 |
|------|------|----------|
| aes256 | AES-256-GCM (默认) | 通用场景，最广泛验证 |
| chacha20 | ChaCha20-Poly1305 | 移动设备，更快 |
| cascade | AES+Serpent 级联 | 最高安全要求 |

### 密钥派生

| KDF | 说明 | 安全等级 |
|-----|------|----------|
| argon2 | Argon2id (默认) | 最高，推荐 |
| pbkdf2 | PBKDF2-HMAC-SHA512 | 兼容性更好 |

### 抗暴力破解

工具内置保护机制：
- 连续 5 次密码错误后，锁定 5 分钟
- 每次失败后延迟递增
- 错误计数按 IP/文件 分开

### 配置文件

默认读取 `~/.cli-encryptrc`，或通过 `-c` 指定：

```ini
[encryption]
algorithm = aes256
kdf = argon2
threads = 4
signature = false

[security]
hide_metadata = true
brute_force_protection = true

[defaults]
compress = true
```

## 文件格式

加密文件格式 (v2)：

```
[文件头 105+ 字节]
  - 魔数: VCCLI (5 bytes)
  - 版本: 2 (1 byte)
  - 算法: 1=AES, 2=ChaCha20 (1 byte)
  - KDF: 1=PBKDF2, 2=Argon2 (1 byte)
  - 标志位 (1 byte)
  - 原始大小 (8 bytes)
  - 元数据长度 (4 bytes)
  - 盐值 64 bytes
  - Nonce 12 bytes
  - 过期天数 (4 bytes)
  - 最大解密次数 (4 bytes)

[加密元数据]
  - JSON 格式，包含文件名、创建时间等

[加密数据块]
  - 块长度 (4 bytes)
  - 加密数据 + GCM标签 (变长)
  - ... 重复 ...
```

## 安全性说明

### 密码建议

- **最小长度**：8 字符（建议 12+）
- **复杂度**：大写+小写+数字+特殊字符
- **避免**：常见单词、生日、键盘序列

### 加密强度

- **算法**：AES-256-GCM / ChaCha20-Poly1305
- **认证**：GCM/Poly1305 提供完整性验证
- **盐值**：64 字节随机盐值
- **密钥派生**：
  - Argon2id：3 次迭代，64MB 内存
  - PBKDF2-SHA512：500,000 次迭代

### 注意事项

1. 密码丢失无法恢复
2. 自毁文件过期后无法解密
3. 批量操作失败不会中断其他文件

## 故障排除

### Argon2 不可用

```bash
pip install argon2-cffi
```

或使用 PBKDF2：
```bash
python3 cli_encrypt.py encrypt file.pdf -k pbkdf2 -p "密码"
```

### 解密失败

可能原因：
1. 密码错误
2. 文件已损坏
3. 文件已过期
4. 解密次数已达上限

### tqdm 未安装

```bash
pip install tqdm
```

未安装时仍可使用，但无进度条显示。

## 与 VeraCrypt 对比

| 特性 | VeraCrypt | 本工具 |
|------|-----------|--------|
| 用途 | 整盘加密 | 文件加密 |
| 平台 | 跨平台 | 跨平台 (Python) |
| 复杂度 | 高 | 低 |
| 自毁功能 | 无 | 有 |
| 流式加密 | 无 | 有 |
| 交互模式 | 无 | 有 |

## 许可证

仅供学习和个人使用，请勿用于非法用途。

## 参考

- [VeraCrypt](https://veracrypt.fr/)
- [AES-GCM](https://csrc.nist.gov/publications/detail/sp/800-38d/final)
- [Argon2](https://github.com/P-H-C/phc-winner-argon2)
- [ChaCha20-Poly1305](https://tools.ietf.org/html/rfc8439)
