#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
少数派文章爬虫主程序
支持单篇文章、批量处理和大规模范围爬取
"""

from sspai_scraper import SSPaiScraper
import logging

def main():
    """主函数 - 演示不同的使用方式"""
    print("=== 少数派文章爬虫 ===\n")
    
    # 创建爬虫实例
    try:
        scraper = SSPaiScraper()
        print("✓ 爬虫初始化成功")
    except ValueError as e:
        print(f"❌ 错误: {e}")
        print("请设置环境变量 OPENAI_API_KEY")
        print("例如: export OPENAI_API_KEY='your-api-key-here'")
        return
    
    print("\n请选择运行模式:")
    print("1. 处理单篇文章（示例）")
    print("2. 批量处理文章列表（示例）") 
    print("3. 大规模范围爬取（推荐用于数据采集）")
    print("4. 交互式模式")
    
    choice = input("\n请输入选择 (1-4): ").strip()
    
    if choice == "1":
        demo_single_article(scraper)
    elif choice == "2":
        demo_batch_processing(scraper)
    elif choice == "3":
        demo_range_crawling(scraper)
    elif choice == "4":
        interactive_mode(scraper)
    else:
        print("无效选择，使用默认的大规模爬取模式")
        demo_range_crawling(scraper)

def demo_single_article(scraper):
    """演示单篇文章处理"""
    print("\n--- 示例1: 处理单篇文章 ---")
    article_id = "92777"  # 可以修改为实际存在的文章ID
    print(f"正在处理文章ID: {article_id}")
    
    result = scraper.process_article(article_id)
    if result:
        print(f"✓ 处理成功!")
        print(f"标题: {result['title']}")
        print(f"作者: {result['author']}")
        print(f"摘要: {result['summary'][:200]}...")
    else:
        print(f"❌ 处理失败，请检查文章ID是否正确")

def demo_batch_processing(scraper):
    """演示批量处理"""
    print("\n--- 示例2: 批量处理文章 ---")
    article_ids = ["92777", "92778", "92779"]  # 可以修改为实际的文章ID
    print(f"正在批量处理 {len(article_ids)} 篇文章...")
    
    results = scraper.process_multiple_articles(article_ids, delay=1.0)
    
    if results:
        print(f"✓ 成功处理 {len(results)} 篇文章")
        
        # 保存结果
        json_filename = "demo_articles.json"
        md_filename = "demo_articles_report.md"
        
        scraper.save_results(results, json_filename)
        scraper.generate_markdown_report(results, md_filename)
        
        print(f"✓ JSON结果已保存到: {json_filename}")
        print(f"✓ Markdown报告已保存到: {md_filename}")
    else:
        print("❌ 批量处理失败")

def demo_range_crawling(scraper):
    """演示大规模范围爬取"""
    print("\n--- 大规模范围爬取 ---")
    print("这是本项目的核心功能，适用于大规模数据采集")
    
    # 获取用户输入的范围
    try:
        start_id = int(input("请输入起始文章ID (默认90001): ") or "90001")
        end_id = int(input("请输入结束文章ID (默认90100): ") or "90100")
        output_file = input("请输入输出文件名 (默认abstract.jsonl): ") or "abstract.jsonl"
        delay = float(input("请输入请求间隔秒数 (默认0.2): ") or "0.2")
    except ValueError:
        print("输入错误，使用默认参数")
        start_id, end_id, output_file, delay = 90001, 90100, "abstract.jsonl", 0.2
    
    print(f"\n开始爬取文章 ID 范围: {start_id} - {end_id-1}")
    print(f"输出文件: {output_file}")
    print(f"请求间隔: {delay} 秒")
    print("按 Ctrl+C 可以随时停止\n")
    
    try:
        scraper.process_article_range(
            start_id=start_id,
            end_id=end_id,
            output_file=output_file,
            delay=delay
        )
        print(f"\n✓ 爬取完成！结果已保存到 {output_file}")
    except KeyboardInterrupt:
        print(f"\n⚠️ 用户中断，已保存的数据在 {output_file} 中")
    except Exception as e:
        print(f"\n❌ 爬取过程中出现错误: {e}")

def interactive_mode(scraper):
    """交互式模式"""
    print("\n=== 交互式模式 ===")
    
    while True:
        print("\n请选择操作:")
        print("1. 处理单篇文章")
        print("2. 批量处理文章")
        print("3. 范围爬取")
        print("4. 分析HTML结构")
        print("5. 返回主菜单")
        
        choice = input("\n请输入选择 (1-5): ").strip()
        
        if choice == "1":
            article_id = input("请输入文章ID: ").strip()
            if article_id:
                result = scraper.process_article(article_id)
                if result:
                    print(f"\n标题: {result['title']}")
                    print(f"作者: {result['author']}")
                    print(f"摘要: {result['summary']}")
                else:
                    print("处理失败")
        
        elif choice == "2":
            ids_input = input("请输入文章ID列表（用逗号分隔）: ").strip()
            if ids_input:
                article_ids = [id.strip() for id in ids_input.split(",") if id.strip()]
                if article_ids:
                    results = scraper.process_multiple_articles(article_ids)
                    if results:
                        filename = input("请输入保存文件名（不含扩展名，默认为articles）: ").strip() or "articles"
                        scraper.save_results(results, f"{filename}.json")
                        scraper.generate_markdown_report(results, f"{filename}.md")
                        print(f"结果已保存到 {filename}.json 和 {filename}.md")
        
        elif choice == "3":
            try:
                start_id = int(input("起始ID: "))
                end_id = int(input("结束ID: "))
                output_file = input("输出文件名 (默认range_output.jsonl): ") or "range_output.jsonl"
                delay = float(input("请求间隔 (默认0.2): ") or "0.2")
                
                scraper.process_article_range(start_id, end_id, output_file, delay)
                print(f"完成！结果保存在 {output_file}")
            except (ValueError, KeyboardInterrupt) as e:
                print(f"操作取消或输入错误: {e}")
        
        elif choice == "4":
            html_file = input("请输入HTML文件路径: ").strip()
            if html_file:
                try:
                    scraper.analyze_html_structure(html_file)
                except Exception as e:
                    print(f"分析失败: {e}")
        
        elif choice == "5":
            break
        
        else:
            print("无效选择，请重试")

if __name__ == "__main__":
    # 设置日志级别
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    main()