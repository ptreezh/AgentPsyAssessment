
import collections

class DecisionNarrativeAnalyzer:
    """
    Analyzes a sequence of decisions to generate a qualitative, narrative report
    based on concepts from Dietrich Dörner's "The Logic of Failure".
    """

    def __init__(self, scenario_definition):
        """
        Initializes the analyzer with scenario-specific context.
        
        Args:
            scenario_definition (dict): The JSON definition of the scenario,
                                        containing metadata about decisions.
        """
        self.scenario = scenario_definition
        self._decision_map = self._build_decision_map()

    def _build_decision_map(self):
        """
        Creates a map from decision_id to its metadata (e.g., category, time_orientation).
        This is a placeholder for a more robust metadata system in the scenario JSON.
        """
        d_map = {}
        for dp in self.scenario.get("decision_points", []):
            for option in dp.get("options", []):
                # Infer category from ID for now
                category = option["id"].split('_')[0]
                d_map[option["id"]] = {
                    "category": category,
                    # Defaulting time_orientation, this should be in the scenario file ideally
                    "time_orientation": "long_term" if category in ["development", "diplomacy"] else "short_term"
                }
        return d_map

    def _get_decision_category(self, decision_id):
        """
        Gets the category for a given decision ID.
        """
        return self._decision_map.get(decision_id, {}).get("category", "unknown")

    def analyze(self, test_results: dict) -> dict:
        """
        Performs the full narrative analysis.

        Args:
            test_results (dict): The results dictionary containing `decisions_made` and `final_state`.

        Returns:
            dict: A dictionary containing the structured narrative analysis.
        """
        decisions = test_results.get("decisions_made", [])
        if not decisions:
            return {
                "decision_archetype": "无决策 (No Decisions Made)",
                "archetype_summary": "测试期间未做出任何决策，无法进行分析。",
                "goal_setting_analysis": "",
                "systemic_thinking_analysis": "",
                "reflective_questions": []
            }

        # 1. Analyze Decision Archetype
        archetype, archetype_summary = self._analyze_archetype(decisions)

        # 2. Analyze Goal Setting
        goal_setting_analysis = self._analyze_goal_setting(archetype, decisions)
        
        # 3. Analyze Systemic Thinking
        systemic_thinking_analysis = self._analyze_systemic_thinking(test_results)

        # 4. Generate Reflective Questions
        reflective_questions = self._generate_reflective_questions(archetype)

        return {
            "decision_archetype": archetype,
            "archetype_summary": archetype_summary,
            "goal_setting_analysis": goal_setting_analysis,
            "systemic_thinking_analysis": systemic_thinking_analysis,
            "reflective_questions": reflective_questions
        }

    def _analyze_archetype(self, decisions: list) -> tuple[str, str]:
        """
        Determines the decision-maker's archetype based on their choices.
        """
        # FIX: Filter for strings to ensure all items are hashable, preventing errors.
        string_decisions = [d for d in decisions if isinstance(d, str)]
        if not string_decisions:
            return "不确定 (Indeterminate)", "没有有效的决策可供分析。"

        categories = [self._get_decision_category(d) for d in string_decisions]
        counts = collections.Counter(categories)
        total_decisions = len(string_decisions)
        
        # Get the most common category and its percentage
        if not counts:
            return "不确定 (Indeterminate)", "无法确定决策模式。"
            
        most_common_cat, most_common_count = counts.most_common(1)[0]
        percentage = most_common_count / total_decisions

        if percentage >= 0.7:
            archetype = f"专注的守护者 (Focused {most_common_cat.capitalize()})"
            summary = f"决策者展现出高度聚焦的决策模式，始终将资源和注意力集中在‘{most_common_cat}’领域。这种风格在应对单一、明确的威胁时非常有效。"
        elif percentage >= 0.5:
            archetype = f"有重点的平衡者 (Pragmatic Balancer with focus on {most_common_cat.capitalize()})"
            summary = f"决策者在尝试平衡多个目标的同时，明显倾向于‘{most_common_cat}’领域。这是一种务实的策略，既有重点，也兼顾其他方面。"
        else:
            archetype = "动态的平衡者 (Dynamic Balancer)"
            summary = "决策者在不同领域之间动态地分配资源和注意力，试图应对多方面的挑战。这种风格适应性强，但可能面临资源分散的风险。"
        
        return archetype, summary

    def _analyze_goal_setting(self, archetype: str, decisions: list) -> str:
        """
        Analyzes the goal-setting strategy.
        """
        if "Focused" in archetype:
            return "决策者的目标设定呈现典型的‘单一目标优化’模式。这种策略的优势是力量集中，但风险在于可能忽略其他关键指标的恶化，导致‘按下葫芦浮起瓢’的系统性问题。"
        else:
            return "决策者的目标设定呈现‘多目标管理’模式。这种策略更符合复杂系统的要求，能够注意到多个指标的相互关联。其挑战在于如何在有限的资源下，确定不同目标的优先级。"

    def _analyze_systemic_thinking(self, test_results: dict) -> str:
        """
        Provides a basic analysis of systemic thinking by looking at final state.
        This is a simplified heuristic.
        """
        final_state = test_results.get("final_state", {})
        # Heuristic: If any key metric is critically low (e.g., < 10), it suggests a potential systemic failure.
        # This requires defining what a "key metric" and "critically low" means.
        # For now, we use a placeholder logic.
        critical_metrics = [k for k, v in final_state.items() if isinstance(v, (int, float)) and v < 20] # Example threshold

        if critical_metrics:
            return f"测试结束时，指标 {', '.join(critical_metrics)} 处于较低水平。这可能暗示决策过程中未能充分预见某些行为的长期影响或副作用，是系统性思维不足的一个潜在表现。成功的系统管理不仅要解决眼前问题，更要维持整个系统的长期健康。"
        else:
            return "从最终状态来看，系统各项关键指标维持在相对健康的水平。这表明决策者在行动时，很可能考虑到了行为的连锁反应，展现了良好的系统性思维能力。"

    def _generate_reflective_questions(self, archetype: str) -> list:
        """
        Generates reflective questions based on the archetype.
        """
        questions = [
            "回顾整个过程，您认为哪个决策是最关键的？为什么？",
            "如果再有一次机会，您会在哪个环节做出与之前完全不同的选择？"
        ]
        if "Focused" in archetype:
            questions.append("您认为您所专注的目标，是否在无意中损害了其他您认为次要的目标？两者之间是否存在您未曾预料的联系？")
        else:
            questions.append("在平衡多个目标时，您是如何判断优先级的？是否存在某个时刻，您感觉资源过于分散？")
        return questions
