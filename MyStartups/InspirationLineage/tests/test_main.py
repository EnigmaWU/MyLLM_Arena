#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主程序流程的单元测试
"""

import unittest
import os
import tempfile
import sys
from unittest.mock import patch, MagicMock
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import MyInspirationLineage

class TestMainProgram(unittest.TestCase):
    """测试主程序流程"""
    
    def setUp(self):
        """测试前的设置"""
        # 创建临时目录和测试文件
        self.test_dir = tempfile.mkdtemp()
        self.test_pdf = os.path.join(self.test_dir, "test.pdf")
        
        # 创建测试PDF文件
        with open(self.test_pdf, 'wb') as f:
            f.write(b'dummy pdf content')
    
    def tearDown(self):
        """测试后的清理"""
        import shutil
        shutil.rmtree(self.test_dir)
    
    @patch('MyInspirationLineage.process_pdf')
    def test_main_with_pdf(self, mock_process_pdf):
        """测试使用PDF文件路径的主流程"""
        mock_process_pdf.return_value = True
        
        # 模拟命令行参数
        test_args = ['MyInspirationLineage.py', '--PDF', self.test_pdf, '--ConceptName', '机器学习']
        with patch('sys.argv', test_args):
            result = MyInspirationLineage.main()
        
        # 验证结果
        self.assertEqual(result, 0)
        mock_process_pdf.assert_called_once_with(self.test_pdf, '机器学习', 1, False)
    
    @patch('MyInspirationLineage.process_url')
    def test_main_with_url(self, mock_process_url):
        """测试使用URL的主流程"""
        mock_process_url.return_value = True
        
        # 模拟命令行参数
        test_url = 'https://arxiv.org/abs/2501.12948'
        test_args = ['MyInspirationLineage.py', '--URL', test_url, '--ConceptName', '机器学习']
        with patch('sys.argv', test_args):
            result = MyInspirationLineage.main()
        
        # 验证结果
        self.assertEqual(result, 0)
        mock_process_url.assert_called_once_with(test_url, '机器学习', 1, False)
    
    @patch('MyInspirationLineage.process_pdf')
    def test_main_with_depth(self, mock_process_pdf):
        """测试带深度参数的主流程"""
        mock_process_pdf.return_value = True
        
        # 模拟命令行参数
        test_args = ['MyInspirationLineage.py', '--PDF', self.test_pdf, '--ConceptName', '机器学习', '--Depth', '3']
        with patch('sys.argv', test_args):
            result = MyInspirationLineage.main()
        
        # 验证结果
        self.assertEqual(result, 0)
        mock_process_pdf.assert_called_once_with(self.test_pdf, '机器学习', 3, False)
    
    @patch('MyInspirationLineage.process_pdf')
    def test_main_with_debug(self, mock_process_pdf):
        """测试带调试参数的主流程"""
        mock_process_pdf.return_value = True
        
        # 模拟命令行参数
        test_args = ['MyInspirationLineage.py', '--PDF', self.test_pdf, '--ConceptName', '机器学习', '--Debug']
        with patch('sys.argv', test_args):
            result = MyInspirationLineage.main()
        
        # 验证结果
        self.assertEqual(result, 0)
        mock_process_pdf.assert_called_once_with(self.test_pdf, '机器学习', 1, True)
    
    @patch('MyInspirationLineage.extract_text_from_pdf')
    @patch('MyInspirationLineage.analyze_concept')
    def test_process_pdf(self, mock_analyze, mock_extract):
        """测试PDF处理流程"""
        # 模拟依赖函数
        mock_extract.return_value = "测试文本内容"
        mock_analyze.return_value = "分析结果"
        
        # 调用被测函数
        result = MyInspirationLineage.process_pdf(self.test_pdf, "机器学习", 1)
        
        # 验证结果
        self.assertTrue(result)
        mock_extract.assert_called_once_with(self.test_pdf, False)
        mock_analyze.assert_called_once_with("测试文本内容", "机器学习", 1, False)
    
    @patch('MyInspirationLineage.download_pdf_from_url')
    @patch('MyInspirationLineage.process_pdf')
    def test_process_url(self, mock_process_pdf, mock_download):
        """测试URL处理流程"""
        # 模拟依赖函数
        test_url = 'https://arxiv.org/abs/2501.12948'
        mock_download.return_value = self.test_pdf
        mock_process_pdf.return_value = True
        
        # 调用被测函数
        result = MyInspirationLineage.process_url(test_url, "机器学习", 1)
        
        # 验证结果
        self.assertTrue(result)
        mock_download.assert_called_once_with(test_url, debug=False)
        mock_process_pdf.assert_called_once_with(self.test_pdf, "机器学习", 1, False)


if __name__ == "__main__":
    unittest.main()
