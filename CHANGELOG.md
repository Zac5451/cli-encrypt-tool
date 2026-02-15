# 更新日志

## v2.1 (2026-02-14)

### 🎉 重大更新：生物识别验证支持

#### 新增功能

- ✨ **Touch ID / Face ID 支持**
  - 无需手动输入密码，使用指纹或面部识别即可解密文件
  - 仅支持 macOS 系统
  - 与系统钥匙串完美集成

- 🔐 **密码管理**
  - 密码安全存储在 macOS 系统钥匙串
  - 硬件级加密保护
  - 每个文件独立的密码凭证
  - 支持通过"钥匙串访问"应用管理

- 🚀 **自动检测**
  - 解密时自动检测已保存的密码
  - 智能提示使用生物识别验证
  - 支持回退到手动输入密码

#### 新增文件

- `biometric_auth.py` - 生物识别认证核心模块
- `test_biometric.py` - 生物识别功能测试脚本
- `demo_biometric.py` - 功能演示脚本
- `BIOMETRIC_AUTH_GUIDE.md` - 详细使用指南
- `QUICKSTART_BIOMETRIC.md` - 快速入门指南

#### 改进

- 📝 更新 `cli_encrypt.py`
  - 集成 `BiometricPasswordManager`
  - 加密时询问是否保存密码
  - 解密时自动检测并使用生物识别

- 📦 更新依赖
  - 添加 `keyring >= 24.0.0`

- 📖 更新文档
  - README.md 添加生物识别功能说明
  - 添加使用示例和安全性说明

#### 技术细节

- 使用 `keyring` 库访问系统钥匙串
- 基于文件路径、inode 和大小生成唯一标识符
- macOS 钥匙串自动触发生物识别验证
- 支持 Touch ID 和 Face ID

#### 安全性

- 密码存储在系统钥匙串，与 Safari 密码同级安全
- 生物识别数据从不离开设备安全区域
- 支持随时删除已保存的密码凭证
- 不影响原有的密码输入方式

#### 使用示例

```bash
# 加密并保存密码
python3 cli_encrypt.py encrypt document.pdf
# 选择 'y' 保存到钥匙串

# 使用生物识别解密
python3 cli_encrypt.py decrypt document.pdf.encrypted
# 系统自动提示使用 Touch ID/Face ID
```

#### 兼容性

- ✅ macOS (Touch ID / Face ID)
- ⚠️ Windows / Linux - 继续使用传统密码输入

---

## v2.0 (之前版本)

### 核心功能

- ✅ 多算法支持：AES-256-GCM、ChaCha20-Poly1305
- ✅ 密钥派生：Argon2id、PBKDF2-HMAC-SHA512
- ✅ 自毁文件：过期时间、最大解密次数
- ✅ 流式加密：stdin/stdout 支持
- ✅ 抗暴力破解：自动锁定机制
- ✅ 元数据隐藏：文件名、大小加密
- ✅ 多线程加速：并行加密支持
- ✅ 大文件支持：分块处理
- ✅ 目录加密：整个目录打包加密
- ✅ 批量处理：通配符支持
- ✅ 进度显示：tqdm 进度条
- ✅ 交互模式：Shell 模式

---

## 路线图

### v2.2 (计划中)

- [ ] Windows Hello 支持
- [ ] Linux PAM 集成
- [ ] 密码强度可视化
- [ ] 加密文件元数据查看工具
- [ ] GUI 界面（可选）

### v2.3 (计划中)

- [ ] 云端密钥备份（可选）
- [ ] 多设备密钥同步
- [ ] 硬件密钥支持（YubiKey）
- [ ] 加密容器支持

---

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

仅供学习和个人使用。

