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
BUPT_access_to_information_and_knowledge
├─ 📁data
│  ├─ 📁npr_articles
│  │  ├─ 📄article_1.txt
│  │  ├─ 📄article_10.txt
│  │  ├─ 📄article_100.txt
│  │  ├─ 📄article_11.txt
│  │  ├─ 📄article_12.txt
│  │  ├─ 📄article_13.txt
│  │  ├─ 📄article_14.txt
│  │  ├─ 📄article_15.txt
│  │  ├─ 📄article_16.txt
│  │  ├─ 📄article_17.txt
│  │  ├─ 📄article_18.txt
│  │  ├─ 📄article_19.txt
│  │  ├─ 📄article_2.txt
│  │  ├─ 📄article_20.txt
│  │  ├─ 📄article_21.txt
│  │  ├─ 📄article_22.txt
│  │  ├─ 📄article_23.txt
│  │  ├─ 📄article_24.txt
│  │  ├─ 📄article_25.txt
│  │  ├─ 📄article_26.txt
│  │  ├─ 📄article_27.txt
│  │  ├─ 📄article_28.txt
│  │  ├─ 📄article_29.txt
│  │  ├─ 📄article_3.txt
│  │  ├─ 📄article_30.txt
│  │  ├─ 📄article_31.txt
│  │  ├─ 📄article_32.txt
│  │  ├─ 📄article_33.txt
│  │  ├─ 📄article_34.txt
│  │  ├─ 📄article_35.txt
│  │  ├─ 📄article_36.txt
│  │  ├─ 📄article_37.txt
│  │  ├─ 📄article_38.txt
│  │  ├─ 📄article_39.txt
│  │  ├─ 📄article_4.txt
│  │  ├─ 📄article_40.txt
│  │  ├─ 📄article_41.txt
│  │  ├─ 📄article_42.txt
│  │  ├─ 📄article_43.txt
│  │  ├─ 📄article_44.txt
│  │  ├─ 📄article_45.txt
│  │  ├─ 📄article_46.txt
│  │  ├─ 📄article_47.txt
│  │  ├─ 📄article_48.txt
│  │  ├─ 📄article_49.txt
│  │  ├─ 📄article_5.txt
│  │  ├─ 📄article_50.txt
│  │  ├─ 📄article_51.txt
│  │  ├─ 📄article_52.txt
│  │  ├─ 📄article_53.txt
│  │  ├─ 📄article_54.txt
│  │  ├─ 📄article_55.txt
│  │  ├─ 📄article_56.txt
│  │  ├─ 📄article_57.txt
│  │  ├─ 📄article_58.txt
│  │  ├─ 📄article_59.txt
│  │  ├─ 📄article_6.txt
│  │  ├─ 📄article_60.txt
│  │  ├─ 📄article_61.txt
│  │  ├─ 📄article_62.txt
│  │  ├─ 📄article_63.txt
│  │  ├─ 📄article_64.txt
│  │  ├─ 📄article_65.txt
│  │  ├─ 📄article_66.txt
│  │  ├─ 📄article_67.txt
│  │  ├─ 📄article_68.txt
│  │  ├─ 📄article_69.txt
│  │  ├─ 📄article_7.txt
│  │  ├─ 📄article_70.txt
│  │  ├─ 📄article_71.txt
│  │  ├─ 📄article_72.txt
│  │  ├─ 📄article_73.txt
│  │  ├─ 📄article_74.txt
│  │  ├─ 📄article_75.txt
│  │  ├─ 📄article_76.txt
│  │  ├─ 📄article_77.txt
│  │  ├─ 📄article_78.txt
│  │  ├─ 📄article_79.txt
│  │  ├─ 📄article_8.txt
│  │  ├─ 📄article_80.txt
│  │  ├─ 📄article_81.txt
│  │  ├─ 📄article_82.txt
│  │  ├─ 📄article_83.txt
│  │  ├─ 📄article_84.txt
│  │  ├─ 📄article_85.txt
│  │  ├─ 📄article_86.txt
│  │  ├─ 📄article_87.txt
│  │  ├─ 📄article_88.txt
│  │  ├─ 📄article_89.txt
│  │  ├─ 📄article_9.txt
│  │  ├─ 📄article_90.txt
│  │  ├─ 📄article_91.txt
│  │  ├─ 📄article_92.txt
│  │  ├─ 📄article_93.txt
│  │  ├─ 📄article_94.txt
│  │  ├─ 📄article_95.txt
│  │  ├─ 📄article_96.txt
│  │  ├─ 📄article_97.txt
│  │  ├─ 📄article_98.txt
│  │  └─ 📄article_99.txt
│  └─ 📄npr_articles.json
├─ 📁results
│  ├─ 📄evaluation_report.json
│  ├─ 📄manual_evaluation.json
│  └─ 📄test_queries.json
├─ 📁src
│  ├─ 📁crawler
│  │  └─ 📄scrape_npr.py
│  ├─ 📁evaluation
│  │  ├─ 📁__pycache__
│  │  │  ├─ 📄__init__.cpython-312.pyc
│  │  │  ├─ 📄evaluation_metrics.cpython-312.pyc
│  │  │  ├─ 📄manual_evaluation.cpython-312.pyc
│  │  │  └─ 📄test_queries.cpython-312.pyc
│  │  ├─ 📄__init__.py
│  │  ├─ 📄evaluation_metrics.py
│  │  ├─ 📄manual_evaluation.py
│  │  └─ 📄test_queries.py
│  ├─ 📁indexing
│  │  ├─ 📄__init__.py
│  │  ├─ 📄document_frequency.py
│  │  ├─ 📄inverted_index.py
│  │  └─ 📄term_frequency.py
│  ├─ 📁preprocessing
│  │  ├─ 📁__pycache__
│  │  │  ├─ 📄__init__.cpython-312.pyc
│  │  │  ├─ 📄data_loader.cpython-312.pyc
│  │  │  ├─ 📄document_processor.cpython-312.pyc
│  │  │  ├─ 📄stopwords.cpython-312.pyc
│  │  │  ├─ 📄text_cleaner.cpython-312.pyc
│  │  │  ├─ 📄text_processor.cpython-312.pyc
│  │  │  └─ 📄tokenizer.cpython-312.pyc
│  │  ├─ 📄__init__.py
│  │  ├─ 📄data_loader.py
│  │  ├─ 📄document_processor.py
│  │  └─ 📄text_processor.py
│  └─ 📁retrieval
│     ├─ 📁__pycache__
│     │  ├─ 📄__init__.cpython-312.pyc
│     │  ├─ 📄bm25_model.cpython-312.pyc
│     │  ├─ 📄multi_field_scoring.cpython-312.pyc
│     │  ├─ 📄query_processor.cpython-312.pyc
│     │  ├─ 📄search_engine.cpython-312.pyc
│     │  ├─ 📄similarity_calculator.cpython-312.pyc
│     │  ├─ 📄temporal_scoring.cpython-312.pyc
│     │  └─ 📄vector_space_model.cpython-312.pyc
│     ├─ 📄__init__.py
│     ├─ 📄bm25_model.py
│     ├─ 📄multi_field_model.py
│     ├─ 📄multi_field_scoring.py
│     ├─ 📄query_processor.py
│     ├─ 📄search_engine.py
│     ├─ 📄similarity_calculator.py
│     ├─ 📄temporal_scoring.py
│     └─ 📄vector_space_model.py
├─ 📄.gitignore
├─ 📄README.md
├─ 📄evaluation_system.py
├─ 📄main.py
└─ 📄search_diagnostics.py
```