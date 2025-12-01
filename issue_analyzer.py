"""
AI-Powered Issue Analyzer
Uses LLM to analyze GitHub issues and generate solution suggestions
"""
import os
import logging
from typing import Dict, Optional
from openai import AzureOpenAI, OpenAI
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class IssueAnalyzer:
    def __init__(self, model: str = "gpt-4-turbo-preview", temperature: float = 0.7):
        """Initialize the AI analyzer"""
        self.model = model
        self.temperature = temperature
        
        # Check AI provider
        ai_provider = os.getenv("AI_PROVIDER", "openai").lower()
        
        # Initialize appropriate client
        if ai_provider == "azure":
            # Azure OpenAI
            self.client = AzureOpenAI(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
            )
            self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", model)
            self.client_type = "azure"
            logger.info(f"Initialized with Azure OpenAI - Deployment: {self.deployment_name}")
        elif "claude" in model:
            self.anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            self.client_type = "anthropic"
            logger.info(f"Initialized with Anthropic Claude - Model: {model}")
        else:
            # Standard OpenAI
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.client_type = "openai"
            logger.info(f"Initialized with OpenAI - Model: {model}")
    
    def analyze_issue(self, issue_context: Dict) -> Optional[Dict]:
        """Analyze an issue and generate solution suggestions"""
        
        # Prepare the prompt
        prompt = self._create_analysis_prompt(issue_context)
        
        try:
            if self.client_type in ["openai", "azure"]:
                response = self._analyze_with_openai(prompt)
            else:
                response = self._analyze_with_anthropic(prompt)
            
            # Parse the response
            analysis = self._parse_analysis_response(response)
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing issue: {e}")
            return None
    
    def _create_analysis_prompt(self, context: Dict) -> str:
        """Create a prompt for the AI to analyze the issue"""
        
        title = context.get('title', '')
        body = context.get('body', '')
        labels = ', '.join(context.get('labels', []))
        comments = context.get('comments', [])
        
        comments_text = ""
        if comments:
            comments_text = "\n\n## Recent Comments:\n"
            for i, comment in enumerate(comments[-3:], 1):
                comments_text += f"\n**Comment {i} by {comment['author']}:**\n{comment['body'][:500]}\n"
        
        prompt = f"""You are an experienced open-source contributor analyzing a GitHub issue to provide a helpful solution.

## Issue Details:
**Title:** {title}

**Labels:** {labels}

**Description:**
{body[:2000]}
{comments_text}

## Your Task:
Analyze this issue and provide a structured response with:

1. **Problem Analysis**: Clearly explain what the issue is asking for (2-3 sentences)
2. **Proposed Solution**: Describe your recommended approach to solve this (3-4 sentences)
3. **Implementation Steps**: List 3-5 concrete steps to implement the solution

## Important Guidelines:
- Be specific and actionable
- Reference relevant parts of the issue description
- Keep it concise but helpful
- Show enthusiasm and professionalism
- If the issue is unclear, mention what clarification would be helpful

Please format your response as JSON with keys: "analysis", "solution", and "steps" (array of strings).
"""
        
        return prompt
    
    def _analyze_with_openai(self, prompt: str) -> str:
        """Analyze using OpenAI API (works for both Azure and standard OpenAI)"""
        model_name = self.deployment_name if self.client_type == "azure" else self.model
        
        response = self.client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert software engineer and open-source contributor. You analyze GitHub issues and provide clear, actionable solutions."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=self.temperature,
            max_tokens=2000,
            response_format={"type": "json_object"}
        )
        
        return response.choices[0].message.content
    
    def _analyze_with_anthropic(self, prompt: str) -> str:
        """Analyze using Anthropic Claude API"""
        message = self.anthropic.messages.create(
            model=self.model,
            max_tokens=2000,
            temperature=self.temperature,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        return message.content[0].text
    
    def _parse_analysis_response(self, response: str) -> Dict:
        """Parse the AI response into structured format"""
        import json
        
        try:
            data = json.loads(response)
            
            return {
                'analysis': data.get('analysis', ''),
                'solution': data.get('solution', ''),
                'steps': data.get('steps', [])
            }
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing AI response: {e}")
            # Fallback to simple parsing
            return {
                'analysis': response[:500],
                'solution': 'See full analysis above',
                'steps': ['Review the issue details', 'Implement the suggested approach', 'Test thoroughly']
            }
    
    def should_attempt_issue(self, issue_context: Dict) -> tuple[bool, str]:
        """
        Determine if the issue is suitable for the bot to attempt
        Returns (should_attempt, reason)
        """
        title = issue_context.get('title', '').lower()
        body = issue_context.get('body', '').lower()
        labels = [l.lower() for l in issue_context.get('labels', [])]
        
        # Check if issue is clear enough
        if not body or len(body) < 50:
            return False, "Issue description too short or missing"
        
        # Check for beginner-friendly labels
        beginner_labels = ['good first issue', 'beginner', 'easy', 'first-timers-only', 'help wanted']
        if not any(label in ' '.join(labels) for label in beginner_labels):
            return False, "Not marked as beginner-friendly"
        
        # Check if too many comments (might be complex discussion)
        if issue_context.get('comments_count', 0) > 10:
            return False, "Too much discussion, might be complex"
        
        # Avoid issues asking for major features
        avoid_keywords = ['redesign', 'refactor', 'rewrite', 'breaking change']
        if any(keyword in title or keyword in body for keyword in avoid_keywords):
            return False, "Appears to be a major feature/refactor"
        
        return True, "Suitable for contribution"
    
    def generate_comment(
        self, 
        analysis: Dict, 
        template: str,
        issue_title: str
    ) -> str:
        """Generate the final comment to post on the issue"""
        
        steps_formatted = '\n'.join([f"{i+1}. {step}" for i, step in enumerate(analysis['steps'])])
        
        comment = template.format(
            analysis=analysis['analysis'],
            solution=analysis['solution'],
            steps=steps_formatted
        )
        
        return comment
