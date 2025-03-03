#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
InspirationLineage - 灵感追溯工具

用于追溯学术论文中概念的来源和发展历程
"""

import argparse
import sys
import os
from utils.pdf_parser import extract_text_from_pdf
from utils.concept_analyzer import analyze_concept
from utils.url_parser import download_pdf_from_url

VERSION = "0.1.0"

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="InspirationLineage - 灵感概念追溯工具")
    
    # 互斥组：PDF或URL必须提供一个且只能提供一个
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--PDF", help="输入论文的PDF文件路径")
    source_group.add_argument("--URL", help="输入论文的URL")
    
    # 必需参数
    parser.add_argument("--ConceptName", required=True, help="需要追溯的概念名称")
    
    # 可选参数
    parser.add_argument("--Depth", type=int, default=1, help="概念追溯的深度，默认为1")
    parser.add_argument("--Debug", action="store_true", help="启用调试模式")
    parser.add_argument("--Version", action="version", version=f"InspirationLineage v{VERSION}")
    
    return parser.parse_args()

def process_pdf(pdf_path, concept_name, depth, debug=False):
    """处理PDF文件并追溯概念"""
    if debug:
        print(f"Debug: 处理PDF文件 '{pdf_path}'")
        print(f"Debug: 追溯概念 '{concept_name}', 深度: {depth}")
    
    # 检查文件是否存在
    if not os.path.exists(pdf_path):
        print(f"错误: PDF文件 '{pdf_path}' 不存在")
        return False
    
    # 提取PDF文本
    text = extract_text_from_pdf(pdf_path, debug)
    if not text:
        print("错误: 无法从PDF中提取文本")
        return False
    
    if debug:
        print(f"Debug: 成功提取PDF文本，长度: {len(text)} 字符")
        print(f"Debug: 文本前300个字符预览: {text[:300]}...")
    
    # 分析概念
    result = analyze_concept(text, concept_name, depth, debug)
    
    # 输出结果
    print("\n" + "="*50)
    print(f"概念 '{concept_name}' 的灵感追溯结果:")
    print("="*50)
    print(result)
    
    return True

def process_url(url, concept_name, depth, debug=False):
    """处理URL并追溯概念"""
    if debug:
        print(f"Debug: 处理URL '{url}'")
        print(f"Debug: 追溯概念 '{concept_name}', 深度: {depth}")
    
    # 从URL下载PDF
    pdf_path = download_pdf_from_url(url, debug=debug)
    if not pdf_path:
        print(f"错误: 无法从URL '{url}' 下载PDF")
        return False
    
    if debug:
        print(f"Debug: PDF已下载到 '{pdf_path}'")
    
    # 使用现有的PDF处理函数处理下载的PDF
    success = process_pdf(pdf_path, concept_name, depth, debug)
    
    # 清理临时文件（可选）
    # import tempfile
    # if pdf_path.startswith(tempfile.gettempdir()):
    #     if debug:
    #         print(f"Debug: 删除临时PDF文件 '{pdf_path}'")
    #     os.remove(pdf_path)
    
    return success

def main():
    """主函数"""
    args = parse_arguments()
    
    if args.Debug:
        print("调试模式已启用")
        print(f"参数: {args}")
    
    if args.PDF:
        success = process_pdf(args.PDF, args.ConceptName, args.Depth, args.Debug)
    elif args.URL:
        success = process_url(args.URL, args.ConceptName, args.Depth, args.Debug)
    else:
        print("错误: 必须提供PDF文件路径或URL")
        return 1
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
