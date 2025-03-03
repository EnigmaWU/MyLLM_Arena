#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
URL解析模块的单元测试
"""

import unittest
import os
import tempfile
from unittest.mock import patch, MagicMock
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.url_parser import is_arxiv_url, extract_arxiv_id, download_pdf_from_url

class TestURLParser(unittest.TestCase):
    """测试URL解析模块的功能"""
    
    def test_is_arxiv_url(self):
        """测试arXiv URL识别"""
        # 有效的arXiv URL
        self.assertTrue(is_arxiv_url("https://arxiv.org/abs/2501.12948"))
        self.assertTrue(is_arxiv_url("https://www.arxiv.org/abs/2501.12948"))
        self.assertTrue(is_arxiv_url("https://arxiv.org/pdf/2501.12948.pdf"))
        
        # 无效的arXiv URL
        self.assertFalse(is_arxiv_url("https://example.com/arxiv/2501.12948"))
        self.assertFalse(is_arxiv_url("https://arxivfake.org/abs/2501.12948"))
        self.assertFalse(is_arxiv_url("http://google.com"))
    
    def test_extract_arxiv_id(self):
        """测试从arXiv URL中提取论文ID"""
        # 标准URL
        self.assertEqual(extract_arxiv_id("https://arxiv.org/abs/2501.12948"), "2501.12948")
        
        # 带版本号的URL
        self.assertEqual(extract_arxiv_id("https://arxiv.org/abs/2501.12948v2"), "2501.12948")
        
        # PDF URL
        self.assertEqual(extract_arxiv_id("https://arxiv.org/pdf/2501.12948.pdf"), "2501.12948")
        
        # 无效URL
        self.assertIsNone(extract_arxiv_id("https://arxiv.org/invalid/format"))
        self.assertIsNone(extract_arxiv_id("https://example.com/arxiv/2501.12948"))
    
    @patch('requests.get')
    def test_download_pdf_from_url_arxiv(self, mock_get):
        """测试从arXiv URL下载PDF"""
        # 模拟成功的HTTP响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_content.return_value = [b'dummy pdf content']
        mock_get.return_value = mock_response
        
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        
        try:
            # 测试arXiv URL下载
            result = download_pdf_from_url("https://arxiv.org/abs/2501.12948", output_dir=temp_dir, debug=True)
            
            # 验证结果
            self.assertIsNotNone(result)
            self.assertTrue(os.path.exists(result))
            self.assertEqual(os.path.basename(result), "arxiv_2501.12948.pdf")
            
            # 验证请求URL
            mock_get.assert_called_with("https://arxiv.org/pdf/2501.12948.pdf", stream=True)
        finally:
            # 清理
            import shutil
            shutil.rmtree(temp_dir)
    
    @patch('requests.get')
    def test_download_pdf_from_url_direct(self, mock_get):
        """测试直接从PDF URL下载"""
        # 模拟成功的HTTP响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_content.return_value = [b'dummy pdf content']
        mock_get.return_value = mock_response
        
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        
        try:
            # 测试直接PDF URL下载
            result = download_pdf_from_url("https://example.com/paper.pdf", output_dir=temp_dir, debug=True)
            
            # 验证结果
            self.assertIsNotNone(result)
            self.assertTrue(os.path.exists(result))
            self.assertEqual(os.path.basename(result), "paper.pdf")
            
            # 验证请求URL
            mock_get.assert_called_with("https://example.com/paper.pdf", stream=True)
        finally:
            # 清理
            import shutil
            shutil.rmtree(temp_dir)
    
    @patch('requests.get')
    def test_download_pdf_http_error(self, mock_get):
        """测试HTTP错误情况"""
        # 模拟HTTP错误
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        
        try:
            # 测试HTTP错误情况
            result = download_pdf_from_url("https://arxiv.org/abs/2501.12948", output_dir=temp_dir, debug=True)
            
            # 验证结果
            self.assertIsNone(result)
        finally:
            # 清理
            import shutil
            shutil.rmtree(temp_dir)
    
    def test_unsupported_url(self):
        """测试不支持的URL类型"""
        result = download_pdf_from_url("https://example.com/not-a-pdf", debug=True)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
