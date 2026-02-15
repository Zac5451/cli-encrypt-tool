# CLI 加密工具 - 手动测试清单

## 测试前准备

```bash
cd /path/to/cli-encrypt-tool
mkdir manual_test && cd manual_test
echo "test content" > test.txt
```

---

## 功能测试清单

### 1. 基础功能 ⬜

- [ ] **加密**: `python3 cli_encrypt.py encrypt test.txt -o test.enc -p "Test123!" -f`
- [ ] **解密**: `python3 cli_encrypt.py decrypt test.enc -o test.dec -p "Test123!" -f`
- [ ] **验证内容**: `diff test.txt test.dec` (应该无输出)

### 2. 算法测试 ⬜

- [ ] **ChaCha20**: `python3 cli_encrypt.py encrypt test.txt -o test.chacha -a chacha20 -p "Test123!" -f`
- [ ] **解密ChaCha20**: `python3 cli_encrypt.py decrypt test.chacha -o test.chacha.dec -p "Test123!" -f`

### 3. 自毁功能 ⬜

- [ ] **过期时间**: `python3 cli_encrypt.py encrypt test.txt -o test.exp -e 7 -p "Test123!" -f`
- [ ] **解密1次**: `python3 cli_encrypt.py encrypt test.txt -o test.max -m 1 -p "Test123!" -f`
- [ ] **验证次数限制**: 解密2次，第二次应该失败

### 4. 流式加密 ⬜

- [ ] **流加密**: `echo "hello" | python3 cli_encrypt.py stream-encrypt -p "Test123!" > test.stream`
- [ ] **流解密**: `python3 cli_encrypt.py stream-decrypt -p "Test123!" < test.stream`

### 5. 目录操作 ⬜

- [ ] **创建测试目录**: `mkdir folder && echo "a" > folder/a.txt && echo "b" > folder/b.txt`
- [ ] **加密目录**: `python3 cli_encrypt.py encrypt-dir folder -o folder.vcdir -p "Test123!" -f`
- [ ] **解密目录**: `python3 cli_encrypt.py decrypt-dir folder.vcdir -o folder_restored -p "Test123!" -f`
- [ ] **验证**: `diff -r folder folder_restored`

### 6. 批量操作 ⬜

- [ ] **批量加密**: `python3 cli_encrypt.py batch-encrypt "*.txt" -o batch_enc/ -p "Test123!"`
- [ ] **批量解密**: `python3 cli_encrypt.py batch-decrypt "*.enc" -o batch_dec/ -p "Test123!"`

### 7. 预览功能 ⬜

- [ ] **Dry-run**: `python3 cli_encrypt.py dry-run test.txt`

### 8. 交互模式 ⬜

- [ ] **启动**: `python3 cli_encrypt.py interactive`
- [ ] **测试命令** (在交互界面输入):
    ```
    enc test.txt
    (输入密码)
    (确认密码)
    
    dec test.txt.encrypted
    (输入密码)
    
    status
    
    exit
    ```
- [ ] **验证**: 检查文件是否正确生成/解密

### 9. 错误处理 ⬜

- [ ] **错误密码**: `python3 cli_encrypt.py decrypt test.enc -p "WrongPass"` (应该失败)
- [ ] **不存在文件**: `python3 cli_encrypt.py encrypt notexist.txt -p "Pass"` (应该报错)
- [ ] **损坏文件**: 创建损坏的 enc 文件，解密应该失败

### 10. 特殊内容 ⬜

- [ ] **中文**: `echo "中文测试" > cn.txt && 加密 && 解密 && 验证`
- [ ] **Emoji**: `echo "🎉🎊" > emoji.txt && 加密 && 解密 && 验证`
- [ ] **二进制**: `dd if=/dev/urandom of=bin.dat bs=1024 count=1 && 加密 && 解密 && 验证`

---

## 快速验证脚本

如果只想快速验证核心功能是否正常工作，运行：

```bash
python3 manual_test.py
```

这将自动执行大部分测试，但仍需手动验证交互模式。

---

## 验收标准

所有项目都 ✅ 通过后，功能才算完整实现。

发现 ❌ 项目请记录：
- 命令
- 预期行为
- 实际行为
