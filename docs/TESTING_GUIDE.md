# 自动化测试指南

## 概述

本项目包含完整的自动化测试体系，包括：
- **单元测试**：测试核心加密功能
- **边界测试**：测试极端情况和边界条件
- **E2E 测试**：端到端测试，模拟真实用户场景
- **性能测试**：测试加密/解密性能
- **覆盖率分析**：代码覆盖率报告

## 快速开始

### 1. 安装测试依赖

```bash
pip install -r requirements.txt
pip install pytest pytest-cov pytest-timeout hypothesis
```

### 2. 运行所有测试

```bash
# 完整测试（推荐）
python auto_test.py

# 快速测试（仅单元测试）
python auto_test.py --quick

# 仅 E2E 测试
python auto_test.py --e2e-only

# 仅覆盖率报告
python auto_test.py --coverage
```

### 3. 运行单个测试套件

```bash
# 单元测试
python -m pytest test_full.py -v

# 边界测试
python -m pytest test_boundary.py -v

# E2E 测试
python test_e2e.py

# 属性测试
python -m pytest test_properties.py -v
```

## 测试套件说明

### 1. 单元测试 (test_full.py)

测试核心加密功能的各个模块：

- **基础加解密**
  - 简单文本加密解密
  - 二进制数据加密解密
  - 中文内容加密解密
  - Emoji 内容加密解密
  - 空文件处理
  - 单字节文件处理

- **加密算法**
  - AES-256-GCM
  - ChaCha20-Poly1305
  - PBKDF2 密钥派生
  - Argon2id 密钥派生

- **自毁功能**
  - 过期时间
  - 最大解密次数

- **流式加密**
  - 流式加密解密
  - 中文流式加密
  - 空数据流式加密

- **批量操作**
  - 批量加密
  - 批量解密
  - 部分失败处理

- **安全功能**
  - 错误密码拒绝
  - 暴力破解保护
  - 文件完整性验证
  - 密码强度检查

**运行方式：**
```bash
python -m pytest test_full.py -v --tb=short
```

### 2. 边界测试 (test_boundary.py)

测试极端情况和边界条件：

- 超大文件（100MB+）
- 超长密码
- 特殊字符密码
- 损坏的加密文件
- 并发操作
- 内存限制

**运行方式：**
```bash
python -m pytest test_boundary.py -v --timeout=120
```

### 3. E2E 测试 (test_e2e.py)

端到端测试，模拟真实用户使用场景：

#### 基础功能测试
- ✓ 基本加密解密流程
- ✓ 错误密码拒绝
- ✓ 帮助命令
- ✓ 不存在文件处理

#### 内容类型测试
- ✓ 中文内容加密解密
- ✓ 空文件处理
- ✓ Emoji 内容处理
- ✓ 大文件加密（10MB）

#### 加密算法测试
- ✓ AES-256-GCM 算法
- ✓ ChaCha20-Poly1305 算法
- ✓ 流式加密解密

#### 高级功能测试
- ✓ 强制覆盖文件
- ✓ 加密后删除原文件
- ✓ 预览模式
- ✓ 批量加密
- ✓ 详细输出模式
- ✓ 多线程加密

#### 边界情况测试
- ✓ 特殊字符文件名
- ✓ 密码强度检查
- ✓ 文件完整性验证

**运行方式：**
```bash
python test_e2e.py
```

**输出示例：**
```
==============================================================
  CLI 加密工具 E2E 测试套件
==============================================================

📋 基础功能测试
------------------------------------------------------------
✓ PASS 基本加密
✓ PASS 基本解密
✓ PASS 错误密码拒绝
✓ PASS 帮助命令

📝 内容类型测试
------------------------------------------------------------
✓ PASS 中文内容加密解密
✓ PASS 空文件加密解密
✓ PASS Emoji 内容处理
✓ PASS 大文件加密解密

==============================================================
  测试总结
==============================================================

总计: 25 个测试
✓ 通过: 23
✗ 失败: 2
⊘ 跳过: 0

通过率: 92.0%
```

### 4. 属性测试 (test_properties.py)

使用 Hypothesis 进行基于属性的测试：

- 随机数据加密解密
- 随机密码测试
- 边界值测试

**运行方式：**
```bash
python -m pytest test_properties.py -v --hypothesis-show-statistics
```

### 5. 自动化测试 (auto_test.py)

整合所有测试的主控脚本：

**功能：**
1. 自动检查和安装依赖
2. 语法检查
3. 运行所有测试套件
4. 生成覆盖率报告
5. 性能测试
6. 生成 JSON 测试报告

**运行方式：**
```bash
# 完整测试
python auto_test.py

# 快速测试
python auto_test.py --quick

# 仅 E2E 测试
python auto_test.py --e2e-only
```

**输出示例：**
```
╔═══════════════════════════════════════════════════════════════════╗
║           CLI 加密工具 - 自动化测试套件                          ║
╚═══════════════════════════════════════════════════════════════════╝

======================================================================
  检查依赖
======================================================================

✓ Python 3 已安装
✓ pytest 已安装

======================================================================
  代码语法检查
======================================================================

✓ cli_encrypt.py 语法正确
✓ crypto_core.py 语法正确
✓ biometric_auth.py 语法正确

======================================================================
  单元测试
======================================================================

▶ 单元测试...
✓ 单元测试 完成 (12.34s)

======================================================================
  E2E 端到端测试
======================================================================

▶ E2E 测试...
✓ E2E 测试 完成 (45.67s)

======================================================================
  性能测试
======================================================================

✓ 加密 5MB 文件耗时: 0.85s
✓ 解密 5MB 文件耗时: 0.72s

======================================================================
  测试总结
======================================================================

总测试数: 5
✓ 通过: 5
✗ 失败: 0
总耗时: 89.23s

性能指标:
  加密速度: 5.88 MB/s
  解密速度: 6.94 MB/s

🎉 所有测试通过！

总运行时间: 95.45s
```

## 覆盖率报告

### 生成覆盖率报告

```bash
# 生成 HTML 报告
python -m pytest test_full.py test_boundary.py \
  --cov=crypto_core \
  --cov=cli_encrypt \
  --cov-report=html \
  --cov-report=term

# 查看报告
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### 覆盖率目标

- **核心模块 (crypto_core.py)**: ≥ 80%
- **CLI 工具 (cli_encrypt.py)**: ≥ 70%
- **辅助模块**: ≥ 60%

## CI/CD 集成

### GitHub Actions

项目已配置 GitHub Actions 自动化测试：

**触发条件：**
- Push 到 main/develop 分支
- Pull Request 到 main 分支
- 每天凌晨 2 点定时运行

**测试矩阵：**
- 操作系统：Ubuntu, macOS
- Python 版本：3.8, 3.9, 3.10, 3.11

**工作流程：**
1. 语法检查
2. 单元测试
3. 边界测试
4. E2E 测试
5. 覆盖率报告
6. 性能测试
7. 安全扫描
8. 构建可执行文件

**查看结果：**
访问 GitHub 仓库的 Actions 标签页查看测试结果。

## 性能基准

### 加密性能

| 文件大小 | 加密时间 | 速度 |
|---------|---------|------|
| 1 MB    | ~0.15s  | ~6.7 MB/s |
| 10 MB   | ~1.5s   | ~6.7 MB/s |
| 100 MB  | ~15s    | ~6.7 MB/s |

### 解密性能

| 文件大小 | 解密时间 | 速度 |
|---------|---------|------|
| 1 MB    | ~0.13s  | ~7.7 MB/s |
| 10 MB   | ~1.3s   | ~7.7 MB/s |
| 100 MB  | ~13s    | ~7.7 MB/s |

*注：性能数据基于 MacBook Pro M1，实际性能可能因硬件而异*

## 测试最佳实践

### 1. 运行测试前

```bash
# 确保代码是最新的
git pull

# 安装/更新依赖
pip install -r requirements.txt --upgrade

# 清理旧的测试文件
rm -rf htmlcov/ .pytest_cache/ test_report_*.json
```

### 2. 开发时测试

```bash
# 快速测试（开发时）
python auto_test.py --quick

# 测试特定功能
python -m pytest test_full.py::TestCryptoBasic::test_encrypt_decrypt_simple_text -v

# 监视模式（需要 pytest-watch）
ptw -- test_full.py
```

### 3. 提交前测试

```bash
# 完整测试
python auto_test.py

# 检查覆盖率
python auto_test.py --coverage
```

### 4. 调试失败的测试

```bash
# 显示详细输出
python -m pytest test_full.py -vv --tb=long

# 在第一个失败时停止
python -m pytest test_full.py -x

# 运行上次失败的测试
python -m pytest test_full.py --lf

# 进入调试器
python -m pytest test_full.py --pdb
```

## 添加新测试

### 1. 添加单元测试

在 `test_full.py` 中添加新的测试类或方法：

```python
class TestNewFeature:
    """新功能测试"""
    
    def test_new_functionality(self):
        """测试：新功能描述"""
        # 准备
        input_data = "test data"
        
        # 执行
        result = new_function(input_data)
        
        # 断言
        assert result == expected_output
```

### 2. 添加 E2E 测试

在 `test_e2e.py` 的 `E2ETestRunner` 类中添加新方法：

```python
def test_new_scenario(self):
    """测试：新场景描述"""
    test_file = self.create_test_file("test.txt", "content")
    
    # 运行 CLI 命令
    returncode, stdout, stderr = self.run_cli([
        'command', test_file, '-p', 'password'
    ])
    
    # 验证结果
    passed = returncode == 0
    self.log_test("新场景测试", passed)
```

然后在 `run_all_tests()` 方法中调用：

```python
def run_all_tests(self):
    # ... 其他测试 ...
    self.test_new_scenario()
```

## 常见问题

### Q: 测试失败怎么办？

A: 
1. 查看详细错误信息：`python -m pytest test_full.py -vv`
2. 检查是否是环境问题（依赖版本、操作系统）
3. 查看测试报告：`test_report_*.json`
4. 运行单个失败的测试进行调试

### Q: 如何跳过某些测试？

A:
```python
import pytest

@pytest.mark.skip(reason="暂时跳过")
def test_something():
    pass

@pytest.mark.skipif(sys.platform == 'win32', reason="Windows 不支持")
def test_unix_only():
    pass
```

### Q: 测试运行太慢？

A:
1. 使用快速模式：`python auto_test.py --quick`
2. 并行运行：`pytest -n auto` (需要 pytest-xdist)
3. 只运行修改相关的测试

### Q: 如何测试生物识别功能？

A: 生物识别功能需要在 macOS 上手动测试，自动化测试会跳过这部分。

## 测试报告

测试完成后会生成以下报告：

1. **JSON 报告**: `test_report_YYYYMMDD_HHMMSS.json`
   - 包含所有测试结果
   - 性能数据
   - 错误信息

2. **HTML 覆盖率报告**: `htmlcov/index.html`
   - 代码覆盖率详情
   - 未覆盖的代码行
   - 分支覆盖率

3. **终端输出**: 实时测试进度和结果

## 贡献指南

添加新功能时，请确保：

1. ✅ 编写对应的单元测试
2. ✅ 添加 E2E 测试场景
3. ✅ 更新测试文档
4. ✅ 确保所有测试通过
5. ✅ 代码覆盖率不降低

## 联系方式

如有问题或建议，请：
- 提交 Issue
- 发起 Pull Request
- 查看项目文档

---

**最后更新**: 2024-02-15

