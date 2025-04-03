# NextBook Agent - macOS版开发计划

## 目录

- [项目概述](#项目概述)
- [技术栈选择](#技术栈选择)
- [开发阶段规划](#开发阶段规划)
- [架构实现方案](#架构实现方案)
- [数据模型实现](#数据模型实现)
- [核心功能实现计划](#核心功能实现计划)
- [UI/UX实现方案](#uiux实现方案)
- [测试策略](#测试策略)
- [部署计划](#部署计划)
- [项目目录结构](#项目目录结构)
- [开发环境选择](#开发环境选择)
- [项目框架操作指导](#项目框架操作指导)

## 项目概述

NextBook Agent macOS版作为概念验证(POC)版本，旨在验证核心功能并建立初始用户群体。本文档定义了macOS版本的开发计划和关键技术决策。

## 技术栈选择

### 前端技术

- **UI框架**: Swift和SwiftUI
  - 理由: 原生macOS开发体验，性能优秀，适合单机应用
  - 替代方案: Electron (跨平台但性能和体验不如原生)

- **状态管理**: SwiftUI内置状态管理 + Combine
  - 理由: 与SwiftUI无缝集成，反应式编程模型简化状态管理

### 后端技术

- **编程语言**: Swift + Python
  - Swift: 应用核心逻辑
  - Python: AI相关功能和数据处理

- **AI框架**: OpenAI API + Ollama + CoreML
  - 理由: 采用混合AI策略以平衡性能、功能和隐私
    - OpenAI API: 提供高质量的内容分析、摘要生成和智能推荐能力
    - Ollama: 支持本地模型部署，减少网络依赖，保护用户隐私
    - CoreML: 处理设备端轻量级AI任务，如基础分类和推荐
  - 这种混合方案结合了云端AI的强大能力与本地处理的隐私保护和离线使用优势

### 数据存储

- **主数据库**: SQLite 
  - 理由: 轻量级，无需服务器，嵌入式数据库适合单机应用
  - 替代方案: Core Data (更强大但复杂度更高)

- **全文搜索**: SQLite FTS5扩展
  - 理由: 直接集成于主数据库，提供强大全文搜索能力

- **文件存储**: 本地文件系统 + 结构化索引
  - 理由: 简单直接，适合管理书籍文件和附件

## 开发阶段规划

### 阶段一: 基础框架构建 (4周)
- 搭建项目基本结构
- 实现基本的UI框架和导航
- 设计并实现数据模型和存储层
- 建立单元测试框架

### 阶段二: 核心功能开发 (8周)

按照优先级矩阵中的P0项目进行开发:
1. **SAVE模块** (3周)
   - 书籍导入功能
   - 基础笔记系统
   - 文件解析器(PDF/EPUB)

2. **NEXT模块** (3周)
   - 基础推荐算法
   - 书籍元数据展示
   - 推荐理由生成

3. **核心基础设施** (2周)
   - 本地数据同步
   - 错误处理机制

### 阶段三: 功能扩展 (6周)

按照优先级矩阵中的P1项目进行开发:
1. **内容分类系统** (1周)
2. **时间线回顾功能** (2周)
3. **基本搜索功能** (1周)
4. **用户设置界面** (1周)
5. **数据备份与恢复** (1周)

### 阶段四: 测试与优化 (4周)
- 系统测试与bug修复
- 性能优化
- 用户体验改进
- 准备App Store发布

## 架构实现方案

### 系统层次结构

## 项目目录结构

```
macOS_Version/
├── App/                        # 应用入口
│   └── NextBookApp.swift
├── Core/                       # 核心领域模型和逻辑
│   ├── Models/                 # 数据模型
│   └── Services/               # 核心业务服务
├── Data/                       # 数据层
│   ├── Database/               # 数据库相关
│   ├── FileSystem/             # 文件存储相关
│   ├── Repositories/           # 仓储模式实现
│   └── AI/                     # AI服务集成
│       ├── OpenAI/             # OpenAI API集成
│       └── Ollama/             # Ollama本地模型集成
├── UI/                         # 用户界面
│   ├── Views/                  # SwiftUI视图
│   ├── ViewModels/             # 视图模型
│   └── Components/             # 可复用UI组件
├── Features/                   # 功能模块
│   ├── Save/                   # 内容保存模块
│   ├── Next/                   # 推荐模块
│   ├── Recall/                 # 知识回忆模块
│   └── Report/                 # 数据报告模块
├── Utilities/                  # 通用工具类
│   ├── Extensions/             # 扩展
│   ├── Helpers/                # 辅助类
│   └── Constants/              # 常量定义
├── Resources/                  # 资源文件
│   ├── Assets.xcassets/        # 图片资源
│   ├── Localizations/          # 本地化资源
│   └── Info.plist              # 应用配置
├── Tests/                      # 测试
│   ├── NextBookTests/          # 单元测试
│   │   ├── Core/               # 核心模型测试
│   │   ├── Data/               # 数据层测试
│   │   │   ├── Models/         # 模型测试
│   │   │   └── Services/       # 服务测试
│   │   └── Features/           # 功能测试
│   │       ├── DatabaseTests/  # 数据库测试
│   │       ├── RepositoriesTests/ # 仓储测试
│   │       └── AITests/        # AI服务测试
│   └── NextBookUITests/        # UI测试
│       ├── SaveTests/          # 保存功能测试
│       ├── NextTests/          # 推荐功能测试
│       ├── RecallTests/        # 回忆功能测试
│       ├── ReportTests/        # 报告功能测试
│       ├── Mocks/              # 测试模拟对象
│       └── Helpers/            # 测试辅助工具
├── NextBook.xcodeproj/         # Xcode工程文件
└── Frameworks/                 # 第三方依赖
```

## 开发环境选择

### 主开发环境：Xcode

NextBook macOS版应主要使用Xcode进行开发，原因如下：

1. **原生支持Swift和SwiftUI**: Xcode提供完整的Swift和SwiftUI工具链，包括实时预览、代码补全和UI设计器
2. **完整的调试工具**: 提供强大的调试、性能分析和内存泄漏检测工具
3. **签名和部署**: 简化应用签名、证书管理和App Store发布流程
4. **CoreML集成**: 无缝支持CoreML框架，便于实现本地AI功能
5. **Interface Builder**: 提供可视化界面设计工具，简化UI开发

### 辅助开发环境：VSCode

对于项目中的Python部分（AI相关功能）建议使用VSCode：

1. **Python开发体验**: VSCode提供出色的Python开发支持
2. **跨语言协作**: 便于在同一环境中处理Swift和Python代码
3. **轻量级**: 处理辅助脚本和工具时启动更快

### 混合开发工作流

1. 使用Xcode进行所有Swift/SwiftUI相关开发
2. 使用VSCode开发Python脚本和AI模型集成代码
3. 使用Git作为版本控制，确保两个环境间的代码同步

### 环境准备

1. **Xcode设置**:
   - 安装最新版Xcode (14.0+)
   - 安装必要的扩展和工具
   - 配置SwiftFormat和SwiftLint插件

2. **VSCode设置**:
   - 安装Python扩展
   - 安装Swift Language扩展（便于查看Swift代码）
   - 配置虚拟环境以管理Python依赖

## 项目框架操作指导

本节提供从零开始搭建NextBook macOS版项目框架的Step-by-Step操作指南。

### 第一阶段：项目初始化与环境配置

#### 步骤1：安装必要工具
1. 确保已安装最新版Xcode（14.0+）
2. 安装VSCode用于Python开发
3. 安装Homebrew：`/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
4. 安装Python 3.10+：`brew install python@3.10`
5. 安装Git：`brew install git`（如果未预装）

#### 步骤2：创建Xcode项目
1. 打开Xcode，选择"Create a new Xcode project"
2. 选择"macOS" → "App"模板
3. 填写项目信息：
   - Product Name: NextBook
   - Organization Identifier: com.yourcompany.nextbook
   - Interface: SwiftUI
   - Language: Swift
   - 勾选"Include Tests"
4. 选择保存位置：`/Users/EnigmaWU/GitHub/MyLLM_Arena/MyStartups/NextBook/macOS_Version`
5. 初始化Git仓库（勾选"Create Git repository"）

#### 步骤3：项目基础配置
1. 在Xcode中设置开发团队（如适用）
2. 配置Bundle Identifier和版本信息
3. 设置部署目标（最低macOS版本，建议macOS 12+）

### 第二阶段：项目结构建立

#### 步骤4：创建基础目录结构
按照项目目录规划创建主要文件夹结构：

1. 在Xcode中，右键点击项目导航栏中的项目名称，选择"New Group"
2. 依次创建以下主要目录：
   - Core
   - Data
   - UI
   - Features
   - Utilities
   - Resources

3. 在各主目录下继续创建子目录（参照项目目录结构）

#### 步骤5：配置SwiftLint（代码质量保证）
1. 通过CocoaPods或SPM添加SwiftLint：
   ```bash
   # 切换到项目目录
   cd /Users/EnigmaWU/GitHub/MyLLM_Arena/MyStartups/NextBook/macOS_Version
   
   # 创建Podfile
   pod init
   
   # 编辑Podfile，添加SwiftLint
   echo "platform :osx, '12.0'\ntarget 'NextBook' do\n  pod 'SwiftLint'\nend" > Podfile
   
   # 安装依赖
   pod install
   ```

2. 创建SwiftLint配置文件：
   ```bash
   touch .swiftlint.yml
   ```

3. 添加基本配置到.swiftlint.yml

### 第三阶段：创建核心模型和服务

#### 步骤6：实现数据模型
1. 在Core/Models目录下创建基础数据模型：
   - Book.swift
   - Note.swift
   - Tag.swift
   - ReadingSession.swift
   - Recommendation.swift

2. 为每个模型实现基本结构，例如在Book.swift中：
   ```swift
   struct Book: Identifiable, Codable {
       let id: UUID
       var title: String
       var author: String
       var path: String
       var coverImage: Data?
       var addedDate: Date
       var lastOpenedDate: Date?
       var tags: [String]
       var notes: [UUID]  // References to Note objects
       var metadata: [String: String]
       
       init(title: String, author: String, path: String) {
           self.id = UUID()
           self.title = title
           self.author = author
           self.path = path
           self.addedDate = Date()
           self.tags = []
           self.notes = []
           self.metadata = [:]
       }
   }
   ```

#### 步骤7：搭建数据层
1. 在Data/Database目录下创建数据库管理类：
   - DatabaseManager.swift
   - SQLiteManager.swift

2. 实现基本的数据库连接和初始化功能

#### 步骤8：创建仓储层
1. 在Data/Repositories目录下创建仓储实现：
   - BookRepository.swift
   - NoteRepository.swift
   - TagRepository.swift

2. 实现基础CRUD操作

### 第四阶段：创建基础UI组件

#### 步骤9：搭建UI结构
1. 在UI/Views目录下创建主要视图：
   - MainView.swift (应用主视图)
   - LibraryView.swift (书籍库视图)
   - ReaderView.swift (阅读器视图)
   - SettingsView.swift (设置视图)

2. 创建基础UI组件（在UI/Components下）：
   - BookCard.swift
   - TagView.swift
   - NoteCard.swift
   - SearchBar.swift

#### 步骤10：设置导航
1. 在MainView中实现基本导航结构：
   ```swift
   struct MainView: View {
       var body: some View {
           NavigationSplitView {
               Sidebar()
           } content: {
               ContentList()
           } detail: {
               DetailView()
           }
       }
   }
   ```

### 第五阶段：实现功能模块

#### 步骤11：SAVE模块实现
1. 在Features/Save目录下创建：
   - BookImporter.swift
   - PDFParser.swift
   - EPUBParser.swift
   - ImportView.swift

#### 步骤12：AI服务集成
1. 创建Python虚拟环境：
   ```bash
   cd /Users/EnigmaWU/GitHub/MyLLM_Arena/MyStartups/NextBook/macOS_Version
   python -m venv venv
   source venv/bin/activate
   pip install openai ollama pyyaml
   ```

2. 在Data/AI目录下创建AI服务接口：
   - AIManager.swift
   - OpenAIService.swift

3. 使用PythonKit或创建Python桥接器连接Swift和Python代码

### 第六阶段：测试与完善

#### 步骤13：创建基础测试
1. 在Xcode测试导航器中为每个主要组件创建单元测试

#### 步骤14：创建构建脚本
1. 在项目根目录创建构建脚本：
   ```bash
   touch build.sh
   chmod +x build.sh
   ```

2. 添加自动化构建和测试命令

### 第七阶段：完善文档

#### 步骤15：创建开发文档
1. 在项目根目录创建docs文件夹
2. 添加关键组件的文档

#### 步骤16：设置持续集成
1. 创建GitHub Actions配置或选择其他CI工具
2. 配置自动构建和测试流程

这套操作指南提供了从零开始搭建项目的详细步骤，开发者可以按照这些步骤一步步构建起完整的NextBook macOS应用框架。
