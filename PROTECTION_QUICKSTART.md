# 使用者保护 - 实用指南

## 问题

如果有人发现你电脑上有加密工具，可能会怀疑你使用了隐写术加密。

## 解决方案

我们提供了一个**伪装版本**的工具：`file_manager.py`

---

## 🎭 伪装策略

### 工具伪装

```
原始工具：cli_encrypt.py（明显是加密工具）
伪装工具：file_manager.py（看起来是文件管理工具）
```

### 功能伪装

| 表面功能 | 实际功能 |
|---------|---------|
| 压缩文件 | 真实的压缩功能 |
| 解压文件 | 真实的解压功能 |
| 备份文件 | 真实的备份功能 |
| **安全备份** | **隐藏的加密功能** ✨ |
| **安全恢复** | **隐藏的解密功能** ✨ |
| 列出文件 | 真实的文件列表 |
| 格式转换 | 真实的格式转换 |

---

## 📖 使用方法

### 1. 普通功能（掩护）

```bash
# 压缩文件
python3 file_manager.py compress document.pdf

# 解压文件
python3 file_manager.py extract document.pdf.gz

# 备份文件（普通备份）
python3 file_manager.py backup important.pdf

# 列出文件
python3 file_manager.py list /path/to/folder
```

**这些都是真实功能，可以正常使用！**

### 2. 隐藏的加密功能

```bash
# 安全备份（实际是加密）
python3 file_manager.py backup secret.pdf --secure

# 安全恢复（实际是解密）
python3 file_manager.py restore backups/secret.pdf --secure
```

**使用 `--secure` 参数触发隐藏的加密功能！**

---

## 🔒 完整使用流程

### 场景：加密敏感文件

```bash
# 步骤 1：创建"安全备份"（实际是加密）
python3 file_manager.py backup 机密文件.pdf --secure
# 输入密码
# 文件被加密并伪装

# 步骤 2：查看备份（看起来很正常）
python3 file_manager.py list backups/
# 显示：📄 机密文件.pdf (1.2 MB)

# 步骤 3：需要时"恢复"（实际是解密）
python3 file_manager.py restore backups/机密文件.pdf --secure
# 输入密码
# 文件被解密
```

### 对外说法

- "我在用文件管理工具整理文件"
- "这是一个备份工具"
- "我在压缩一些文件"

**完全合理，不引起怀疑！**

---

## 🧹 清理痕迹

### 使用后清理

```bash
# 清理所有使用历史
python3 file_manager.py --clean-history
```

**这会清理**：
- ✅ 配置文件
- ✅ Shell 历史记录
- ✅ 临时文件

### 便携模式

```bash
# 从 USB 运行（不在系统留下痕迹）
python3 file_manager.py --portable backup file.pdf --secure

# 使用后清理
python3 file_manager.py --portable --clean-history
```

### 自毁功能

```bash
# 完全删除工具本身
python3 file_manager.py --self-destruct
```

**警告**：这会永久删除工具！

---

## 🎯 最佳实践

### 1. 重命名工具

```bash
# 重命名为更普通的名字
mv file_manager.py system_backup.py
# 或
mv file_manager.py doc_converter.py
```

### 2. 混合使用

```bash
# 经常使用普通功能（掩护）
python3 file_manager.py compress file1.txt
python3 file_manager.py list documents/
python3 file_manager.py backup file2.pdf

# 偶尔使用安全功能（加密）
python3 file_manager.py backup secret.pdf --secure
```

### 3. 从 USB 运行

```bash
# 1. 将工具放在 USB
cp file_manager.py /Volumes/USB/tools/

# 2. 从 USB 运行
cd /Volumes/USB/tools/
python3 file_manager.py backup secret.pdf --secure --portable

# 3. 使用后清理
python3 file_manager.py --clean-history --portable

# 4. 拔出 USB
# 系统中没有任何痕迹！
```

---

## 🛡️ 安全建议

### 对于一般用户

1. **使用伪装工具**
   - 使用 `file_manager.py` 而不是 `cli_encrypt.py`
   - 重命名为更普通的名字

2. **混合使用功能**
   - 经常使用普通功能
   - 偶尔使用安全功能

3. **使用后清理**
   - 运行 `--clean-history`
   - 清除 shell 历史

### 对于高级用户

1. **便携模式**
   - 从 USB 运行
   - 使用 `--portable` 参数
   - 不在系统留下痕迹

2. **虚拟机**
   - 在虚拟机中使用
   - 使用后删除虚拟机快照

3. **在线版本**
   - 使用 Web 版本（如果有）
   - 隐私模式浏览
   - 使用后清除缓存

---

## 📊 对比

| 方案 | 隐蔽性 | 便捷性 | 安全性 |
|------|--------|--------|--------|
| 原始工具 | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 伪装工具 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 便携模式 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 在线版本 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## ❓ 常见问题

### Q: 伪装工具安全吗？
A: 是的。加密算法完全相同（AES-256-GCM），只是外观不同。

### Q: 普通功能真的能用吗？
A: 是的。压缩、解压、备份等都是真实功能，可以正常使用。

### Q: 如何触发加密功能？
A: 使用 `--secure` 参数：
```bash
python3 file_manager.py backup file.pdf --secure
```

### Q: 清理历史会删除什么？
A: 会清理：
- 配置文件
- Shell 历史中的相关命令
- 临时文件

但**不会**删除你的加密文件。

### Q: 自毁功能安全吗？
A: 是的。它会：
1. 清理所有历史
2. 删除工具本身
3. 不会删除你的文件

---

## 🎯 推荐方案

### 方案 A：日常使用（推荐）

```bash
# 1. 重命名工具
mv file_manager.py doc_tools.py

# 2. 正常使用
python3 doc_tools.py compress file.txt
python3 doc_tools.py backup important.pdf

# 3. 需要加密时
python3 doc_tools.py backup secret.pdf --secure

# 4. 定期清理
python3 doc_tools.py --clean-history
```

### 方案 B：高度隐蔽（最安全）

```bash
# 1. 从 USB 运行
cd /Volumes/USB/tools/

# 2. 便携模式
python3 file_manager.py --portable backup secret.pdf --secure

# 3. 使用后清理
python3 file_manager.py --portable --clean-history

# 4. 拔出 USB
# 完全没有痕迹！
```

### 方案 C：一次性使用

```bash
# 1. 使用工具
python3 file_manager.py backup secret.pdf --secure

# 2. 自毁
python3 file_manager.py --self-destruct

# 工具被完全删除！
```

---

## 📝 总结

**核心思想**：让工具看起来完全正常和合理！

✅ **伪装工具** - 看起来像文件管理工具  
✅ **真实功能** - 提供真实的文件管理功能  
✅ **隐藏加密** - 使用 `--secure` 触发加密  
✅ **清理痕迹** - 使用后不留痕迹  
✅ **便携模式** - 从 USB 运行更安全  

**记住**：最好的保护是让一切看起来正常！🎭

