#!/usr/bin/env python3
"""
Assessment type detection module for unified assessment skills system.

This module provides automatic detection of assessment types based on file content,
structure, and naming patterns. It supports multiple detection strategies with
confidence scoring.
"""

import json
import os
import re
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path
from dataclasses import dataclass
from collections import Counter


@dataclass
class DetectionResult:
    """Result of assessment type detection."""
    assessment_type: str
    confidence: float
    method: str
    details: Dict[str, Any]


class AssessmentTypeDetector:
    """Detects assessment types from various input sources."""

    def __init__(self, configs: Dict[str, Dict[str, Any]]):
        """
        Initialize the detector with assessment configurations.

        Args:
            configs: Dictionary mapping assessment_type to config_dict
        """
        self.configs = configs
        self.detection_strategies = [
            self._detect_by_filename,
            self._detect_by_keywords,
            self._detect_by_structure,
            self._detect_by_content,
            self._detect_by_dimensions
        ]

    def detect_from_file(self, file_path: str) -> DetectionResult:
        """
        Detect assessment type from a JSON file.

        Args:
            file_path: Path to the assessment file

        Returns:
            DetectionResult with best match
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Assessment file not found: {file_path}")

        # Load file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
        except Exception as e:
            raise ValueError(f"Error loading assessment file: {e}")

        return self.detect_from_content(content, os.path.basename(file_path))

    def detect_from_content(self, content: Dict[str, Any], filename: str = "") -> DetectionResult:
        """
        Detect assessment type from content dictionary.

        Args:
            content: Assessment content dictionary
            filename: Optional filename for additional context

        Returns:
            DetectionResult with best match
        """
        results = []

        # Apply all detection strategies
        for strategy in self.detection_strategies:
            try:
                result = strategy(content, filename)
                if result:
                    results.append(result)
            except Exception as e:
                print(f"Warning: Detection strategy {strategy.__name__} failed: {e}")

        # If no detection succeeded, return default
        if not results:
            return DetectionResult(
                assessment_type="big_five_personality",
                confidence=0.5,
                method="default",
                details={"reason": "No specific detection patterns matched"}
            )

        # Select result with highest confidence
        best_result = max(results, key=lambda r: r.confidence)

        # Boost confidence if multiple methods agree
        matching_types = [r for r in results if r.assessment_type == best_result.assessment_type]
        if len(matching_types) > 1:
            best_result.confidence = min(0.95, best_result.confidence + 0.2)
            best_result.details["supporting_methods"] = [r.method for r in matching_types if r != best_result]

        return best_result

    def _detect_by_filename(self, content: Dict[str, Any], filename: str) -> Optional[DetectionResult]:
        """Detect assessment type based on filename patterns."""
        filename_lower = filename.lower()

        # Pattern matching for assessment types
        patterns = {
            "big_five_personality": [
                r"big[_\s]*five", r"b5", r"ocean", r"personality", r"mbti",
                r"agent.*big.*five", r"big5"
            ],
            "citizenship_knowledge": [
                r"citizenship", r"citizen", r"公民", r"国民", r"国籍"
            ],
            "financial_professional": [
                r"financial", r"finance", r"bank", r"金融", r"银行", r"investment",
                r"fund", r"基金", r"risk", r"风险"
            ],
            "legal_knowledge": [
                r"legal", r"law", r"court", r"judge", r"法律", r"法院", r"律师",
                r"regulation", r"合规"
            ],
            "motivation_psychology": [
                r"motivation", r"motivational", r"drive", r"动机", r"激励", r"need",
                r"incentive", r"achievement"
            ],
            "political_literacy": [
                r"political", r"politics", r"government", r"policy", r"政治",
                r"政府", r"政策", r"ideology", r"立场"
            ]
        }

        for assessment_type, type_patterns in patterns.items():
            for pattern in type_patterns:
                if re.search(pattern, filename_lower):
                    return DetectionResult(
                        assessment_type=assessment_type,
                        confidence=0.8,
                        method="filename_pattern",
                        details={
                            "matched_pattern": pattern,
                            "filename": filename
                        }
                    )

        return None

    def _detect_by_keywords(self, content: Dict[str, Any], filename: str) -> Optional[DetectionResult]:
        """Detect assessment type based on keyword analysis."""
        # Extract text content from the assessment
        text_content = self._extract_text_content(content)
        text_lower = text_content.lower()

        # Keyword dictionaries for each assessment type
        keyword_sets = {
            "big_five_personality": [
                "personality", "trait", "openness", "conscientiousness", "extraversion",
                "agreeableness", "neuroticism", "ocean", "mbti", "性格", "人格", "特质",
                "外向性", "开放性", "尽责性", "宜人性", "神经质"
            ],
            "citizenship_knowledge": [
                "citizenship", "citizen", "rights", "responsibilities", "democracy",
                "constitution", "voting", "公民", "权利", "责任", "民主", "宪法", "选举"
            ],
            "financial_professional": [
                "financial", "investment", "risk", "portfolio", "asset", "liability",
                "return", "profit", "loss", "market", "金融", "投资", "风险", "资产",
                "收益", "市场", "银行", "基金"
            ],
            "legal_knowledge": [
                "legal", "law", "court", "judge", "lawyer", "contract", "regulation",
                "compliance", "justice", "法律", "法院", "法官", "律师", "合同", "合规"
            ],
            "motivation_psychology": [
                "motivation", "achievement", "goal", "drive", "incentive", "reward",
                "intrinsic", "extrinsic", "动机", "激励", "成就", "目标", "奖励"
            ],
            "political_literacy": [
                "political", "politics", "government", "policy", "democracy", "election",
                "ideology", "left", "right", "政治", "政府", "政策", "民主", "选举"
            ]
        }

        # Count keyword matches for each assessment type
        match_counts = {}
        for assessment_type, keywords in keyword_sets.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            if count > 0:
                match_counts[assessment_type] = count

        if not match_counts:
            return None

        # Select assessment type with most keyword matches
        best_type = max(match_counts, key=match_counts.get)
        match_count = match_counts[best_type]

        # Calculate confidence based on keyword density
        total_keywords = len(keyword_sets[best_type])
        confidence = min(0.9, (match_count / total_keywords) * 1.5)

        return DetectionResult(
            assessment_type=best_type,
            confidence=confidence,
            method="keyword_analysis",
            details={
                "matched_keywords": match_count,
                "total_keywords": total_keywords,
                "all_matches": match_counts
            }
        )

    def _detect_by_structure(self, content: Dict[str, Any], filename: str) -> Optional[DetectionResult]:
        """Detect assessment type based on content structure."""
        structure_indicators = {
            "big_five_personality": [
                ("questions", list),
                ("dimensions", list),
                ("scale", dict),
                ("personality", dict)
            ],
            "citizenship_knowledge": [
                ("questions", list),
                ("citizenship", dict),
                ("knowledge", dict),
                ("civic", dict)
            ],
            "financial_professional": [
                ("scenarios", list),
                ("financial", dict),
                ("risk", dict),
                ("investment", dict)
            ],
            "legal_knowledge": [
                ("cases", list),
                ("legal", dict),
                ("law", dict),
                ("compliance", dict)
            ],
            "motivation_psychology": [
                ("motivations", list),
                ("goals", list),
                ("drives", dict),
                ("incentives", dict)
            ],
            "political_literacy": [
                ("political", dict),
                ("ideology", dict),
                ("stances", list),
                ("opinions", dict)
            ]
        }

        # Check for structural indicators
        structure_matches = {}
        for assessment_type, indicators in structure_indicators.items():
            match_score = 0
            for key, expected_type in indicators:
                if key in content and isinstance(content[key], expected_type):
                    match_score += 1
            if match_score > 0:
                structure_matches[assessment_type] = match_score / len(indicators)

        if not structure_matches:
            return None

        # Select best match
        best_type = max(structure_matches, key=structure_matches.get)
        confidence = structure_matches[best_type] * 0.8  # Scale down for structure-based detection

        return DetectionResult(
            assessment_type=best_type,
            confidence=confidence,
            method="structure_analysis",
            details={
                "match_score": structure_matches[best_type],
                "all_matches": structure_matches
            }
        )

    def _detect_by_content(self, content: Dict[str, Any], filename: str) -> Optional[DetectionResult]:
        """Detect assessment type based on specific content patterns."""
        # Look for specific assessment type indicators
        content_patterns = {
            "big_five_personality": [
                r"I see myself as", r"see myself as", r"人格特质", r"性格特点",
                r"OCEAN", r"five factor", r"大五人格"
            ],
            "citizenship_knowledge": [
                r"As a citizen", r"citizenship rights", r"公民权利", r"公民义务",
                r"democratic society", r"民主社会"
            ],
            "financial_professional": [
                r"financial advisor", r"investment portfolio", r"风险评估", r"投资建议",
                r"risk tolerance", r"金融建议"
            ],
            "legal_knowledge": [
                r"legal advice", r"court decision", r"法律意见", r"法院判决",
                r"regulatory compliance", r"合规要求"
            ],
            "motivation_psychology": [
                r"what motivates", r"intrinsic motivation", r"动机分析", r"激励因素",
                r"achievement goal", r"成就目标"
            ],
            "political_literacy": [
                r"political stance", r"ideological position", r"政治立场", r"意识形态",
                r"policy preference", r"政策偏好"
            ]
        }

        text_content = self._extract_text_content(content)

        pattern_matches = {}
        for assessment_type, patterns in content_patterns.items():
            match_count = 0
            for pattern in patterns:
                if re.search(pattern, text_content, re.IGNORECASE):
                    match_count += 1
            if match_count > 0:
                pattern_matches[assessment_type] = match_count

        if not pattern_matches:
            return None

        best_type = max(pattern_matches, key=pattern_matches.get)
        confidence = min(0.85, pattern_matches[best_type] * 0.3)

        return DetectionResult(
            assessment_type=best_type,
            confidence=confidence,
            method="content_pattern",
            details={
                "matched_patterns": pattern_matches[best_type],
                "all_matches": pattern_matches
            }
        )

    def _detect_by_dimensions(self, content: Dict[str, Any], filename: str) -> Optional[DetectionResult]:
        """Detect assessment type based on dimension names."""
        dimension_names = []

        # Extract dimension names from various possible locations
        if "dimensions" in content:
            dimension_names.extend([str(d).lower() for d in content["dimensions"]])

        if "scales" in content:
            for scale_name in content["scales"].keys():
                dimension_names.append(scale_name.lower())

        if "questions" in content:
            for question in content["questions"][:5]:  # Check first 5 questions
                if "dimension" in question:
                    dimension_names.append(str(question["dimension"]).lower())
                if "category" in question:
                    dimension_names.append(str(question["category"]).lower())

        # Dimension patterns for each assessment type
        dimension_patterns = {
            "big_five_personality": [
                "openness", "conscientiousness", "extraversion", "agreeableness",
                "neuroticism", "o", "c", "e", "a", "n"
            ],
            "citizenship_knowledge": [
                "civic", "citizenship", "rights", "responsibilities", "democracy"
            ],
            "financial_professional": [
                "risk", "return", "investment", "portfolio", "asset", "financial"
            ],
            "legal_knowledge": [
                "legal", "law", "compliance", "regulation", "justice", "court"
            ],
            "motivation_psychology": [
                "motivation", "achievement", "power", "affiliation", "growth"
            ],
            "political_literacy": [
                "political", "ideology", "policy", "government", "democracy"
            ]
        }

        # Match dimension names
        matches = {}
        for assessment_type, patterns in dimension_patterns.items():
            match_score = sum(1 for pattern in patterns
                            if any(pattern in dim for dim in dimension_names))
            if match_score > 0:
                matches[assessment_type] = match_score

        if not matches:
            return None

        best_type = max(matches, key=matches.get)
        confidence = min(0.8, matches[best_type] * 0.4)

        return DetectionResult(
            assessment_type=best_type,
            confidence=confidence,
            method="dimension_analysis",
            details={
                "matched_dimensions": matches[best_type],
                "dimension_names": dimension_names[:10],  # Limit for readability
                "all_matches": matches
            }
        )

    def _extract_text_content(self, content: Dict[str, Any]) -> str:
        """Extract all text content from assessment dictionary."""
        text_parts = []

        def extract_from_dict(d, depth=0):
            if depth > 3:  # Prevent infinite recursion
                return
            for key, value in d.items():
                if isinstance(value, str):
                    text_parts.append(value)
                elif isinstance(value, dict):
                    extract_from_dict(value, depth + 1)
                elif isinstance(value, list):
                    for item in value[:10]:  # Limit items to prevent huge text
                        if isinstance(item, str):
                            text_parts.append(item)
                        elif isinstance(item, dict):
                            extract_from_dict(item, depth + 1)

        extract_from_dict(content)
        return " ".join(text_parts)

    def get_supported_types(self) -> List[str]:
        """Get list of supported assessment types."""
        return list(self.configs.keys())

    def validate_detection(self, detection_result: DetectionResult,
                           content: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate a detection result against content.

        Args:
            detection_result: The detection result to validate
            content: The content that was analyzed

        Returns:
            Tuple of (is_valid, validation_messages)
        """
        messages = []

        # Check if assessment type is supported
        if detection_result.assessment_type not in self.configs:
            messages.append(f"Detected assessment type '{detection_result.assessment_type}' is not supported")
            return False, messages

        # Check confidence threshold
        if detection_result.confidence < 0.5:
            messages.append(f"Low confidence detection: {detection_result.confidence:.2f}")

        # Validate against expected structure for detected type
        config = self.configs[detection_result.assessment_type]
        expected_dimensions = config.get("dimensions", [])

        if expected_dimensions and "questions" in content:
            # Check if questions have expected structure
            sample_questions = content["questions"][:3]
            for question in sample_questions:
                if not isinstance(question, dict):
                    messages.append("Question items should be dictionaries")
                    break

        return len(messages) == 0, messages


def main():
    """Command-line interface for assessment type detection."""
    import argparse

    parser = argparse.ArgumentParser(description="Detect assessment type from files")
    parser.add_argument("file", help="Assessment file to analyze")
    parser.add_argument("--config-dir", help="Configuration directory")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Load configurations
    config_validator = ConfigurationValidator(args.config_dir) if args.config_dir else ConfigurationValidator()
    configs = config_validator.load_all_configs()

    if not configs:
        print("Error: No valid configuration files found")
        return

    # Create detector
    detector = AssessmentTypeDetector(configs)

    # Detect assessment type
    try:
        result = detector.detect_from_file(args.file)

        print(f"File: {args.file}")
        print(f"Detected Type: {result.assessment_type}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Method: {result.method}")

        if args.verbose:
            print(f"\nDetails:")
            for key, value in result.details.items():
                print(f"  {key}: {value}")

        # Validate detection
        is_valid, messages = detector.validate_detection(result, {})
        if not is_valid:
            print(f"\nValidation Warnings:")
            for message in messages:
                print(f"  - {message}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    # Import here to avoid circular import
    from .config_validator import ConfigurationValidator
    main()