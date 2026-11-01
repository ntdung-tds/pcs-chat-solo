# Prompt chuẩn — PCS Chat Solo

Sao chép đoạn sau khi bắt đầu hoặc tiếp tục dự án:

```text
Hãy triển khai hoặc tiếp tục dự án của tôi dựa trên yêu cầu/SRS và repository dự án thực tế.

Sử dụng PCS Chat Solo tại https://github.com/ntdung-tds/pcs-chat-solo. Trước tiên chỉ đọc START_HERE.md; mở tài liệu PCS khác khi công việc cụ thể cần. Không đọc toàn bộ repository PCS hoặc mã nguồn không liên quan.

Nếu dự án đã có PCS, đọc pcs/MOMENT.md và pcs/STATE.json mới nhất cùng revision, xác minh tiến độ, rồi tiếp tục đúng phần đang dở. Nếu dự án mới, phân tích yêu cầu và khởi tạo một nguồn trạng thái phù hợp. Tự lựa chọn kiến trúc, lập kế hoạch, thực hiện và kiểm thử với các công cụ thực sự được cấp; chỉ hỏi tôi về quyền hoặc quyết định quan trọng.

GitHub (khi kết nối) là nguồn lưu trạng thái dự án. Repository có thể Public hoặc Private theo lựa chọn của tôi; nếu tạo mới mà tôi chưa chỉ định, hãy hỏi tôi. Chỉ công khai tài liệu, metadata và mã nguồn đã được phép xuất bản. Không tự nhận đã lưu, đã test hoặc đã triển khai nếu chưa xác minh. Không đưa dữ liệu mật lên repo công khai. Những hành động production/nhạy cảm phải có phê duyệt đúng quyền.

Tôi là Owner: hãy đưa kết quả chức năng hoặc mốc để tôi xem và góp ý; bạn tự xử lý công việc kỹ thuật bình thường. Cuối mỗi chặng, cập nhật STATE/MOMENT khi có quyền, rồi báo kết quả, bằng chứng, vướng mắc và hành động tiếp theo.
```

**Tiếp tục phiên khác:** dùng lại prompt này với liên kết repository dự án. Agent ưu tiên trạng thái và thay đổi mới nhất của dự án thay vì nạp lại các tài liệu PCS đã biết.

## Lệnh tiếp tục chuẩn (khi đã biết dự án)

```text
Tiếp tục dự án theo PCS, sử dụng trạng thái mới nhất trên GitHub.
```

AI dùng repository dự án đã xác định, ưu tiên `pcs/MOMENT.md` và đối chiếu revision/HEAD với `pcs/STATE.json`. Chỉ truy xuất nhiệm vụ, code, thay đổi và test có liên quan; sau đó tiếp tục và checkpoint theo quyền thực tế. Nếu chưa biết repository, hỏi đúng liên kết dự án; không suy đoán. Nếu GitHub không truy cập được, thông báo trạng thái chưa được đồng bộ.
