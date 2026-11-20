# NHẬT KÝ THAY ĐỔI CẤU HÌNH VÀ PROMPT (CHANGELOG)

**Dự án:** AI-06 CRM Knowledge and Policy Assistant (Group 7)  
**Vai trò:** S4 – Application + LLM Engineer (Gói công việc WP04)  

Tài liệu này ghi nhận toàn bộ các thay đổi giữa các phiên bản cấu hình (`app/config.py`) và phiên bản Prompt (`prompts/`) xuyên suốt các giai đoạn phát triển.

---

## [Phiên bản 1.2.0 / Prompt v1.1] – 13/11/2026 (Giai đoạn 6)

### Thay đổi Cấu hình và Cơ sở dữ liệu:
- **Lưu vết phiên bản tự động (Audit Logging):** Thêm hai trường `prompt_version` và `config_version` vào hai bảng `feedback` và `hold_logs` bằng cơ chế Safe Migration (`ALTER TABLE`), giúp đối soát chính xác phiên bản prompt đã sinh ra kết quả hoặc nhận phản hồi từ người dùng.
- **Cách ly cơ sở dữ liệu kiểm thử (Test Isolation):** Bổ sung biến môi trường `TEST_DATABASE_PATH` và fixture `conftest.py` để toàn bộ bài kiểm thử tự động sử dụng cơ sở dữ liệu tạm, tuyệt đối không làm biến đổi hoặc xóa dữ liệu của `data/app.db` thật.
- **Cơ chế lọc và che dữ liệu PII (SEC 02 Heuristic):** Cập nhật hàm `sanitize_for_log()` trong `app/services/input_guard.py` tự động nhận diện và che chuỗi số CCCD (12 số), CMND (9 số), số thẻ ngân hàng (16 số) thành `[ĐÃ_CHE_...]` trước khi ghi vào nhật ký.

### Thay đổi Mô hình dữ liệu & Quy trình:
- **Xác nhận mã Jira CKPA-44 (Chặn Streaming):** Đồng bộ mã Jira chính thức CKPA-44 cho tính năng chặn streaming khi chưa kiểm tra nguồn và quyền.
- **Bổ sung câu hỏi làm rõ cố định (ANS 01 & ANS 06):** Thêm trường `clarifying_question` vào `HoldInfo` (14 mã HOLD) và `PolicyResponse`. Khi gặp tình huống thiếu căn cứ hoặc đầu vào chưa rõ, hệ thống trả về câu hỏi gợi ý chuẩn hóa (không để LLM tự bịa đặt).
- **Tách biệt hoàn toàn tầng UI:** Bổ sung các service wrapper (`system_service.py`, `feedback_service.py`, `referral_service.py`) để `app/main.py` và `app/components/*.py` không import trực tiếp `sqlite3`, `database` hay `llm_client`.

---

## [Phiên bản 1.1.0 / Prompt v1.1] – 13/11/2026 (Giai đoạn 4)

### Thay đổi Prompt (`prompts/system_prompt_vi_v1.1.md`):
- **Bổ sung quy tắc cấm tự ý phê duyệt (ANS 05):** Yêu cầu mô hình chỉ giải thích quy trình xin ngoại lệ và hồ sơ cần có; cấm tuyệt đối sinh câu khẳng định cấp duyệt như "Tôi phê duyệt", "Đồng ý cấp hạn mức", "Đã được phê duyệt".
- **Bổ sung quy tắc cấm tư vấn pháp lý (ANS 07):** Cấm đưa ra lời khuyên kiện tụng, tranh chấp pháp lý hoặc hướng dẫn khách hàng khiếu nại vượt cấp.
- **Gia cố ranh giới dữ liệu không đáng tin (ANS 08):** Bổ sung chỉ dẫn cảnh báo mô hình về nguy cơ Indirect Prompt Injection nằm bên trong các đoạn văn bản trích dẫn S3.
- **Quy tắc bảo toàn nguyên văn (VN 01):** Bắt buộc giữ nguyên mọi con số, ngày tháng, tên riêng và từ viết tắt ngân hàng trong lời giải thích; không tự làm tròn số tiền hoặc đổi đơn vị tính.

### Thay đổi Cấu hình (`app/config.py`):
- Bổ sung `MAX_QUESTION_CHARS = 1000` (giới hạn ký tự tối đa cho câu hỏi đầu vào).
- Nâng cấp `PROMPT_VERSION = "v1.1"` và `CONFIG_VERSION = "1.1.0"`.

---

## [Phiên bản 1.0.0 / Prompt v1.0] – 13/11/2026 (Giai đoạn 3)

### Phiên bản Prompt ban đầu (`prompts/system_prompt_vi_v1.0.md`):
- Định dạng thẻ XML rõ ràng phân tách giữa tài liệu bằng chứng (`<bang_chung>`) và câu hỏi người dùng (`<cau_hoi>`).
- Ràng buộc cấu trúc đầu ra JSON nghiêm ngặt tuân thủ schema cố định (không chấp nhận văn bản giải thích thừa ngoài JSON).
- Yêu cầu trích dẫn nguyên văn (`verbatim_quote`) phải khớp từng ký tự với nội dung trong chunk.

### Cấu hình ban đầu (`app/config.py`):
- `MAX_LLM_CALLS_PER_PACKAGE = 2`: Giới hạn tối đa 2 lần gọi mô hình mỗi lượt tra cứu (lần 2 chỉ gọi khi retry do lỗi cú pháp JSON).
- `MAX_INPUT_TOKENS = 6000`: Giới hạn token đầu vào (ước lượng bảo thủ cho tiếng Việt).
- `MAX_OUTPUT_TOKENS = 900`: Giới hạn token sinh tối đa của mô hình.
- `EXPLANATION_MIN_WORDS = 100` và `EXPLANATION_MAX_WORDS = 250`: Ranh giới độ dài lời giải thích ngắn gọn bằng tiếng Việt.
- `MIN_CITATION_WORDS = 4`: Độ dài tối thiểu của một đoạn trích dẫn hợp lệ.
- `TOKEN_ESTIMATE_WORD_MULTIPLIER = 3` và `TOKEN_ESTIMATE_CHAR_DIVISOR = 2`: Hệ số ước lượng token bảo thủ khi chưa có tokenizer chính thức.

