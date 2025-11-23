# Technical Reference Recommendation Agent

## Vision

An **LLM-powered intelligent coding agent specialized for Embedded C/C++ experts**. It provides **async, silent advice** on **Embedded Linux (User/Kernel)**, **HAL usage**, and **RTOS patterns**, helping experienced engineers code confidently from memory while catching subtle **concurrency, memory, and hardware-interaction pitfalls**.

While focused on Embedded Systems (Linux & RTOS), it also supports general software development contexts.

## Architecture

### System Components

```mermaid
flowchart TB
    subgraph IDE["IDE Extensions"]
        VSCode["VS Code Extension<br/>- TechRefForYou Panel<br/>- Language Client (LSP)"]
        JetBrains["JetBrains Plugin<br/>- TechRefForYou Tool Window<br/>- Language Client (LSP)"]
    end
    
    subgraph Backend["REST API Service (Backend)"]
        subgraph LLM["LLM Integration Layer"]
            GPT["GPT-4o / Claude 3.5 Sonnet"]
            Prompt["Prompt Engineering"]
            Context["Context Window Management"]
        end
        
        subgraph Analysis["Analysis Engine"]
            Parser["Code Parser<br/>(Tree-sitter)"]
            Matcher["API Pattern Matcher"]
            Semantic["Semantic Analysis"]
        end
        
        subgraph Knowledge["Knowledge Base"]
            VectorDB["API Misuse Patterns<br/>(Vector DB)"]
            CVE["CVE/CWE Database"]
            Docs["Framework Documentation<br/>Index"]
            Examples["Code Examples Repository"]
            Internal["Internal Knowledge<br/>(RAG-powered)<br/>- Design Docs<br/>- Course Materials<br/>- RCA Reports"]
        end
    end
    
    VSCode -->|HTTPS/WebSocket| Backend
    JetBrains -->|HTTPS/WebSocket| Backend
    
    Backend --> LLM
    Backend --> Analysis
    Backend --> Knowledge
    
    LLM -.->|retrieves| Knowledge
    Analysis -.->|queries| Knowledge
```

### Tech Stack

**IDE Extensions:**
- **VS Code**: TypeScript, VS Code Extension API, LSP (Code Actions), Integration with C/C++ Extension (ms-vscode.cpptools)
- **JetBrains**: Kotlin/Java, CLion Plugin SDK, LSP support

**Backend Service:**
- **API Framework**: FastAPI (Python) or Express (Node.js)
- **Identity & User Profile**: 
  - Auth0 / Clerk for authentication
  - PostgreSQL for user profiles, preferences, and "seen" history
- **LLM Integration**: 
  - OpenAI API (GPT-4o, GPT-4-turbo)
  - Anthropic API (Claude 3.5 Sonnet)
  - LangChain for orchestration
- **Code Analysis & Remediation**: 
  - **Clangd & Clang-Tidy**: Gold standard for C/C++ static analysis and AST matching
  - **Tree-sitter**: For robust, error-tolerant parsing of C/C++/DeviceTree/Kconfig
  - **AST Transformers**: Clang-Repl/LibTooling for safe refactoring
  - **Custom Rule Engine**: OPA/Rego for team governance
- **Vector Database**: Pinecone/Weaviate for semantic search
- **Caching**: Redis for response caching
- **Message Queue**: RabbitMQ for async processing

**Knowledge Base:**
- **Vector embeddings** for API documentation and code examples
- **Graph database** (Neo4j) for API relationship mapping
- **CVE/CWE database** integration for security patterns
- **Community-sourced patterns** from GitHub, Stack Overflow
- **Internal Knowledge Base** (RAG-powered):
  - Design documents (architecture decisions, system designs)
  - Course materials (internal training, best practices guides)
  - Root-cause analysis docs (post-mortems, incident reports)
  - Team coding standards and conventions
  - Historical bug patterns and fixes

### API Endpoints

**OpenAI-Compatible Format** (Drop-in replacement for OpenAI API)

```http
POST /v1/chat/completions
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY

Request:
{
  "model": "techref-advisor-v1",
  "messages": [
    {
      "role": "system",
      "content": "You are a technical reference advisor for code analysis."
    },
    {
      "role": "user", 
      "content": "Analyze: int fd = open(filename, O_RDWR);"
    }
  ],
  "temperature": 0.7,
  "stream": false,
  
  // Custom extensions (optional)
  "techref_context": {
    "language": "c",
    "file_path": "src/main.c",
    "severity_filter": ["critical", "warning"],
    "include_examples": true,
    "internal_knowledge": true
  }
}

Response (OpenAI-compatible):
{
  "id": "techref-chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1700000000,
  "model": "techref-advisor-v1",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "🔴 **Missing Error Check**\n\nThe `open()` system call returns -1 on error...",
        "techref_metadata": {
          "suggestions": [
            {
              "severity": "critical",
              "category": "error_handling",
              "line": 1,
              "message": "Missing error check for open()",
              "code_example": "if (fd < 0) { perror(\"open\"); return -1; }"
            }
          ],
          "related_docs": [
            {"type": "rca", "title": "RCA-2024-03-15", "relevance": 0.92}
          ]
        }
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 45,
    "completion_tokens": 120,
    "total_tokens": 165
  }
}
```

**Streaming Support (Server-Sent Events)**

```http
POST /v1/chat/completions
{
  "model": "techref-advisor-v1",
  "messages": [...],
  "stream": true
}

Response Stream:
data: {"id":"techref-1","object":"chat.completion.chunk","choices":[{"delta":{"role":"assistant"}}]}

data: {"id":"techref-1","object":"chat.completion.chunk","choices":[{"delta":{"content":"🔴"}}]}

data: {"id":"techref-1","object":"chat.completion.chunk","choices":[{"delta":{"content":" Missing"}}]}

data: [DONE]
```

**Additional Endpoints**

```http
GET /v1/models
  - Lists available analysis models
  - Response: { "data": [{"id": "techref-advisor-v1", ...}] }

POST /v1/embeddings
  - Generate embeddings for code snippets
  - Request: { "model": "techref-embeddings", "input": "code..." }
  - Response: { "data": [{"embedding": [...]}] }

POST /v1/knowledge/query
  - Query internal knowledge base
  - Request: { "query": "...", "doc_types": ["design", "rca"] }
  - Response: { "results": [...] }

POST /v1/knowledge/ingest
  - Index internal documents
  - Request: { "content": "...", "metadata": {...}, "doc_type": "rca" }
  - Response: { "indexed": true, "id": "doc-123" }
```

**Client Usage Example**

```python
from openai import OpenAI

# Just change base_url - existing OpenAI code works!
client = OpenAI(
    base_url="https://techref-service.yourcompany.com/v1",
    api_key="your-api-key"
)

response = client.chat.completions.create(
    model="techref-advisor-v1",
    messages=[
        {"role": "system", "content": "Analyze code for API misuse"},
        {"role": "user", "content": "int fd = open(file, O_RDWR);"}
    ],
    extra_body={
        "techref_context": {
            "language": "c",
            "internal_knowledge": True
        }
    }
)

print(response.choices[0].message.content)
```

## User Stories

### Story 1: System Call & HAL Safety Assistant
**AS** an Embedded C/C++ engineer coding from memory,
**I WANT** real-time advice when I use system calls (Linux `ioctl`, `mmap`) or HAL APIs (STM32 `HAL_GPIO_WritePin`, ESP-IDF `gpio_set_level`),
**SO THAT** I can catch hardware interaction issues, ISR-unsafe calls, and platform-specific constraints immediately.

**Acceptance Criteria:**
- **Context-Aware Checks**:
  - Warns if blocking APIs are called inside an ISR (Interrupt Service Routine)
  - Checks for correct peripheral clock enablement before usage
  - Validates `ioctl` command arguments against driver specs
- **Safety Warnings**:
  - Flags missing `volatile` qualifiers for memory-mapped I/O
  - Warns about potential race conditions in Read-Modify-Write operations on registers
- **Examples**:
  - Shows correct HAL initialization sequences
  - Provides safe alternatives for ISR context (e.g., `xQueueSendFromISR`)

### Story 2: Embedded Linux & RTOS Guard
**AS** a developer using Embedded Linux (Yocto, Buildroot, Kernel Modules) or RTOS (Zephyr, FreeRTOS, Autosar),
**I WANT** proactive warnings about configuration mismatches, priority inversion risks, and deprecated board support package (BSP) APIs,
**SO THAT** I can ensure system stability and real-time performance.

**Acceptance Criteria:**
- **Linux Kernel & Drivers**:
  - Checks for correct use of kernel locking primitives (`mutex`, `spinlock`, `RCU`)
  - Warns about sleeping in atomic context (e.g., `kmalloc(..., GFP_KERNEL)` inside spinlock)
  - Validates Device Tree properties against binding schemas
- **RTOS Awareness**:
  - Detects potential Priority Inversion (e.g., low-priority task holding mutex needed by high-priority task)
  - Warns about stack overflow risks in recursive functions
  - Checks for correct mutex/semaphore pairing
- **Framework Specifics**:
  - Validates Zephyr Device Tree overlays
  - Checks Autosar RTE contract compliance
- **Performance**:
  - Flags excessive logging in hot paths or ISRs
  - Warns about busy-wait loops that kill power efficiency

### Story 3: Concurrency & Hardware Resource Advisor
**AS** an embedded engineer managing limited hardware resources,
**I WANT** alerts about DMA buffer coherency, cache maintenance, and peripheral conflicts,
**SO THAT** I can prevent data corruption and hardware lockups.

**Acceptance Criteria:**
- **Memory & Cache**:
  - Warns if DMA buffers are not aligned to cache lines
  - Reminds to flush/invalidate cache before/after DMA transfers
- **Concurrency**:
  - Identifies race conditions on shared hardware registers
  - Suggests atomic operations or critical sections where needed
  - Warns about "volatile" misuse (it's not a mutex!)

### Story 4: Embedded Memory Management
**AS** a developer working with constrained RAM/Flash,
**I WANT** detection of stack overflows, heap fragmentation risks, and flash wear patterns,
**SO THAT** I can write robust firmware that runs for years without crashing.

**Acceptance Criteria:**
- **Heap/Stack**:
  - Flags dynamic allocation (`malloc`/`new`) in critical real-time paths
  - Warns about large stack variables that could blow the stack
- **Flash/NVM**:
  - Detects frequent writes to the same flash sector (wear leveling risk)
  - Checks for proper alignment of flash writes
- **Safety**:
  - Flags use of functions known to be unsafe in embedded (e.g., `printf` with floating point in small stack)

### Story 5: Security & Secure Boot Advisor
**AS** an engineer implementing secure IoT devices,
**I WANT** warnings about weak crypto, insecure boot chains, and debug port exposure,
**SO THAT** I can protect the device against physical and remote attacks.

**Acceptance Criteria:**
- **Crypto**:
  - Recommends hardware crypto accelerators over software implementations
  - Flags weak RNG usage (use TRNG if available)
- **Device Security**:
  - Warns if JTAG/SWD is left open in production configurations
  - Checks for secure boot signature verification steps
  - Flags unencrypted storage of sensitive keys in flash

### Story 6: Internal Knowledge Advisor (RAG-Powered)
**AS** a team member working on an existing codebase,
**I WANT** contextual recommendations from our internal design docs, training courses, and past RCA reports when I'm coding,
**SO THAT** I can leverage team knowledge, avoid repeating past mistakes, and follow established architectural patterns without searching through documentation.

**Acceptance Criteria:**
- **Context-aware suggestions**: 
  - When working on payment module → surfaces payment service design doc
  - When using deprecated pattern → shows RCA from similar past incident
  - When implementing feature → recommends relevant internal course material
- **Document types indexed**:
  - 📋 Design documents (architecture decisions, system designs, API specs)
  - 📚 Course materials (onboarding guides, best practices, coding standards)
  - 🔍 Root-cause analysis (post-mortems, incident reports, bug patterns)
  - 📖 Team conventions (code style, review guidelines, deployment procedures)
- **Smart retrieval**:
  - Semantic search across all internal docs
  - Relevance ranking based on current code context
  - Shows "Related Docs" section in TechRefForYou panel
- **Continuous learning**:
  - Auto-indexes new docs from Confluence, Notion, Google Docs
  - Updates embeddings when documents are modified
  - Learns from which suggestions developers actually use
- **Privacy & security**:
  - Internal knowledge stays within company infrastructure
  - Role-based access control for sensitive docs
  - Audit logs for compliance

**Example Scenarios:**
```
Scenario A: Avoiding Repeated Mistakes
  You write: void UART_IRQHandler() { strcpy(buffer, rx_reg); }
  
  TechRefForYou shows:
  🔴 Buffer Overflow Risk (from RCA-2024-03-15)
      "Unbounded string copy in ISR caused crash in v1.2.
       Use circular buffer or bounded copy."
  📚 Related: Embedded C Coding Standard - Section 5.2
```

```
Scenario B: Following Design Decisions
  You create: class TempSensor { ... }
  
  TechRefForYou shows:
  🔵 HAL Alignment (from Design Doc: Sensor-HAL-v2)
      "All sensor drivers must implement ISensor interface
       to support hardware abstraction. See hal_sensor.h."
  📋 Related: sensor-driver-architecture.md
```

```
Scenario C: Learning from Past Experience
  You implement: volatile int flag; ... flag++;
  
  TechRefForYou shows:
  🟡 ISR Race Condition (from RCA-2023-11-20)
      "Read-Modify-Write on volatile variable is not atomic.
       Caused intermittent bug in motor control loop.
       Use atomic_int or critical section."
  📚 Related: Concurrency Best Practices Course
```

### Story 7: Personalized & Noise-Free Experience
**AS** a developer using the service daily,
**I WANT** the agent to remember what I've already seen and adapt to my specific context,
**SO THAT** I'm not annoyed by repetitive advice and only see relevant, "new" information.

**Acceptance Criteria:**
- **Smart Deduplication**:
  - Tracks "seen" advice per user/project
  - Suppresses warnings I've explicitly dismissed or fixed previously
  - Doesn't show the same "best practice" tip 50 times a day
- **User Context Isolation**:
  - Maintains separate profiles for different developers
  - Adapts to my role (e.g., Junior Dev gets more educational tips, Senior Dev gets only critical architectural warnings)
  - Learns my preferences (e.g., "Don't warn me about `printf` in debug builds")
- **Project-Specific Context**:
  - Understands project-specific conventions (e.g., "In this legacy repo, we use `MyString` instead of `std::string`")
  - Filters advice based on project configuration (e.g., C++11 vs C++20 standards)

### Story 8: One-Click Remediation
**AS** a developer who wants to fix an issue quickly,
**I WANT** to apply the recommended code fix with a single click directly from the "TechRefForYou" panel,
**SO THAT** I can resolve the warning immediately without manually typing boilerplate code.

**Acceptance Criteria:**
- **Quick Fix Actions**:
  - "Apply Fix" button next to the warning
  - Preview diff before applying
  - Supports multiple fix options (e.g., "Use `strncpy`" vs "Use `strlcpy`")
- **Smart Refactoring**:
  - Automatically handles imports/includes
  - Preserves existing comments and formatting
  - Updates related code references if needed

### Story 9: Team-Wide Rule Enforcement
**AS** a team lead or architect,
**I WANT** to define and enforce custom API usage rules for my team,
**SO THAT** I can ensure consistency and prevent specific anti-patterns relevant to our project.

**Acceptance Criteria:**
- **Custom Rule Definition**:
  - Simple configuration file (YAML/JSON) to define banned APIs
  - Ability to add custom warning messages and suggested replacements
- **Shared Configuration**:
  - Rules are checked into the repository (e.g., `.techref/rules.yaml`)
  - Automatically synced to all team members' IDEs
- **Severity Levels**:
  - Configurable severity (Error, Warning, Info) for custom rules
  - Option to block commits (via CI integration) for critical violations

## Key Features

### 🎯 "TechRefForYou" Panel
- **Dedicated view panel** alongside PROBLEMS, OUTPUT, TERMINAL
- **Categorized advice**: 
  - 🔴 Critical (security, memory safety)
  - 🟡 Warning (common pitfalls, deprecated APIs)
  - 🔵 Info (best practices, performance tips)
- **Non-blocking**: Updates asynchronously as you code
- **Clickable items**: Jump to code location
- **Filterable**: By severity, by API category (syscall, framework, crypto, etc.)
- **Collapsible groups**: Organize by file or by issue type
- **Personalized View**: Shows "New for You" vs "All Issues"

### 🧠 Smart Filtering & Personalization
- **History Tracking**: Remembers dismissed suggestions
- **Role-Based Tuning**: Junior/Senior/Security-Specialist profiles
- **Noise Reduction**: Auto-suppresses repetitive tips
- **Context Awareness**: User + Project + Team settings

### 🌊 Flow-Preserving UX
- **Silent analysis**: Triggers after typing pause (500ms debounce)
- **Gutter icons**: Subtle 💡 in editor for quick reference
- **Hover tooltips**: Detailed advice on mouseover
- **No interruptions**: No modals, no auto-focus stealing
- **Badge count**: Shows new suggestions without disruption

### 🧠 Memory-Assist Mode
- Detects when you're "coding from memory"
- Validates against actual API contracts
- Highlights differences between what you wrote vs. recommended patterns
- Shows migration paths for outdated knowledge
