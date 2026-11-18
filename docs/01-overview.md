# 01 — Tổng quan Dự án, Phạm vi & Tổ chức Đội ngũ

> Tài liệu nền tảng định nghĩa mục tiêu kinh doanh, ranh giới **Base Scope (`M`)** so với tùy chọn (`O1` / `O`), các tham số **Common Bid Basis**, `10` điều cấm ngoài phạm vi và cơ cấu đội ngũ `10` người theo chuẩn RFP Mục 11.

---

## 1. Bối cảnh & Mục tiêu Dự án

### 1.1 Bối cảnh nghiệp vụ
- **Đơn vị thụ hưởng (Purchaser):** Công ty Song Nhật (*SongNhat*), hoạt động trong lĩnh vực phân phối và dịch vụ thiết bị công nghiệp (động cơ công nghiệp, bộ truyền động và truyền tải).
- **Vấn đề cần giải quyết:** Nhân viên kinh doanh, chăm sóc khách hàng và bảo hành mất nhiều thời gian tra cứu thủ công qua nhiều tài liệu quy trình/chính sách rời rạc; dễ diễn giải thiếu thống nhất về ngưỡng phê duyệt, ngày hiệu lực, ngoại lệ hoặc thiếu thông tin CRM cần thu thập.

### 1.2 Mục tiêu & Giới hạn Giá trị
- **Mục tiêu cốt lõi:** Xây dựng trợ lý tri thức và chính sách CRM nội bộ bằng tiếng Việt (**CKPA**) giúp nhân viên được ủy quyền tra cứu quy trình đã phê duyệt, đối chiếu nguyên văn trích dẫn kèm số trang/điều khoản, hiển thị các trường chính sách trọng yếu có cấu trúc (`Critical Fields`), nhận biết dữ kiện còn thiếu hoặc mâu thuẫn (`HOLD`), và chuyển đúng tuyến chủ sở hữu (`Local Referral`).
- **Tài liệu nội bộ hỗ trợ quyết định:** Trợ lý chỉ cung cấp hướng dẫn làm việc nội bộ. Chủ sở hữu chính sách (`Policy Owners`) và các hệ thống nghiệp vụ hiện hữu của SongNhat vẫn giữ toàn quyền quyết định, phê duyệt và thực thi giao dịch.
- **Giả thuyết chưa chứng minh:** Các kỳ vọng như giảm tỷ lệ khách hàng rời bỏ, giảm doanh số bị mất hoặc giảm sự cố tuân thủ được RFP xếp là giả thuyết chưa chứng minh; không được cam kết thành ROI trước khi đo đạc thực tế qua Pilot `20` ngày làm việc tại Gate `G3`.

---

## 2. Phạm vi Dự án: `Base Scope (M)` vs Tùy chọn (`O1` / `O`)

### 2.1 Ba họ chính sách khởi đầu (`PolicyFamily` tại Gate `G0`)
Khớp với `PolicyFamily` trong [backend/src/shared/enums.py](../backend/src/shared/enums.py), phạm vi nền dự kiến khảo sát và phê duyệt tại Gate `G0` gồm `3` nhóm:

| Mã `PolicyFamily` | Tên họ chính sách | Phạm vi hỗ trợ được phép (`Base Scope M`) | Ranh giới cứng không được vượt |
|---|---|---|---|
| `commercial_quoting_approval` | **Báo giá & Phê duyệt thương mại** | Giải thích trường thông tin CRM bắt buộc, ngưỡng chiết khấu/đơn hàng và tuyến xin ngoại lệ đã duyệt. | Không tự cấp chiết khấu/ngoại lệ, không suy luận phê duyệt từ doanh số hay tiền lệ cũ. |
| `customer_info_handling` | **Xử lý thông tin khách hàng** | Giải thích quy trình ghi nhận, xác minh hoặc đính chính thông tin khách hàng theo quy định đã duyệt. | Không nhập hồ sơ khách hàng vào Base Scope, không tự cấp quyền tiết lộ dữ liệu. |
| `service_warranty_routing` | **Định tuyến dịch vụ & Bảo hành** | Xác định hồ sơ bắt buộc, tuyến chuyển tiếp và chủ sở hữu bảo hành được ủy quyền. | Không tự phán quyết điều kiện bảo hành, không hướng dẫn sửa chữa kỹ thuật thiết bị. |

*(Lưu ý: Nếu bất kỳ họ nào thiếu Policy Owner hoặc thiếu nguồn đã phê duyệt tại `G0`, phạm vi phải thu hẹp tương ứng hoặc nâng cấp nguồn trước khi build; Supplier Team tuyệt đối không tự bịa quy tắc.)*

### 2.2 Tách biệt `Base Scope (M)` và Tùy chọn `O1` / `O`
- **`M` (Mandatory — Base Scope):** Hệ thống chỉ xử lý đúng **`2` nguồn CSV UTF-8** đã biên tập và phê duyệt: `passages` và `critical_fields`. Không nhập hồ sơ khách hàng, lịch sử giao dịch CRM hay hộp thư.
- **`O1` (Selected CRM Context — Ngoài Codebase Base Scope):**
  - **Trạng thái hiện tại:** **Không được triển khai trong Base Scope**. Trong mã nguồn, cấu hình (`backend/src/config.py`), schema DB và endpoint API hiện tại **không chứa** bảng, trường hay luồng nào cho `O1` (được kiểm soát bằng contract tests tại [backend/tests/test_srs_scaffold_contracts.py](../backend/tests/test_srs_scaffold_contracts.py) và [backend/tests/test_architecture_contracts.py](../backend/tests/test_architecture_contracts.py)).
  - **Điều kiện kích hoạt sau này (nếu có):** Chỉ thực hiện dưới dạng **Change Request tách biệt có báo giá và phê duyệt pháp lý riêng tại Gate `G0`** (hoặc sau `G0`) về nhu cầu lặp lại, quyền xử lý dữ liệu tối thiểu (`allowlist`), quyền người dùng và mức giá tăng thêm (schema CSV thứ `3`: trần `2.000` dòng ban đầu, `5.000` dòng lưu giữ, chọn tối đa `1` bản ghi kiểm soát theo `DAT 07`).
- **`O` (Optional):** Mọi hạng mục tùy chọn khác (ví dụ: sinh câu trả lời tiếng Anh, tích hợp thêm họ chính sách mới, hỗ trợ OCR/trích xuất bảng biểu tự động) phải được báo giá, phê duyệt phạm vi, kiểm soát quyền và kiểm thử tách biệt.

---

## 3. Tham số Giới hạn Cơ sở (`Common Bid Basis`)

Toàn bộ giới hạn dưới đây lấy trực tiếp từ RFP Mục 2 và được cấu hình cứng trong [backend/src/config.py](../backend/src/config.py) cùng [.env.example](../.env.example). Các giả định này phải được xác nhận lại bằng văn bản tại Gate `G0`:

| Nhóm tham số | Giới hạn `Base Scope (M)` | Biến cấu hình trong `config.py` | Quy tắc kiểm soát vận hành |
|---|---|---|---|
| **Tổ chức & Người dùng** | `1` công ty (`SN`); tối đa **`20`** người dùng định danh; **`5`** phiên đồng thời | `PILOT_MAX_NAMED_USERS = 20`, `PILOT_MAX_CONCURRENT_SESSIONS = 5` | RBAC đặc quyền tối thiểu (`reader`, `steward`, `policy_owner`, `referral_handler`, `administrator`, `privacy_security_owner`, `independent_evaluator`). |
| **Kho tri thức (`Corpus`)** | Tối đa **`30`** tài liệu; **`300`** đoạn (`passages`); **`<= 6.000`** ký tự Unicode/đoạn; **`50`** `critical_fields` | `CORPUS_MAX_DOCUMENTS = 30`, `CORPUS_MAX_PASSAGES = 300`, `PASSAGE_MAX_CHARS = 6000`, `CORPUS_MAX_CRITICAL_FIELDS = 50` | Mốc `G0` duyệt trước tối thiểu `30` đoạn + `10` trường trọng yếu đầu tiên; phần còn lại xong trước `G1`. Cấm cắt ngắn âm thầm. |
| **Làm mới dữ liệu (`Refresh`)** | `1` batch/ngày/schema; tối đa **`500`** dòng thay đổi/batch; cảnh báo snapshot **`> 25h`** | `IMPORT_MAX_ROWS_PER_BATCH = 500`, `IMPORT_SNAPSHOT_STALENESS_HOURS = 25` | Rút chính sách (`withdrawn`) có hiệu lực ngay và dọn cache vật lý **`<= 300s`** (`CACHE_WITHDRAWAL_MAX_SECONDS`), không chờ batch ngày. |
| **Hạn mức Gói hỏi đáp** | Tối đa **`1.000`** `AnswerPackage`/tháng (tính cả `hold` và `error`) | `ANSWER_MAX_PACKAGES_PER_MONTH = 1000` | Mỗi gói gắn `1` `task_id`. `Follow-up` và `Regenerate` giữ nguyên `task_id` và vẫn tính đủ vào mức sử dụng tháng. |
| **Hạn mức Gọi LLM & Token** | Tối đa **`2.000`** calls/tháng; tối đa **`2`** calls/package; **`6.000`** input tokens / **`900`** output tokens mỗi call; timeout **`20s`** | `LLM_MAX_CALLS_PER_MONTH = 2000`, `LLM_MAX_CALLS_PER_PACKAGE = 2`, `LLM_MAX_INPUT_TOKENS = 6000`, `LLM_MAX_OUTPUT_TOKENS = 900`, `LLM_REQUEST_TIMEOUT_SECONDS = 20` | `Retry`/`Repair` dùng chung trần `2` calls/package. Cạn hạn mức phải dừng/HOLD rõ ràng, không cắt cụt im lặng (`OPS 08`). |
| **Ngữ cảnh & Đầu ra** | Tối đa **`8`** đoạn/truy vấn; đầu ra thường `100–250` từ tiếng Việt; **cấm stream trước kiểm chứng**; **`p95 <= 25s`** | `ANSWER_MAX_PASSAGES = 8`, `ENABLE_ANSWER_STREAMING = False`, `OPS_LATENCY_P95_SECONDS = 25`, `APP_TIMEZONE = "Asia/Ho_Chi_Minh"`, `ANSWER_SYSTEM_PROMPT_PATH = "prompts/answer_system_vi.txt"` | Mọi ngày hiệu lực/giao dịch dùng giờ Việt Nam (`UTC+7`); khóa tắt khẩn cấp `EMERGENCY_DISABLE_CACHE_KEY = "ckpa:emergency_disable"`. |
| **Khung thời gian & Hỗ trợ** | `2` tuần Discovery (`G0`) + `10` tuần Triển khai (`G1–G4`, gồm `>= 20` ngày làm việc Pilot) | `SUPPORT_HOURS_START = "08:00"`, `SUPPORT_HOURS_END = "17:00"` | Hỗ trợ giờ hành chính Việt Nam ngày làm việc; không nén lịch dưới `20` ngày quan sát Pilot. |

---

## 4. Mười (10) Điều Cấm Ngoài Phạm vi (`Out of Scope`)

Đội dự án tuyệt đối **không** thiết kế, lập trình hoặc đưa vào Pilot các hạng mục sau nếu chưa có Change Request được phê duyệt và kiểm thử riêng:

1. **Không kết nối CRM sống (`No Live CRM Connector`):** Không đồng bộ trực tiếp vào hệ thống CRM hay CSDL vận hành đang chạy.
2. **Không OCR, Audio, Zalo hay Mailbox:** Không đọc ảnh scan/giọng nói, không tích hợp Zalo OA/cá nhân, không nạp lịch sử hộp thư.
3. **Không tự động trích xuất PDF/Bảng/Sơ đồ:** Không tự động parse bảng biểu, sơ đồ hoặc PDF gốc; văn bản nguồn và chú thích thiết yếu phải do Steward/Owner biên tập thủ công trước khi xuất CSV (`DAT 08`).
4. **Không tự động mở rộng ngôn ngữ hay họ chính sách:** Không trả lời bằng tiếng Anh (là tùy chọn `O`), không tự ý dịch điều khoản ràng buộc khi chưa được Policy Owner duyệt ngôn ngữ chi phối, không thêm họ chính sách ngoài `3` họ đã chốt.
5. **Không soạn phản hồi gửi khách hàng (`KNW 02`):** Không tạo email/tin nhắn sẵn sàng gửi ra bên ngoài cho khách hàng.
6. **Không ghi ngược CRM hay tự phê duyệt (`ANS 07`, `KNW 05`):** Không `writeback` vào CRM, không tự tạo tác vụ CRM, không xây rule engine phức tạp hay tự động phê duyệt/thực thi giao dịch thay người có thẩm quyền.
7. **Không tư vấn pháp lý, thuế hay kỹ thuật sửa chữa (`ANS 07`):** Phải từ chối (`refused_out_of_scope`) và chuyển tuyến khi được hỏi tư vấn pháp lý/thuế, cấp quyền tiết lộ dữ liệu nhạy cảm, duyệt điều kiện bảo hành hoặc hướng dẫn sửa chữa thiết bị.
8. **Không tự huấn luyện từ phản hồi (`KNW 06`):** Tuyệt đối không dùng `Feedback` hay ghi chú của nhân viên để tự động huấn luyện lại mô hình hoặc tự động sửa quy tắc chính sách (`auto_applied = False`).
9. **Không Streaming trước kiểm chứng (`INV-03`, RFP trang 4):** Cấm tuyệt đối truyền phát (`stream`) nội dung câu trả lời ra giao diện trước khi `Validation` hoàn tất đối chiếu trích dẫn, trường trọng yếu và kiểm tra lại quyền/trạng thái nguồn cuối cùng trong DB (`ENABLE_ANSWER_STREAMING = False`).
10. **Không cam kết hỗ trợ `24/7` ngoài giờ thỏa thuận:** Chỉ vận hành hỗ trợ theo khung thỏa thuận `08:00–17:00` giờ Việt Nam ngày làm việc (`DEL 06`).

---

## 5. Tóm tắt Đội ngũ 10 Người (`P1–P5` & `S1–S5`) & Nguyên tắc Phối hợp

Cơ cấu dự án gồm `10` thành viên ánh xạ `1–1` vào `10` vai chuẩn **RFP Mục 11**:

| Phía RFP | Mã Role | Thành viên | Định danh nguyên văn RFP | Vai trò tiếng Việt & Trọng tâm |
|---|---|---|---|---|
| **Purchaser** | `P1` | **Mỹ Vân** | `Purchaser sponsor` | Nhà tài trợ / Chủ đầu tư — chốt phạm vi, ngân sách, tuyến giải pháp, quyết định `O1` và ký duyệt qua `5` Gate (`G0–G4`). |
| **Purchaser** | `P2` | **Hữu Tài** | `Policy owners` | Chủ sở hữu chính sách — duyệt `3` họ chính sách, Authority/Date Matrix, Critical Fields, ngoại lệ, chỉ định substitutes & **Policy Reviewer #1**. |
| **Purchaser** | `P3` | **Chí Kha** | `Knowledge and data steward` | Quản lý tri thức & Dữ liệu — chuẩn bị `2` CSV UTF-8, xử lý `quarantine`, trạng thái xuất bản/thu hồi, đối soát xuất mở & **Policy Reviewer #2**. |
| **Purchaser** | `P4` | **Trà My** | `Staff users` | Người dùng đại diện — cung cấp câu hỏi thực tế, kiểm tra nguồn/trích dẫn, điều phối **`5 representative users`** đo effort `20` ngày Pilot. |
| **Purchaser** | `P5` | **Anh Khoa** | `Privacy and security owners` | Chủ sở hữu Quyền riêng tư & Bảo mật — duyệt RBAC, lưu giữ dữ liệu, rà soát pháp lý **Phụ lục F**, sự cố `SEC 07` và điều khoản thoát. |
| **Supplier Team** | `S1` | **Hoàng Tiến** | `Named lead` | Trưởng nhóm định danh Nhà cung cấp — điều phối tiến độ, giờ công theo vai/tuần, phụ thuộc hai phía, TCO `DEL 05` & bàn giao `DEL 04/06`. |
| **Supplier Team** | `S2` | **Quốc Hưng** | `Integration engineer` | Kỹ sư Tích hợp & Dữ liệu (Đội Build) — xây dựng `ingestion`, `knowledge`, `2` CSV validators, quarantine, tombstone & công cụ export mở `OPS 08`. |
| **Supplier Team** | `S3` | **Yến Nhi** | `Retrieval and application engineer` | Kỹ sư Truy xuất & Ứng dụng (Đội Build) — xây dựng `policy`, `retrieval`, `answer`, `validation`, `referral`, `prompts/` và UI Split-Screen. |
| **Supplier Team** | `S4` | **Quý Hải** | `Quality lead` | Trưởng nhóm Chất lượng & Kiểm định độc lập — giữ niêm phong **`100 Sealed`** & `80 Challenges`, thực hiện nghiệm thu độc lập & audit `20` ngày Pilot. |
| **Supplier Team** | `S5` | **Ngọc Duy** | `Operations specialist` | Chuyên viên Vận hành & Hỗ trợ — xây dựng `identity`/RBAC, `pii_guard`, `admin`/`audit`, Cost Meter, cache purge `<= 5` phút, Backup/Restore & trực SLA. |

### Hai nguyên tắc phối hợp bắt buộc
1. **Mô hình Dual-Hat (Hai Mũ):** Mỗi thành viên giữ đúng `1` mũ trách nhiệm bàn giao theo RFP Mục 11 (`P1–P5`, `S1–S5`), đồng thời gánh các tác vụ thực thi cụ thể trên từng Gate `G0–G4` (soát nhãn, diễn tập thu hồi, kiểm toán phân quyền, phát triển phần mềm, đo lường Pilot) để không ai trống việc trong `12` tuần. Chi tiết tại [05-roadmap-and-team.md](./05-roadmap-and-team.md).
2. **Hàng rào Độc lập (Chinese Wall — RFP Mục 8 & Mục 11):**
   - **`S4` Quý Hải tuyệt đối không tham gia viết code hay tinh chỉnh hệ thống cùng `S2`, `S3`, `S5`** (*Independent reviewers must not be the developers who tuned the system*).
   - **Đội Build (`S2`, `S3`, `S5`) bị cấm truy cập tập `100 Sealed`** và không được đóng vai `Staff User` trong `20` ngày Pilot.
   - **Hai người rà nhãn chính sách (`Two policy reviewers`):** `P2` Hữu Tài phối hợp `P3` Chí Kha (hoặc `P5` Anh Khoa), đều độc lập với đội Build.
   - **Năm người dùng đại diện (`Five representative users`):** `P4` Trà My điều phối `5` thành viên phi-lập-trình (`P1`, `P2`, `P3`/`P5`, `P4`, `S1`) trong quan sát Pilot.
