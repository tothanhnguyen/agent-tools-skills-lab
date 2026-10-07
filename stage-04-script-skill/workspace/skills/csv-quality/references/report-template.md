# Báo cáo chất lượng và quá tải: `{đường dẫn CSV}`

Nguồn: `{đường dẫn CSV}` | Script: `skills/csv-quality/scripts/check_csv.py` | Exit: {exit_code}

## Ngưỡng và tổng giờ

Ngưỡng: **{max_hours} giờ**. Quá tải khi tổng giờ **lớn hơn** ngưỡng; bằng ngưỡng không quá tải.
Tổng chỉ bao gồm dòng hợp lệ, không trùng. Mỗi ID giữ lần xuất hiện đầu tiên kể cả khi lần đầu lỗi; các dòng trống bỏ qua.

| Owner | Tổng giờ | Trạng thái theo overloaded_owners |
|---|---|---|
| {owner từ hours_by_owner} | {total_hours} | {vượt ngưỡng / không vượt} |

## Người quá tải

{Danh sách owner và total_hours lấy từ overloaded_owners; nếu danh sách rỗng ghi Không có người quá tải.}

## Dòng bị loại

| Line | task_id | Tất cả reasons |
|---|---|---|
| {line} | {task_id hoặc null} | {reasons theo JSON} |

Mã: wrong_field_count = sai số trường; missing_task_id = thiếu ID; duplicate_id = ID trùng; missing_owner = thiếu người phụ trách; invalid_hours = giờ không hữu hạn/âm/không phải số.

## Chất lượng toàn bộ dữ liệu

| Chỉ số | Giá trị |
|---|---|
| Số dòng dữ liệu không trống | {row_count} |
| Dòng thiếu owner | {missing_owner_count} |
| Dòng hours không hợp lệ | {invalid_hours_count} |
| Số ID trùng (distinct) | {duplicate_id_count} ({duplicate_ids}) |

## Chi tiết lỗi

| Line | Cột | Loại | task_id | Mô tả |
|---|---|---|---|---|
| {line} | {column} | {type} | {task_id} | {message} |

## Đánh giá và khuyến nghị

{Giới hạn của tổng đã lọc; đề xuất sửa dữ liệu. Không sửa đầu vào. Không bịa số liệu ngoài JSON.}
