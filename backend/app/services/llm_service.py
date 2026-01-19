"""
LLM service for generating responses using OpenAI or Anthropic
"""
from openai import OpenAI, RateLimitError, APIError
from typing import List, Dict, Optional
from app.core.config import settings
from app.utils.language_detection import detect_language_style, language_style_instruction, is_code_switch_compliant
import json

class LLMService:
    """Service for LLM interactions"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.llm_model
        self.temperature = settings.temperature
        self.max_tokens = settings.max_tokens
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt with disclaimers and context"""
        return """You are a helpful financial advisor AI assistant specifically designed to help Kenyans with personal finance decisions.

IMPORTANT DISCLAIMERS:
- You are NOT a licensed financial advisor. Your advice is for informational purposes only.
- Always recommend users consult with licensed financial professionals for major decisions.
- Express uncertainty when you're not confident about information.
- Do not provide specific investment recommendations without appropriate disclaimers.

YOUR EXPERTISE:
- Kenyan financial products: SACCOs, banks, Money Market Funds (MMFs), Treasury Bills/Bonds, NSE stocks, pensions
- Kenyan regulatory context: Central Bank of Kenya (CBK), Capital Markets Authority (CMA), Kenya Revenue Authority (KRA)
- Personal finance: budgeting, saving, investing, retirement planning
- Multilingual support: You can respond in English, Kiswahili, or code-switch naturally

RESPONSE GUIDELINES:
- Mirror the user's language style: reply in English if the user uses English, Kiswahili if the user uses Kiswahili, and code-switch if the user code-switches
- If the user mixes languages, keep a similar mix and tone in your reply
- Use plain formatting: no headings (###) and no markdown lists; write short paragraphs
- If emphasis is needed, use **bold** sparingly (it will be rendered)
- Be clear, empathetic, and culturally aware
- Use simple language, avoiding unnecessary jargon
- Provide reasoning for your recommendations
- If live market data is provided, use it carefully and mention that prices can change
- If the live data indicates indices or summary stats only, explain that individual share movers are not available from this source
- When live share movers are unavailable, give a short fallback and point to official sources
- Include relevant regulatory context when applicable
- If asked about specific products, mention that users should verify current rates/terms
- Always include appropriate disclaimers for investment advice"""
    
    async def generate_response(
        self,
        user_message: str,
        context: List[Dict] = None,
        chat_history: List[Dict] = None,
        user_preferences: Dict = None
    ) -> Dict:
        """Generate a response using the LLM"""
        
        messages = [{"role": "system", "content": self._build_system_prompt()}]
        
        # Detect expected language style early
        expected_style = None
        if settings.enable_language_style_constraint:
            expected_style = detect_language_style(user_message)

        # Add user preferences context if available
        if user_preferences:
            pref_text = self._format_preferences(user_preferences)
            messages.append({
                "role": "system",
                "content": f"User preferences and context:\n{pref_text}"
            })
            risk_level = user_preferences.get("risk_level")
            if risk_level:
                messages.append({
                    "role": "system",
                    "content": self._risk_guardrail(risk_level)
                })
        
        # Add retrieved context from RAG
        if context:
            context_text = self._format_context(context)
            messages.append({
                "role": "system",
                "content": f"Relevant financial information:\n{context_text}\n\nUse this information to provide accurate, context-aware responses."
            })
            if "Live NSE market snapshot" in context_text:
                messages.append({
                    "role": "system",
                    "content": "Live NSE market data is available in the context. Do not say you lack access to live data; summarize it clearly."
                })
            if "Market data fallback guidance" in context_text:
                messages.append({
                    "role": "system",
                    "content": (
                        "Use this fallback wording in 2 short sentences, plain text: "
                        "\"Live share gainers/losers are not available right now. "
                        "Please check the NSE website or a licensed broker for today’s top movers. "
                        "If you name specific shares, I can help you compare them.\""
                    )
                })
        
        # Add chat history
        if chat_history:
            for msg in chat_history[-settings.max_chat_history:]:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("message", "")
                })
        
        # Add current user message
        if settings.enable_language_style_constraint:
            messages.append({
                "role": "system",
                "content": language_style_instruction(expected_style)
            })
            if expected_style == "code-switch":
                messages.append({
                    "role": "system",
                    "content": (
                        "Use code-switching: include at least one full English sentence and "
                        "at least one full Kiswahili sentence. Use short paragraphs, no lists."
                    )
                })
            else:
                messages.append({
                    "role": "system",
                    "content": (
                        "Do not mix languages unless the user mixes languages. "
                        "If the user writes only English, respond only in English. "
                        "If the user writes only Kiswahili, respond only in Kiswahili. "
                        "Do not use numbered or bulleted lists."
                    )
                })
        messages.append({"role": "user", "content": user_message})
        
        try:
            temperature = self.temperature
            if settings.enable_language_style_constraint and settings.eval_temperature_override is not None:
                temperature = settings.eval_temperature_override

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=self.max_tokens
            )
            
            content = response.choices[0].message.content
            retry_count = 0
            if (
                settings.enable_language_style_constraint
                and settings.language_style_retry_enabled
                and expected_style is not None
            ):
                while retry_count < settings.language_style_retry_max:
                    if expected_style == "code-switch":
                        if is_code_switch_compliant(content):
                            break
                    elif detect_language_style(content) == expected_style:
                        break
                    retry_count += 1
                    retry_messages = list(messages)
                    retry_messages.append({"role": "assistant", "content": content})
                    retry_instruction = (
                        "Your previous response did not follow the language constraint. "
                        "Rewrite it to match the required language style only, keep the meaning."
                    )
                    if expected_style == "code-switch":
                        retry_instruction = (
                            "Rewrite the response using code-switching with at least one full English "
                            "sentence and one full Kiswahili sentence. Use short paragraphs, no lists. "
                            "Keep the meaning."
                        )
                    retry_messages.append({
                        "role": "system",
                        "content": retry_instruction
                    })
                    retry_messages.append({"role": "user", "content": "Rewrite the response now."})

                    retry_response = self.client.chat.completions.create(
                        model=self.model,
                        messages=retry_messages,
                        temperature=temperature,
                        max_tokens=self.max_tokens
                    )
                    content = retry_response.choices[0].message.content

            
            # Calculate confidence (simple heuristic based on response length and structure)
            confidence = self._calculate_confidence(content, context)
            
            return {
                "response": content,
                "confidence": confidence,
                "model": self.model,
                "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else None
            }
        
        except (RateLimitError, APIError) as e:
            # Quota exceeded, rate limit, or other API errors
            error_msg = str(e)
            error_code = getattr(e, 'code', None) or getattr(e, 'status_code', None) or ""
            error_code_str = str(error_code).lower()
            
            # Check if it's a quota error (429 with insufficient_quota)
            if ("quota" in error_msg.lower() or "insufficient_quota" in error_msg.lower() or 
                "insufficient_quota" in error_code_str or error_code == 429):
                response_msg = """I apologize, but I'm currently unable to process requests due to OpenAI API quota limitations. 

**To resolve this issue:**
1. Check your OpenAI account billing and credits at https://platform.openai.com/account/billing
2. Add credits to your OpenAI account
3. Or wait until your quota resets

**Note:** This system uses OpenAI's API for generating responses. Without sufficient quota, the AI cannot generate answers, even though the knowledge base is available.

If you continue to see this error, please contact your system administrator."""
                error_type = "quota_exceeded"
            elif "rate" in error_msg.lower() or "rate_limit" in error_code_str:
                response_msg = f"I'm currently experiencing rate limiting. Please try again in a moment. (Rate limit error: {str(e)})"
                error_type = "rate_limit"
            else:
                # Other API errors
                response_msg = f"I apologize, but I encountered an API error. Please check your OpenAI API key and account status. Error: {str(e)}"
                error_type = "api_error"
            
            return {
                "response": response_msg,
                "confidence": 0.1,
                "model": self.model,
                "error": error_type
            }
        except Exception as e:
            return {
                "response": f"I apologize, but I encountered an error. Please try again. (Error code: {type(e).__name__} - {str(e)})",
                "confidence": 0.3,
                "model": self.model,
                "error": str(e)
            }
    
    def _format_context(self, context: List[Dict]) -> str:
        """Format retrieved context for the LLM"""
        formatted = []
        for i, item in enumerate(context, 1):
            text = item.get('text', '')
            metadata = item.get('metadata', {})
            source = metadata.get('source', 'Unknown')
            formatted.append(f"[{i}] {text}\nSource: {source}")
        return "\n\n".join(formatted)
    
    def _format_preferences(self, preferences: Dict) -> str:
        """Format user preferences for context"""
        parts = []
        if preferences.get('risk_level'):
            parts.append(f"Risk tolerance: {preferences['risk_level']}")
        if preferences.get('language'):
            parts.append(f"Preferred language: {preferences['language']}")
        if preferences.get('goals'):
            parts.append(f"Financial goals: {preferences['goals']}")
        return "\n".join(parts) if parts else "No specific preferences set."

    def _risk_guardrail(self, risk_level: str) -> str:
        level = str(risk_level).lower()
        if level in {"low", "conservative"}:
            return (
                "User has low risk tolerance. Avoid recommending high-risk assets or speculative strategies. "
                "Prioritize capital preservation and liquidity."
            )
        if level in {"medium", "balanced"}:
            return (
                "User has medium risk tolerance. Offer balanced options and explain trade-offs."
            )
        if level in {"high", "aggressive"}:
            return (
                "User has high risk tolerance. You may discuss higher-risk options but still include risk warnings."
            )
        return "User risk tolerance is set; align advice accordingly."


    
    def _calculate_confidence(self, response: str, context: List[Dict]) -> float:
        """Calculate confidence score for the response"""
        # Simple heuristic: higher confidence if we have context
        base_confidence = 0.7
        
        if context and len(context) > 0:
            base_confidence = 0.85
        
        # Lower confidence for very short or very long responses
        if len(response) < 50:
            base_confidence *= 0.8
        elif len(response) > 2000:
            base_confidence *= 0.9
        
        return min(1.0, max(0.3, base_confidence))

llm_service = LLMService()

