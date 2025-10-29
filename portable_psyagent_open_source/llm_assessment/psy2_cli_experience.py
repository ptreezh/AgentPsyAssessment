#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Psy2 Human Assessment CLI - Simple Interactive Experience
"""

import os
import sys
import random

def clear_screen():
    """清屏"""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_welcome():
    """显示欢迎信息"""
    clear_screen()
    print("=" * 60)
    print("           Psy2心理评估CLI工具 - 交互式体验")
    print("=" * 60)
    print()
    print("欢迎使用Psy2心理评估CLI工具！")
    print("在这个交互式体验中，您可以体验完整的心理评估流程。")
    print()
    print("按 Enter 键开始...")

def show_menu():
    """显示主菜单"""
    print("\n" + "=" * 60)
    print("                          主菜单")
    print("=" * 60)
    print("1. 开始新的心理评估会话")
    print("2. 查看可用的心理测试")
    print("3. 完整演示流程")
    print("4. 退出程序")
    print("\n请选择操作 (1-4): ", end="")

def show_tests_menu():
    """显示测试菜单"""
    print("\n" + "=" * 60)
    print("                      可用的心理测试")
    print("=" * 60)
    print("1. IPIP-FFM-50 大五人格测试")
    print("2. DASS-42 抑郁-焦虑-压力量表")
    print("3. 返回主菜单")
    print("\n请选择测试 (1-3): ", end="")

def show_big5_test():
    """进行Big Five测试"""
    print("\n" + "=" * 60)
    print("                 IPIP-FFM-50 大五人格测试")
    print("=" * 60)
    print("说明：请根据您的典型行为和感受，对下列陈述进行评分。")
    print("评分标准：1=非常不准确, 2=比较不准确, 3=中立, 4=比较准确, 5=非常准确")
    
    questions = [
        "我是团队活动的核心人物。",
        "我喜欢与人交往。",
        "我总是做好准备。",
        "我注意细节。",
        "我很少感到忧虑。"
    ]
    
    responses = []
    
    for i, question in enumerate(questions, 1):
        print(f"\n问题 {i}/{len(questions)}: {question}")
        while True:
            try:
                answer = input("请选择 (1-5): ").strip()
                if answer in ["1", "2", "3", "4", "5"]:
                    responses.append(int(answer))
                    break
                else:
                    print("请输入有效的评分 (1-5)")
            except KeyboardInterrupt:
                print("\n\n程序已被用户中断")
                return None
    
    return responses

def show_dass_test():
    """进行DASS测试"""
    print("\n" + "=" * 60)
    print("              DASS-42 抑郁-焦虑-压力量表")
    print("=" * 60)
    print("说明：请指出在过去一周里，下列陈述对您的适用程度。")
    print("评分标准：0=完全不适用, 1=有时适用, 2=经常适用, 3=总是适用")
    
    questions = [
        "我感到难以放松。",
        "我感到口干舌燥。",
        "我似乎没有任何积极的感觉。"
    ]
    
    responses = []
    
    for i, question in enumerate(questions, 1):
        print(f"\n问题 {i}/{len(questions)}: {question}")
        while True:
            try:
                answer = input("请选择 (0-3): ").strip()
                if answer in ["0", "1", "2", "3"]:
                    responses.append(int(answer))
                    break
                else:
                    print("请输入有效的评分 (0-3)")
            except KeyboardInterrupt:
                print("\n\n程序已被用户中断")
                return None
    
    return responses

def show_big5_report(responses):
    """显示Big Five报告"""
    print("\n" + "=" * 60)
    print("                   Big Five 人格测试报告")
    print("=" * 60)
    
    # 模拟分数计算
    scores = {
        "开放性": round(sum(responses) / len(responses), 1),
        "责任心": round(sum(responses) / len(responses) * 1.1, 1),
        "外向性": round(sum(responses) / len(responses) * 0.9, 1),
        "宜人性": round(sum(responses) / len(responses) * 1.05, 1),
        "神经质": round(5 - sum(responses) / len(responses) * 0.8, 1)
    }
    
    print("\n您的人格特质得分 (满分5分):")
    print("-" * 40)
    for trait, score in scores.items():
        bar_length = int(score * 3)
        bar = "█" * bar_length + "░" * (15 - bar_length)
        print(f"{trait:8}: [{bar}] {score}")
    
    print("\n详细分析:")
    print("-" * 40)
    print("责任心 (Conscientiousness) - 高分特质")
    print("   您展现出高度的自律性和组织能力。")
    print("\n宜人性 (Agreeableness) - 中高分特质")
    print("   您在人际交往中表现出合作和友善的倾向。")
    print("\n情绪稳定性 (Neuroticism) - 低分特质")
    print("   您的情绪稳定性较高，面对压力时能够保持冷静。")
    
    print("\n发展建议:")
    print("-" * 40)
    print("1. 职业规划: 建议考虑项目管理、咨询等职业。")
    print("2. 人际关系: 继续发挥您的合作优势。")
    print("3. 个人成长: 可以通过参与创新项目来发展开放性特质。")

def show_dass_report(responses):
    """显示DASS报告"""
    print("\n" + "=" * 60)
    print("                DASS-42 情绪状态评估报告")
    print("=" * 60)
    
    # 模拟分数计算
    scores = {
        "抑郁": sum(responses),
        "焦虑": sum(responses) * 0.8,
        "压力": sum(responses) * 1.2
    }
    
    print("\n您的得分情况:")
    print("-" * 40)
    for dimension, score in scores.items():
        bar_length = min(int(score), 20)
        bar = "█" * bar_length + "░" * (20 - bar_length)
        print(f"{dimension:6}: [{bar}] {int(score)}分")
    
    print("\n详细分析:")
    print("-" * 40)
    print("压力水平 (Stress) - 轻度")
    print("   您目前承受一定程度的生活压力。")
    print("\n焦虑水平 (Anxiety) - 正常范围")
    print("   您的焦虑水平在正常范围内。")
    print("\n抑郁水平 (Depression) - 正常范围")
    print("   您的抑郁水平在正常范围内。")
    
    print("\n应对策略:")
    print("-" * 40)
    print("1. 压力管理: 建议采用正念冥想、规律运动等方法。")
    print("2. 情绪调节: 保持良好的社交联系。")
    print("3. 生活方式: 确保充足睡眠。")

def demo_process():
    """演示完整流程"""
    print("\n开始完整演示...")
    
    # 1. 显示测试选择
    print("\n1. 选择测试:")
    print("   选择 'IPIP-FFM-50 大五人格测试'")
    
    # 2. 模拟测试过程
    print("\n2. 进行测试:")
    questions = [
        "我是团队活动的核心人物。",
        "我喜欢与人交往。",
        "我总是做好准备。"
    ]
    
    responses = []
    for i, question in enumerate(questions, 1):
        answer = random.choice([1, 2, 3, 4, 5])
        print(f"   问题 {i}: {question}")
        print(f"   答案: {answer}")
        responses.append(answer)
    
    # 3. 显示报告
    print("\n3. 生成报告:")
    show_big5_report(responses)
    
    print("\n演示完成！")
    input("\n按 Enter 键返回主菜单...")

def main():
    """主函数"""
    show_welcome()
    try:
        input()
    except KeyboardInterrupt:
        print("\n\n再见！")
        return
    
    while True:
        show_menu()
        try:
            choice = input().strip()
            
            if choice == "1":
                # 开始新的会话
                print("\n创建新的心理评估会话...")
                print("会话已创建！")
                print("会话ID: SESSION-" + "".join(random.choices("0123456789ABCDEF", k=8)))
                
                # 显示测试选择
                while True:
                    show_tests_menu()
                    test_choice = input().strip()
                    
                    if test_choice == "1":
                        # 进行Big Five测试
                        responses = show_big5_test()
                        if responses is not None:
                            show_big5_report(responses)
                            input("\n按 Enter 键返回主菜单...")
                        break
                    
                    elif test_choice == "2":
                        # 进行DASS测试
                        responses = show_dass_test()
                        if responses is not None:
                            show_dass_report(responses)
                            input("\n按 Enter 键返回主菜单...")
                        break
                    
                    elif test_choice == "3":
                        # 返回主菜单
                        break
                    
                    else:
                        print("无效选择，请重新输入。")
            
            elif choice == "2":
                # 查看可用测试
                print("\n" + "=" * 60)
                print("                      可用的心理测试")
                print("=" * 60)
                print("1. IPIP-FFM-50 大五人格测试")
                print("   - 测量五个主要人格维度")
                print("   - 适用于职业规划和个人发展")
                print("\n2. DASS-42 抑郁-焦虑-压力量表")
                print("   - 评估情绪状态")
                print("   - 适用于心理健康监测")
                input("\n按 Enter 键返回主菜单...")
            
            elif choice == "3":
                # 完整演示
                demo_process()
            
            elif choice == "4":
                # 退出程序
                print("\n感谢使用Psy2心理评估CLI工具！再见！")
                break
            
            else:
                print("无效选择，请重新输入。")
        
        except KeyboardInterrupt:
            print("\n\n程序已被用户中断，再见！")
            break
        except Exception as e:
            print(f"\n程序发生错误: {e}")
            print("请按 Enter 键继续...")
            input()

if __name__ == '__main__':
    main()