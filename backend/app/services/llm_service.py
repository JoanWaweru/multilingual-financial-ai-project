"""
LLM service for generating responses using Anthropic
"""
import anthropic
from typing import List, Dict, Optional, Tuple
from app.core.config import settings
from app.utils.language_detection import detect_language_style, language_style_instruction, is_code_switch_compliant
import json

class LLMService:
    """Service for LLM interactions"""
    
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
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
- Answer only the current user query. Do not introduce unrelated topics.
- Do not invent facts, figures, or rates. If a detail is not in the provided context, say you do not have verified information.
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
            if settings.require_citations:
                sources_list = self._extract_sources(context)
                if sources_list:
                    messages.append({
                        "role": "system",
                        "content": (
                            "Answer only using the provided sources. "
                            f"End your response with a final line: {self._citation_label(expected_style or 'english')} "
                            + "; ".join(sources_list)
                        )
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

            system_text, non_system_messages = self._to_anthropic_messages(messages)
            response, content = self._anthropic_request(
                system_text,
                non_system_messages,
                temperature,
                self.max_tokens
            )
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

                    retry_system, retry_non_system = self._to_anthropic_messages(retry_messages)
                    retry_response, content = self._anthropic_request(
                        retry_system,
                        retry_non_system,
                        temperature,
                        self.max_tokens
                    )

            
            # Calculate confidence (weighted heuristic with forecasting penalty)
            confidence = self._calculate_confidence(content, context, user_message)

            if settings.require_citations and context:
                sources_list = self._extract_sources(context)
                label = self._citation_label(expected_style or "english")
                has_label = label.lower() in content.lower()
                has_source = any(source.lower() in content.lower() for source in sources_list)
                if sources_list and not (has_label and has_source):
                    content = self._no_verified_info_message(user_message)
                else:
                    context_text = self._format_context(context)
                    if self._has_unsupported_numbers(content, context_text):
                        content = self._no_verified_info_message(user_message)

            # If code-switch was requested but the response isn't compliant, keep the
            # response (it may still be correct); don't replace with "no verified info"
            if expected_style == "code-switch" and not is_code_switch_compliant(content):
                confidence = min(confidence, 0.7)  # Slightly lower confidence for style mismatch
            
            return {
                "response": content,
                "confidence": confidence,
                "model": self.model,
                "tokens_used": response.usage.output_tokens if hasattr(response, 'usage') else None
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

    def _citation_label(self, style: str) -> str:
        if style == "kiswahili":
            return "Vyanzo:"
        if style == "code-switch":
            return "Sources/Vyanzo:"
        return "Sources:"

    def _extract_sources(self, context: List[Dict]) -> List[str]:
        sources = []
        for item in context:
            source = item.get("metadata", {}).get("source")
            if source and source not in sources:
                sources.append(source)
        return sources

    def _no_verified_info_message(self, user_message: str) -> str:
        style = detect_language_style(user_message)
        if style == "kiswahili":
            return (
                "Samahani, sina taarifa zilizothibitishwa za kujibu swali hilo kwa sasa. "
                "Tafadhali toa chanzo au uliza kuhusu jambo lililo kwenye nyaraka zilizopo."
            )
        if style == "code-switch":
            return (
                "I don't have verified information to answer that right now. "
                "Tafadhali toa chanzo au uliza kuhusu jambo lililo kwenye nyaraka zilizopo."
            )
        return (
            "I don't have verified information to answer that right now. "
            "Please provide a source or ask about something covered in the available documents."
        )

    async def summarize_session_title(self, message: str) -> str:
        """Generate a short session title (4-6 words)."""
        try:
            system_text = "Summarize the message into a 4-6 word title. No punctuation."
            _, title = self._anthropic_request(
                system_text,
                [{"role": "user", "content": message.strip()}],
                temperature=0.2,
                max_tokens=20
            )
            title = title.strip()
            return " ".join(title.split())[:60]
        except Exception:
            trimmed = " ".join(message.strip().split())
            return trimmed[:60] + ("..." if len(trimmed) > 60 else "")


    
    def _calculate_confidence(self, response: str, context: List[Dict], user_message: str) -> float:
        """Calculate confidence score for the response"""
        # Weighted confidence: C = wR*R + wS*S + wL*L
        w_r, w_s, w_l = 0.4, 0.3, 0.3

        # Retrieval relevance (mean similarity)
        if context:
            similarities = [c.get("similarity_score", 0.0) for c in context]
            r = sum(similarities) / max(len(similarities), 1)
        else:
            r = 0.3

        # Source quality (simple heuristic by source name)
        s = 0.7
        if context:
            scores = []
            for item in context:
                source = (item.get("metadata", {}).get("source") or "").lower()
                if any(key in source for key in ["cbk", "cma", "sasra", "rba", "kra"]):
                    scores.append(1.0)
                elif "nse" in source:
                    scores.append(0.9)
                elif "guide" in source or "policy" in source:
                    scores.append(0.85)
                else:
                    scores.append(0.7)
            s = sum(scores) / max(len(scores), 1)

        # Response length completeness (cap at 1.0)
        length = len(response)
        l = min(1.0, max(0.3, length / 800.0))

        confidence = (w_r * r) + (w_s * s) + (w_l * l)

        # Penalize forecasting/prediction queries since outcomes are uncertain
        if self._is_forecast_query(user_message):
            confidence *= 0.75

        return min(1.0, max(0.3, confidence))

    def _is_forecast_query(self, text: str) -> bool:
        import re
        t = (text or "").lower()
        patterns = [
            r"\bnext\s+(week|month|quarter|year)\b",
            r"\bwill\s+(the|nse|market|stocks|shares)\b",
            r"\bwhat\s+will\s+(the\s+)?(market|nse|stocks|shares)\b",
            r"\bforecast\b",
            r"\bprediction\b",
            r"\bpredict\b",
            r"\boutlook\b",
            r"\bwhere\s+is\s+(the\s+)?(market|nse)\s+going\b",
            r"\bshould\s+i\s+(buy|sell)\s+(now|next)\b",
        ]
        return any(re.search(p, t) for p in patterns)

    def _has_unsupported_numbers(self, response: str, context_text: str) -> bool:
        import re
        numbers = re.findall(r"\b\d+(?:\.\d+)?\b", response)
        if not numbers:
            return False
        context_lower = context_text.lower()
        for number in numbers:
            # Skip single digits 1-9 (often list indices or "one of the N")
            if number in ("1", "2", "3", "4", "5", "6", "7", "8", "9"):
                continue
            # Skip common years (likely from context or general knowledge)
            try:
                y = int(number.split(".")[0])
                if 1990 <= y <= 2030:
                    continue
            except ValueError:
                pass
            if number.lower() not in context_lower:
                return True
        return False

    def _to_anthropic_messages(self, messages: List[Dict]) -> Tuple[str, List[Dict]]:
        system_parts = [m["content"] for m in messages if m.get("role") == "system"]
        system_text = "\n\n".join(system_parts)
        non_system = []
        for m in messages:
            role = m.get("role")
            if role == "system":
                continue
            if role not in ("user", "assistant"):
                role = "user"
            non_system.append({"role": role, "content": m.get("content", "")})
        return system_text, non_system

    def _anthropic_request(
        self,
        system_text: str,
        messages: List[Dict],
        temperature: float,
        max_tokens: int
    ) -> Tuple[object, str]:
        # New SDK path
        if hasattr(self.client, "messages"):
            response = self.client.messages.create(
                model=self.model,
                system=system_text,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            content = response.content[0].text if response.content else ""
            return response, content

        # Fallback for older SDKs
        human_prompt = getattr(anthropic, "HUMAN_PROMPT", "\n\nHuman:")
        ai_prompt = getattr(anthropic, "AI_PROMPT", "\n\nAssistant:")
        prompt_parts = [f"{human_prompt} {system_text}"]
        for m in messages:
            role = m.get("role")
            text = m.get("content", "")
            if role == "assistant":
                prompt_parts.append(f"{ai_prompt} {text}")
            else:
                prompt_parts.append(f"{human_prompt} {text}")
        prompt_parts.append(ai_prompt)
        prompt = "".join(prompt_parts)
        response = self.client.completions.create(
            model=self.model,
            prompt=prompt,
            temperature=temperature,
            max_tokens_to_sample=max_tokens
        )
        content = getattr(response, "completion", "")
        return response, content

llm_service = LLMService()

