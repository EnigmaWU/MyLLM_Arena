#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行所有单元测试
"""

import unittest
import os
import sys

# 确保可以导入项目模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # 发现并运行所有测试
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 返回适当的退出码
    sys.exit(not result.wasSuccessful())
