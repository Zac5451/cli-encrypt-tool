#!/bin/bash
# 自动编译和混淆脚本
# 将 Python 代码编译成无法查看源代码的二进制文件

set -e

echo "=========================================="
echo "  文件管理工具 - 编译脚本"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查依赖
echo "检查依赖..."

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ 未找到 Python 3${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3${NC}"

# 检查 PyInstaller
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo -e "${YELLOW}⚠ PyInstaller 未安装，正在安装...${NC}"
    pip3 install pyinstaller
fi
echo -e "${GREEN}✓ PyInstaller${NC}"

# 可选：检查 pyarmor
PYARMOR_AVAILABLE=false
if python3 -c "import pyarmor" 2>/dev/null; then
    PYARMOR_AVAILABLE=true
    echo -e "${GREEN}✓ pyarmor (可选)${NC}"
else
    echo -e "${YELLOW}⚠ pyarmor 未安装 (可选，用于代码加密)${NC}"
    echo -e "${YELLOW}  安装命令: pip3 install pyarmor${NC}"
fi

echo ""

# 选择编译模式
echo "选择编译模式："
echo "  1) 基本编译（快速，推荐）"
echo "  2) 加密编译（需要 pyarmor，更安全）"
echo "  3) 多层混淆（最安全，需要 pyarmor）"
echo ""
read -p "请选择 (1-3): " mode

case $mode in
    1)
        MODE="basic"
        echo -e "${GREEN}选择：基本编译${NC}"
        ;;
    2)
        if [ "$PYARMOR_AVAILABLE" = false ]; then
            echo -e "${RED}✗ 需要安装 pyarmor: pip3 install pyarmor${NC}"
            exit 1
        fi
        MODE="encrypted"
        echo -e "${GREEN}选择：加密编译${NC}"
        ;;
    3)
        if [ "$PYARMOR_AVAILABLE" = false ]; then
            echo -e "${RED}✗ 需要安装 pyarmor: pip3 install pyarmor${NC}"
            exit 1
        fi
        MODE="obfuscated"
        echo -e "${GREEN}选择：多层混淆${NC}"
        ;;
    *)
        echo -e "${RED}✗ 无效选择${NC}"
        exit 1
        ;;
esac

echo ""

# 输入输出文件名
read -p "输出文件名 (默认: file_tools): " OUTPUT_NAME
OUTPUT_NAME=${OUTPUT_NAME:-file_tools}

echo ""
echo "=========================================="
echo "  开始编译"
echo "=========================================="
echo ""

# 清理旧文件
echo "清理旧文件..."
rm -rf build/ dist/ __pycache__/ *.spec
echo -e "${GREEN}✓ 清理完成${NC}"
echo ""

# 根据模式编译
if [ "$MODE" = "basic" ]; then
    # 基本编译
    echo "正在编译（基本模式）..."
    pyinstaller --onefile \
        --name "$OUTPUT_NAME" \
        --hidden-import=crypto_core \
        --hidden-import=steganography \
        --hidden-import=biometric_auth \
        --hidden-import=keyring \
        file_manager_obfuscated.py
    
elif [ "$MODE" = "encrypted" ]; then
    # 加密编译
    echo "步骤 1/2: 加密代码..."
    python3 -m pyarmor gen --output dist_encrypted file_manager_obfuscated.py
    echo -e "${GREEN}✓ 代码加密完成${NC}"
    
    echo "步骤 2/2: 编译..."
    pyinstaller --onefile \
        --name "$OUTPUT_NAME" \
        --hidden-import=crypto_core \
        --hidden-import=steganography \
        --hidden-import=biometric_auth \
        --hidden-import=keyring \
        dist_encrypted/file_manager_obfuscated.py
    
    # 清理临时文件
    rm -rf dist_encrypted/
    
elif [ "$MODE" = "obfuscated" ]; then
    # 多层混淆
    echo "步骤 1/3: 加密代码..."
    python3 -m pyarmor gen --output dist_encrypted file_manager_obfuscated.py
    echo -e "${GREEN}✓ 代码加密完成${NC}"
    
    echo "步骤 2/3: 编译..."
    pyinstaller --onefile \
        --name "$OUTPUT_NAME" \
        --hidden-import=crypto_core \
        --hidden-import=steganography \
        --hidden-import=biometric_auth \
        --hidden-import=keyring \
        --strip \
        dist_encrypted/file_manager_obfuscated.py
    echo -e "${GREEN}✓ 编译完成${NC}"
    
    echo "步骤 3/3: 优化..."
    # 移除调试信息
    strip dist/"$OUTPUT_NAME" 2>/dev/null || true
    
    # 清理临时文件
    rm -rf dist_encrypted/
fi

echo ""
echo "=========================================="
echo "  编译完成"
echo "=========================================="
echo ""

# 显示结果
if [ -f "dist/$OUTPUT_NAME" ]; then
    FILE_SIZE=$(du -h "dist/$OUTPUT_NAME" | cut -f1)
    echo -e "${GREEN}✓ 编译成功！${NC}"
    echo ""
    echo "输出文件: dist/$OUTPUT_NAME"
    echo "文件大小: $FILE_SIZE"
    echo ""
    
    # 测试
    echo "测试编译后的文件..."
    if ./dist/"$OUTPUT_NAME" --help &>/dev/null; then
        echo -e "${GREEN}✓ 文件可以正常运行${NC}"
    else
        echo -e "${YELLOW}⚠ 文件可能无法正常运行，请手动测试${NC}"
    fi
    echo ""
    
    # 使用说明
    echo "=========================================="
    echo "  使用说明"
    echo "=========================================="
    echo ""
    echo "1. 测试工具："
    echo "   ./dist/$OUTPUT_NAME list ."
    echo ""
    echo "2. 移动到系统目录（可选）："
    echo "   sudo cp dist/$OUTPUT_NAME /usr/local/bin/"
    echo ""
    echo "3. 清理源代码（重要！）："
    echo "   rm file_manager_obfuscated.py"
    echo "   rm -rf build/ __pycache__/ *.spec"
    echo ""
    echo "4. 使用工具："
    echo "   $OUTPUT_NAME backup file.pdf --secure"
    echo ""
    
    # 询问是否清理
    read -p "是否现在清理源代码和临时文件？(y/N): " CLEAN
    if [ "$CLEAN" = "y" ] || [ "$CLEAN" = "Y" ]; then
        echo ""
        echo "清理中..."
        rm -rf build/ __pycache__/ *.spec
        echo -e "${GREEN}✓ 临时文件已清理${NC}"
        echo ""
        echo -e "${YELLOW}注意：源代码 file_manager_obfuscated.py 未删除${NC}"
        echo "如需删除，请手动执行："
        echo "  rm file_manager_obfuscated.py"
    fi
    
else
    echo -e "${RED}✗ 编译失败${NC}"
    exit 1
fi

echo ""
echo "=========================================="
echo "  完成"
echo "=========================================="

