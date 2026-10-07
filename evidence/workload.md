# Báo cáo chất lượng và quá tải: `data/workload.csv`

Nguồn: `data/workload.csv` | Script: `skills/csv-quality/scripts/check_csv.py` | Exit: 0

## Ngưỡng và tổng giờ

Ngưỡng: **8.0 giờ**. Quá tải khi tổng giờ **lớn hơn** ngưỡng; bằng ngưỡng không quá tải.
Tổng chỉ bao gồm dòng hợp lệ, không trùng. Mỗi ID giữ lần xuất hiện đầu tiên kể cả khi lần đầu lỗi; các dòng trống bỏ qua.

| Owner | Tổng giờ | Trạng thái theo overloaded_owners |
|---|---|---|
| Lan | 9.0 | Vượt ngưỡng |
| Minh | 3.0 | Không vượt |

## Người quá tải

- **Lan**: 9.0 giờ

## Dòng bị loại

| Line | task_id | Tất cả reasons |
|---|---|---|
| 5 | T04 | invalid_hours |
| 6 | T02 | duplicate_id |
| 7 | T05 | missing_owner |

Mã: wrong_field_count = sai số trường; missing_task_id = thiếu ID; duplicate_id = ID trùng; missing_owner = thiếu người phụ trách; invalid_hours = giờ không hữu hạn/âm/không phải số.

## Chất lượng toàn bộ dữ liệu

| Chỉ số | Giá trị |
|---|---|
| Số dòng dữ liệu không trống | 6 |
| Dòng thiếu owner | 1 |
| Dòng hours không hợp lệ | 1 |
| Số ID trùng (distinct) | 1 (T02) |

## Chi tiết lỗi

| Line | Cột | Loại | task_id | Mô tả |
|---|---|---|---|---|
| 5 | hours | invalid_hours | T04 | hours 'abc' không phải số hữu hạn không âm. |
| 6 | task_id | duplicate_id | T02 | task_id T02 đã xuất hiện ở line 3. |
| 7 | owner | missing_owner | T05 | owner trống. |

## Đánh giá và khuyến nghị

Tổng giờ được tính trên các dòng hợp lệ, không trùng (loại bỏ các dòng bị lỗi cấu trúc/dữ liệu). Dữ liệu có các vấn đề cần khắc phục: dòng 5 có giờ không hợp lệ ('abc'), dòng 6 bị trùng task_id (T02), và dòng 7 thiếu owner. Cần chuẩn hóa lại file CSV nguồn để đảm bảo độ chính xác của workload.
