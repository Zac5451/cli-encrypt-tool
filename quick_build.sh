#!/bin/bash
# 快速编译脚本 - 基本模式（不需要交互）

echo "=========================================="
echo "  快速编译 - 基本模式"
echo "=========================================="
echo ""

# 清理
echo "清理旧文件..."
rm -rf build/ dist/ __pycache__/ *.spec
echo "✓ 清理完成"
echo ""

# 编译
echo "正在编译..."
TMPDIR=/tmp python3 -m PyInstaller --onefile \
    --name FileManager \
    --hidden-import=crypto_core \
    --hidden-import=steganography \
    --hidden-import=biometric_auth \
    --hidden-import=keyring \
    --workpath /tmp/build \
    --distpath ./dist \
    file_manager_obfuscated.py

echo ""
if [ -f "dist/FileManager" ]; then
    echo "=========================================="
    echo "  ✓ 编译成功！"
    echo "=========================================="
    echo ""
    echo "输出文件: dist/FileManager"
    echo "文件大小: $(du -h dist/FileManager | cut -f1)"
    echo ""
    echo "测试运行:"
    echo "  ./dist/FileManager --help"
    echo ""
    echo "使用示例:"
    echo "  ./dist/FileManager backup file.pdf --secure"
    echo ""
else
    echo "✗ 编译失败"
    exit 1
fi

