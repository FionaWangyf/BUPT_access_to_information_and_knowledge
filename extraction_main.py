#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
信息抽取系统主程序
提供命令行界面和交互式功能
文件位置：extraction_main.py
"""

import sys
import os
import json
import argparse
from typing import List, Dict, Any
sys.path.append('src')

from src.extraction.extraction_manager import ExtractionManager

class ExtractionApp:
    """信息抽取应用程序"""
    
    def __init__(self):
        self.manager = None
        self.config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'enable_regex_extractor': True,
            'regex_confidence_threshold': 0.6,
            'merge_duplicate_entities': True,
            'max_entities_per_type': 50,
            'enable_cache': True,
            'min_entity_confidence': 0.5
        }
    
    def initialize(self, config_file: str = None) -> bool:
        """初始化应用程序"""
        # 加载配置文件
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                self.config.update(user_config)
                print(f"✅ 已加载配置文件: {config_file}")
            except Exception as e:
                print(f"⚠️ 配置文件加载失败，使用默认配置: {e}")
        
        # 初始化管理器
        self.manager = ExtractionManager(self.config)
        return self.manager.initialize()
    
    def extract_from_text(self, text: str, doc_id: int = 1) -> List[Dict[str, Any]]:
        """从文本中抽取信息"""
        if not self.manager:
            raise RuntimeError("管理器未初始化")
        
        results = self.manager.extract_from_text(text, doc_id, "input")
        return [result.to_dict() for result in results]
    
    def extract_from_file(self, filepath: str) -> List[Dict[str, Any]]:
        """从文件中抽取信息"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
            
            print(f"📄 正在处理文件: {filepath}")
            return self.extract_from_text(text, doc_id=hash(filepath))
            
        except Exception as e:
            print(f"❌ 文件处理失败: {e}")
            return []
    
    def extract_from_npr_data(self, data_file: str = "data/npr_articles.json", 
                             max_articles: int = None) -> Dict[int, List[Dict[str, Any]]]:
        """从NPR数据文件中抽取信息"""
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                articles = json.load(f)
            
            if max_articles:
                articles = articles[:max_articles]
            
            print(f"📰 正在处理 {len(articles)} 篇NPR文章...")
            
            # 创建文档对象
            from test_extraction_system import MockDocument
            documents = []
            for i, article in enumerate(articles):
                doc = MockDocument(
                    doc_id=i,
                    title=article['title'],
                    content=article['content'],
                    summary=article.get('summary', '')
                )
                documents.append(doc)
            
            # 批量处理
            def progress_callback(current, total, progress):
                if current % 10 == 0 or current == total:
                    print(f"  进度: {current}/{total} ({progress:.1%})")
            
            results = self.manager.extract_from_documents(documents, progress_callback)
            
            # 转换为字典格式
            dict_results = {}
            for doc_id, doc_results in results.items():
                dict_results[doc_id] = [result.to_dict() for result in doc_results]
            
            return dict_results
            
        except FileNotFoundError:
            print(f"❌ 数据文件不存在: {data_file}")
            return {}
        except Exception as e:
            print(f"❌ NPR数据处理失败: {e}")
            return {}
    
    def interactive_mode(self):
        """交互式模式"""
        print("🎯 信息抽取系统 - 交互式模式")
        print("=" * 50)
        print("输入 'help' 查看帮助，输入 'quit' 退出")
        
        while True:
            try:
                user_input = input("\n请输入文本 (或命令): ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 再见！")
                    break
                
                if user_input.lower() == 'help':
                    self._show_help()
                    continue
                
                if user_input.lower() == 'stats':
                    self._show_stats()
                    continue
                
                if user_input.lower() == 'config':
                    self._show_config()
                    continue
                
                if user_input.startswith('file:'):
                    filepath = user_input[5:].strip()
                    results = self.extract_from_file(filepath)
                    self._display_results(results)
                    continue
                
                # 普通文本抽取
                results = self.extract_from_text(user_input)
                self._display_results(results)
                
            except KeyboardInterrupt:
                print("\n👋 再见！")
                break
            except Exception as e:
                print(f"❌ 处理失败: {e}")
    
    def _show_help(self):
        """显示帮助信息"""
        print("\n📖 帮助信息:")
        print("  直接输入文本 - 进行信息抽取")
        print("  file:路径     - 从文件中抽取信息")
        print("  stats        - 显示统计信息")
        print("  config       - 显示当前配置")
        print("  help         - 显示此帮助")
        print("  quit/exit/q  - 退出程序")
    
    def _show_stats(self):
        """显示统计信息"""
        if not self.manager:
            print("❌ 管理器未初始化")
            return
        
        stats = self.manager.get_summary_statistics()
        print("\n📊 系统统计信息:")
        print(f"  📄 处理文档数: {stats['total_documents_processed']}")
        print(f"  🔍 总抽取数: {stats['total_extractions']}")
        print(f"  ⭐ 平均置信度: {stats['average_confidence']:.3f}")
        print(f"  ⏱️ 总处理时间: {stats['total_processing_time']:.3f}秒")
        
        if stats['extractions_by_type']:
            print(f"\n📋 各类型统计:")
            for entity_type, count in stats['extractions_by_type'].items():
                print(f"    {entity_type}: {count} 个")
    
    def _show_config(self):
        """显示当前配置"""
        print("\n⚙️ 当前配置:")
        for key, value in self.config.items():
            print(f"  {key}: {value}")
    
    def _display_results(self, results: List[Dict[str, Any]]):
        """显示抽取结果"""
        if not results:
            print("📝 未找到任何实体")
            return
        
        print(f"\n🔍 找到 {len(results)} 个实体:")
        print("-" * 50)
        
        # 按类型分组
        by_type = {}
        for result in results:
            entity_type = result['entity_type']
            if entity_type not in by_type:
                by_type[entity_type] = []
            by_type[entity_type].append(result)
        
        # 显示结果
        for entity_type, type_results in by_type.items():
            print(f"\n🏷️ {entity_type.upper()} ({len(type_results)} 个):")
            
            # 按置信度排序
            sorted_results = sorted(type_results, key=lambda x: x['confidence'], reverse=True)
            
            for result in sorted_results:
                confidence = result['confidence']
                value = result['entity_value']
                field = result['field']
                
                print(f"  ✓ {value}")
                print(f"    置信度: {confidence:.3f} | 字段: {field}")
                
                # 显示上下文（截断）
                context = result.get('context', '')
                if context and len(context) > 80:
                    context = context[:80] + "..."
                if context:
                    print(f"    上下文: {context}")
                print()

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="信息抽取系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python extraction_main.py                     # 交互式模式
  python extraction_main.py --text "文本内容"    # 抽取指定文本
  python extraction_main.py --file input.txt    # 抽取文件内容
  python extraction_main.py --npr-data          # 处理NPR数据
  python extraction_main.py --config config.json # 使用自定义配置
        """
    )
    
    parser.add_argument('--text', type=str, help='要抽取的文本内容')
    parser.add_argument('--file', type=str, help='要抽取的文件路径')
    parser.add_argument('--npr-data', action='store_true', help='处理NPR数据')
    parser.add_argument('--config', type=str, help='配置文件路径')
    parser.add_argument('--output', type=str, help='输出文件路径')
    parser.add_argument('--format', choices=['json', 'csv', 'txt'], default='json', help='输出格式')
    parser.add_argument('--max-articles', type=int, help='最大处理文章数')
    parser.add_argument('--threshold', type=float, default=0.6, help='置信度阈值')
    
    args = parser.parse_args()
    
    # 创建应用程序
    app = ExtractionApp()
    
    # 设置置信度阈值
    if args.threshold:
        app.config['regex_confidence_threshold'] = args.threshold
    
    # 初始化
    if not app.initialize(args.config):
        print("❌ 系统初始化失败")
        return 1
    
    try:
        if args.text:
            # 处理指定文本
            print(f"🔍 抽取文本: {args.text[:100]}...")
            results = app.extract_from_text(args.text)
            app._display_results(results)
            
            if args.output:
                app.manager.export_results(results, args.output, args.format)
        
        elif args.file:
            # 处理文件
            results = app.extract_from_file(args.file)
            app._display_results(results)
            
            if args.output:
                app.manager.export_results(results, args.output, args.format)
        
        elif args.npr_data:
            # 处理NPR数据
            results = app.extract_from_npr_data(max_articles=args.max_articles)
            
            if results:
                total_entities = sum(len(doc_results) for doc_results in results.values())
                print(f"\n✅ 处理完成，总计 {total_entities} 个实体")
                
                # 显示统计
                app._show_stats()
                
                # 保存结果
                output_file = args.output or 'results/npr_extraction_results.json'
                app.manager.export_results(results, output_file, args.format)
                print(f"📤 结果已保存到: {output_file}")
        
        else:
            # 交互式模式
            app.interactive_mode()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n👋 程序被用户中断")
        return 0
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())