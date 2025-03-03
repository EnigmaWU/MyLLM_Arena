#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
概念分析模块 - 用于分析文本中的概念及其追溯
"""

def analyze_concept(text, concept_name, depth=1, debug=False):
    """
    分析文本中的概念及其灵感追溯
    
    参数:
        text (str): 要分析的文本内容
        concept_name (str): 概念名称
        depth (int): 追溯深度
        debug (bool): 是否打印调试信息
        
    返回:
        str: 概念追溯分析结果
    """
    if debug:
        print(f"Debug: 开始分析概念 '{concept_name}'，深度: {depth}")
    
    # 简单的初始实现，仅检查概念在文本中出现的次数和上下文
    # 在实际项目中，这里应该使用更高级的NLP或LLM技术
    
    concept_lower = concept_name.lower()
    text_lower = text.lower()
    
    # 计算概念出现次数
    occurrences = text_lower.count(concept_lower)
    
    if debug:
        print(f"Debug: 概念 '{concept_name}' 在文本中出现了 {occurrences} 次")
    
    # 简单提取概念周围的上下文
    contexts = []
    start_pos = 0
    for _ in range(min(3, occurrences)):  # 最多提取3个上下文示例
        pos = text_lower.find(concept_lower, start_pos)
        if pos == -1:
            break
            
        # 提取概念前后200个字符作为上下文
        context_start = max(0, pos - 200)
        context_end = min(len(text), pos + len(concept_name) + 200)
        context = text[context_start:context_end]
        contexts.append(context.replace("\n", " ").strip())
        
        start_pos = pos + len(concept_name)
    
    # 构建分析结果
    result = f"概念: {concept_name}\n"
    result += f"│\n"
    result += f"├── 出现次数: {occurrences}\n"
    
    if occurrences > 0:
        result += f"│\n"
        result += f"├── 上下文示例:\n"
        for i, context in enumerate(contexts):
            result += f"│   ├── 示例{i+1}: \"{context[:100]}...\"\n"
    
    result += f"│\n"
    result += f"└── 注意: 这是一个初始版本，尚未实现完整的概念追溯分析。未来版本将使用LLM进行深入分析。\n"
    
    if debug:
        print(f"Debug: 概念分析完成")
    
    return result
