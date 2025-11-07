---
name: evaluation-report-generator
description: Generate comprehensive HTML evaluation reports for psychological assessments and personality-based AI testing
allowed-tools:
  - Bash
  - Read
  - Write
---

# Evaluation Report Generator Skill

This skill generates comprehensive HTML evaluation reports for psychological assessments, personality-based AI testing, and knowledge evaluation scenarios.

## When to Use This Skill

Activate this skill when you need to:
- Generate professional HTML reports from assessment results
- Create personality-based evaluation reports with detailed analysis
- Produce interactive multi-tab reports for complex assessments
- Format question-answer pairs with detailed reasoning
- Create visual dashboards for assessment outcomes

## Capabilities

### Report Generation Features
- **Multi-TAB Interface**: Interactive tabbed navigation for different report sections
- **Visual Data Display**: Charts, score cards, and statistical visualizations
- **Q&A Analysis**: Detailed question-answer breakdown with reasoning
- **Personality Analysis**: MBTI trait consistency evaluation
- **Interactive Filtering**: Search and filter capabilities for large datasets
- **Responsive Design**: Mobile-friendly layout with modern UI

### Assessment Types Supported
- **Personality-Based Assessments**: MBTI, Big Five, and other personality frameworks
- **Knowledge Evaluation**: Subject matter testing with keyword matching
- **Psychological Analysis**: Comprehensive mental health assessments
- **Comparative Analysis**: Multiple personality type comparisons
- **Application Scenarios**: Use case recommendations and implementation guidance

## Usage Examples

### Generate Report from Assessment Results
```bash
Generate a comprehensive HTML evaluation report from assessment data
--input-file assessment_results.json
--output-file html/evaluation_report.html
--template-style professional
--include-qa-analysis
--add-personality-analysis
```

### Create Personality Comparison Report
```bash
Create comparative analysis report for multiple personality types
--assessment-data intj_results.json enfj_results.json estp_results.json
--output-file html/personality_comparison.html
--comparison-metrics scores consistency traits
--application-scenarios
```

### Knowledge Assessment Report
```bash
Generate knowledge evaluation report with detailed Q&A analysis
--data-file knowledge_assessment.json
--output-file html/knowledge_report.html
--include-keyword-matching
--add-reliability-analysis
--tab-sections methodology results applications
```

## Input Data Format

### Assessment Results JSON Structure
```json
{
  "assessment_metadata": {
    "persona": "INTJ",
    "test_name": "National Knowledge Assessment",
    "date": "[CURRENT_DATE]",
    "total_questions": 42
  },
  "evaluation_results": {
    "overall_score": 96.5,
    "grade": "A+",
    "dimension_scores": {
      "historical_knowledge": 97.5,
      "geographical_knowledge": 96.0,
      "political_knowledge": 96.8,
      "cultural_knowledge": 95.2,
      "comprehensive_analysis": 98.0
    },
    "personality_consistency": 98.0,
    "keyword_match_rate": 97.2
  },
  "detailed_responses": [
    {
      "question_id": "history_1",
      "question": "中国的四大发明是什么？",
      "dimension": "historical_knowledge",
      "response": "中国的四大发明是：造纸术、指南针、火药、印刷术...",
      "reasoning": "作为INTJ，我倾向于系统性地整理和呈现信息...",
      "keywords_matched": ["造纸术", "指南针", "火药", "印刷术"]
    }
  ]
}
```

## Output Features

### Interactive TAB Structure
1. **📊 评测概览** - Overall assessment overview and key metrics
2. **🔬 评测方法** - Methodology, reliability, and validity analysis
3. **📈 详细评分** - Detailed scoring breakdown and statistics
4. **❓ 问答分析** - Interactive Q&A analysis with filtering
5. **🎯 应用场景** - Application scenarios and use cases
6. **📊 对比分析** - Comparative analysis with other types
7. **📝 结论建议** - Conclusions and recommendations

### Visual Elements
- **Score Cards**: Color-coded performance metrics
- **Data Tables**: Comprehensive statistical breakdowns
- **Personality Grids**: MBTI trait analysis visualization
- **Interactive Filters**: Search and dimension-based filtering
- **Pagination**: Large dataset navigation

### Footer Integration
- **AI人格实验室**: Links to https://cn.agentpsy.com
- **Professional Branding**: Consistent with AI personality research
- **Contact Information**: Research center and resource links

## Implementation Notes

### Technical Features
- **Responsive Design**: Mobile and desktop optimized
- **Interactive JavaScript**: Dynamic content loading and filtering
- **Modern CSS**: Gradient backgrounds, animations, and transitions
- **Accessibility**: Screen reader compatible and keyboard navigation
- **Performance**: Optimized loading with lazy content initialization

### Customization Options
- **Color Themes**: Adjustable color schemes for different personality types
- **Language Support**: Multi-language report generation
- **Branding**: Custom logos and organization information
- **Data Sources**: Support for various assessment frameworks
- **Export Formats**: HTML with optional PDF conversion

### Quality Assurance
- **Scientific Validity**: Based on established psychological assessment principles
- **Statistical Reliability**: Comprehensive reliability and validity analysis
- **Professional Standards**: Adherence to psychological testing standards
- **Privacy Protection**: Data anonymization and secure handling

## Future Enhancements

### Planned Features
- **Real-time Updates**: Dynamic assessment result streaming
- **Advanced Analytics**: Machine learning-based pattern recognition
- **Integration APIs**: Connection with assessment platforms
- **Collaborative Features**: Multi-user assessment sharing
- **Mobile Applications**: Native mobile report viewing

### Research Applications
- **Longitudinal Studies**: Progress tracking over time
- **Cross-cultural Validation**: International assessment comparison
- **Clinical Applications**: Mental health assessment integration
- **Educational Uses**: Learning outcome evaluation

This skill provides a comprehensive solution for generating professional, interactive, and scientifically sound evaluation reports for psychological and knowledge-based assessments.