"""
app/services/system_service.py
Dịch vụ hệ thống cung cấp các tiện ích khởi tạo và kiểm tra sức khỏe
cho tầng giao diện (UI) mà không làm lộ các tầng cơ sở dữ liệu hay LLM client.
"""

from app.services.database import init_database, check_connection
from app.services.policy_service import PolicyService
from app.services.llm_client import MockLLMClient
from app.services.token_guard import LLMGateway


def init_system() -> None:
    """Khởi tạo toàn bộ cơ sở hạ tầng lưu trữ và cấu hình hệ thống."""
    init_database()


def check_system_health() -> bool:
    """Kiểm tra tính sẵn sàng của hệ thống lưu trữ cục bộ."""
    return check_connection()


def create_policy_service(demo_mode: bool = False) -> PolicyService:
    """
    Tạo đối tượng PolicyService phù hợp với chế độ hoạt động.
    Nếu demo_mode=True, gắn MockLLMClient sẵn để phục vụ kiểm thử trực quan.
    """
    if demo_mode:
        gateway = LLMGateway(client=MockLLMClient())
        return PolicyService(llm_gateway=gateway)
    return PolicyService()
