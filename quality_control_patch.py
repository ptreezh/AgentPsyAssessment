
# 数据质量增强补丁
# 添加到 three_model_ollama_evaluator.py

def apply_quality_control_enhancement(self):
    """应用质量控制增强"""
    self.min_success_rate = 0.9  # 90%最低成功率
    self.quality_stats = {
        'total_analyzed': 0,
        'passed_quality': 0,
        'failed_quality': 0
    }

def check_data_quality(self, model_results):
    """检查数据质量"""
    success_rates = []
    for model, result in model_results.items():
        if 'success_rate' in result:
            success_rates.append(result['success_rate'])

    if not success_rates:
        return False, 0.0

    avg_success_rate = sum(success_rates) / len(success_rates)
    meets_threshold = avg_success_rate >= self.min_success_rate

    return meets_threshold, avg_success_rate

def enhance_result_with_quality(self, result):
    """增强结果包含质量信息"""
    if 'model_results' in result:
        meets_threshold, success_rate = self.check_data_quality(result['model_results'])

        result['quality_assessment'] = {
            'meets_90_percent_threshold': meets_threshold,
            'average_success_rate': success_rate,
            'quality_score': success_rate * 100,
            'timestamp': datetime.now().isoformat()
        }

        # 更新质量统计
        self.quality_stats['total_analyzed'] += 1
        if meets_threshold:
            self.quality_stats['passed_quality'] += 1
        else:
            self.quality_stats['failed_quality'] += 1

    return result
