#!/bin/bash
# 快速安装和测试脚本

echo "================================"
echo "CLI 加密工具 - 安装脚本"
echo "================================"
echo ""

# 检查 Python 版本
echo "检查 Python 版本..."
python3 --version

if [ $? -ne 0 ]; then
    echo "错误: 未找到 Python 3"
    exit 1
fi

echo ""
echo "安装依赖包..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "警告: 部分依赖安装失败，尝试继续..."
fi

echo ""
echo "================================"
echo "运行测试..."
echo "================================"
echo ""

python3 test_crypto.py

if [ $? -eq 0 ]; then
    echo ""
    echo "================================"
    echo "✓ 安装和测试完成！"
    echo "================================"
    echo ""
    echo "使用方法："
    echo "  加密: python3 cli_encrypt.py encrypt <文件>"
    echo "  解密: python3 cli_encrypt.py decrypt <文件>"
    echo "  帮助: python3 cli_encrypt.py --help"
    echo ""
else
    echo ""
    echo "警告: 部分测试失败，但工具可能仍然可用"
    echo ""
fi

