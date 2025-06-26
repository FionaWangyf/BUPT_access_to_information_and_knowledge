#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可交互的信息检索+信息抽取集成系统
文件位置：interactive_integrated_system.py
"""

import sys
import os
import json
import time
from typing import List, Dict, Any, Optional
sys.path.append('src')

# 导入现有的检索系统
from src.retrieval.search_engine import EnhancedSearchEngine

# 导入抽取系统
from src.extraction.extraction_manager import ExtractionManager

class InteractiveIntegratedSystem:
    """可交互的信息检索+信息抽取集成系统"""
    
    def __init__(self, data_file: str):
        self.data_file = data_file
        self.search_engine = None
        self.extraction_manager = None
        self.is_initialized = False
        
        # 操作模式
        self.current_mode = "integrated"  # integrated, search_only, extract_only
        
    def initialize(self) -> bool:
        """初始化系统"""
        try:
            print("🔧 初始化集成系统...")
            
            # 1. 初始化检索引擎
            print("📚 初始化信息检索引擎...")
            self.search_engine = EnhancedSearchEngine(self.data_file)
            if not self.search_engine.initialize():
                print("❌ 检索引擎初始化失败")
                return False
            
            # 2. 初始化抽取管理器
            print("🔍 初始化信息抽取引擎...")
            config = {
                'enable_regex_extractor': True,
                'regex_confidence_threshold': 0.6,
                'merge_duplicate_entities': True,
                'max_entities_per_type': 30,
                'enable_cache': True,
            }
            
            self.extraction_manager = ExtractionManager(config)
            if not self.extraction_manager.initialize():
                print("❌ 抽取管理器初始化失败")
                return False
            
            self.is_initialized = True
            print("✅ 集成系统初始化成功！")
            return True
            
        except Exception as e:
            print(f"❌ 系统初始化失败: {e}")
            return False
    
    def search_only(self, query: str, top_k: int = 10):
        """纯信息检索模式（作业2功能）"""
        print(f"\n🔍 【信息检索模式】查询: '{query}'")
        print("目标：找到与查询相关的文档")
        
        start_time = time.time()
        results = self.search_engine.search(query, top_k)
        search_time = time.time() - start_time
        
        print(f"\n📊 检索结果 (耗时 {search_time:.3f}秒):")
        print(f"找到 {len(results)} 个相关文档")
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. 【相似度: {result.similarity:.3f}】")
            print(f"   标题: {result.title}")
            print(f"   内容预览: {result.content[:150]}...")
            print(f"   URL: {result.url}")
            if hasattr(result, 'matched_terms') and result.matched_terms:
                print(f"   匹配词汇: {', '.join(result.matched_terms)}")
        
        return results
    
    def extract_only(self, text: str):
        """纯信息抽取模式（作业3功能）"""
        print(f"\n🔬 【信息抽取模式】")
        print("目标：从文本中抽取结构化实体")
        print(f"输入文本: {text[:100]}...")
        
        start_time = time.time()
        results = self.extraction_manager.extract_from_text(text, 1, "input")
        extract_time = time.time() - start_time
        
        print(f"\n📊 抽取结果 (耗时 {extract_time:.3f}秒):")
        
        if not results:
            print("未找到任何实体")
            return results
        
        print(f"抽取到 {len(results)} 个实体:")
        
        # 按类型分组显示
        by_type = {}
        for result in results:
            if result.entity_type not in by_type:
                by_type[result.entity_type] = []
            by_type[result.entity_type].append(result)
        
        for entity_type, entities in by_type.items():
            print(f"\n🏷️ {entity_type.upper()} ({len(entities)} 个):")
            for entity in sorted(entities, key=lambda x: x.confidence, reverse=True):
                print(f"   ✓ {entity.entity_value} (置信度: {entity.confidence:.3f})")
                print(f"     上下文: {entity.context[:80]}...")
        
        return results
    
    def integrated_search_extract(self, query: str, top_k: int = 5):
        """集成模式：检索+抽取"""
        print(f"\n🎯 【集成模式】查询: '{query}'")
        print("目标：先检索相关文档，再从文档中抽取实体")
        
        # 第一步：信息检索
        print("\n📋 步骤1: 信息检索")
        search_start = time.time()
        search_results = self.search_engine.search(query, top_k)
        search_time = time.time() - search_start
        
        print(f"✅ 检索完成: 找到 {len(search_results)} 个相关文档 (耗时 {search_time:.3f}秒)")
        
        if not search_results:
            print("❌ 未找到相关文档，无法进行抽取")
            return
        
        # 第二步：信息抽取
        print("\n📋 步骤2: 信息抽取")
        extract_start = time.time()
        all_entities = []
        doc_entities = {}
        
        for i, doc in enumerate(search_results):
            print(f"  正在抽取文档 {i+1}/{len(search_results)}...")
            
            # 从标题和内容片段抽取
            doc_text = f"{doc.title}. {doc.content[:500]}"
            entities = self.extraction_manager.extract_from_text(doc_text, doc.doc_id, "search_result")
            
            all_entities.extend(entities)
            doc_entities[i] = {
                'doc_info': doc,
                'entities': entities
            }
        
        extract_time = time.time() - extract_start
        total_time = search_time + extract_time
        
        print(f"✅ 抽取完成: 从 {len(search_results)} 个文档中抽取 {len(all_entities)} 个实体 (耗时 {extract_time:.3f}秒)")
        
        # 第三步：结果展示
        print(f"\n📊 集成结果摘要 (总耗时 {total_time:.3f}秒):")
        
        # 统计所有实体
        entity_stats = {}
        for entity in all_entities:
            entity_type = entity.entity_type
            if entity_type not in entity_stats:
                entity_stats[entity_type] = []
            entity_stats[entity_type].append(entity)
        
        print(f"  📈 总体统计:")
        print(f"    检索文档: {len(search_results)} 篇")
        print(f"    抽取实体: {len(all_entities)} 个")
        print(f"    实体类型: {len(entity_stats)} 种")
        
        # 显示各类型热门实体
        print(f"\n🔥 热门实体 (按类型):")
        for entity_type, entities in entity_stats.items():
            # 统计实体出现频次
            entity_counts = {}
            for entity in entities:
                value = entity.entity_value
                if value not in entity_counts:
                    entity_counts[value] = {'count': 0, 'confidence': entity.confidence}
                entity_counts[value]['count'] += 1
                entity_counts[value]['confidence'] = max(entity_counts[value]['confidence'], entity.confidence)
            
            # 按频次排序，显示前3个
            top_entities = sorted(entity_counts.items(), key=lambda x: (x[1]['count'], x[1]['confidence']), reverse=True)[:3]
            
            print(f"  🏷️ {entity_type.upper()}:")
            for entity_value, stats in top_entities:
                print(f"     {entity_value} (出现{stats['count']}次, 最高置信度{stats['confidence']:.3f})")
        
        # 显示每个文档的详细结果
        print(f"\n📄 分文档结果:")
        for i, doc_data in doc_entities.items():
            doc_info = doc_data['doc_info']
            entities = doc_data['entities']
            
            print(f"\n  文档 {i+1}: {doc_info.title[:60]}...")
            print(f"    相似度: {doc_info.similarity:.3f}")
            print(f"    抽取实体: {len(entities)} 个")
            
            if entities:
                # 按类型分组显示
                doc_by_type = {}
                for entity in entities:
                    if entity.entity_type not in doc_by_type:
                        doc_by_type[entity.entity_type] = []
                    doc_by_type[entity.entity_type].append(entity.entity_value)
                
                for entity_type, values in doc_by_type.items():
                    unique_values = list(set(values))[:3]  # 去重，显示前3个
                    print(f"      {entity_type}: {', '.join(unique_values)}")
        
        return {
            'search_results': search_results,
            'all_entities': all_entities,
            'entity_stats': entity_stats,
            'processing_time': {
                'search_time': search_time,
                'extract_time': extract_time,
                'total_time': total_time
            }
        }
    
    def interactive_mode(self):
        """交互式模式"""
        print("🎯 交互式信息检索+抽取系统")
        print("=" * 60)
        
        # 显示功能介绍
        self._show_introduction()
        
        while True:
            try:
                print(f"\n当前模式: {self._get_mode_description()}")
                user_input = input("请输入命令或查询 (输入 'help' 查看帮助): ").strip()
                
                if not user_input:
                    continue
                
                # 处理命令
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 再见！")
                    break
                
                elif user_input.lower() == 'help':
                    self._show_help()
                    continue
                
                elif user_input.lower().startswith('mode '):
                    mode = user_input[5:].strip()
                    self._change_mode(mode)
                    continue
                
                elif user_input.lower() == 'demo':
                    self._run_demo()
                    continue
                
                elif user_input.lower() == 'stats':
                    self._show_stats()
                    continue
                
                elif user_input.lower().startswith('extract '):
                    text = user_input[8:].strip()
                    self.extract_only(text)
                    continue
                
                # 处理查询
                if self.current_mode == "search_only":
                    self.search_only(user_input)
                elif self.current_mode == "extract_only":
                    print("❌ 抽取模式需要使用 'extract 文本内容' 格式")
                else:  # integrated mode
                    self.integrated_search_extract(user_input)
                
            except KeyboardInterrupt:
                print("\n👋 再见！")
                break
            except Exception as e:
                print(f"❌ 处理失败: {e}")
    
    def _show_introduction(self):
        """显示系统介绍"""
        print("\n📖 系统功能:")
        print("  🔍 信息检索 (作业2): 从文档库中找到与查询相关的文档")
        print("  🔬 信息抽取 (作业3): 从文档中抽取结构化实体信息")
        print("  🎯 集成模式: 先检索后抽取，获得结构化知识")
        
        print("\n💡 使用场景对比:")
        print("  信息检索: '想了解关于Biden的新闻' → 返回相关新闻文档")
        print("  信息抽取: '从这段文本中找出所有人名和地名' → 返回实体列表")
        print("  集成模式: '关于Ukraine的新闻中涉及哪些人物和金额?' → 检索+抽取")
    
    def _show_help(self):
        """显示帮助信息"""
        print("\n📋 命令帮助:")
        print("  直接输入查询 - 根据当前模式执行搜索或抽取")
        print("  extract 文本内容 - 对指定文本进行实体抽取")
        print("  mode search - 切换到纯检索模式")
        print("  mode extract - 切换到纯抽取模式") 
        print("  mode integrated - 切换到集成模式（默认）")
        print("  demo - 运行预设演示")
        print("  stats - 显示系统统计")
        print("  help - 显示此帮助")
        print("  quit - 退出程序")
        
        print("\n🎯 推荐查询示例:")
        print("  NPR funding lawsuit - 政治、法律、金额实体丰富")
        print("  Biden Ukraine aid - 人名、地名、金额")
        print("  Katherine Maher testimony - 人名、组织、时间")
        print("  China trade tariffs - 国家、经济、百分比")
    
    def _get_mode_description(self):
        """获取当前模式描述"""
        descriptions = {
            'search_only': '🔍 纯检索模式 (作业2功能)',
            'extract_only': '🔬 纯抽取模式 (作业3功能)',
            'integrated': '🎯 集成模式 (检索+抽取)'
        }
        return descriptions.get(self.current_mode, '未知模式')
    
    def _change_mode(self, mode: str):
        """切换操作模式"""
        valid_modes = ['search', 'extract', 'integrated']
        mode_map = {
            'search': 'search_only',
            'extract': 'extract_only', 
            'integrated': 'integrated'
        }
        
        if mode in valid_modes:
            self.current_mode = mode_map[mode]
            print(f"✅ 已切换到: {self._get_mode_description()}")
        else:
            print(f"❌ 无效模式。有效选项: {', '.join(valid_modes)}")
    
    def _run_demo(self):
        """运行演示"""
        demo_queries = [
            "NPR funding lawsuit",
            "Biden Ukraine aid", 
            "Katherine Maher testimony"
        ]
        
        print("\n🎬 运行预设演示...")
        for query in demo_queries:
            print(f"\n{'='*50}")
            self.integrated_search_extract(query, top_k=3)
            time.sleep(2)
    
    def _show_stats(self):
        """显示系统统计"""
        print("\n📊 系统统计:")
        
        if self.extraction_manager:
            extract_stats = self.extraction_manager.get_summary_statistics()
            print(f"  🔬 抽取系统:")
            print(f"    处理文档: {extract_stats['total_documents_processed']}")
            print(f"    总抽取数: {extract_stats['total_extractions']}")
            print(f"    平均置信度: {extract_stats['average_confidence']:.3f}")
        
        if self.search_engine:
            search_info = self.search_engine.get_system_info()
            print(f"  🔍 检索系统:")
            print(f"    状态: {search_info.get('系统状态', '未知')}")
            if '文档统计' in search_info:
                print(f"    文档数: {search_info['文档统计'].get('总文档数', '未知')}")


def main():
    """主函数"""
    print("🚀 启动交互式集成系统")
    
    # 初始化系统
    system = InteractiveIntegratedSystem("data/npr_articles.json")
    if not system.initialize():
        print("❌ 系统初始化失败")
        return 1
    
    # 启动交互模式
    system.interactive_mode()
    
    return 0

if __name__ == "__main__":
    exit(main())