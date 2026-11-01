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

## Chính sách cố định: Chỉ lưu thay đổi, không đồng bộ SRS trong lúc triển khai

**Quyết định của Owner:** SRS/đề cương ban đầu là tài liệu tham chiếu được giữ nguyên suốt vòng đời phát triển. Dù CR đã được đề xuất, chốt, triển khai, kiểm thử hoặc nghiệm thu, PCS **không được tự sửa, ghi đè hoặc đồng bộ SRS/đề cương**. Một CR được chốt chỉ cập nhật **yêu cầu có hiệu lực để thực hiện dự án trong PCS**, không có nghĩa tài liệu gốc đã được cập nhật.

- **Trong quá trình làm:** Lưu tất cả lần đề xuất, sửa, từ chối, chốt và thay thế; giữ nội dung trước/sau, lý do, người đề xuất, quyết định, thời điểm và bằng chứng GitHub. AI triển khai, kiểm thử, nghiệm thu theo **bản chốt cuối hiện hành** của từng mục. Không tạo công việc cập nhật SRS tự động, không lấy việc SRS chưa sửa làm lý do chặn nghiệm thu chức năng hay hoàn tất dự án.
- **Khi hoàn tất toàn bộ dự án:** PCS chỉ **tổng hợp báo cáo thay đổi để Owner xem xét** theo từng mục SRS/đề cương: bản gốc, bản chốt cuối, lịch sử CR (kể cả bản bị thay thế/từ chối), liên kết bằng chứng và những đề xuất chưa chốt. Báo cáo phải ghi **CHỜ OWNER QUYẾT ĐỊNH — CHƯA ĐỒNG BỘ**.
- **Chỉ nếu Owner quyết định đồng bộ:** Khi ấy mới tạo đề xuất cập nhật tài liệu/PR riêng, giữ nguyên bản gốc và lịch sử, kiểm tra tác động và nghiệm thu thay đổi tài liệu. Không suy diễn quyền đồng bộ từ lời đồng ý một CR, nghiệm thu chức năng, CI PASS, việc hoàn tất dự án hoặc lệnh tiếp tục PCS. Nếu Owner hoãn/không đồng ý, giữ SRS cũ và lưu lịch sử để dùng sau.

**Ba trạng thái độc lập:** CR được chốt ≠ chức năng hoàn thành/nghiệm thu ≠ SRS được đồng bộ. Đồng bộ SRS là **không bắt buộc** và luôn do Owner quyết định sau khi hoàn tất dự án.

Công cụ tùy chọn (chỉ đọc, không kết nối GitHub):

```bash
python tools/pcs_requirements.py --file=/project/pcs/STATE.json --item=FEAT-001
```

Công cụ kiểm tra record/chuỗi quyết định; **không** xác thực nguồn ngoài, phê duyệt hay tiến độ triển khai. Không có Python vẫn có thể dùng GitHub connector và cùng nguyên tắc trên.
