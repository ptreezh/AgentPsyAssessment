# Contributing to AgentPsyAssessment

We welcome contributions to AgentPsyAssessment! This document provides guidelines and information about how to contribute to the project.

## Table of Contents
- [Ways to Contribute](#ways-to-contribute)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Style](#code-style)
- [Testing](#testing)
- [Documentation](#documentation)
- [Issue Reporting](#issue-reporting)
- [Pull Request Process](#pull-request-process)
- [Community Guidelines](#community-guidelines)

## Ways to Contribute

There are many ways you can contribute to the project:

- **Code**: Implement new features, fix bugs, optimize performance
- **Documentation**: Improve README, write tutorials, update user manuals
- **Testing**: Write tests, verify assessments, check reproducibility
- **Analysis**: Contribute new analytical methods, validation studies
- **Models**: Improve prompt engineering, add new LLM integrations
- **Feedback**: Report bugs, suggest features, improve UX
- **Assessment Component**: Enhance LLM-based questionnaire administration
- **Analysis Component**: Develop new psychometric analysis methods

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your forked repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/AgentPsyAssessment.git
   cd AgentPsyAssessment
   ```
3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # if available
   ```
5. **Create a new branch** for your feature or fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

1. **Create an issue** (if one doesn't exist) describing the problem or feature you want to work on
2. **Assign yourself** to the issue or comment that you're working on it
3. **Create a feature branch** from the main branch
4. **Make your changes** following the code style guidelines
5. **Write tests** if applicable
6. **Update documentation** for new features
7. **Run tests** to ensure everything works
8. **Consider both components** - if working on assessment, consider impacts on analysis and vice versa
9. **Submit a pull request** with a clear description of your changes

## Code Style

### Python Code Style
- Follow PEP 8 style guide
- Use 4 spaces for indentation (no tabs)
- Line length should be less than 100 characters
- Use descriptive variable and function names
- Add type hints where appropriate
- Include docstrings for all public functions and classes

### Example
```python
def calculate_personality_score(responses: List[int], weights: List[float]) -> float:
    """
    Calculate a personality trait score based on responses and weights.

    Args:
        responses: List of numerical responses to personality questions
        weights: List of weights for each response
    
    Returns:
        float: Calculated personality score
    """
    if len(responses) != len(weights):
        raise ValueError("Responses and weights must have the same length")
    
    score = sum(r * w for r, w in zip(responses, weights))
    return score
```

### Git Commit Messages
- Use present tense: "Add feature" not "Added feature"
- Use imperative mood: "Change" not "Changes"
- Limit first line to 72 characters
- Reference issues and pull requests if applicable

## Testing

### Running Tests
```bash
python -m pytest tests/
# Or for more verbose output:
python -m pytest tests/ -v
```

### Writing Tests
- Add tests for new functionality
- Follow pytest conventions
- Keep tests focused and fast
- Test edge cases and error conditions

### Example Test
```python
import pytest
from llm_assessment.analyze_results import validate_assessment

def test_validate_assessment_valid_data():
    """Test validation with valid assessment data."""
    valid_data = {
        "id": "test123",
        "model": "gpt-4o",
        "big_five": {
            "openness": {"raw_score": 50, "percentile": 0.5, "analysis": "test"}
        }
    }
    
    result = validate_assessment(valid_data)
    assert result is True

def test_validate_assessment_invalid_data():
    """Test validation with invalid assessment data."""
    invalid_data = {"id": "test123"}  # Missing required fields
    
    result = validate_assessment(invalid_data)
    assert result is False
```

## Documentation

### Code Documentation
- Include docstrings for all public functions, classes, and modules
- Use Sphinx-style docstrings
- Document parameters, return values, and exceptions

### User Documentation
- Update README.md when adding major features
- Update USER_MANUAL.md for new functionality
- Write clear, concise, and helpful documentation

### Update Process
When making code changes:
1. Update docstrings if changing function signatures or behavior
2. Update README.md for new features or breaking changes
3. Update USER_MANUAL.md for new functionality

## Issue Reporting

### Before Creating an Issue
- Search existing issues to avoid duplicates
- Check if the issue has been resolved in the latest version
- Try to reproduce the issue with a minimal example

### Creating an Issue
When creating an issue, please include:

**For Bug Reports:**
- Clear title summarizing the bug
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Python version and library versions (`pip list`)
- Error messages (with stacktrace if applicable)
- Screenshots if helpful

**For Feature Requests:**
- Clear title describing the feature
- Motivation for the feature
- Proposed implementation approach
- Potential alternatives considered
- Any additional context

### Example Bug Report
```
Title: Assessment fails when using certain Ollama models

Description:
When running an assessment with the phi3 model from Ollama, the assessment fails with a JSON parsing error.

Steps to reproduce:
1. Install Ollama and pull phi3 model
2. Run: python run_assessment_unified.py --model phi3 --ollama
3. Error occurs during response parsing

Expected: Assessment completes successfully
Actual: JSON parsing error

Version: Python 3.9, Ollama 0.1.22
Error: json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

## Pull Request Process

1. **Follow the development workflow** described above
2. **Ensure your code is well-documented** and follows the style guidelines
3. **Write tests** for your changes if applicable
4. **Run the full test suite** to ensure no regressions
5. **Update documentation** for new features
6. **Fill out the pull request template** (if available)
7. **Submit your pull request** with a clear description
8. **Respond to feedback** from maintainers in a timely manner

### Pull Request Template
When creating a pull request, please include:

- **Title**: Brief summary of the changes
- **Description**: Detailed explanation of the changes, including:
  - What problem this solves
  - How it's implemented
  - Any breaking changes
  - Related issues (if applicable)

### Example Pull Request Description
```
Title: Add support for new LLM model integration

Description:
This PR adds support for the new Gemini 1.5 Pro model integration.

Changes:
- Added new model configuration in services/llm_client.py
- Updated model settings in config.json
- Added tests for the new model integration
- Updated documentation in README.md

Fixes #123

Testing:
- Ran all existing tests - all pass
- Added new tests for Gemini 1.5 Pro - all pass
- Manually tested the new model with sample assessments
```

## Community Guidelines

### Be Respectful
- Be respectful to other contributors and maintainers
- Use welcoming and inclusive language
- Be patient with newcomers
- Be constructive in discussions

### Be Collaborative
- Be open to feedback and suggestions
- Be willing to help others
- Share knowledge and expertise
- Collaborate to solve problems

### Be Professional
- Keep discussions focused on the project
- Avoid personal attacks or offensive language
- Focus on technical aspects of contributions
- Be objective when reviewing code

## First Time Contributors

We welcome first-time contributors! Here are some ways to get started:

### Good First Issues
Look for issues labeled `good first issue` or `beginner-friendly` in the issue tracker.

### Simple Ways to Contribute
- Improve documentation
- Fix typos in README or code comments
- Update or add examples
- Report bugs you've found
- Answer questions in the issue tracker

### Setting Up Your Environment
Follow the installation instructions in the README to set up your development environment.

## Questions?
If you have questions about contributing:
- Check the existing issues
- Open a new issue labeled as "question"
- Contact the maintainers through the project repository

Thank you for contributing to AgentPsyAssessment!