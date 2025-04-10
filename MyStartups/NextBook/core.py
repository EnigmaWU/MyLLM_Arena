"""
NextBook Agent 核心模块
包含应用的主要业务逻辑
"""

class AppCore:
    def __init__(self, config, infra):
        self.config = config
        self.infra = infra
        print("AppCore初始化完成")
    
    def shutdown(self):
        """关闭应用资源"""
        print("正在关闭应用资源...")
