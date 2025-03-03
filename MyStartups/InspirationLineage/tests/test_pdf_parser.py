#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF解析模块的单元测试
"""

import unittest
import os
import tempfile
from unittest.mock import patch, MagicMock
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.pdf_parser import extract_text_from_pdf

class TestPDFParser(unittest.TestCase):
    """测试PDF解析模块的功能"""
    
    def setUp(self):
        """测试前的设置"""
        # 创建一个临时目录来存放测试文件
        self.test_dir = tempfile.mkdtemp()
        
        # 创建一个空的测试PDF文件路径（不会实际创建文件）
        self.empty_pdf_path = os.path.join(self.test_dir, "empty.pdf")
        
        # 不存在的PDF文件路径
        self.nonexistent_pdf_path = os.path.join(self.test_dir, "nonexistent.pdf")
    
    def tearDown(self):
        """测试后的清理"""
        # 清理临时目录
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_nonexistent_file(self):
        """测试处理不存在的PDF文件"""
        result = extract_text_from_pdf(self.nonexistent_pdf_path)
        self.assertEqual(result, "")
        
        # 带调试信息
        result = extract_text_from_pdf(self.nonexistent_pdf_path, debug=True)
        self.assertEqual(result, "")
    
    @patch('PyPDF2.PdfReader')
    def test_empty_pdf(self, mock_pdf_reader):
        """测试空PDF文件的处理"""
        # 模拟空PDF文件
        mock_reader_instance = MagicMock()
        mock_reader_instance.pages = []
        mock_pdf_reader.return_value = mock_reader_instance
        
        # 创建一个空文件用于测试
        with open(self.empty_pdf_path, 'wb') as f:
            f.write(b'')
            
        result = extract_text_from_pdf(self.empty_pdf_path)
        self.assertEqual(result, "")
    
    @patch('PyPDF2.PdfReader')
    def test_valid_pdf(self, mock_pdf_reader):
        """测试有效PDF文件的文本提取"""
        # 模拟有效PDF文件
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "This is page 1 content."
        
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "This is page 2 content."
        
        mock_reader_instance = MagicMock()
        mock_reader_instance.pages = [mock_page1, mock_page2]
        mock_pdf_reader.return_value = mock_reader_instance
        
        # 创建一个测试文件路径
        test_pdf_path = os.path.join(self.test_dir, "test.pdf")
        with open(test_pdf_path, 'wb') as f:
            f.write(b'dummy pdf content')
            
        result = extract_text_from_pdf(test_pdf_path)
        expected = "This is page 1 content.\n\nThis is page 2 content.\n\n"
        self.assertEqual(result, expected)
    
    @patch('PyPDF2.PdfReader')
    def test_pdf_with_empty_pages(self, mock_pdf_reader):
        """测试包含空页面的PDF文件处理"""
        # 模拟包含空页面的PDF文件
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "This is page 1 content."
        
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = ""  # 空页面
        
        mock_page3 = MagicMock()
        mock_page3.extract_text.return_value = "This is page 3 content."
        
        mock_reader_instance = MagicMock()
        mock_reader_instance.pages = [mock_page1, mock_page2, mock_page3]
        mock_pdf_reader.return_value = mock_reader_instance
        
        # 创建一个测试文件路径
        test_pdf_path = os.path.join(self.test_dir, "test_with_empty_page.pdf")
        with open(test_pdf_path, 'wb') as f:
            f.write(b'dummy pdf content')
            
        result = extract_text_from_pdf(test_pdf_path)
        expected = "This is page 1 content.\n\n\n\nThis is page 3 content.\n\n"
        self.assertEqual(result, expected)
    
    @patch('PyPDF2.PdfReader')
    def test_pdf_processing_exception(self, mock_pdf_reader):
        """测试PDF处理异常"""
        # 模拟处理PDF时抛出异常
        mock_pdf_reader.side_effect = Exception("PDF processing error")
        
        # 创建一个测试文件路径
        test_pdf_path = os.path.join(self.test_dir, "error.pdf")
        with open(test_pdf_path, 'wb') as f:
            f.write(b'error pdf content')
        
        result = extract_text_from_pdf(test_pdf_path)
        self.assertEqual(result, "")
        
        # 带调试信息
        result = extract_text_from_pdf(test_pdf_path, debug=True)
        self.assertEqual(result, "")


if __name__ == "__main__":
    unittest.main()
