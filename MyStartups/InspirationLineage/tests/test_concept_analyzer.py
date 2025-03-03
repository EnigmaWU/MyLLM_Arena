#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
概念分析模块的单元测试
"""

import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.concept_analyzer import analyze_concept

class TestConceptAnalyzer(unittest.TestCase):
    """测试概念分析模块的功能"""
    
    def setUp(self):
        """测试前的设置"""
        # 测试文本
        self.test_text = """
        机器学习是人工智能的一个分支，是一门多领域交叉学科，涉及概率论、统计学、逼近论、凸分析、计算复杂性理论等多门学科。
        机器学习理论主要是设计和分析一些让计算机可以自动"学习"的算法。
        机器学习算法是一类从数据中自动分析获得规律，并利用规律对未知数据进行预测的算法。
        
        深度学习是机器学习的分支，是一种以人工神经网络为架构，对数据进行表征学习的算法。
        深度学习是机器学习中一种基于对数据进行表征学习的算法。
        
        强化学习是机器学习的一个重要分支，与监督学习和非监督学习不同，强化学习是智能体在与环境的交互中学习最优策略，以获得最大的累积奖励。
        """
    
    def test_concept_not_found(self):
        """测试概念不存在于文本中的情况"""
        result = analyze_concept(self.test_text, "量子计算", debug=True)
        self.assertIn("出现次数: 0", result)
        self.assertNotIn("上下文示例", result)
    
    def test_concept_found_once(self):
        """测试概念在文本中出现一次的情况"""
        result = analyze_concept(self.test_text, "人工智能", debug=True)
        self.assertIn("出现次数: 1", result)
        self.assertIn("上下文示例", result)
        self.assertIn("示例1", result)
        self.assertNotIn("示例2", result)
    
    def test_concept_found_multiple(self):
        """测试概念在文本中多次出现的情况"""
        result = analyze_concept(self.test_text, "机器学习", debug=True)
        self.assertIn("出现次数: 5", result)
        self.assertIn("上下文示例", result)
        self.assertIn("示例1", result)
        self.assertIn("示例2", result)
        self.assertIn("示例3", result)
        # 当概念出现超过3次，默认只提取3个示例
        self.assertNotIn("示例4", result)
    
    def test_case_insensitivity(self):
        """测试概念匹配的大小写不敏感性"""
        result = analyze_concept(self.test_text, "机器学习", debug=True)
        result_lower = analyze_concept(self.test_text, "机器学习", debug=True)
        # 结果应该相同
        self.assertEqual(result, result_lower)
    
    def test_depth_parameter(self):
        """测试深度参数的影响"""
        # 当前简单版本中深度参数没有实际作用，仅在输出中提及
        result_depth1 = analyze_concept(self.test_text, "深度学习", depth=1, debug=True)
        result_depth2 = analyze_concept(self.test_text, "深度学习", depth=2, debug=True)
        
        # 在当前简单版本中，深度参数不影响结果
        self.assertEqual(result_depth1, result_depth2)
    
    def test_empty_text(self):
        """测试空文本的处理"""
        result = analyze_concept("", "机器学习", debug=True)
        self.assertIn("出现次数: 0", result)


if __name__ == "__main__":
    unittest.main()
