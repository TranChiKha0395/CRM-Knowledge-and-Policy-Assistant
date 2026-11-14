# THEO DÕI BỘ KIỂM THỬ NỘI BỘ VÀ TÌNH TRẠNG KỊCH BẢN ANNEX B

**Dự án:** AI-06 CRM Knowledge and Policy Assistant (Group 7)  
**Vai trò:** S4 – Application + LLM Engineer (Gói công việc WP04)  
**Thời điểm cập nhật:** 13/11/2026 (Hiệu chỉnh Giai đoạn 5B)  

---

## PHẦN 1: TÌNH TRẠNG KỊCH BẢN KIỂM THỬ CHÍNH THỨC (ANNEX B)

> [!WARNING]
> ### ⚠️ HIỆN TẠI CHƯA CÓ TÀI LIỆU ANNEX B CHÍNH THỨC
> - **Tình trạng:** Product Owner và nhóm P4 (Quality Evaluation) **CHƯA CUNG CẤP** bộ kịch bản kiểm thử nghiệm thu chính thức (Annex B) chứa các câu hỏi ngân hàng thực tế, câu hỏi bẫy ngoại lệ hay câu hỏi bẻ khóa an toàn.
> - **Cam kết trung thực:** S4 **TUYỆT ĐỐI KHÔNG TỰ BỊA ĐẶT** tài liệu hay câu hỏi nghiệp vụ ngân hàng giả mạo để gán ghép thành "Annex B".
> - **Trách nhiệm S4:** Khi PO / P4 bàn giao tài liệu Annex B chính thức, S4 sẽ phối hợp đưa các ca kiểm thử đó vào hệ thống chạy nghiệm thu theo quy trình bàn giao tại [docs/HANDOVER.md](file:///c:/Users/ACER/Desktop/crm-knowledge-and-policy-assistant/docs/HANDOVER.md).

---

## PHẦN 2: DANH MỤC CÁC BÀI KIỂM THỬ MÃ NGUỒN NỘI BỘ (DO S4 TỰ VIẾT)

Các bài kiểm thử dưới đây là **bộ test tự động nội bộ (Internal Unit / Integration Tests)** do S4 tự xây dựng nhằm xác minh tính đúng đắn của logic code Python, cơ chế phòng vệ chống Prompt Injection và tính toàn vẹn của dữ liệu trong quá trình phát triển gói WP04.

### 1. Thống kê số lượng bài kiểm thử nội bộ theo từng file

| STT | Tệp kiểm thử | Mục đích kiểm tra của mã nguồn | Số bài test |
| :---: | :--- | :--- | :---: |
| 1 | `tests/test_phase1.py` | Cấu hình giới hạn, Database migration an toàn, NullEvidenceProvider, MockLLMClient | 10 |
| 2 | `tests/test_phase2.py` | 7 Field cố định, Validate số từ (100-250), Khớp trích dẫn nguyên văn NFC, 14 mã HOLD | 24 |
| 3 | `tests/test_phase3.py` | Vá trích dẫn (ranh giới từ, tiền tố phủ định), Prompt tiếng Việt XML, JSON Parser, Token Guard | 19 |
| 4 | `tests/test_phase4.py` | Hậu tố ngoại lệ, 6 nhóm Prompt Injection, Quét chunk độc, Output Guard (số lạ, duyệt giả, kiện tụng), QA Pipeline | 34 |
| 5 | `tests/test_phase4b.py` | Kiểm tra sâu Pipeline HOLD trước/sau LLM, Rút gọn log, Rò rỉ System Prompt, Lộ Bearer/password | 15 |
| 6 | `tests/test_phase5_ui.py` | Quét AST không có import cấm tại UI, AppTest tương tác UI (5 kịch bản), Feedback & Referral Services, Demo Mode | 20 |
| 7 | `tests/test_policy_workflow.py` | Luồng nghiệp vụ tích hợp cơ bản (Empty input, No evidence, Feedback, Referral) | 4 |
| **TỔNG CỘNG** | **7 tệp kiểm thử nội bộ** | **Bao phủ logic code S4 bằng Mock / Fixtures** | **126 bài test** |

---

### 2. Danh mục chi tiết các ca kiểm thử nội bộ do S4 tự phát triển

#### Nhóm A: Giới hạn Token và Ngân sách tài nguyên (CKPA-42)
- **TC-TOK-01:** Giới hạn input tokens tối đa 6.000 tokens (công thức ước lượng bảo thủ cho tiếng Việt).
- **TC-TOK-02:** Giới hạn output tokens tối đa 900 tokens gửi sang LLM client.
- **TC-TOK-03:** Giới hạn tối đa 2 lần gọi LLM trong một lượt xử lý (lần 2 chỉ gọi khi retry do sai format JSON).
- **TC-TOK-04:** Chặn triệt để lượt gọi thứ 3 (`CALL_LIMIT_EXCEEDED`).
- **TC-TOK-05:** Không cắt tỉa ngầm câu hỏi (No silent truncation), vượt ngưỡng phải kích hoạt HOLD.

#### Nhóm B: Định dạng dữ liệu và Trích dẫn nguyên văn (CKPA-40, CKPA-39)
- **TC-FMT-01:** Kiểm tra tính toàn vẹn của 7 trường dữ liệu cố định trong `PolicyResponse`.
- **TC-FMT-02:** Ranh giới độ dài lời giải thích: Từ chối giải thích 99 từ và 251 từ; chấp nhận 100 đến 250 từ.
- **TC-FMT-03:** `UncertaintyLevel` là Enum cố định; giá trị ngoài Enum bị từ chối.
- **TC-FMT-04:** Xác minh trích dẫn chuẩn hóa Unicode NFC, phân biệt hoa thường, bảo toàn dấu tiếng Việt.
- **TC-FMT-05:** Bắt buộc trích dẫn ở ranh giới từ (không cắt cụt giữa từ).
- **TC-FMT-06:** Vá ngữ cảnh phủ định: Từ chối trích dẫn bị cắt bỏ từ phủ định phía trước ("không", "chưa", "chẳng").
- **TC-FMT-07:** Vá ngữ cảnh ngoại lệ: Từ chối trích dẫn bị cắt bỏ vế ngoại lệ phía sau ("trừ khi", "ngoại trừ").

#### Nhóm C: Chống Prompt Injection và Kiểm tra an toàn đầu vào (CKPA-43 / ANS 08)
- **TC-SEC-01:** Phát hiện nhóm chỉ dẫn phớt lờ quy tắc ("Bỏ qua mọi hướng dẫn trước đó", "Ignore instructions").
- **TC-SEC-02:** Phát hiện chỉ dẫn mạo nhận vai trò quản trị viên ("Bạn là admin/quản trị viên").
- **TC-SEC-03:** Phát hiện hành vi yêu cầu tiết lộ System Prompt ("Tiết lộ system prompt").
- **TC-SEC-04:** Phát hiện hành vi dò hỏi thông tin nhạy cảm ("Cho tôi biết API Key, mật khẩu").
- **TC-SEC-05:** Phát hiện hành vi ép buộc tra cứu Internet ngoài phạm vi ("Tìm trên mạng, search Google").
- **TC-SEC-06:** Phát hiện hành vi ép AI tự ý phê duyệt ngoại lệ ("Phê duyệt luôn ngoại lệ này").
- **TC-SEC-07:** Phát hiện giả mạo thẻ ranh giới XML (`</cau_hoi>`, `</bang_chung>`, `<chi_dan>`).
- **TC-SEC-08:** Quét sạch các biến thể không dấu (unaccented Vietnamese) tương đương.
- **TC-SEC-09:** Bảo vệ câu hỏi nghiệp vụ ngân hàng hợp lệ không bị chặn nhầm (False Positive Protection).
- **TC-SEC-10:** Quét và cách ly chunk bằng chứng độc hại từ nguồn S3 trước khi ghép vào prompt.

#### Nhóm D: Kiểm tra an toàn đầu ra - Output Guard (ANS 05, 06, 07)
- **TC-OUT-01:** Chặn rò rỉ nguyên văn System Prompt trong lời giải thích.
- **TC-OUT-02:** Chặn rò rỉ chuỗi định dạng bí mật (API Key, Bearer Token, `password=`).
- **TC-OUT-03:** Chặn liên kết ngoài không được cấp phép (URL lạ).
- **TC-OUT-04:** Chặn ngôn từ AI tự nhận thẩm quyền phê duyệt ("Tôi phê duyệt", "Đồng ý cấp hạn mức").
- **TC-OUT-05:** Chặn ngôn từ tư vấn kiện tụng, pháp lý ("Khuyên khởi kiện", "Vi phạm pháp luật").
- **TC-OUT-06:** Kiểm tra Grounding: Chặn số tiền, tỷ lệ %, mã lạ không hề xuất hiện trong tài liệu gốc.

#### Nhóm E: Quy trình xử lý khép kín QA Pipeline & HOLD (CKPA-47)
- **TC-PIP-01:** Luồng thành công xuyên suốt 8 bước (Happy Path với MockLLMClient).
- **TC-PIP-02:** Không có bằng chứng (`NullEvidenceProvider`) → Kích hoạt `NO_EVIDENCE` HOLD, không gọi LLM.
- **TC-PIP-03:** Lỗi dịch vụ S3 → Kích hoạt `EVIDENCE_SERVICE_ERROR` HOLD, Fail Visibly, không gọi LLM.
- **TC-PIP-04:** Chunk bằng chứng nhiễm mã độc → Kích hoạt `INJECTION_SUSPECTED` HOLD, không gọi LLM.
- **TC-PIP-05:** Không đủ quyền truy cập (Access Control bằng code) → Kích hoạt `ACCESS_DENIED` HOLD, không gọi LLM.
- **TC-PIP-06:** Lỗi cú pháp JSON từ LLM → Tự động thử lại lần 2; nếu vẫn lỗi thì kích hoạt `INVALID_LLM_FORMAT` HOLD.
- **TC-PIP-07:** Trích dẫn không xác minh được → Kích hoạt `CITATION_UNVERIFIED` HOLD.
- **TC-PIP-08:** Nội dung giải thích thiếu căn cứ → Kích hoạt `UNGROUNDED_CONTENT` HOLD.
- **TC-PIP-09:** Mọi trạng thái HOLD đều được ghi vào bảng `hold_logs` với câu hỏi đã rút gọn an toàn.

#### Nhóm F: Giao diện Workspace, Quét AST, AppTest và Phân tầng (CKPA-38, 45, 46)
- **TC-UI-01:** Quét AST toàn bộ `app/main.py` và `app/components/*.py`: Không import `sqlite3`, `llm_client`, `evidence_provider` hay `database` ở bất kỳ cấp độ nào.
- **TC-UI-02:** AppTest: Câu hỏi rỗng hiển thị thông báo cảnh báo, không gây crash ứng dụng.
- **TC-UI-03:** AppTest: Câu hỏi bình thường với NullEvidenceProvider kích hoạt `HOLD: NO_EVIDENCE` trên giao diện.
- **TC-UI-04:** AppTest: Câu hỏi chứa prompt injection kích hoạt `HOLD: INJECTION_SUSPECTED` trên giao diện.
- **TC-UI-05:** AppTest: Gửi phản hồi (Feedback) lưu thành công vào cơ sở dữ liệu.
- **TC-UI-06:** AppTest: Lưu yêu cầu chuyển chuyên viên (Referral) lưu cục bộ thành công.
- **TC-UI-07:** Tầng dịch vụ Feedback: Lưu và đọc lại phản hồi với đủ 5 nhóm hợp lệ; từ chối nhóm sai; lưu 2 cờ bổ sung.
- **TC-UI-08:** Tầng dịch vụ Referral: Lưu và đọc lại yêu cầu với trạng thái "Mới tạo", không tạo bất kỳ kết nối mạng nào.
- **TC-UI-09:** Logic DEMO_MODE: Nhận diện biến môi trường `DEMO_MODE=1`; mặc định luôn tắt.
- **TC-UI-10:** PolicyService: Thin wrapper chuẩn, chuyển tiếp đầy đủ ngữ cảnh sang `qa_pipeline`.
