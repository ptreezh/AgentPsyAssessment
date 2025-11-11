#!/usr/bin/env python3
"""
Configuration file validator for unified assessment skills system.

This module provides validation and loading functionality for assessment type
configuration files, ensuring they meet the required schema and standards.
"""

import json
import os
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import jsonschema


class ConfigurationValidator:
    """Validates and loads assessment type configuration files."""

    # Configuration schema definition
    SCHEMA = {
        "type": "object",
        "required": [
            "assessment_type", "name", "description", "scoring_method",
            "dimensions", "evaluation_focus", "report_template"
        ],
        "properties": {
            "assessment_type": {
                "type": "string",
                "pattern": "^[a-z_]+$",
                "description": "Unique identifier for the assessment type"
            },
            "name": {
                "type": "string",
                "minLength": 3,
                "maxLength": 100,
                "description": "Human-readable name of the assessment"
            },
            "description": {
                "type": "string",
                "minLength": 10,
                "maxLength": 500,
                "description": "Detailed description of the assessment type"
            },
            "scoring_method": {
                "type": "string",
                "enum": [
                    "rating_scale", "keyword_matching", "professional_scoring",
                    "motivation_analysis", "thinking_analysis", "big_five_scoring"
                ],
                "description": "Method used for scoring responses"
            },
            "dimensions": {
                "type": "array",
                "minItems": 1,
                "maxItems": 20,
                "items": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 50
                },
                "description": "List of dimensions assessed by this type"
            },
            "evaluation_focus": {
                "type": "array",
                "minItems": 1,
                "maxItems": 10,
                "items": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 100
                },
                "description": "Key focus areas for evaluation"
            },
            "report_template": {
                "type": "string",
                "enum": [
                    "personality_report", "knowledge_report", "professional_report",
                    "motivation_report", "thinking_report", "comprehensive_report"
                ],
                "description": "Type of report template to use"
            },
            "keywords": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional keywords for type identification"
            },
            "file_patterns": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional file patterns for auto-detection"
            },
            "response_format": {
                "type": "object",
                "properties": {
                    "type": {"type": "string"},
                    "validation_rules": {"type": "array"}
                },
                "description": "Expected format for responses"
            },
            "scoring_weights": {
                "type": "object",
                "patternProperties": {
                    "^[a-z_]+$": {"type": "number", "minimum": 0, "maximum": 1}
                },
                "description": "Optional weights for different dimensions"
            }
        },
        "additionalProperties": True
    }

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the configuration validator.

        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = Path(config_dir) if config_dir else None
        self.validator = jsonschema.Draft7Validator(self.SCHEMA)

    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate a configuration dictionary against the schema.

        Args:
            config: Configuration dictionary to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        for error in self.validator.iter_errors(config):
            error_path = " -> ".join(str(p) for p in error.path) if error.path else "root"
            errors.append(f"Error at {error_path}: {error.message}")

        return len(errors) == 0, errors

    def load_config(self, config_path: str) -> Tuple[Optional[Dict[str, Any]], List[str]]:
        """
        Load and validate a configuration file.

        Args:
            config_path: Path to the configuration file

        Returns:
            Tuple of (config_dict, error_messages)
        """
        errors = []

        # Check if file exists
        if not os.path.exists(config_path):
            errors.append(f"Configuration file not found: {config_path}")
            return None, errors

        # Load JSON file
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON in {config_path}: {e}")
            return None, errors
        except Exception as e:
            errors.append(f"Error loading {config_path}: {e}")
            return None, errors

        # Validate against schema
        is_valid, validation_errors = self.validate_config(config)
        if not is_valid:
            errors.extend(validation_errors)
            return None, errors

        return config, errors

    def load_all_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        Load all valid configuration files from the config directory.

        Returns:
            Dictionary mapping assessment_type to config_dict
        """
        configs = {}

        if not self.config_dir or not self.config_dir.exists():
            return configs

        for config_file in self.config_dir.glob("*.json"):
            config, errors = self.load_config(str(config_file))
            if config:
                configs[config["assessment_type"]] = config
            else:
                print(f"Warning: Failed to load {config_file}: {'; '.join(errors)}")

        return configs

    def create_config_template(self, assessment_type: str) -> Dict[str, Any]:
        """
        Create a configuration template for a new assessment type.

        Args:
            assessment_type: The assessment type identifier

        Returns:
            Configuration dictionary template
        """
        return {
            "assessment_type": assessment_type,
            "name": f"{assessment_type.replace('_', ' ').title()} Assessment",
            "description": f"Comprehensive {assessment_type.replace('_', ' ')} assessment and evaluation",
            "scoring_method": "rating_scale",
            "dimensions": ["dimension1", "dimension2"],
            "evaluation_focus": ["focus_area1", "focus_area2"],
            "report_template": "comprehensive_report",
            "keywords": [],
            "file_patterns": [],
            "response_format": {
                "type": "text",
                "validation_rules": []
            },
            "scoring_weights": {
                "dimension1": 0.5,
                "dimension2": 0.5
            }
        }

    def save_config(self, config: Dict[str, Any], output_path: str) -> Tuple[bool, List[str]]:
        """
        Validate and save a configuration file.

        Args:
            config: Configuration dictionary to save
            output_path: Path where to save the configuration

        Returns:
            Tuple of (success, error_messages)
        """
        # Validate configuration
        is_valid, errors = self.validate_config(config)
        if not is_valid:
            return False, errors

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save configuration
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True, []
        except Exception as e:
            return False, [f"Error saving configuration to {output_path}: {e}"]

    def get_config_summary(self, config: Dict[str, Any]) -> str:
        """
        Generate a human-readable summary of a configuration.

        Args:
            config: Configuration dictionary

        Returns:
            Summary string
        """
        return f"""
Configuration Summary:
- Assessment Type: {config.get('assessment_type', 'N/A')}
- Name: {config.get('name', 'N/A')}
- Description: {config.get('description', 'N/A')[:100]}{'...' if len(config.get('description', '')) > 100 else ''}
- Scoring Method: {config.get('scoring_method', 'N/A')}
- Dimensions: {', '.join(config.get('dimensions', []))}
- Evaluation Focus: {', '.join(config.get('evaluation_focus', []))}
- Report Template: {config.get('report_template', 'N/A')}
        """.strip()


def main():
    """Command-line interface for configuration validation."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate assessment configuration files")
    parser.add_argument("config_file", help="Configuration file to validate")
    parser.add_argument("--schema", action="store_true", help="Show configuration schema")
    parser.add_argument("--template", help="Generate a config template for assessment type")

    args = parser.parse_args()

    validator = ConfigurationValidator()

    if args.schema:
        print("Configuration Schema:")
        print(json.dumps(validator.SCHEMA, indent=2))
        return

    if args.template:
        template = validator.create_config_template(args.template)
        print(f"Configuration template for '{args.template}':")
        print(json.dumps(template, indent=2))
        return

    # Validate configuration file
    config, errors = validator.load_config(args.config_file)

    if config:
        print(f"✅ Configuration file '{args.config_file}' is valid!")
        print(validator.get_config_summary(config))
    else:
        print(f"❌ Configuration file '{args.config_file}' has errors:")
        for error in errors:
            print(f"  - {error}")


if __name__ == "__main__":
    main()