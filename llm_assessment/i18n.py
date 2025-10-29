class i18n:
    """Simple internationalization support class."""
    
    # Default language
    _language = 'en'
    
    # Translation dictionary
    _translations = {
        'en': {
            '--- Starting Batch Processing Suite (v2) ---': '--- Starting Batch Processing Suite (v2) ---',
            '*** DEBUG MODE ENABLED ***': '*** DEBUG MODE ENABLED ***',
            'Running Test Suite': 'Running Test Suite',
            'Unnamed Suite': 'Unnamed Suite',
            'Warning: Model \'{model_name}\' not found in config. Skipping.': 'Warning: Model \'{model_name}\' not found in config. Skipping.',
            '--- Skipping model {model_name} (previously failed connectivity test) ---': '--- Skipping model {model_name} (previously failed connectivity test) ---',
            '--- Checking connectivity for model: {model_id} ---': '--- Checking connectivity for model: {model_id} ---',
            '!!! Connectivity test failed for {model_id}. Skipping all tasks for this model. !!!': '!!! Connectivity test failed for {model_id}. Skipping all tasks for this model. !!!',
            '--- Connectivity OK for {model_id} ---': '--- Connectivity OK for {model_id} ---',
            '--- Running Task: \'{task_name}\' for Model: \'{model_name}\' ---': '--- Running Task: \'{task_name}\' for Model: \'{model_name}\' ---',
            'Error: Task \'{task_name}\' is missing \'test_file\' or model is invalid. Skipping.': 'Error: Task \'{task_name}\' is missing \'test_file\' or model is invalid. Skipping.',
            'Warning: Unknown task type \'{task_type}\'. Skipping.': 'Warning: Unknown task type \'{task_type}\'. Skipping.',
            '    -> Executing command: {command}': '    -> Executing command: {command}',
            '    -> Retry attempt {retry_count}/{max_retries}': '    -> Retry attempt {retry_count}/{max_retries}',
            '    -> Starting task execution...': '    -> Starting task execution...',
            'Task \'{task_name}\' completed successfully for \'{model_name}\'': 'Task \'{task_name}\' completed successfully for \'{model_name}\'',
            '  !! ERROR running task \'{task_name}\' for \'{model_name}\'': '  !! ERROR running task \'{task_name}\' for \'{model_name}\'',
            '  !! Return Code: {returncode}': '  !! Return Code: {returncode}',
            '  -> Retrying in 5 seconds...': '  -> Retrying in 5 seconds...',
            '  -> Cleaned up empty directory: {dir}': '  -> Cleaned up empty directory: {dir}',
            '  !! Warning: Could not clean up directory {dir}: {error}': '  !! Warning: Could not clean up directory {dir}: {error}',
            '  !! Unexpected ERROR running task \'{task_name}\' for \'{model_name}\': {error}': '  !! Unexpected ERROR running task \'{task_name}\' for \'{model_name}\': {error}',
            'Error loading {config_file}: {e}': 'Error loading {config_file}: {e}',
            '\n--- Batch Processing Suite Finished ---': '\n--- Batch Processing Suite Finished ---',
            '**Total execution time:** {duration}': '**Total execution time:** {duration}',
            '\n--- Generating Summary Report ---': '\n--- Generating Summary Report ---',
            'Batch Suite Summary Report': 'Batch Suite Summary Report',
            'Execution Date:': 'Execution Date:',
            'Total Execution Time:': 'Total Execution Time:',
            'Run Details': 'Run Details',
            'Model': 'Model',
            'Task Name': 'Task Name',
            'Status': 'Status',
            'Report Link': 'Report Link',
            'View Report': 'View Report',
            '  -> Successfully generated {report_path}': '  -> Successfully generated {report_path}',
            '  !! ERROR: Failed to generate summary report: {e}': '  !! ERROR: Failed to generate summary report: {e}',
            'Starting PSY2 assessment': 'Starting PSY2 assessment',
            'Loading test configuration': 'Loading test configuration',
            'Running scenario': 'Running scenario',
            'scenario': 'scenario',
            'prompt': 'prompt',
            'Please enter your response': 'Please enter your response',
            'Analysis complete': 'Analysis complete',
            'Test Results': 'Test Results',
            'dimension': 'dimension',
            'Extraversion': 'Extraversion',
            'Agreeableness': 'Agreeableness',
            'Conscientiousness': 'Conscientiousness',
            'score': 'score',
            'Overall Score': 'Overall Score',
            'Detailed Analysis': 'Detailed Analysis',
            'Agent-IPIP-FFM-50': 'Agent-IPIP-FFM-50',
        },
        'zh': {
            '--- Starting Batch Processing Suite (v2) ---': '--- 开始批处理套件 (v2) ---',
            '*** DEBUG MODE ENABLED ***': '*** 调试模式已启用 ***',
            'Running Test Suite': '运行测试套件',
            'Unnamed Suite': '未命名套件',
            'Warning: Model \'{model_name}\' not found in config. Skipping.': '警告: 在配置中未找到模型 \'{model_name}\'。跳过。',
            '--- Skipping model {model_name} (previously failed connectivity test) ---': '--- 跳过模型 {model_name} (之前的连接测试失败) ---',
            '--- Checking connectivity for model: {model_id} ---': '--- 检查模型连接: {model_id} ---',
            '!!! Connectivity test failed for {model_id}. Skipping all tasks for this model. !!!': '!!! 模型 {model_id} 连接测试失败。跳过该模型的所有任务。 !!!',
            '--- Connectivity OK for {model_id} ---': '--- 模型 {model_id} 连接正常 ---',
            '--- Running Task: \'{task_name}\' for Model: \'{model_name}\' ---': '--- 运行任务: \'{task_name}\' 模型: \'{model_name}\' ---',
            'Error: Task \'{task_name}\' is missing \'test_file\' or model is invalid. Skipping.': '错误: 任务 \'{task_name}\' 缺少 \'test_file\' 或模型无效。跳过。',
            'Warning: Unknown task type \'{task_type}\'. Skipping.': '警告: 未知任务类型 \'{task_type}\'。跳过。',
            '    -> Executing command: {command}': '    -> 执行命令: {command}',
            '    -> Retry attempt {retry_count}/{max_retries}': '    -> 重试 {retry_count}/{max_retries}',
            '    -> Starting task execution...': '    -> 开始任务执行...',
            'Task \'{task_name}\' completed successfully for \'{model_name}\'': '任务 \'{task_name}\' 在模型 \'{model_name}\' 上成功完成',
            '  !! ERROR running task \'{task_name}\' for \'{model_name}\'': '  !! 运行任务 \'{task_name}\' 在模型 \'{model_name}\' 时出错',
            '  !! Return Code: {returncode}': '  !! 返回码: {returncode}',
            '  -> Retrying in 5 seconds...': '  -> 5秒后重试...',
            '  -> Cleaned up empty directory: {dir}': '  -> 清理空目录: {dir}',
            '  !! Warning: Could not clean up directory {dir}: {error}': '  !! 警告: 无法清理目录 {dir}: {error}',
            '  !! Unexpected ERROR running task \'{task_name}\' for \'{model_name}\': {error}': '  !! 运行任务 \'{task_name}\' 在模型 \'{model_name}\' 时发生意外错误: {error}',
            'Error loading {config_file}: {e}': '加载 {config_file} 时出错: {e}',
            '\n--- Batch Processing Suite Finished ---': '\n--- 批处理套件完成 ---',
            '**Total execution time:** {duration}': '**总执行时间:** {duration}',
            '\n--- Generating Summary Report ---': '\n--- 生成摘要报告 ---',
            'Batch Suite Summary Report': '批处理套件摘要报告',
            'Execution Date:': '执行日期:',
            'Total Execution Time:': '总执行时间:',
            'Run Details': '运行详情',
            'Model': '模型',
            'Task Name': '任务名称',
            'Status': '状态',
            'Report Link': '报告链接',
            'View Report': '查看报告',
            '  -> Successfully generated {report_path}': '  -> 成功生成 {report_path}',
            '  !! ERROR: Failed to generate summary report: {e}': '  !! 错误: 生成摘要报告失败: {e}',
            'Starting PSY2 assessment': '开始PSY2评估',
            'Loading test configuration': '加载测试配置',
            'Running scenario': '运行场景',
            'scenario': '场景',
            'prompt': '提示',
            'Please enter your response': '请输入您的回答',
            'Analysis complete': '分析完成',
            'Test Results': '测试结果',
            'dimension': '维度',
            'Extraversion': '外向性',
            'Agreeableness': '宜人性',
            'Conscientiousness': '尽责性',
            'score': '得分',
            'Overall Score': '总分',
            'Detailed Analysis': '详细分析',
            'Agent-IPIP-FFM-50': 'Agent-IPIP-FFM-50',
        }
    }
    
    @classmethod
    def set_language(cls, language):
        """Set the current language."""
        if language in cls._translations:
            cls._language = language
        else:
            cls._language = 'en'  # Default to English if language not supported
    
    @classmethod
    def t(cls, key):
        """Translate a key to the current language."""
        translations = cls._translations.get(cls._language, cls._translations['en'])
        return translations.get(key, key)