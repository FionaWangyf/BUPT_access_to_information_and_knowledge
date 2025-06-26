# 信息检索系统


## 功能特点

### 检索功能
- 支持多种检索算法：
  - BM25算法
  - 向量空间模型
  - 混合检索模型
- 支持多字段检索（标题、内容、作者等）
- 支持查询扩展和优化
- 提供详细的检索结果，包括相似度分数和匹配词汇

### 评价系统
- 支持人工评价模式
- 提供自动评价指标计算
- 支持批量评价功能
- 可导出评价结果



## 使用指南

### 1. 搜索系统

#### 1.1 交互式搜索模式
```bash
python main.py
```
在交互式界面中，您可以：
- 输入查询语句进行搜索
- 查看详细的搜索结果，包括相似度分数和匹配词汇
- 使用 `quit` 或 `exit` 退出程序

#### 1.2 演示模式
```bash
python main.py --demo
```
系统将自动运行预设的示例查询，展示系统的检索能力。

#### 1.3 单次查询模式
```bash
python main.py --query "your query here"
```
直接执行单次查询并显示结果。

#### 1.4 算法比较模式
```bash
python main.py --compare "your query here"
```
比较不同检索算法（BM25、向量空间模型、混合模型）的检索效果。

### 2. 评价系统

#### 2.1 运行评价系统
```bash
# 人工评价模式
python evaluation_system.py --mode manual

# 演示评价功能
python evaluation_system.py --demo

# 计算评价指标
python evaluation_system.py --mode metrics

# 交互式评价菜单
python evaluation_system.py
```

#### 2.2 评价系统命令

在交互式界面中，可以使用以下命令：

- `list` - 显示所有测试查询
- `eval <query_id>` - 评估指定查询
- `batch [query_ids]` - 批量评估多个查询
- `summary` - 显示评估摘要
- `add <query_text> [description]` - 添加自定义查询
- `quit` - 退出评估

#### 2.3 评估过程

1. 使用 `list` 命令查看可用的测试查询
2. 使用 `eval <query_id>` 开始评估特定查询
3. 对每个搜索结果进行评分：
   - 3分：非常相关（完全匹配查询意图）
   - 2分：相关（与查询有明确关联）
   - 1分：部分相关（有一定关联但不太符合）
   - 0分：不相关（与查询无关）
   - s：跳过当前结果
   - q：退出当前查询评价

#### 2.4 添加自定义查询

使用 `add` 命令添加新的查询：
```bash
add "查询文本" 查询描述
```

例如：
```bash
add "人工智能发展" 关于AI技术的最新进展
```

#### 2.5 查看评价结果

- 评价结果保存在 `results/manual_evaluation.json`
- 测试查询列表保存在 `results/test_queries.json`
- 使用 `summary` 命令查看评价统计信息

#### 2.6 计算系统指标

```bash
python evaluation_system.py --mode metrics
```

系统会计算以下指标：
- Precision@K（精确率）
- Recall@K（召回率）
- F1@K（F1分数）
- NDCG@K（归一化折损累积增益）
- MAP（平均精确率）
- MRR（平均倒数排名）

# 信息抽取系统实用指南

## 🎯 系统概述

本系统集成了**信息检索**（作业2）和**信息抽取**（作业3）功能，基于NPR新闻数据，能够：
- 🔍 **信息检索**：从100篇NPR新闻中找到与查询相关的文档
- 🔬 **信息抽取**：从文本中自动识别7种实体类型（人名、地名、组织、时间、金额、联系方式、引用）
- 🎯 **智能集成**：先检索后抽取，获得结构化知识

---

## 📋 核心程序说明

### 🎯 `integrated_system.py` - 集成系统（主要演示程序）
**功能**：信息检索 + 信息抽取的集成应用
**适用**：完整系统演示、功能对比、交互式体验

### 🔬 `extraction_main.py` - 抽取系统（专业工具）
**功能**：专门的信息抽取工具，支持多种输入方式
**适用**：批量处理、文件处理、配置调优

---

## 🚀 快速开始

### 系统初始化检查
```bash
# 确保系统正常工作
python test_extraction_system.py
```

---

## 🎯 集成系统使用指南 (`integrated_system.py`)

### 启动系统
```bash
python integrated_system.py
```

### 🎮 交互命令

#### 基本操作
| 命令 | 功能 | 示例 |
|------|------|------|
| 直接输入查询 | 执行当前模式的操作 | `Biden Ukraine aid` |
| `help` | 显示帮助信息 | `help` |
| `quit` / `exit` / `q` | 退出程序 | `quit` |

#### 模式切换
| 命令 | 模式 | 说明 |
|------|------|------|
| `mode integrated` | 🎯 集成模式（默认） | 先检索相关文档，再抽取实体 |
| `mode search` | 🔍 纯检索模式 | 只执行信息检索（作业2功能） |
| `mode extract` | 🔬 纯抽取模式 | 只执行信息抽取（作业3功能） |

#### 特殊功能
| 命令 | 功能 | 示例 |
|------|------|------|
| `extract 文本内容` | 对指定文本抽取实体 | `extract President Biden announced aid` |
| `demo` | 运行预设演示 | `demo` |
| `stats` | 显示系统统计 | `stats` |

### 🔍 推荐测试查询

#### 政治类（实体丰富）
```
NPR funding lawsuit
Biden Ukraine aid  
Katherine Maher testimony
Congress public broadcasting
```

#### 经济贸易类
```
China trade tariffs
manufacturing jobs America
8.1% export growth
European customers export
```

#### 媒体机构类
```
NPR PBS lawsuit
CBS 60 Minutes interview
public radio stations
broadcasting licenses FCC
```



---

## 🔬 抽取系统使用指南 (`extraction_main.py`)

### 🎯 基本用法

#### 交互式模式
```bash
python extraction_main.py
```
然后直接输入文本进行抽取

#### 单次文本抽取
```bash
python extraction_main.py --text "President Biden announced $2.5 billion aid to Ukraine yesterday"
```

#### 文件抽取
```bash
python extraction_main.py --file input.txt
```

#### NPR数据批量处理
```bash
python extraction_main.py --npr-data --max-articles 50
```

### ⚙️ 高级参数

#### 输出控制
```bash
# 指定输出文件和格式
python extraction_main.py --npr-data --output results.json --format json
python extraction_main.py --npr-data --output results.csv --format csv
python extraction_main.py --npr-data --output results.txt --format txt
```

#### 精度调优
```bash
# 调整置信度阈值（0.1-1.0，默认0.6）
python extraction_main.py --threshold 0.8 --text "your text here"
```

#### 自定义配置
```bash
# 使用自定义配置文件
python extraction_main.py --config my_config.json --npr-data
```

### 🎮 交互式命令

启动交互模式后，可以使用：

| 命令 | 功能 | 示例 |
|------|------|------|
| 直接输入文本 | 进行信息抽取 | `President Biden announced aid` |
| `file:路径` | 从文件抽取 | `file:data/news.txt` |
| `stats` | 显示统计信息 | `stats` |
| `config` | 显示当前配置 | `config` |
| `help` | 显示帮助 | `help` |
| `quit` | 退出程序 | `quit` |

---


## 🎯 实体类型说明

| 类型 | 说明 | 示例 |
|------|------|------|
| **PERSON** | 人名（政治人物、记者、专家等） | Biden, Katherine Maher, David Folkenflik |
| **LOCATION** | 地名（国家、城市、政治中心等） | Ukraine, Washington D.C., White House |
| **ORGANIZATION** | 组织机构（政府、媒体、大学等） | NPR, Congress, Department of Defense |
| **TIME** | 时间信息（日期、相对时间等） | March 26 2025, yesterday, 2:30 PM |
| **MONEY** | 金额信息（货币、百分比等） | $2.5 billion, 8-10%, €100 million |
| **CONTACT** | 联系方式（邮箱、电话、网址） | press@npr.org, 202-456-1414 |
| **QUOTE** | 引用内容（发言、声明等） | "This support is crucial for democracy" |

---
