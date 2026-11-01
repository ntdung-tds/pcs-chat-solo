# PCS Chat Solo — SRS/đề cương change history

**Một mục được sửa nhiều lần, nhưng chỉ bản đã được chốt cuối cùng mới có hiệu lực.**

- SRS/đề cương gốc giữ nguyên: mã mục, nguồn, SHA-256, bản/commit.
- Mỗi lần đề xuất sửa được tạo `CR-###` và tài liệu ở **repository dự án** `docs/project/changes/CR-###.md` (đảm bảo có Git history); ghi lý do, phần cũ, phần mới, phạm vi ảnh hưởng, tác giả, thời điểm, ý kiến Owner và link Issue/PR.
- Chỉ khi Owner chốt và quyết định có bằng chứng xác minh, CR mới chuyển sang `APPROVED`. Các sửa `PROPOSED` hoặc `REJECTED` không thay đổi yêu cầu có hiệu lực. Bản duy nhất có hiệu lực được tìm bằng chuỗi `based_on`: `BASELINE → CR-001 → CR-002`.
- Ví dụ: 12 ký tự (SRS) → CR-001 chốt 10 → CR-002 chốt 8 → CR-003 đang đề xuất 9: yêu cầu hiệu lực là **8 ký tự**. Cấm chấp thuận hai bản cùng thay thế một phiên bản; phải reconcile và chốt lại rõ ràng.
- Lưu index gọn vào `pcs/STATE.json` tại `state.requirement_changes[]` (trường **tùy chọn**, không đổi schema). Mỗi record có `id`, `item_id`, `baseline_ref`, `baseline_sha256` (64 hex), `based_on`, `status`. Với `APPROVED`, yêu cầu thêm `final_ref`, `final_sha256`, `decision.by`, `decision.ref` đến bằng chứng trên GitHub. Nội dung chi tiết nằm trong các CR đã version hóa, không chép dài vào context.
- AI phải đối chiếu thật thông tin xác minh Owner, bản gốc, final wording và digest; metadata `APPROVED` **không phải** tự động chứng minh phê duyệt thật. Với thao tác production, IAM, bảo mật, xóa dữ liệu, chi phí, phải có approval cấp nền tảng phù hợp.
- Đưa checklist tiến độ vào bốn cổng riêng: **Change approved → Implementation updated → Tests updated/passed → Feature accepted**. Việc chốt yêu cầu không đồng nghĩa đã sửa code hoặc nghiệm thu.
- Khi resume, chỉ lấy bản chốt hiện hành, số yêu cầu đang đề xuất và mã CR liên quan, không nạp cả lịch sử. Khi ghi, giữ CAS revision, PR/branch protection và kiểm tra Git HEAD. Không dual-write nguồn thứ hai.

Công cụ tùy chọn (chỉ đọc, không kết nối GitHub):

```bash
python tools/pcs_requirements.py --file=/project/pcs/STATE.json --item=FEAT-001
```

Công cụ kiểm tra record/chuỗi quyết định; **không** xác thực nguồn ngoài, phê duyệt hay tiến độ triển khai. Không có Python vẫn có thể dùng GitHub connector và cùng nguyên tắc trên.
