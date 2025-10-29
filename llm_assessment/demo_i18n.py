import sys
import os

# Ensure proper encoding for Chinese text
if sys.stdout.encoding != 'utf-8':
    # Reconfigure stdout to use UTF-8
    from python_utf8_config import ensure_utf8
    ensure_utf8()

# Add the project root to the Python path
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

from i18n import i18n

def demo_i18n():
    """
    Demonstrate internationalization functionality.
    """
    print("PSY2 Internationalization Demo")
    print("=" * 40)
    
    # Test English
    print("\n1. English Mode:")
    i18n.set_language('en')
    print(f"   Test Name: {i18n.t('Agent-IPIP-FFM-50')}")
    print(f"   Dimensions: {i18n.t('Extraversion')}, {i18n.t('Agreeableness')}, {i18n.t('Conscientiousness')}")
    print(f"   Messages: {i18n.t('Starting PSY2 assessment')}, {i18n.t('Analysis complete')}")
    
    # Test Chinese
    print("\n2. Chinese Mode:")
    i18n.set_language('zh')
    print(f"   测试名称: {i18n.t('Agent-IPIP-FFM-50')}")
    print(f"   维度: {i18n.t('Extraversion')}, {i18n.t('Agreeableness')}, {i18n.t('Conscientiousness')}")
    print(f"   消息: {i18n.t('Starting PSY2 assessment')}, {i18n.t('Analysis complete')}")
    
    print("\nDemo complete!")

if __name__ == '__main__':
    demo_i18n()