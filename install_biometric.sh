#!/bin/bash
# 生物识别功能安装脚本

echo "=========================================="
echo "  CLI 加密工具 - 生物识别功能安装"
echo "=========================================="
echo ""

# 检查操作系统
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "⚠️  警告：生物识别功能仅支持 macOS"
    echo "   您仍然可以使用传统的密码输入方式"
    echo ""
    read -p "是否继续安装其他依赖？(y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

# 检查 Python
echo "检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    echo "✗ 未找到 Python 3"
    echo "  请先安装 Python 3: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✓ Python 版本: $PYTHON_VERSION"
echo ""

# 检查 pip
echo "检查 pip..."
if ! command -v pip3 &> /dev/null; then
    echo "✗ 未找到 pip3"
    echo "  请先安装 pip"
    exit 1
fi
echo "✓ pip 已安装"
echo ""

# 安装依赖
echo "安装依赖包..."
echo "----------------------------------------"

pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ 依赖安装成功"
else
    echo ""
    echo "✗ 依赖安装失败"
    exit 1
fi

echo ""
echo "=========================================="
echo "  安装完成！"
echo "=========================================="
echo ""

# 检查生物识别可用性
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "测试生物识别功能..."
    python3 -c "from biometric_auth import BiometricAuth; print('✓ 生物识别可用' if BiometricAuth.is_available() else '✗ 生物识别不可用')"
    echo ""
fi

echo "快速开始："
echo "  1. 加密文件:"
echo "     python3 cli_encrypt.py encrypt myfile.pdf"
echo ""
echo "  2. 解密文件:"
echo "     python3 cli_encrypt.py decrypt myfile.pdf.encrypted"
echo ""

if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "  3. 使用生物识别:"
    echo "     - 加密时选择保存密码到钥匙串"
    echo "     - 解密时使用 Touch ID/Face ID 验证"
    echo ""
fi

echo "查看文档："
echo "  - README.md - 完整使用说明"
echo "  - QUICKSTART_BIOMETRIC.md - 生物识别快速入门"
echo "  - BIOMETRIC_AUTH_GUIDE.md - 详细指南"
echo ""

echo "运行测试："
echo "  python3 test_biometric.py"
echo ""

echo "查看演示："
echo "  python3 demo_biometric.py"
echo ""

echo "=========================================="
echo "  享受无密码的加密体验！🎉"
echo "=========================================="

