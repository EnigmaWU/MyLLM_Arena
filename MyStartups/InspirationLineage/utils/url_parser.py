#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
URL解析模块 - 用于从URL下载学术论文PDF
"""

import os
import re
import requests
import tempfile
from urllib.parse import urlparse

def is_arxiv_url(url):
    """判断是否为arXiv URL"""
    parsed = urlparse(url)
    return parsed.netloc in ['arxiv.org', 'www.arxiv.org']

def extract_arxiv_id(url):
    """从arXiv URL中提取论文ID"""
    # 处理形如 https://arxiv.org/abs/2501.12948 的URL
    match = re.search(r'arxiv\.org\/(?:abs|pdf)\/([0-9]+\.[0-9]+)(?:v[0-9]+)?', url)
    if match:
        return match.group(1)
    return None

def download_pdf_from_url(url, output_dir=None, debug=False):
    """
    从URL下载论文的PDF
    
    参数:
        url (str): 论文URL
        output_dir (str, optional): 输出目录，如果为None则使用临时目录
        debug (bool): 是否打印调试信息
        
    返回:
        str: 下载的PDF文件路径，下载失败则返回None
    """
    if debug:
        print(f"Debug: 开始从URL '{url}' 下载PDF")
    
    # 确定输出目录
    if output_dir is None:
        output_dir = tempfile.gettempdir()
    
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except Exception as e:
            if debug:
                print(f"Debug: 创建输出目录失败: {str(e)}")
            return None
    
    # 处理arXiv URL
    if is_arxiv_url(url):
        arxiv_id = extract_arxiv_id(url)
        if arxiv_id:
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
            output_path = os.path.join(output_dir, f"arxiv_{arxiv_id}.pdf")
            
            if debug:
                print(f"Debug: 识别为arXiv论文, ID: {arxiv_id}")
                print(f"Debug: PDF URL: {pdf_url}")
                print(f"Debug: 输出路径: {output_path}")
            
            try:
                response = requests.get(pdf_url, stream=True)
                if response.status_code == 200:
                    with open(output_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    if debug:
                        print(f"Debug: arXiv论文下载成功: {output_path}")
                    
                    return output_path
                else:
                    if debug:
                        print(f"Debug: arXiv PDF请求失败, 状态码: {response.status_code}")
                    return None
            except Exception as e:
                if debug:
                    print(f"Debug: 下载arXiv论文时出错: {str(e)}")
                return None
        else:
            if debug:
                print(f"Debug: 无法从URL提取arXiv ID")
            return None
    
    # 尝试直接下载PDF (如果URL直接指向PDF)
    elif url.lower().endswith('.pdf'):
        try:
            filename = os.path.basename(urlparse(url).path)
            output_path = os.path.join(output_dir, filename)
            
            if debug:
                print(f"Debug: 直接下载PDF: {url}")
                print(f"Debug: 输出路径: {output_path}")
            
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                if debug:
                    print(f"Debug: PDF下载成功: {output_path}")
                
                return output_path
            else:
                if debug:
                    print(f"Debug: PDF请求失败, 状态码: {response.status_code}")
                return None
        except Exception as e:
            if debug:
                print(f"Debug: 下载PDF时出错: {str(e)}")
            return None
    
    else:
        if debug:
            print(f"Debug: 不支持的URL类型: {url}")
        return None
