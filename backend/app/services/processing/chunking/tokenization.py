import tiktoken
from typing import List

class TokenCounterService:
    def __init__(self, default_model: str = "cl100k_base"):
        self.default_model = default_model
        self._encoders = {}

    def _get_encoder(self, model: str):
        if model not in self._encoders:
            try:
                self._encoders[model] = tiktoken.get_encoding(model)
            except Exception:
                self._encoders[model] = tiktoken.get_encoding("cl100k_base")
        return self._encoders[model]

    def count_tokens(self, text: str, model: str = None) -> int:
        if not text:
            return 0
        model = model or self.default_model
        encoder = self._get_encoder(model)
        return len(encoder.encode(text, disallowed_special=()))

    def encode(self, text: str, model: str = None) -> List[int]:
        if not text:
            return []
        model = model or self.default_model
        encoder = self._get_encoder(model)
        return encoder.encode(text, disallowed_special=())

    def decode(self, tokens: List[int], model: str = None) -> str:
        if not tokens:
            return ""
        model = model or self.default_model
        encoder = self._get_encoder(model)
        return encoder.decode(tokens)

    def estimate_cost(self, tokens: int, cost_per_1k: float = 0.0001) -> float:
        """
        Estimate API cost based on standard token pricing.
        """
        return (tokens / 1000) * cost_per_1k

token_counter_service = TokenCounterService()
