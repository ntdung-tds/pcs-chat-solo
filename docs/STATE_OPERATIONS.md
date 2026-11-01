# Chat Solo — trạng thái gọn, chẩn đoán và GitHub an toàn

## Nguyên tắc

- Dùng chat + GitHub connector nếu đã kết nối; **không bắt buộc chạy Python**. Bộ Python chỉ là công cụ kiểm tra tùy chọn, không tạo GitHub credentials hay tự đồng bộ.
- Với dự án có sẵn, đọc `pcs/MOMENT.md`, rồi kiểm tra `pcs/STATE.json` canonical tại revision/commit hiện tại; mở mã nguồn và test liên quan. Không đọc toàn bộ repo PCS hoặc mọi tệp dự án.
- Moment giới hạn công việc được trình bày; toàn bộ backlog vẫn ở STATE. Nếu state lớn, connector nên tìm và chỉ xuất các mục liên quan, nhưng **trước khi ghi** phải kiểm tra revision, các tham chiếu và chính sách dự án.

## Public hoặc Private — chủ dự án lựa chọn

AI sử dụng repository sẵn có. Nếu tạo mới mà chưa được chỉ định quyền hiển thị, hãy hỏi chủ dự án chọn `Public` hoặc `Private`; không tự áp đặt. `USER_CHOICE` trong mẫu có nghĩa là **chưa quyết định**, không phải giấy phép tạo repo Public.

- Public: chỉ đưa dữ liệu được phép công khai. Chính sách STATE cần `repository_visibility:'PUBLIC'`, `content_classification:'PUBLIC'`, `public_content_reviewed:true`. Các phần việc, quyết định, rủi ro, nguồn và artifact ghi trong state phải được phân loại PUBLIC. Phải kiểm tra cả Git history, Issue/PR, ảnh và báo cáo; không chỉ quét regex. Cờ review do AI ghi không thay thế phê duyệt Owner có thể xác minh.
- Private: dành cho nội bộ và quyền hạn chế; cũng không được lưu secrets/credential dưới dạng plaintext. Dữ liệu CONFIDENTIAL/RESTRICTED phải có chính sách lưu và kiểm soát riêng, không được mặc nhiên upload chỉ vì repo Private.
- Những thao tác quyền hạn, production, xóa dữ liệu hoặc công khai thông tin quan trọng cần được Owner phê duyệt phù hợp.

## Chẩn đoán khi thực sự cần

Với ứng dụng AI có Python 3.10+ và workspace cục bộ, có thể gọi công cụ **chỉ đọc**:
```bash
python tools/pcs_solo.py inspect --root=/path/to/project --group=tasks --limit=12
python tools/pcs_solo.py diff --before=/path/to/old_state.json --after=/path/to/new_state.json --limit=12
```
Chỉ xuất ID, trạng thái, số lượng và tên trường thay đổi; không in toàn bộ mô tả để hạn chế rò rỉ nội dung. Giới hạn 1–50 mục. Khi không có Python, AI dùng GitHub connector/công cụ đã kết nối để xem dữ liệu tương ứng. Không yêu cầu người dùng cài runtime chỉ để bắt đầu làm dự án.

## Các giới hạn thực tế

Solo không cung cấp KMS, mã hóa artifact hoặc dịch vụ xoay vòng khóa. Nếu dự án cần bảo mật dữ liệu nhạy cảm, phải dùng nền tảng lưu trữ và hệ thống quản trị khóa được phép, không tự mở rộng đặc quyền từ hướng dẫn PCS. Kiểm thử hiện tại là kiểm thử cấu trúc/cục bộ; kiểm thử GitHub kết nối thật và đổi chat vẫn phải thực hiện theo [ACCEPTANCE_MATRIX](ACCEPTANCE_MATRIX.md) / [Issue #4](https://github.com/ntdung-tds/pcs-chat-solo/issues/4). Không đánh dấu E2E PASS từ unit tests.

Khi GitHub trả 403/409 hoặc một phiên khác đã cập nhật STATE, không force push; tải revision mới, xác định diff, hòa giải rồi checkpoint nhất quán; PR chưa merge không đồng nghĩa đã lưu canonical.
