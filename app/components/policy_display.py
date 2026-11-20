"""
app/components/policy_display.py
Hiển thị kết quả tra cứu chính sách với 7 field cố định (CKPA-40).
Phân biệt rõ: Trích dẫn nguyên văn vs Giải thích AI (CKPA-39).
Hiển thị HOLD rõ ràng với màu cảnh báo (CKPA-47 Fail Visibly).
Phong cách: Enterprise Banking — Navy Blue, trang trọng, hành chính.
"""

import streamlit as st
from app.models import PolicyResponse, ResponseStatus, UncertaintyLevel


# Màu badge theo mức độ chắc chắn
_UNCERTAINTY_COLOR = {
    UncertaintyLevel.THAP: "green",
    UncertaintyLevel.TRUNG_BINH: "orange",
    UncertaintyLevel.CAO: "red",
    UncertaintyLevel.KHONG_XAC_DINH: "gray",
}

_UNCERTAINTY_LABEL = {
    UncertaintyLevel.THAP: "Thấp",
    UncertaintyLevel.TRUNG_BINH: "Trung bình",
    UncertaintyLevel.CAO: "Cao",
    UncertaintyLevel.KHONG_XAC_DINH: "Chưa xác định",
}

# SVG icons inline — chuẩn banking, không dùng emoji trang trí
_SVG_PAUSE = (
    '<svg width="22" height="22" viewBox="0 0 24 24" fill="none">'
    '<rect x="6" y="4" width="4" height="16" rx="2" fill="#B45309"/>'
    '<rect x="14" y="4" width="4" height="16" rx="2" fill="#B45309"/>'
    '</svg>'
)
_SVG_SHIELD_GRAY = (
    '<svg width="14" height="14" viewBox="0 0 24 24" fill="none">'
    '<path d="M12 2L4 7v5c0 5.25 3.4 10.15 8 11.35C17.6 22.15 21 17.25 21 12V7l-8-5z"'
    ' fill="#94A3B8"/></svg>'
)
_SVG_SHIELD_NAVY = (
    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none">'
    '<path d="M12 2L4 7v5c0 5.25 3.4 10.15 8 11.35C17.6 22.15 21 17.25 21 12V7l-8-5z"'
    ' fill="#1F5C99"/></svg>'
)
_SVG_CHECK = (
    '<svg width="22" height="22" viewBox="0 0 24 24" fill="none">'
    '<circle cx="12" cy="12" r="10" fill="#16A34A"/>'
    '<path d="M8 12l3 3 5-5" stroke="white" stroke-width="2.2"'
    ' stroke-linecap="round" stroke-linejoin="round"/>'
    '</svg>'
)
_SVG_DOC = (
    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none">'
    '<path d="M4 6h16M4 10h16M4 14h10" stroke="#1F5C99" stroke-width="2.2"'
    ' stroke-linecap="round"/></svg>'
)
_SVG_INFO = (
    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none">'
    '<circle cx="12" cy="12" r="9" stroke="#1F5C99" stroke-width="2"/>'
    '<path d="M12 8v4M12 16h.01" stroke="#1F5C99" stroke-width="2.2"'
    ' stroke-linecap="round"/></svg>'
)
_SVG_BLOCK = (
    '<svg width="22" height="22" viewBox="0 0 24 24" fill="none">'
    '<circle cx="12" cy="12" r="10" fill="#DC2626"/>'
    '<rect x="7" y="11" width="10" height="2" rx="1" fill="white"/>'
    '</svg>'
)
_SVG_HINT = (
    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none">'
    '<circle cx="12" cy="12" r="9" stroke="#16A34A" stroke-width="2"/>'
    '<path d="M12 7c-1.66 0-3 1.34-3 3 0 1.31.84 2.42 2 2.83V14h2v-1.17'
    'c1.16-.41 2-1.52 2-2.83 0-1.66-1.34-3-3-3zm-1 9h2v2h-2v-2z"'
    ' fill="#16A34A"/></svg>'
)


def render_policy_response(response: PolicyResponse) -> None:
    """Render toàn bộ kết quả tra cứu chính sách."""

    if response.status == ResponseStatus.HOLD:
        _render_hold(response)
        return

    if response.status == ResponseStatus.REFUSAL:
        _render_refusal(response)
        return

    _render_success(response)


# ---------------------------------------------------------------------------
# HOLD — Thông báo hành chính tạm dừng
# ---------------------------------------------------------------------------
def _render_hold(response: PolicyResponse) -> None:
    """CKPA-47 Fail Visibly — Thông báo hành chính trang trọng."""
    code = response.hold_reason_code or "HOLD_GENERAL"

    # ── Banner hành chính chính ──
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
            border-left: 5px solid #D97706;
            border-top: 1px solid #FDE68A;
            border-right: 1px solid #FDE68A;
            border-bottom: 1px solid #FDE68A;
            border-radius: 0 10px 10px 0;
            padding: 20px 24px;
            margin-bottom: 16px;
        ">
            <div style="display:flex;align-items:flex-start;gap:14px">
                <div style="margin-top:2px;flex-shrink:0">{_SVG_PAUSE}</div>
                <div style="flex:1">
                    <div style="font-size:0.68rem;font-weight:800;letter-spacing:0.14em;
                                color:#92400E;text-transform:uppercase;margin-bottom:4px">
                        Thông báo hành chính &nbsp;—&nbsp; Trạng thái hệ thống
                    </div>
                    <div style="font-size:1.1rem;font-weight:700;color:#78350F;line-height:1.3;
                                margin-bottom:10px">
                        TẠM DỪNG XỬ LÝ &nbsp;(HOLD)
                    </div>
                    <div style="font-size:0.88rem;color:#92400E;line-height:1.65;
                                border-top:1px solid #FDE68A;padding-top:10px">
                        Hệ thống không thể hoàn thành yêu cầu tra cứu do <strong>thiếu văn bản
                        dẫn chiếu hợp lệ</strong> hoặc bằng chứng chính sách xác thực.
                        Nhân viên CRM không được tự suy diễn hoặc đưa ra câu trả lời khi chưa
                        có căn cứ văn bản.
                    </div>
                </div>
                <div style="flex-shrink:0;text-align:right">
                    <div style="background:#FEF3C7;border:1px solid #FDE68A;border-radius:6px;
                                padding:6px 12px;font-size:0.72rem;font-weight:700;
                                color:#78350F;white-space:nowrap">
                        Mã phân loại:<br>
                        <code style="background:transparent;color:#78350F;font-size:0.85rem">{code}</code>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):

        # Nguyên nhân tạm dừng
        st.markdown(
            f"""<div style="margin-bottom:14px">
                <div style="font-size:0.7rem;font-weight:700;letter-spacing:0.09em;
                            color:#64748B;text-transform:uppercase;margin-bottom:5px">
                    Nguyên nhân tạm dừng
                </div>
                <div style="font-size:0.95rem;color:#1E293B;line-height:1.65;
                            padding:10px 14px;background:#F8FAFC;border-radius:6px;
                            border:1px solid #E2E8F0">
                    {response.hold_reason or 'Không xác định — Vui lòng liên hệ bộ phận kỹ thuật.'}
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

        # Hướng dẫn xử lý nghiệp vụ
        if response.guidance:
            st.markdown(
                f"""<div style="margin-bottom:14px;background:#EFF6FF;border:1px solid #BFDBFE;
                             border-radius:8px;padding:14px 16px">
                    <div style="font-size:0.7rem;font-weight:700;letter-spacing:0.09em;
                                color:#1D4ED8;text-transform:uppercase;margin-bottom:6px">
                        Hướng dẫn xử lý nghiệp vụ
                    </div>
                    <div style="font-size:0.9rem;color:#1E3A5F;line-height:1.65">
                        {response.guidance}
                    </div>
                </div>""",
                unsafe_allow_html=True,
            )

        # Gợi ý bổ sung (thay thế mã kỹ thuật ANS 01, ANS 06 bằng ngôn ngữ nghiệp vụ)
        if response.clarifying_question:
            st.markdown(
                f"""<div style="margin-bottom:14px;background:#F0FDF4;border:1px solid #BBF7D0;
                             border-radius:8px;padding:14px 16px">
                    <div style="font-size:0.7rem;font-weight:700;letter-spacing:0.09em;
                                color:#166534;text-transform:uppercase;margin-bottom:6px;
                                display:flex;align-items:center;gap:6px">
                        {_SVG_HINT}
                        <span>Gợi ý bổ sung thông tin tra cứu</span>
                    </div>
                    <div style="font-size:0.9rem;color:#14532D;line-height:1.65;margin-bottom:8px">
                        {response.clarifying_question}
                    </div>
                    <div style="font-size:0.8rem;color:#166534;font-style:italic;
                                border-top:1px solid #BBF7D0;padding-top:8px">
                        Vui lòng cung cấp thêm số hiệu văn bản hoặc từ khóa chuyên ngành
                        để hệ thống tiếp tục tra cứu chính xác hơn.
                    </div>
                </div>""",
                unsafe_allow_html=True,
            )

        # Footer nguyên tắc an toàn
        st.markdown(
            f"""<div style="padding-top:10px;border-top:1px solid #E2E8F0;
                         font-size:0.75rem;color:#94A3B8;display:flex;
                         align-items:center;gap:6px">
                {_SVG_SHIELD_GRAY}
                <span>Nguyên tắc kiểm soát rủi ro (CKPA-47): Hệ thống không tự suy luận
                ngoại lệ khi thiếu căn cứ văn bản xác thực.</span>
            </div>""",
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------------
# REFUSAL — Từ chối
# ---------------------------------------------------------------------------
def _render_refusal(response: PolicyResponse) -> None:
    """Hiển thị trạng thái TỪ CHỐI (Prompt Injection / vi phạm)."""
    code = response.hold_reason_code or "REFUSAL"
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #FFF1F2 0%, #FFF5F5 100%);
            border-left: 5px solid #DC2626;
            border-top: 1px solid #FECACA;
            border-right: 1px solid #FECACA;
            border-bottom: 1px solid #FECACA;
            border-radius: 0 10px 10px 0;
            padding: 20px 24px;
            margin-bottom: 16px;
        ">
            <div style="display:flex;align-items:flex-start;gap:14px">
                <div style="margin-top:2px">{_SVG_BLOCK}</div>
                <div>
                    <div style="font-size:0.68rem;font-weight:800;letter-spacing:0.14em;
                                color:#9F1239;text-transform:uppercase;margin-bottom:3px">
                        Thông báo hệ thống &nbsp;—&nbsp; Từ chối xử lý
                    </div>
                    <div style="font-size:1.05rem;font-weight:700;color:#7F1D1D;margin-bottom:8px">
                        REFUSAL &nbsp;—&nbsp; VI PHẠM QUY TẮC AN TOÀN
                    </div>
                    <div>
                        <span style="background:#FEE2E2;border:1px solid #FECACA;
                                     border-radius:5px;padding:3px 10px;font-size:0.78rem;
                                     font-weight:700;color:#991B1B">
                            Mã: {code}
                        </span>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        st.write(response.hold_reason or "Yêu cầu không phù hợp với quy tắc an toàn hệ thống.")
        if response.guidance:
            st.info(f"💡 {response.guidance}")


# ---------------------------------------------------------------------------
# SUCCESS — Kết quả thành công
# ---------------------------------------------------------------------------
def _render_success(response: PolicyResponse) -> None:
    """Hiển thị câu trả lời thành công với 7 field cố định."""
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #F0FDF4 0%, #ECFDF5 100%);
            border-left: 5px solid #16A34A;
            border-top: 1px solid #BBF7D0;
            border-right: 1px solid #BBF7D0;
            border-bottom: 1px solid #BBF7D0;
            border-radius: 0 10px 10px 0;
            padding: 14px 20px;
            margin-bottom: 16px;
            display:flex;align-items:center;gap:12px
        ">
            {_SVG_CHECK}
            <div>
                <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.1em;
                            color:#166534;text-transform:uppercase">Kết quả tra cứu</div>
                <div style="font-size:0.95rem;font-weight:600;color:#14532D">
                    Đã xác thực và giải đáp theo chính sách — Thông tin có căn cứ văn bản
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- Thông tin tổng quan (3 trường metadata) ---
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(
                """<div style="font-size:0.7rem;font-weight:700;letter-spacing:0.07em;
                              color:#64748B;text-transform:uppercase;margin-bottom:4px">
                    Ngày hiệu lực
                </div>""",
                unsafe_allow_html=True,
            )
            st.write(response.effective_date or "Không xác định theo bằng chứng")
        with col2:
            st.markdown(
                """<div style="font-size:0.7rem;font-weight:700;letter-spacing:0.07em;
                              color:#64748B;text-transform:uppercase;margin-bottom:4px">
                    Phạm vi áp dụng
                </div>""",
                unsafe_allow_html=True,
            )
            st.write(response.scope or "Không xác định theo bằng chứng")
        with col3:
            st.markdown(
                """<div style="font-size:0.7rem;font-weight:700;letter-spacing:0.07em;
                              color:#64748B;text-transform:uppercase;margin-bottom:4px">
                    Đơn vị phụ trách
                </div>""",
                unsafe_allow_html=True,
            )
            st.write(response.policy_owner or "Không xác định theo bằng chứng")

    # --- Field 4: Thông tin cần bổ sung ---
    st.markdown(
        """<div style="font-size:0.7rem;font-weight:700;letter-spacing:0.07em;
                      color:#64748B;text-transform:uppercase;margin:16px 0 6px 0">
            Thông tin cần bổ sung từ khách hàng
        </div>""",
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        st.write(response.required_information or "_Không yêu cầu thêm thông tin_")

    # --- Field 5: Mức độ chắc chắn ---
    uncertainty = response.uncertainty_level or UncertaintyLevel.KHONG_XAC_DINH
    badge_color = _UNCERTAINTY_COLOR.get(uncertainty, "gray")
    badge_label = _UNCERTAINTY_LABEL.get(uncertainty, str(uncertainty.value))
    st.markdown(
        """<div style="margin:12px 0 4px 0;font-size:0.7rem;font-weight:700;
                       letter-spacing:0.07em;color:#64748B;text-transform:uppercase">
            Mức độ chắc chắn của câu trả lời
        </div>""",
        unsafe_allow_html=True,
    )
    st.markdown(f":{badge_color}[**{badge_label}**]")

    st.divider()

    # --- Field 6: Trích dẫn nguyên văn từ tài liệu (CKPA-39) ---
    st.markdown(
        f"""<div style="font-size:1.0rem;font-weight:700;color:#0F172A;margin-bottom:8px;
                      display:flex;align-items:center;gap:8px">
            {_SVG_DOC}
            <span>Trích dẫn nguyên văn từ tài liệu</span>
        </div>""",
        unsafe_allow_html=True,
    )
    st.markdown(
        """<div style="font-size:0.8rem;color:#92400E;margin-bottom:14px;
                      background:#FFFBEB;border:1px solid #FDE68A;border-radius:6px;
                      padding:8px 14px">
            ⚠️ Các đoạn văn bản dưới đây được giữ <strong>NGUYÊN VĂN</strong> từ nguồn chính thống,
            không chỉnh sửa. Đây là căn cứ pháp lý duy nhất.
        </div>""",
        unsafe_allow_html=True,
    )

    if not response.citations:
        st.warning("_Không có tài liệu trích dẫn đi kèm._")
    else:
        for idx, citation in enumerate(response.citations, 1):
            with st.expander(
                f"Nguồn {idx}: {citation.document_name} — {citation.section}",
                expanded=True,
            ):
                quote_lines = citation.verbatim_quote.replace("\n", "\n> ")
                st.markdown(f"> {quote_lines}")

                meta_parts = []
                if citation.clause_code:
                    meta_parts.append(f"Điều khoản: **{citation.clause_code}**")
                if citation.section:
                    meta_parts.append(f"Vị trí: {citation.section}")
                if meta_parts:
                    st.caption(" | ".join(meta_parts))

                if citation.source_url:
                    st.caption(f"🔗 [Xem tài liệu gốc]({citation.source_url})")
                else:
                    st.caption("🔗 Không có liên kết nguồn")

    st.divider()

    # --- Field 7: Giải thích của AI (CKPA-39: phân biệt với nguyên văn) ---
    st.markdown(
        f"""<div style="font-size:1.0rem;font-weight:700;color:#0F172A;margin-bottom:8px;
                      display:flex;align-items:center;gap:8px">
            {_SVG_INFO}
            <span>Giải thích của AI</span>
        </div>""",
        unsafe_allow_html=True,
    )
    st.markdown(
        """<div style="font-size:0.8rem;color:#1D4ED8;margin-bottom:12px;
                      background:#EFF6FF;border:1px solid #BFDBFE;border-radius:6px;
                      padding:8px 14px">
            Nội dung bên dưới là <strong>diễn giải</strong> của AI dựa trên tài liệu nguồn,
            không phải nội dung gốc của tài liệu. Cần kiểm tra lại trước khi tư vấn khách hàng.
        </div>""",
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        st.write(response.short_explanation or "_Không có giải thích_")

    st.markdown(
        f"""<div style="margin-top:16px;padding:10px 16px;background:#F8FAFC;
                      border:1px solid #E2E8F0;border-radius:8px;
                      font-size:0.76rem;color:#64748B;display:flex;align-items:center;gap:8px">
            {_SVG_SHIELD_GRAY}
            <span>Chỉ dùng nội bộ. Nhân viên CRM tự chịu trách nhiệm kiểm tra tính cập nhật
            của chính sách trước khi tư vấn khách hàng.</span>
        </div>""",
        unsafe_allow_html=True,
    )
