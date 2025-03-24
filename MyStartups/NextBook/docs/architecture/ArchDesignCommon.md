# NextBook 通用架构设计原则

本文档描述了NextBook Agent的基本架构设计原则和思路，适用于所有版本的实现。

## 架构设计原则

* **本地优先**：核心功能不依赖网络连接
* **模块化设计**：组件可独立升级和替换
* **渐进增强**：基础功能的技术方案保持简单，只有在必要时，才引入更复杂技术方案
* **隐私保护**：敏感数据默认存储在本地，云同步为可选项

## 数据流架构

系统的数据流被分为四个主要功能流，所有流程共享核心存储系统。

### 核心存储架构

```mermaid
flowchart LR
    %% 定义主要数据节点及连接
    DB[(本地数据库)]
    VDB[(向量数据库)]
    FS[(文件系统)]
    
    DB <--> VDB
    DB <--> FS
    
    subgraph "存储内容分类"
        DB --> MD[元数据存储]
        DB --> UD[用户数据]
        VDB --> VS[语义向量]
        FS --> RAW[原始文件]
        FS --> GEN[生成内容]
    end
    
    classDef storage fill:#f5f5f5,stroke:#666666,stroke-width:2px
    classDef content fill:#e6f7ff,stroke:#1890ff,stroke-width:1px
    
    class DB,VDB,FS storage
    class MD,UD,VS,RAW,GEN content
```

**存储组件用途解释**:

| 存储组件             | 类型     | 用途说明                                                             |
| -------------------- | -------- | -------------------------------------------------------------------- |
| **本地数据库 (DB)**  | 核心存储 | 存储结构化数据，管理用户信息、阅读历史、书籍元数据和系统配置         |
| **向量数据库 (VDB)** | 核心存储 | 管理文本语义向量，支持相似度搜索和语义匹配，为推荐和回忆功能提供支持 |
| **文件系统 (FS)**    | 核心存储 | 存储原始书籍文件、图像和导出内容，提供高效的大文件管理               |
| **元数据存储 (MD)**  | 内容分类 | 保存书籍信息（标题、作者、出版信息）、阅读状态和标签数据             |
| **用户数据 (UD)**    | 内容分类 | 记录用户配置、阅读习惯、偏好设置和推荐历史                           |
| **语义向量 (VS)**    | 内容分类 | 存储文本内容的向量表示，用于相似内容查找和语义检索                   |
| **原始文件 (RAW)**   | 内容分类 | 保存原始PDF、EPUB等格式的完整书籍文件，确保内容完整性                |
| **生成内容 (GEN)**   | 内容分类 | 存储AI生成的摘要、见解、报告和知识关联等衍生内容                     |

### 内容获取流程 (SAVE)

```mermaid
flowchart LR
    %% SAVE流程
    DB[(本地数据库)]
    VDB[(向量数据库)]
    FS[(文件系统)]
    
    subgraph "内容获取流"
        A1[用户上传/导入] --> A2[文档解析]
        A2 --> A3[内容提取]
        A3 --> A4[元数据识别]
        A3 --> A5[文本向量化]
        A4 --> A6[分类标签生成]
        A5 --> A7[语义索引构建]
        A6 & A7 --> A8[存储索引]
    end
    
    A3 --> FS
    A5 --> VDB
    A8 --> DB
    
    classDef flow1 fill:#ffe6cc,stroke:#d79b00,stroke-width:2px
    classDef storage fill:#f5f5f5,stroke:#666666,stroke-dasharray:5 5
    
    class A1,A2,A3,A4,A5,A6,A7,A8 flow1
    class DB,VDB,FS storage
```

### 推荐系统流程 (NEXT)

```mermaid
flowchart LR
    %% NEXT流程
    DB[(本地数据库)]
    VDB[(向量数据库)]
    
    subgraph "推荐流程"
        B1[用户历史分析] --> B2[兴趣模型构建]
        B2 --> B3[LLM生成候选]
        B2 --> B6[网络搜索]
        B3 <--> B8[本地书库检索]
        B6 --> B7[搜索结果处理]
        B3 & B7 --> B4[多维度排序]
        B4 --> B5[个性化推荐展示]
        B5 --> B9[用户反馈收集]
        B9 --> B1
    end
    
    DB --> B1
    DB --> B8
    VDB --> B3
    B9 --> DB
    
    classDef flow2 fill:#d5e8d4,stroke:#82b366,stroke-width:2px
    classDef storage fill:#f5f5f5,stroke:#666666,stroke-dasharray:5 5
    
    class B1,B2,B3,B4,B5,B6,B7,B8,B9 flow2
    class DB,VDB storage
```

### 知识回忆流程 (RECALL)

```mermaid
flowchart LR
    %% RECALL流程
    DB[(本地数据库)]
    VDB[(向量数据库)]
    
    subgraph "回忆流程"
        C1[用户检索查询] --> C2[混合检索策略]
        C2 --> C3[语义搜索]
        C2 --> C6[关键词搜索]
        C3 & C6 --> C4[结果融合排序]
        C4 --> C7[上下文关联构建]
        C7 --> C5[可视化呈现]
        C5 --> C8[交互式探索]
        C8 --> C1
    end
    
    DB --> C2
    VDB --> C3
    C7 --> VDB
    C8 --> DB
    
    classDef flow3 fill:#dae8fc,stroke:#6c8ebf,stroke-width:2px
    classDef storage fill:#f5f5f5,stroke:#666666,stroke-dasharray:5 5
    
    class C1,C2,C3,C4,C5,C6,C7,C8 flow3
    class DB,VDB storage
```

### 数据报告流程 (REPORT)

```mermaid
flowchart LR
    %% REPORT流程
    DB[(本地数据库)]
    
    subgraph "报告生成流"
        D1[数据收集] --> D2[多维度统计]
        D2 --> D3[模式识别]
        D2 --> D4[趋势分析]
        D3 & D4 --> D5[洞见生成]
        D5 --> D6[可视化图表]
        D6 --> D7[报告组装]
    end
    
    DB --> D1
    D7 --> DB
    
    classDef flow4 fill:#e1d5e7,stroke:#9673a6,stroke-width:2px
    classDef storage fill:#f5f5f5,stroke:#666666,stroke-dasharray:5 5
    
    class D1,D2,D3,D4,D5,D6,D7 flow4
    class DB storage
```

### 跨流程数据交互

```mermaid
flowchart LR
    %% 流程间的交互连接
    SAVE[内容获取系统] --> DB[(数据存储)]
    NEXT[推荐系统] --> DB
    RECALL[回忆系统] --> DB
    REPORT[报告系统] --> DB
    
    SAVE -.-> |"提供内容"| NEXT
    SAVE -.-> |"提供索引"| RECALL
    NEXT -.-> |"影响推荐"| RECALL
    RECALL -.-> |"提供见解"| NEXT
    NEXT -.-> |"用户喜好"| REPORT
    RECALL -.-> |"知识关联"| REPORT
    REPORT -.-> |"阅读分析"| NEXT
    
    classDef system fill:#f5f5f5,stroke:#666666,stroke-width:2px
    classDef storage fill:#e6f7ff,stroke:#1890ff,stroke-width:2px
    classDef flow fill:#fff2e8,stroke:#fa8c16,stroke-width:1px,stroke-dasharray:5 5
    
    class SAVE,NEXT,RECALL,REPORT system
    class DB storage
```

## 相关架构设计

- [返回README](../../README.md)
- [macOS版架构设计](ArchDesignMacOsVersion.md)
- [多平台版架构设计](ArchDesignMultiOsVersion.md)
