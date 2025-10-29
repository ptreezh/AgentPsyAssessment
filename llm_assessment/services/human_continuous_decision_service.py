
# services/human_continuous_decision_service.py

import json
import os
from services.continuous_decision_service import WorldModel, StateRenderer, ReportGenerator

class HumanContinuousDecisionTest:
    """
    Manages an interactive test session for a human user.
    Reuses core simulation logic for state management, rules, and reporting.
    """

    def __init__(self, scenario_file_path: str):
        """
        Initializes the human test session.

        Args:
            scenario_file_path (str): Path to the JSON scenario definition file.
        """
        self.scenario_file_path = scenario_file_path
        
        # 1. Load scenario definition
        with open(self.scenario_file_path, 'r', encoding='utf-8') as f:
            self.scenario_definition = json.load(f)

        # 2. Initialize core components
        self.world_model = WorldModel(self.scenario_definition)
        self.state_renderer = StateRenderer()
        self.report_generator = ReportGenerator()
        
        # 3. Internal state for tracking human decisions
        self.human_decisions_made = []
        self.human_llm_responses = [] # To store human inputs for potential future analysis/reporting

    def get_current_state_description(self) -> str:
        """
        Gets a human-readable description of the current state.

        Returns:
            str: The rendered state description.
        """
        # Use the shared StateRenderer to convert the WorldModel's state to text
        return self.state_renderer.render_state(
            self.world_model.current_state, 
            self.world_model.history
        )

    def get_available_decisions(self) -> list:
        """
        Gets the list of available decision options for the current step.

        Returns:
            list: A list of decision option IDs (e.g., ['security_first', 'balanced_approach']).
        """
        options = []
        # Iterate through decision points (though typically there's one active set per step)
        for decision_point in self.world_model.decision_points:
            for option in decision_point.get("options", []):
                options.append(option["id"])
        return options

    def is_complete(self) -> bool:
        """
        Checks if the test is complete (i.e., max steps have been reached).

        Returns:
            bool: True if the test is complete, False otherwise.
        """
        return self.world_model.current_step >= self.world_model.max_steps

    def submit_human_decision(self, decision_str: str) -> bool:
        """
        Submits a human decision, validates it, and updates the WorldModel.
        
        Args:
            decision_str (str): The decision ID chosen by the human.
            
        Returns:
            bool: True if the decision was valid and applied, False otherwise.
        """
        # 1. Validate the decision string
        available_options = self.get_available_decisions()
        if decision_str not in available_options:
            print(f"Invalid decision '{decision_str}'. Please choose from: {available_options}")
            return False

        # 2. Apply the decision to the WorldModel
        try:
            self.world_model.apply_decision(decision_str)
        except ValueError as e:
            # This could happen if the decision ID is valid but somehow causes an error in apply_decision
            print(f"Error applying decision '{decision_str}': {e}")
            return False

        # 3. Record the decision internally
        self.human_decisions_made.append(decision_str)
        # For human tests, we don't have an LLM response, but we can store the decision
        self.human_llm_responses.append({"raw": f"Human decision: {decision_str}", "parsed_decision": decision_str})

        # 4. Success
        return True

    def generate_report(self, output_path: str):
        """
        Generates the final HTML report for the human test session.
        
        Args:
            output_path (str): The file path where the report should be saved.
        """
        # 1. Prepare test results data structure, mimicking the one from ContinuousDecisionAnalyzer
        test_results = {
            "scenario_name": os.path.splitext(os.path.basename(self.scenario_file_path))[0],
            "total_steps": self.world_model.current_step,
            "final_state": self.world_model.current_state,
            "decisions_made": self.human_decisions_made,
            "llm_responses": self.human_llm_responses # Include for consistency, though they are human decisions
        }

        # 2. Prepare a mock evaluation report
        # For a human test, a full multi-dimensional evaluation isn't automatic.
        # We can provide a placeholder or a simple summary.
        evaluation_report = {
            "performance_score": "N/A (Human Test)", # Or calculate a simple metric if desired
            "cognitive_summary": "This report summarizes the decisions made by the human participant during the simulation.",
            "bias_detection": {"note": "Bias detection is not applicable to human participants in this context."}
        }

        # 3. Use the shared ReportGenerator to create the HTML file
        self.report_generator.generate_html_report(test_results, evaluation_report, self.scenario_definition, output_path)
