#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF解析模块 - 用于从PDF文件中提取文本
"""

import PyPDF2
import os

def extract_text_from_pdf(pdf_path, debug=False):
    """
    从PDF文件中提取文本内容
    
    参数:
        pdf_path (str): PDF文件的路径
        debug (bool): 是否打印调试信息
        
    返回:
        str: 提取的文本内容，如果提取失败则返回空字符串
    """
    if debug:
        print(f"Debug: 开始从 '{pdf_path}' 提取文本")
    
    if not os.path.exists(pdf_path):
        if debug:
            print(f"Debug: PDF文件不存在: '{pdf_path}'")
        return ""
    
    try:
        text = ""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            num_pages = len(reader.pages)
            
            if debug:
                print(f"Debug: PDF共有 {num_pages} 页")
            
            # 提取所有页面的文本
            for page_num in range(num_pages):
                page = reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
                    
                if debug and (page_num + 1) % 10 == 0:
                    print(f"Debug: 已处理 {page_num + 1} 页")
        
        if debug:
            print(f"Debug: PDF文本提取完成，共 {len(text)} 字符")
            
        return text
    
    except Exception as e:
        if debug:
            print(f"Debug: PDF处理错误: {str(e)}")
        return ""
