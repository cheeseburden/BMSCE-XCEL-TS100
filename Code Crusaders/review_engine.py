"""
Core Review Engine for the AI Code Review Assistant.
Uses LangChain + Groq (free tier) for LLM-powered code analysis.
Falls back to HuggingFace Inference API if Groq is unavailable.
"""

import json
import os
from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage
from prompts import SYSTEM_PROMPT, CODE_REVIEW_PROMPT, OPTIMIZE_CODE_PROMPT
from utils import parse_llm_json


class CodeReviewEngine:
    """
    LLM-powered code review engine.
    Primary: Groq (free tier - Llama 3 / Mixtral)
    Fallback: HuggingFace Inference API (free models)
    """

    GROQ_MODELS = {
        "Llama 3.3 70B": "llama-3.3-70b-versatile",
        "Llama 3.1 8B (Fast)": "llama-3.1-8b-instant",
        "Mixtral 8x7B": "mixtral-8x7b-32768",
        "Gemma 2 9B": "gemma2-9b-it",
    }

    def __init__(self, api_key: str, model_name: str = "Llama 3.3 70B", provider: str = "groq"):
        self.api_key = api_key
        self.model_name = model_name
        self.provider = provider
        self.llm = self._init_llm()

    def _init_llm(self):
        """Initialize the LLM client based on provider."""
        if self.provider == "groq":
            return self._init_groq()
        elif self.provider == "huggingface":
            return self._init_huggingface()
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def _init_groq(self):
        """Initialize Groq LLM (free tier)."""
        try:
            from langchain_groq import ChatGroq

            model_id = self.GROQ_MODELS.get(self.model_name, "llama-3.3-70b-versatile")
            return ChatGroq(
                api_key=self.api_key,
                model_name=model_id,
                temperature=0.1,
                max_tokens=4096,
            )
        except ImportError:
            raise ImportError(
                "langchain-groq not installed. Run: pip install langchain-groq"
            )

    def _init_huggingface(self):
        """Initialize HuggingFace Inference API (free)."""
        try:
            from langchain_community.llms import HuggingFaceEndpoint

            return HuggingFaceEndpoint(
                repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1",
                huggingfacehub_api_token=self.api_key,
                temperature=0.1,
                max_new_tokens=4096,
            )
        except ImportError:
            raise ImportError(
                "langchain-community not installed. Run: pip install langchain-community"
            )

    # ─── Review Methods ──────────────────────────────────────────────────

    def review_code(self, code: str, language: str = "Python") -> dict:
        """
        Perform a comprehensive code review using the LLM.
        Returns structured review with issues, fixes, teaching, and scores.
        """
        prompt = CODE_REVIEW_PROMPT.format(language=language, code=code)
        response = self._invoke(prompt)
        return parse_llm_json(response)
    def optimize_code(self, code: str, language: str = "Python") -> str:
        """
        Generate the full optimized/corrected version of the code.
        Returns the rewritten code as a string (not JSON).
        """
        prompt = OPTIMIZE_CODE_PROMPT.format(language=language, code=code)
        response = self._invoke(prompt)
        # Strip markdown fences if the LLM wraps the code
        import re
        cleaned = response.strip()
        cleaned = re.sub(r"^```[\w]*\s*\n?", "", cleaned)
        cleaned = re.sub(r"\n?```\s*$", "", cleaned)
        return cleaned.strip()

    def chat(self, messages: list, code: str, review_summary: str, language: str = "Python") -> str:
        """
        Follow-up chat about the code review.
        Takes conversation history and returns the AI response.
        """
        system_content = (
            "You are an expert code review assistant. The user has just received a code review "
            "and wants to ask follow-up questions. You have full context of their code and review.\n\n"
            f"**Language:** {language}\n\n"
            f"**Code being reviewed:**\n```{language.lower()}\n{code[:3000]}\n```\n\n"
            f"**Review Summary:** {review_summary}\n\n"
            "Answer questions clearly and concisely. When showing code, use proper markdown formatting. "
            "If asked to fix something, show the corrected code. Be helpful and educational."
        )

        langchain_messages = [SystemMessage(content=system_content)]
        for msg in messages:
            if msg["role"] == "user":
                langchain_messages.append(HumanMessage(content=msg["content"]))
            else:
                from langchain_core.messages import AIMessage
                langchain_messages.append(AIMessage(content=msg["content"]))

        try:
            response = self.llm.invoke(langchain_messages)
            if hasattr(response, "content"):
                return response.content
            return str(response)
        except Exception as e:
            return f"⚠️ Error: {str(e)[:200]}"

    # ─── LLM Invocation ─────────────────────────────────────────────────

    def _invoke(self, user_prompt: str) -> str:
        """Send the prompt to the LLM and return the response text."""
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]

        try:
            response = self.llm.invoke(messages)
            # Handle different response types
            if hasattr(response, "content"):
                return response.content
            return str(response)
        except Exception as e:
            error_msg = str(e)
            if "rate_limit" in error_msg.lower() or "429" in error_msg:
                return json.dumps({
                    "overall_score": 0,
                    "summary": "⚠️ Rate limit reached. Groq's free tier allows ~30 requests/minute. Please wait a moment and try again.",
                    "issues": [],
                    "strengths": [],
                    "metrics": {"readability": 0, "maintainability": 0, "security": 0, "performance": 0, "best_practices": 0},
                })
            elif "authentication" in error_msg.lower() or "401" in error_msg:
                return json.dumps({
                    "overall_score": 0,
                    "summary": "❌ Invalid API key. Please check your Groq API key and try again. Get a free key at https://console.groq.com/keys",
                    "issues": [],
                    "strengths": [],
                    "metrics": {"readability": 0, "maintainability": 0, "security": 0, "performance": 0, "best_practices": 0},
                })
            else:
                return json.dumps({
                    "overall_score": 0,
                    "summary": f"❌ Error: {error_msg[:200]}",
                    "issues": [],
                    "strengths": [],
                    "metrics": {"readability": 0, "maintainability": 0, "security": 0, "performance": 0, "best_practices": 0},
                })

    # ─── Static Helpers ──────────────────────────────────────────────────

    @classmethod
    def get_available_models(cls) -> list:
        """Return list of available model names."""
        return list(cls.GROQ_MODELS.keys())

    @classmethod
    def get_model_id(cls, model_name: str) -> str:
        """Get the model ID for a given display name."""
        return cls.GROQ_MODELS.get(model_name, "llama-3.3-70b-versatile")
