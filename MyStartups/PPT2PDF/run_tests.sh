#!/bin/bash

# 运行单元测试的脚本
echo "正在运行 MyPPT2PDF 单元测试..."
python3 -m unittest test_MyPPT2PDF.py

# 检查测试结果
if [ $? -eq 0 ]; then
    echo "✅ 所有测试通过"
else
    echo "❌ 测试失败"
    exit 1
fi
