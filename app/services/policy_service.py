"""
app/services/policy_service.py
Thin wrapper: Chuyển tiếp toàn bộ xử lý sang qa_pipeline.answer_question().
Lý do refactoring (Giai đoạn 5):
  - policy_service cũ dùng logic song song với qa_pipeline → vi phạm nguyên tắc
    single-path processing (tất cả câu hỏi phải qua 8 bước pipeline chuẩn).
  - Nay chỉ là adapter: nhận câu hỏi từ UI → gọi answer_question() → trả kết quả.
  - Giữ nguyên class PolicyService để không phá vỡ import cũ trong tests và main.py.
"""

from typing import Optional, Dict, Any
from app.models import PolicyResponse
from app.services.evidence_provider import EvidenceProvider
from app.services.token_guard import LLMGateway
from app.services.qa_pipeline import answer_question


class PolicyService:
    """
    Thin wrapper điều phối qua qa_pipeline 8 bước.
    Không chứa logic xử lý độc lập.
    """

    def __init__(
        self,
        evidence_provider: Optional[EvidenceProvider] = None,
        llm_gateway: Optional[LLMGateway] = None,
    ):
        # Lưu để truyền vào answer_question; None → pipeline tự dùng default
        self._evidence_provider = evidence_provider
        self._llm_gateway = llm_gateway

    def process_question(
        self,
        question: str,
        user_context: Optional[Dict[str, Any]] = None,
    ) -> PolicyResponse:
        """
        Tiếp nhận câu hỏi từ UI và ủy thác hoàn toàn cho qa_pipeline.
        Không có logic xử lý thêm ở đây.
        """
        return answer_question(
            question=question,
            user_context=user_context,
            evidence_provider=self._evidence_provider,
            llm_gateway=self._llm_gateway,
        )
