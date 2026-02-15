# 隐写术加密使用指南

## 概述

隐写术（Steganography）加密功能允许你将加密文件**伪装成普通文件**，让别人无法察觉这是一个加密文件。

## 核心特性

- 🎭 **完美伪装** - 加密文件看起来像普通文件
- 📁 **保持功能** - 伪装文件仍然可以正常打开和使用
- 🔒 **双重保护** - 既隐藏又加密
- 🎨 **多种格式** - 支持文本、图片、视频、文档等
- 🔍 **难以检测** - 无明显的加密特征

## 工作原理

```
普通加密：
secret.pdf → encrypt → secret.pdf.encrypted
                        ↑ 明显是加密文件

隐写术加密：
secret.pdf + cover.txt → stego-encrypt → document.txt
                                          ↑ 看起来像普通文本文件
```

### 文件结构

```
┌─────────────────────────────────────────┐
│         伪装文件数据                    │
│      (可以正常打开和查看)               │
│                                         │
├─────────────────────────────────────────┤
│         加密的秘密数据                  │
│      (隐藏在文件末尾)                   │
│                                         │
├─────────────────────────────────────────┤
│         元数据和标记                    │
│      (很小，难以察觉)                   │
└─────────────────────────────────────────┘
```

## 使用方法

### 1. 基本隐写加密

```bash
# 将 secret.pdf 隐藏在 cover.txt 中
python3 cli_encrypt.py stego-encrypt secret.pdf cover.txt -o document.txt -p "密码"
```

**结果**：
- `document.txt` 看起来像普通文本文件
- 可以用文本编辑器打开，显示 cover.txt 的内容
- 但实际上包含了加密的 secret.pdf

### 2. 解密隐藏的文件

```bash
# 从 document.txt 中解密出 secret.pdf
python3 cli_encrypt.py stego-decrypt document.txt -o secret.pdf -p "密码"
```

### 3. 查看隐写文件信息

```bash
# 查看文件是否包含隐藏数据
python3 cli_encrypt.py stego-info document.txt
```

**输出示例**：
```
✓ 这是一个隐写加密文件

文件信息：
  总大小: 1.5 MB
  伪装文件大小: 500 KB
  加密数据大小: 1.0 MB
  秘密文件名: secret.pdf
  伪装文件名: cover.txt
  伪装类型: text
  隐藏比例: 66.7%
```

### 4. 提取伪装文件（不解密）

```bash
# 只提取伪装文件，不解密秘密数据
python3 cli_encrypt.py stego-extract document.txt -o cover.txt
```

## 使用场景

### 场景 1：隐藏敏感文档

```bash
# 将机密合同隐藏在普通的会议记录中
python3 cli_encrypt.py stego-encrypt 机密合同.pdf 会议记录.txt -o 2024年会议记录.txt -p "密码"

# 别人看到的：普通的会议记录文本文件
# 实际包含：加密的机密合同
```

### 场景 2：伪装成图片

```bash
# 将私密照片隐藏在风景照中
python3 cli_encrypt.py stego-encrypt 私密照片.jpg 风景.jpg -o 度假照片.jpg -p "密码"

# 别人看到的：普通的风景照片
# 实际包含：加密的私密照片
```

### 场景 3：伪装成视频

```bash
# 将重要视频隐藏在普通视频中
python3 cli_encrypt.py stego-encrypt 重要会议.mp4 旅游视频.mp4 -o 假期旅游.mp4 -p "密码"

# 别人看到的：旅游视频（可以正常播放）
# 实际包含：加密的重要会议视频
```

### 场景 4：伪装成日志文件

```bash
# 将敏感数据隐藏在系统日志中
python3 cli_encrypt.py stego-encrypt 敏感数据.xlsx 系统日志.log -o system.log -p "密码"

# 别人看到的：普通的系统日志
# 实际包含：加密的敏感数据
```

## 支持的文件类型

### 文本文件
- `.txt`, `.log`, `.md`, `.json`, `.xml`, `.csv`
- 优点：体积小，不引人注目
- 适合：隐藏小型文档

### 图片文件
- `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`
- 优点：常见，不易引起怀疑
- 适合：隐藏中等大小的文件

### 视频文件
- `.mp4`, `.avi`, `.mov`, `.mkv`, `.flv`
- 优点：体积大，可以隐藏大文件
- 适合：隐藏大型文档或视频

### 音频文件
- `.mp3`, `.wav`, `.flac`, `.aac`, `.ogg`
- 优点：常见，体积适中
- 适合：隐藏中小型文件

### 文档文件
- `.pdf`, `.doc`, `.docx`, `.xls`, `.xlsx`
- 优点：专业，不易引起怀疑
- 适合：隐藏商业文档

### 压缩文件
- `.zip`, `.rar`, `.7z`, `.tar`, `.gz`
- 优点：体积大，可以隐藏多个文件
- 适合：批量隐藏

## 完整示例

### 示例 1：隐藏财务报表

```bash
# 1. 准备文件
# - 秘密文件：财务报表.xlsx
# - 伪装文件：年度总结.docx

# 2. 隐写加密
python3 cli_encrypt.py stego-encrypt 财务报表.xlsx 年度总结.docx \
    -o 2024年度总结.docx -p "MySecretPass123!"

# 3. 查看结果
python3 cli_encrypt.py stego-info 2024年度总结.docx

# 输出：
# ✓ 这是一个隐写加密文件
# 文件信息：
#   总大小: 2.3 MB
#   伪装文件大小: 1.5 MB
#   加密数据大小: 800 KB
#   秘密文件名: 财务报表.xlsx
#   伪装文件名: 年度总结.docx

# 4. 解密（需要时）
python3 cli_encrypt.py stego-decrypt 2024年度总结.docx \
    -o 财务报表.xlsx -p "MySecretPass123!"
```

### 示例 2：隐藏视频文件

```bash
# 1. 准备大型伪装文件
# - 秘密文件：机密会议.mp4 (500MB)
# - 伪装文件：电影.mp4 (2GB)

# 2. 隐写加密
python3 cli_encrypt.py stego-encrypt 机密会议.mp4 电影.mp4 \
    -o 周末电影.mp4 -p "VideoPass2024"

# 3. 结果
# - 周末电影.mp4 看起来是普通电影
# - 可以用播放器正常播放
# - 实际包含加密的机密会议视频
# - 文件大小约 2.5GB（2GB + 500MB）

# 4. 解密
python3 cli_encrypt.py stego-decrypt 周末电影.mp4 \
    -o 机密会议.mp4 -p "VideoPass2024"
```

## 安全性说明

### 优势

1. **隐蔽性**
   - 文件看起来完全正常
   - 没有 `.encrypted` 等明显后缀
   - 伪装文件可以正常打开

2. **双重保护**
   - 即使被发现是隐写文件
   - 仍然需要密码才能解密
   - 使用 AES-256-GCM 加密

3. **难以检测**
   - 标记隐藏在文件末尾
   - 文件大小增加不明显
   - 没有明显的加密特征

### 注意事项

1. **文件大小**
   - 输出文件 = 伪装文件 + 加密数据 + 少量元数据
   - 如果伪装文件太小，大小增加会很明显
   - 建议：伪装文件至少是秘密文件的 2 倍大

2. **伪装文件选择**
   - 选择常见的文件类型
   - 选择合理大小的文件
   - 确保伪装文件可以正常打开

3. **密码安全**
   - 使用强密码
   - 不要在文件名中暴露信息
   - 可以结合生物识别功能

## 与普通加密对比

| 特性 | 普通加密 | 隐写术加密 |
|------|---------|-----------|
| 隐蔽性 | ❌ 明显是加密文件 | ✅ 看起来像普通文件 |
| 文件名 | `.encrypted` 后缀 | 任意正常后缀 |
| 可打开性 | ❌ 无法打开 | ✅ 可以打开伪装内容 |
| 安全性 | ✅ AES-256 | ✅ AES-256 |
| 文件大小 | 略大于原文件 | 伪装文件 + 原文件 |
| 适用场景 | 一般加密需求 | 需要隐蔽的场景 |

## 检测和防御

### 如何检测隐写文件

```bash
# 使用 stego-info 命令
python3 cli_encrypt.py stego-info suspicious_file.txt

# 如果是隐写文件，会显示详细信息
# 如果不是，会提示"这不是一个隐写加密文件"
```

### 防止被检测

1. **选择合适的伪装文件**
   - 使用常见文件类型
   - 文件大小要合理
   - 确保可以正常打开

2. **控制隐藏比例**
   - 隐藏比例 < 50% 较难察觉
   - 大型伪装文件可以隐藏更多数据

3. **文件命名**
   - 使用普通的文件名
   - 避免可疑的命名模式

## 高级用法

### 多层隐藏

```bash
# 第一层：加密文件A
python3 cli_encrypt.py encrypt fileA.pdf -o fileA.enc -p "pass1"

# 第二层：将加密文件隐藏在图片中
python3 cli_encrypt.py stego-encrypt fileA.enc photo.jpg -o vacation.jpg -p "pass2"

# 第三层：再次隐藏
python3 cli_encrypt.py stego-encrypt vacation.jpg video.mp4 -o movie.mp4 -p "pass3"

# 解密需要三个密码和三个步骤
```

### 批量隐写

```bash
# 创建脚本批量处理
for secret in secrets/*.pdf; do
    cover="covers/$(basename $secret .pdf).txt"
    output="hidden/$(basename $secret .pdf).txt"
    python3 cli_encrypt.py stego-encrypt "$secret" "$cover" -o "$output" -p "password"
done
```

## 故障排除

### 问题：伪装文件无法打开

**原因**：文件格式不兼容或损坏

**解决**：
```bash
# 提取原始伪装文件
python3 cli_encrypt.py stego-extract hidden.txt -o cover.txt
```

### 问题：文件太大

**原因**：伪装文件 + 秘密文件导致总大小过大

**解决**：
- 压缩秘密文件
- 选择更大的伪装文件
- 使用视频作为伪装文件

### 问题：被检测出是隐写文件

**原因**：文件大小异常或使用了检测工具

**解决**：
- 选择更大的伪装文件
- 降低隐藏比例
- 使用多层隐藏

## 总结

隐写术加密提供了额外的隐蔽层，适合需要高度保密的场景：

✅ **适合使用的情况**：
- 需要隐藏文件的存在
- 担心被搜查或检查
- 需要在公开场合传输敏感文件
- 想要额外的安全层

❌ **不适合使用的情况**：
- 只需要基本加密保护
- 文件大小受限
- 需要频繁访问文件

**记住**：隐写术加密 = 隐蔽性 + 加密安全性 = 双重保护！

