---
name: refund-policy
description: Tra cứu chính sách hoàn tiền trong tài liệu của workspace, chọn phiên bản theo ngày mua và đánh giá điều kiện hoàn tiền, thời hạn và phí. Dùng khi người dùng hỏi có được hoàn tiền, yêu cầu kiểm tra điều kiện hoàn tiền hoặc chính sách hoàn tiền áp dụng cho một giao dịch.
---

# Tra cứu chính sách hoàn tiền

1. Đọc `references/answer-template.md` bằng `read_file`, tức `skills/refund-policy/references/answer-template.md`.
2. Cần ngày mua, ngày yêu cầu hoàn và trạng thái kích hoạt của giao dịch hiện tại. Nếu thiếu thông tin nào, hỏi lại thông tin đó và dừng trước khi kết luận đủ hay không đủ điều kiện. Không tự giả định trạng thái kích hoạt; không dùng ngày hiện tại của máy làm ngày yêu cầu. Ngày dạng DD/MM/YYYY là ngày/tháng/năm; nếu ngày không hợp lệ, không rõ hoặc yêu cầu trước ngày mua, hỏi lại để xác nhận.
3. Gọi `list_files` với `data/policies/` để tìm các tài liệu chính sách hiện có. Không đoán hoặc cố định tên file. Đọc các file văn bản chính sách trong kết quả bằng `read_file` để kiểm tra phạm vi hiệu lực và các điều kiện trong nội dung. Tên file không quyết định phiên bản.
4. Chọn chính sách theo **ngày mua**, không theo ngày yêu cầu hoàn. Đọc rõ cận ngày nào có bao gồm hay không từ tài liệu. Nếu không có chính sách phù hợp, có nhiều chính sách chồng lấn hoặc nội dung mâu thuẫn, giải thích và hỏi thêm; không tự chọn tùy ý.
5. Số ngày đã qua là chênh lệch ngày lịch giữa ngày yêu cầu và ngày mua. So sánh với thời hạn trong chính sách được chọn; bằng đúng giới hạn vẫn đạt điều kiện thời gian. Kiểm tra cả điều kiện kích hoạt và các điều kiện khác ghi trong tài liệu trước khi kết luận.
6. Trình bày theo template: tên/phạm vi chính sách, ngày giao dịch, số ngày, kết luận và lý do, phí nếu đủ điều kiện, đường dẫn tài liệu đã đọc làm căn cứ. Chỉ nêu phí từ nguồn; không bịa giá trị đơn hàng hay số tiền. Nếu không đủ điều kiện, phí là không áp dụng.
7. Chỉ dùng `list_files`, `read_file` và `write_file` khi cần lưu báo cáo theo yêu cầu. Không dùng Bash hoặc script. Nếu tool lỗi, báo lỗi và dừng phần đánh giá dựa trên dữ liệu chưa đọc được.
