#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
单元测试 MyPPT2PDF.py
"""

import os
import sys
import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from pathlib import Path

# 导入被测试模块
import MyPPT2PDF

class TestMyPPT2PDF(unittest.TestCase):
    """测试 MyPPT2PDF.py 的功能"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        
        # 创建测试用的PPT文件（仅为空文件用于测试路径处理）
        self.test_ppt_path = os.path.join(self.temp_dir, "test.pptx")
        Path(self.test_ppt_path).touch()
        
        # 创建测试用的输出路径
        self.test_output_path = os.path.join(self.temp_dir, "output.pdf")
    
    def tearDown(self):
        """测试后清理"""
        # 删除临时目录
        shutil.rmtree(self.temp_dir)
    
    def test_file_exists(self):
        """测试文件存在性检查"""
        # 存在的文件
        self.assertTrue(MyPPT2PDF.check_file_exists(self.test_ppt_path))
        
        # 不存在的文件
        nonexistent_file = os.path.join(self.temp_dir, "nonexistent.pptx")
        self.assertFalse(MyPPT2PDF.check_file_exists(nonexistent_file))
    
    def test_file_extension(self):
        """测试文件扩展名检查"""
        # 有效的扩展名
        self.assertTrue(MyPPT2PDF.check_file_extension(self.test_ppt_path, [".ppt", ".pptx"]))
        
        # 无效的扩展名
        invalid_file = os.path.join(self.temp_dir, "test.txt")
        Path(invalid_file).touch()
        self.assertFalse(MyPPT2PDF.check_file_extension(invalid_file, [".ppt", ".pptx"]))
    
    @patch('argparse.ArgumentParser.parse_args')
    def test_parse_arguments(self, mock_parse_args):
        """测试命令行参数解析"""
        # 模拟正常参数
        mock_args = MagicMock()
        mock_args.PPT = self.test_ppt_path
        mock_args.Output = self.test_output_path
        mock_args.Split = False
        mock_args.Help = False
        mock_args.Version = False
        mock_args.Debug = False
        mock_parse_args.return_value = mock_args
        
        args = MyPPT2PDF.parse_arguments()
        
        self.assertEqual(args.PPT, self.test_ppt_path)
        self.assertEqual(args.Output, self.test_output_path)
        self.assertFalse(args.Split)
        self.assertFalse(args.Debug)
    
    @patch('platform.system')
    @patch('MyPPT2PDF.convert_ppt_to_pdf_windows')
    @patch('MyPPT2PDF.convert_ppt_to_pdf_mac')
    @patch('MyPPT2PDF.convert_ppt_to_pdf_linux')
    def test_convert_ppt_to_pdf_platform(self, mock_linux, mock_mac, mock_windows, mock_platform):
        """测试平台检测和相应转换函数的调用"""
        # 测试Windows平台
        mock_platform.return_value = "Windows"
        mock_windows.return_value = True
        
        result = MyPPT2PDF.convert_ppt_to_pdf(self.test_ppt_path, self.test_output_path, False)
        self.assertTrue(result)
        mock_windows.assert_called_once_with(self.test_ppt_path, self.test_output_path, False)
        mock_mac.assert_not_called()
        mock_linux.assert_not_called()
        
        # 重置模拟对象
        mock_windows.reset_mock()
        mock_mac.reset_mock()
        mock_linux.reset_mock()
        
        # 测试Mac平台
        mock_platform.return_value = "Darwin"
        mock_mac.return_value = True
        
        result = MyPPT2PDF.convert_ppt_to_pdf(self.test_ppt_path, self.test_output_path, False)
        self.assertTrue(result)
        mock_mac.assert_called_once_with(self.test_ppt_path, self.test_output_path, False)
        mock_windows.assert_not_called()
        mock_linux.assert_not_called()
        
        # 重置模拟对象
        mock_windows.reset_mock()
        mock_mac.reset_mock()
        mock_linux.reset_mock()
        
        # 测试Linux平台
        mock_platform.return_value = "Linux"
        mock_linux.return_value = True
        
        result = MyPPT2PDF.convert_ppt_to_pdf(self.test_ppt_path, self.test_output_path, False)
        self.assertTrue(result)
        mock_linux.assert_called_once_with(self.test_ppt_path, self.test_output_path, False)
        mock_windows.assert_not_called()
        mock_mac.assert_not_called()
        
        # 测试不支持的平台
        mock_platform.return_value = "Unsupported"
        result = MyPPT2PDF.convert_ppt_to_pdf(self.test_ppt_path, self.test_output_path, False)
        self.assertFalse(result)
    
    @patch('os.path.exists')
    @patch('os.makedirs')
    @patch('MyPPT2PDF.convert_ppt_to_pdf')
    def test_main_successful_conversion(self, mock_convert, mock_makedirs, mock_exists):
        """测试主函数成功执行流程"""
        # 设置模拟行为
        mock_exists.return_value = True
        mock_convert.return_value = True
        
        # 模拟命令行参数
        test_args = ['MyPPT2PDF.py', '--PPT', self.test_ppt_path, '--Output', self.test_output_path]
        with patch.object(sys, 'argv', test_args):
            result = MyPPT2PDF.main()
        
        self.assertEqual(result, 0)  # 成功执行返回0
        mock_convert.assert_called_once()
    
    @patch('os.path.exists')
    def test_main_file_not_exists(self, mock_exists):
        """测试主函数处理不存在的输入文件"""
        # 模拟文件不存在
        mock_exists.return_value = False
        
        # 模拟命令行参数
        test_args = ['MyPPT2PDF.py', '--PPT', self.test_ppt_path, '--Output', self.test_output_path]
        with patch.object(sys, 'argv', test_args):
            result = MyPPT2PDF.main()
        
        self.assertEqual(result, 1)  # 错误执行返回1


class TestIntegration(unittest.TestCase):
    """集成测试类（模拟实际转换过程但不执行真实的转换）"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        
        # 创建测试用的PPT文件路径（但不实际创建文件）
        self.test_ppt_path = os.path.join(self.temp_dir, "test.pptx")
        
        # 设置输出路径
        self.test_output_path = os.path.join(self.temp_dir, "output.pdf")
    
    def tearDown(self):
        """测试后清理"""
        # 删除临时目录
        shutil.rmtree(self.temp_dir)
    
    @unittest.skip("这是一个需要真实环境的集成测试示例")
    def test_real_conversion(self):
        """真实环境测试（需要实际的PPT文件和转换环境）"""
        # 此测试默认被跳过，需要在实际环境中手动启用并提供真实文件
        # 为了运行此测试：
        # 1. 移除 @unittest.skip 装饰器
        # 2. 将 self.test_ppt_path 指向真实的PPT文件
        # 3. 确保系统中安装了所需的转换应用程序
        
        # 创建空文件，仅用于演示（实际测试时需要真实PPT文件）
        Path(self.test_ppt_path).touch()
        
        # 执行转换
        result = MyPPT2PDF.convert_ppt_to_pdf(self.test_ppt_path, self.test_output_path, False)
        
        # 验证转换结果
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.test_output_path))


if __name__ == '__main__':
    unittest.main()
