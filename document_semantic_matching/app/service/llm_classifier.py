import json
import logging
import time
from typing import Optional

from google import genai
from google.genai.types import GenerateContentResponse
from pydantic import ValidationError

from app.schema.document_record import ClassificationResult


class ClassifyLLMService:
    """
    Service class for calling Gemini model.
    """

    def __init__(self, model: str = "gemini-2.5-flash-lite", max_attempts: int = 3, backoff: float = 0.5):
        self.client = genai.Client()
        self.model = model
        self.max_attempts = max_attempts
        self.backoff = backoff
        self._schema = ClassificationResult.model_json_schema()

    def classify(self, passage: str) -> ClassificationResult:
        prompt = self._build_base_prompt(passage)
        logging.info(f'Model in use : {self.model}')
        attempt = 1
        last_text: Optional[str] = None
        last_exc: Optional[Exception] = None

        while attempt <= self.max_attempts:

            resp: GenerateContentResponse = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_json_schema": self._schema,
                    "temperature": 0.0,
                    "max_output_tokens": 1000
                }
            )
            self._log_token_usage(resp)
            text = (resp.text or "").strip()
            last_text = text
            try:
                return ClassificationResult.model_validate_json(text)
            except ValidationError as ve:
                last_exc = ve
                if attempt >= self.max_attempts:
                    # give up after max_attempts
                    raise ve
                prompt = self._build_repair_prompt(passage, text, attempt)
                time.sleep(self.backoff * attempt)  # backoff
                attempt += 1
                continue

        # If we exit loop unexpectedly, raise last known error
        raise last_exc or RuntimeError("Failed to validate model output and no exception captured.")

    def _build_base_prompt(self, passage: str) -> str:
        return f"""
        Passage:
        {passage}

        Task:
        Identify at least 10 high-level topics the passage most likely relates to.
        For each topic, include a confidence (probability between 0 and 1).
        You must come up with at least 10 topics.
        Return ONLY valid JSON in this format matching the schema provided.
        Schema:
        {json.dumps(self._schema)}
        Example:
        {{ "result": [ {{ "name": "topic", "confidence": 0.12 }}, ... ] }}
        """

    def _build_repair_prompt(self, passage: str, last_output: str, attempt: int) -> str:
        # Ask model to correct its previous (invalid) JSON output.
        return f"""
        Passage:
        {passage}

        The model's previous response (attempt {attempt}) was not valid JSON matching the required schema.
        
        Previous output:
        {last_output}

        Please **fix the JSON** and return ONLY valid JSON matching this schema (no commentary):
        {json.dumps(self._schema)}

        Return exactly one JSON object; do not add surrounding markdown or explanation.
        Return 10 high-level topics the passage most likely relates to.
        """

    def _log_token_usage(self, resp):
        """Log total token usage for a Gemini response."""
        meta = getattr(resp, "usage_metadata", None)
        if not meta:
            logging.warning("[Gemini] usage_metadata not available in response")
            return

        # Try all possible total fields across SDK versions
        total = (
                getattr(meta, "total_token_count", None)
                or getattr(meta, "total_tokens", None)
                or getattr(meta, "token_count", None)
        )

        if total is not None:
            logging.info(f"[Gemini] Total token usage: {total}")
        else:
            logging.info("[Gemini] total_token_count not available in response")
