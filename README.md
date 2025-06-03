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

## 文件结构

```
.
├── data/
│   └── npr_articles.json    # 新闻文章数据
├── src/
│   ├── retrieval/          # 检索相关代码
│   │   ├── search_engine.py
│   │   └── ...
│   └── evaluation/         # 评价相关代码
│       ├── manual_evaluation.py
│       ├── evaluation_metrics.py
│       └── test_queries.py
├── results/                # 评价结果
│   ├── manual_evaluation.json
│   └── test_queries.json
├── main.py                # 搜索系统主程序
└── evaluation_system.py   # 评价系统主程序
```


