"""
tests/test_policy_workflow.py
Kiểm thử tự động cho quy trình xử lý chính sách:
- CKPA-40: 7 Field dữ liệu cố định
- CKPA-45: Ghi nhận Referral
- CKPA-46: Ghi nhận Feedback
- CKPA-47: Kích hoạt HOLD khi thiếu căn cứ
"""

import sys
import unittest
from pathlib import Path

# Đảm bảo import được module 'app'
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.models import ResponseStatus, UncertaintyLevel
from app.services.database import init_database, save_feedback, save_referral, save_hold_log
from app.services.policy_service import PolicyService


class TestPolicyWorkflow(unittest.TestCase):
    """Bộ kiểm thử cho các chức năng S4."""

    def setUp(self):
        """Khởi tạo database trước mỗi bài test."""
        init_database()
        self.service = PolicyService()

    def test_empty_question_triggers_hold(self):
        """Kiểm tra: Câu hỏi rỗng phải kích hoạt trạng thái HOLD ngay lập tức."""
        response = self.service.process_question("   ")
        self.assertEqual(response.status, ResponseStatus.HOLD)
        # Message từ input_guard hoặc hold_reasons đều chấp nhận (có "rỗng" hoặc "trống")
        reason_lower = response.hold_reason.lower() if response.hold_reason else ""
        self.assertTrue(
            "rỗng" in reason_lower or "trống" in reason_lower or "empty" in reason_lower,
            f"hold_reason không chứa từ chỉ trống/rỗng: {response.hold_reason}"
        )

    def test_missing_evidence_triggers_hold_and_fail_visibly(self):
        """Kiểm tra CKPA-47: Không có bằng chứng từ S3 thì phải HOLD, không tự bịa câu trả lời."""
        response = self.service.process_question("Khách hàng VIP có được miễn lãi vô hạn không?")
        self.assertEqual(response.status, ResponseStatus.HOLD)
        self.assertEqual(response.uncertainty_level, UncertaintyLevel.HOLD)
        self.assertIsNotNone(response.hold_reason)
        self.assertIn("không tìm thấy", response.hold_reason.lower())
        self.assertEqual(len(response.citations), 0)

    def test_save_feedback_categories(self):
        """Kiểm tra CKPA-46: Ghi nhận đầy đủ 5 nhóm phản hồi."""
        categories = [
            "Missing Source",
            "Outdated Rule",
            "Wrong Scope",
            "Missing Exception",
            "Refusal"
        ]
        for cat in categories:
            success = save_feedback("Câu hỏi test", cat, f"Góp ý cho {cat}")
            self.assertTrue(success, f"Không thể lưu nhóm phản hồi: {cat}")

    def test_save_referral_local(self):
        """Kiểm tra CKPA-45: Ghi nhận yêu cầu chuyển người phụ trách cục bộ."""
        success = save_referral(
            question="Xin miễn phí bảo lãnh tín dụng",
            reason="Vượt thẩm quyền chi nhánh",
            policy_owner="Khối Quản trị Rủi ro Tín dụng"
        )
        self.assertTrue(success)


if __name__ == "__main__":
    unittest.main()

