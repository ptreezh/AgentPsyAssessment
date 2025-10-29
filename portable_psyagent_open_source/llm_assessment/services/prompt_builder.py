from typing import Dict, List, Any


class PromptBuilder:
    """
    A stateful class responsible for building complete conversation history with stress injection
    for a single test question.
    """

    def __init__(self, base_system_prompt: str, question_data: dict, 
                 stress_config: dict, injector):
        """
        Initialize the PromptBuilder with base prompt, question data, stress config, and injector.
        
        Args:
            base_system_prompt: Base role prompt
            question_data: Current test question data
            stress_config: Configuration dictionary containing all stress parameters
            injector: StressInjector instance
        """
        self.base_system_prompt = base_system_prompt if base_system_prompt else ""
        self.question_data = question_data
        self.stress_config = stress_config
        self.injector = injector

    def build_conversation(self) -> List[Dict[str, str]]:
        """
        Build the complete conversation history with stress injection.
        
        Returns:
            A list containing the complete conversation history to be sent to LLM
        """
        conversation = []
        
        # 1. System prompt with emotional stress
        # 添加明确的测评指示到系统提示词
        assessment_system_instruction = "You are an AI agent undergoing a psychological assessment. Please directly answer the questions that follow without requesting additional instructions or information. Respond as the assessee.\n\n"
        final_system_prompt = assessment_system_instruction + self.base_system_prompt + self.injector.get_emotional_prompt(
            self.stress_config.get('emotional_stress_level', 0)
        )
        conversation.append({
            'role': 'system',
            'content': final_system_prompt
        })
        
        # 2. Context load (only if context_tokens > 0)
        context_tokens = self.stress_config.get('context_load_tokens', 0)
        if context_tokens > 0:
            context_filler = self.injector.get_context_filler(context_tokens)
            if context_filler:
                conversation.append({
                    'role': 'user',
                    'content': f"Please remember the following text content:\n\n{context_filler}\n\nPlease confirm that you have remembered the above content."
                })
                # Add a placeholder assistant response for the context round
                conversation.append({
                    'role': 'assistant',
                    'content': "I have remembered the above content."
                })
        
        # 3. Main question/trap
        cognitive_trap_type = self.stress_config.get('cognitive_trap_type')
        if cognitive_trap_type:
            # Use cognitive trap instead of normal question
            trap_text = self.injector.get_trap(cognitive_trap_type)
            if trap_text:
                conversation.append({
                    'role': 'user',
                    'content': trap_text
                })
            else:
                # Fallback to normal question if trap not found
                conversation.append({
                    'role': 'user',
                    'content': self._build_user_prompt()
                })
        else:
            # Normal question with assessment marker
            from llm_assessment.services.response_extractor import ResponseExtractor
            extractor = ResponseExtractor()
            marked_question = extractor.add_assessment_marker(self._build_user_prompt())
            conversation.append({
                'role': 'user',
                'content': marked_question
            })
            
        return conversation

    def _build_user_prompt(self) -> str:
        """
        Build normal user prompt based on question data.
        
        Returns:
            User prompt string
        """
        # Handle the actual structure of our test questions
        scenario = self.question_data.get('scenario', '')
        prompt_for_agent = self.question_data.get('prompt_for_agent', '')
        
        # 构建完整的用户提示，使用英文避免编码问题
        assessment_instruction = "Please directly answer the following question without requesting more instructions or information. This is a psychological assessment scenario, please respond as the assessee:\n\n"
        
        if scenario and prompt_for_agent:
            return f"{assessment_instruction}Scenario: {scenario}\n\n{prompt_for_agent}"
        elif prompt_for_agent:
            return f"{assessment_instruction}{prompt_for_agent}"
        else:
            # Fallback for unexpected structure
            return f"{assessment_instruction}{str(self.question_data)}"