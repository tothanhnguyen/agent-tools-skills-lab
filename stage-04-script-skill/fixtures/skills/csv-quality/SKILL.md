---
name: csv-quality
description: Kiểm tra chất lượng CSV công việc (task_id, owner, hours), tính tổng giờ theo người và xác định người quá tải theo ngưỡng người dùng cung cấp bằng script có sẵn; ghi báo cáo Markdown dưới output/. Dùng khi người dùng yêu cầu kiểm tra CSV công việc, tổng giờ theo owner, người vượt ngưỡng hoặc quá tải công việc.
---

# CSV quality và workload

## Xác nhận đầu vào

1. Cần đường dẫn CSV và ngưỡng tối đa giờ cho **yêu cầu hiện tại**. Nếu thiếu ngưỡng, hỏi lại trước khi chạy phân tích hoặc kết luận người quá tải. Không mặc định ngưỡng, không dùng ngưỡng từ cuộc trò chuyện/lượt yêu cầu cũ. Quy tắc này cũng áp dụng khi người dùng chỉ hỏi chất lượng CSV vì CLI yêu cầu ngưỡng.
2. Ngưỡng là số hữu hạn không âm; giá trị 0 hợp lệ. Nếu không rõ, âm hoặc không hữu hạn, hỏi ngưỡng hợp lệ.
3. Đọc `references/report-template.md`, tức `skills/csv-quality/references/report-template.md`, để dùng cấu trúc báo cáo.

## Chạy script

Dùng tool `bash` có cwd là workspace:

```text
python skills/csv-quality/scripts/check_csv.py --input <đường dẫn CSV> --max-hours <ngưỡng trong yêu cầu hiện tại>
```

Đường dẫn trong lệnh tương đối workspace, không thêm `workspace/`. Quote đường dẫn nếu có khoảng trắng. Không cần đọc source script để chạy. Không tự tính số liệu bằng mắt hoặc tự viết thuật toán thay thế script này.

## Diễn giải JSON

- Exit 0 và ok=true, timed_out=false: phân tích thành công, kể cả có lỗi chất lượng dữ liệu hoặc người quá tải. Lấy số liệu từ stdout JSON.
- Giữ các trường chất lượng `row_count`, `missing_owner_count`, `invalid_hours_count`, `duplicate_id_count`, `duplicate_ids`, `issues`; chúng phân tích toàn bộ dòng dữ liệu không trống.
- `max_hours` là ngưỡng đã truyền; `hours_by_owner` là tổng giờ từ những dòng được chấp nhận; `overloaded_owners` là người có tổng **lớn hơn** ngưỡng, bằng ngưỡng không quá tải.
- Chuẩn hóa khoảng trắng nhưng không gộp tên owner khác hoa/thường. Mỗi task_id không rỗng giữ lần xuất hiện đầu tiên, kể cả lần đầu không hợp lệ. Dòng sau không thay thế lần đầu.
- `excluded_rows` liệt kê mỗi dòng bị loại một lần cùng tất cả reasons: wrong_field_count, missing_task_id, duplicate_id, missing_owner, invalid_hours. Header là line 1. Giờ 0 hợp lệ.
- Dữ liệu lỗi vẫn có thể có tổng giờ hợp lệ của các dòng được chấp nhận. Không bỏ toàn bộ kết quả chỉ vì có issues; nêu rõ tổng giờ này loại các dòng sai và trùng.
- Exit khác 0, timed_out=true hoặc ok=false: đọc stderr/error và báo không phân tích được. Không đưa tổng giờ, không ghi báo cáo như thể thành công. Thiếu ngưỡng/CLI không hợp lệ cũng là lỗi thực thi.

## Báo cáo

1. Dùng template đã đọc; ghi ngưỡng, bảng tổng theo người, danh sách vượt ngưỡng (hoặc Không có), excluded_rows với line/task_id/reasons và các thống kê/chi tiết chất lượng cũ.
2. Lấy mọi con số từ JSON; không tự thêm owner, giờ hay dòng được chấp nhận. Nêu tổng tính trên dữ liệu đã lọc và quy tắc lần xuất hiện đầu tiên.
3. Không sửa CSV. Chỉ đề xuất cách sửa trong phần khuyến nghị.
4. Nếu người dùng yêu cầu lưu báo cáo, dùng `write_file` vào đường dẫn chỉ định (mặc định `output/csv-quality.md`). Chỉ xác nhận đã ghi sau tool result thành công. Nếu không yêu cầu file, trả kết quả theo cùng cấu trúc.
