"""
用户相关的领域模型
"""

import uuid
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime

@dataclass
class UserPreferences:
    """用户偏好设置"""
    theme: str = "system"  # system, light, dark
    font_size: str = "medium"  # small, medium, large
    reading_interests: List[str] = field(default_factory=list)
    notification_enabled: bool = True
    auto_sync: bool = True
    custom_settings: Dict[str, Any] = field(default_factory=dict)

@dataclass
class User:
    """表示系统用户"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    username: str = ""
    email: Optional[str] = None
    display_name: Optional[str] = None
    preferences: UserPreferences = field(default_factory=UserPreferences)
    
    # 系统字段
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_active_at: Optional[datetime] = None
    
    def update_preferences(self, new_preferences: UserPreferences):
        """更新用户偏好设置"""
        self.preferences = new_preferences
        self.updated_at = datetime.now()
    
    def record_activity(self):
        """记录用户活动"""
        self.last_active_at = datetime.now()
