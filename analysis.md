# Báo cáo kết quả thực hành: Block 1 và Block 2

Sinh viên: Tô Thành Nguyên (24521207)
Ngày thực hiện: 07/10/2026. Dữ liệu thử nghiệm dùng mock và hệ thống dùng Gemini thật cho model. Hướng dẫn chạy lab có trong README.md.

# Phân tích Block 1: tra cứu chính sách đúng phiên bản

Block 1 được triển khai ở Stage 01/02; Block 2 ở Stage 03/04. Phân tích và evidence của cả hai phần nằm trong repository này.

## Thay đổi và giới hạn phạm vi

- Stage 01/02: thêm `_list` và tool `list_files(path)` trong `tools/files.py`, export ở `tools/__init__.py` và đăng ký vào `TOOLS` trong `agent.py`.
- Liệt kê các mục trực tiếp, không đệ quy, sắp xếp theo tên. JSON thành công có `ok`, `path`, `entries`; mỗi mục có `name`, `path` tương đối workspace và `type` là file/directory.
- Dùng lại `_resolve` và `_error`. Kiểm tra cả đường dẫn thư mục và từng mục sau resolve để chặn escape qua `..`, absolute path, symlink/junction. File/missing path trả lỗi rõ ràng; thư mục rỗng trả thành công với entries rỗng.
- Stage 02 thêm `skills/refund-policy/SKILL.md` và `references/answer-template.md`. Skill hướng dẫn tìm tài liệu bằng tool, chọn theo ngày mua, dùng ngày yêu cầu trong câu hỏi, tính chênh lệch ngày lịch, kiểm tra kích hoạt và hỏi lại dữ liệu thiếu trước khi kết luận.
- Hai tài liệu chính sách và skill/reference có bản đồng bộ trong `workspace` và `fixtures` để giữ bài làm qua reset.
- Không sửa system prompt; không hard-code tên file chính sách, ngày hiệu lực, điều khoản hoặc đáp án trong tool. Stage 02 không dùng Bash/script để làm nghiệp vụ.
- Cập nhật test kỳ vọng tools/catalog và thêm test list_files. `runtime/gemini_app.py` là launcher tương thích provider từ bước setup, giữ thought-signature metadata của Gemini; không thay đổi nghiệp vụ hoặc thêm tool. Các model test dưới đây gọi Gemini thật.

## Test trực tiếp và tự động

Mỗi stage có 5/5 direct tool checks thành công: valid directory; file → NOT_A_DIRECTORY; missing → FILE_NOT_FOUND; traversal/absolute → PATH_OUTSIDE_WORKSPACE. JSON ở `evidence/stage-01-files_direct_tools.json` và `evidence/stage-02-skills_direct_tools.json`.

Stage 01: **43 passed, 4 skipped, 0 failed**. Stage 02: **52 passed, 4 skipped, 0 failed**. Các skip do Windows error 1314 khi tạo symlink fixture; không coi là đã xác minh symlink. Test directory-junction escape thực tế trên Windows pass ở cả hai stage. Xem `evidence/test-results.json`; tái chạy `uv run --locked pytest -q -rs` trong mỗi stage.

Các test còn bao phủ non-recursion, thứ tự, thư mục rỗng, lỗi I/O có cấu trúc, schema `path`, tool result đến request sau và initial context chỉ có metadata skill. Khi hoàn thành Block 1, Stage 03/04 chưa thay đổi; Block 2 được triển khai sau đó.

## Stage 00 và Stage 01

### stage-00-chat — case A

1 model call, 0 tool call. Trace: `evidence\stage-00-chat_A.jsonl`.

Câu trả lời thực tế (giữ nguyên):

> Tôi không có tool truy cập vào hệ thống dữ liệu hoặc chính sách đổi trả của cửa hàng để kiểm tra trường hợp của bạn. Do đó, tôi không thể xác định chính xác bạn có được hoàn tiền hay không. 
> 
> Tuy nhiên, tính từ ngày mua (28/09/2026) đến ngày yêu cầu hoàn (06/10/2026) là **8 ngày**, và sản phẩm **chưa kích hoạt**. Bạn vui lòng cung cấp thông tin này trực tiếp cho bộ phận hỗ trợ khách hàng của nơi bạn mua để được tư vấn chính xác theo chính sách hiện hành nhé.

Stage 00 không có khả năng tìm/đọc chính sách; không có tool result làm căn cứ để kết luận điều kiện hoàn tiền.

### stage-01-files — case A

6 model call, 5 tool call. Trace: `evidence\stage-01-files_A.jsonl`.

Câu trả lời thực tế (giữ nguyên):

> Dựa trên thông tin bạn cung cấp và chính sách áp dụng:
> 
> - **Ngày mua:** 28/09/2026 (trước ngày 01/10/2026 nên áp dụng **Chính sách hoàn tiền trước tháng 10**).
> - **Quy định thời hạn:** Được yêu cầu hoàn tiền trong **7 ngày** kể từ ngày mua.
> - **Tính thời gian:** Từ 28/09/2026 đến 06/10/2026 là **8 ngày** (vượt quá thời hạn 7 ngày cho phép).
> - **Trạng thái:** Sản phẩm chưa kích hoạt.
> 
> Do thời gian yêu cầu hoàn (8 ngày) đã vượt quá hạn mức 7 ngày theo chính sách, **bạn không được hoàn tiền**. Ngoài ra, nếu mua trong khoảng thời gian này, chính sách cũng quy định phí hoàn tiền là 10% (nếu trong hạn).

Stage 01 có thể khám phá tên thật rồi đọc tài liệu; Stage 02 bổ sung quy trình nghiệp vụ bằng skill.

## Các trường hợp Stage 02

Mỗi case dùng cuộc trò chuyện mới, không nêu skill/tên file/thứ tự tool trong câu hỏi. Renamed_A/B dùng terms-alpha.md và terms-beta.md, giữ nguyên nội dung; tên gốc được khôi phục sau kiểm tra.

| Case | Kết quả | Model/tool calls | Trace |
|---|---|---|---|
| A | Chính sách cũ; 8 ngày; không đủ điều kiện | 4/5 | `evidence\stage-02-skills_A.jsonl` |
| B | Chính sách mới; 10 ngày; đủ điều kiện; không phí | 5/4 | `evidence\stage-02-skills_B.jsonl` |
| renamed_A | 8 ngày; không đủ; nguồn terms-alpha.md | 7/6 | `evidence\stage-02-skills_renamed_A.jsonl` |
| renamed_B | 10 ngày; đủ; không phí; nguồn terms-beta.md | 6/5 | `evidence\stage-02-skills_renamed_B.jsonl` |
| missing_activation | Hỏi trạng thái kích hoạt; chưa kết luận | 5/4 | `evidence\stage-02-skills_missing_activation.jsonl` |

## Bằng chứng cụ thể trong trace

Sequence là số thứ tự event; tool_call_id nối request thực thi với tool message.

### A — `evidence\stage-02-skills_A.jsonl`

- Request đầu sequence 2: schema có list_files; system prompt chứa metadata, chưa có body skill.
- Tool result sequence 5: `read_file(skills/refund-policy/SKILL.md)`, ID `call_751377`, ok=True.
- Tool result sequence 10: `read_file(skills/refund-policy/references/answer-template.md)`, ID `call_531434`, ok=True.
- Tool result sequence 11: `list_files(data/policies)`, ID `call_531435`, ok=True.
- Tool result sequence 16: `read_file(data/policies/policy-from-oct.md)`, ID `call_594093`, ok=True.
- Tool result sequence 17: `read_file(data/policies/policy-before-oct.md)`, ID `call_594092`, ok=True.
- Skill ở message index 2; ID `call_751377`; vào request lần đầu Lượt 1, model call #2.
- run_completed sequence 20.

### B — `evidence\stage-02-skills_B.jsonl`

- Request đầu sequence 2: schema có list_files; system prompt chứa metadata, chưa có body skill.
- Tool result sequence 5: `read_file(skills/refund-policy/SKILL.md)`, ID `call_691527`, ok=True.
- Tool result sequence 9: `read_file(skills/refund-policy/references/answer-template.md)`, ID `call_865383`, ok=True.
- Tool result sequence 13: `list_files(data/policies)`, ID `call_783305`, ok=True.
- Tool result sequence 17: `read_file(data/policies/policy-from-oct.md)`, ID `call_202934`, ok=True.
- Skill ở message index 2; ID `call_691527`; vào request lần đầu Lượt 1, model call #2.
- run_completed sequence 20.

### renamed_A — `evidence\stage-02-skills_renamed_A.jsonl`

- Request đầu sequence 2: schema có list_files; system prompt chứa metadata, chưa có body skill.
- Tool result sequence 5: `read_file(skills/refund-policy/SKILL.md)`, ID `call_414289`, ok=True.
- Tool result sequence 9: `read_file(skills/refund-policy/references/answer-template.md)`, ID `call_568876`, ok=True.
- Tool result sequence 13: `list_files(data/policies)`, ID `call_853689`, ok=True.
- Tool result sequence 17: `read_file(data/policies/terms-alpha.md)`, ID `call_643943`, ok=True.
- Tool result sequence 21: `read_file(data/policies/terms-beta.md)`, ID `call_345547`, ok=True.
- Tool result sequence 25: `write_file(output/refund-result.md)`, ID `call_542314`, ok=True.
- Skill ở message index 2; ID `call_414289`; vào request lần đầu Lượt 1, model call #2.
- run_completed sequence 28.

### renamed_B — `evidence\stage-02-skills_renamed_B.jsonl`

- Request đầu sequence 2: schema có list_files; system prompt chứa metadata, chưa có body skill.
- Tool result sequence 5: `read_file(skills/refund-policy/SKILL.md)`, ID `call_803709`, ok=True.
- Tool result sequence 9: `read_file(skills/refund-policy/references/answer-template.md)`, ID `call_578087`, ok=True.
- Tool result sequence 13: `list_files(data/policies)`, ID `call_537087`, ok=True.
- Tool result sequence 17: `read_file(data/policies/terms-alpha.md)`, ID `call_599179`, ok=True.
- Tool result sequence 21: `read_file(data/policies/terms-beta.md)`, ID `call_750348`, ok=True.
- Skill ở message index 2; ID `call_803709`; vào request lần đầu Lượt 1, model call #2.
- run_completed sequence 24.

### missing_activation — `evidence\stage-02-skills_missing_activation.jsonl`

- Request đầu sequence 2: schema có list_files; system prompt chứa metadata, chưa có body skill.
- Tool result sequence 5: `read_file(skills/refund-policy/SKILL.md)`, ID `call_578397`, ok=True.
- Tool result sequence 9: `read_file(skills/refund-policy/references/answer-template.md)`, ID `call_13405`, ok=True.
- Tool result sequence 13: `list_files(data/policies)`, ID `call_594165`, ok=True.
- Tool result sequence 17: `read_file(data/policies/policy-from-oct.md)`, ID `call_384217`, ok=True.
- Skill ở message index 2; ID `call_578397`; vào request lần đầu Lượt 1, model call #2.
- run_completed sequence 20.

## Câu hỏi cuối bài

**Vì sao cần tool tìm file và skill chọn chính sách?** Tool thực thi quan sát môi trường: liệt kê tên/path thật đang tồn tại rồi đọc nội dung vào context. Skill hướng dẫn cách sử dụng thông tin: chọn theo ngày mua, tính số ngày, kiểm tra kích hoạt, hỏi thông tin thiếu và trình bày căn cứ. Một phần là năng lực thực thi, phần còn lại là quy trình nghiệp vụ.

**Nếu chưa có tool tìm file, sửa prompt có giải quyết được đổi tên file không?** Không bảo đảm. Prompt không tự tạo khả năng liệt kê. Chỉ có read_file thì model phải biết/đoán đường dẫn hoặc hỏi người dùng; tên đổi sẽ làm đường dẫn đoán không còn hợp lệ. list_files cung cấp bằng chứng tên hiện tại, còn skill yêu cầu lựa chọn từ nội dung hiệu lực thay vì tên file.

## Tái hiện kết quả

Xem README.md để khởi động app và chạy tests. Các JSONL có tên case trong evidence/ giữ snapshot và tool results; evidence/stage-02-skills_results.json giữ prompt, answer và inventory của từng trường hợp.

Gemini free tier trước đó trả giới hạn 15 request/phút; runner giãn cách 60 giây giữa các case. Final answer có thể khác cách diễn đạt; đối chiếu số ngày, kết luận, phí và đường dẫn thực sự đã đọc. Nếu gặp 429, chờ rồi chạy lại cuộc trò chuyện mới; không coi lượt lỗi là pass.

Tất cả mã nguồn, policy documents, skill/reference, tests, traces và phân tích đều nằm trong repository. Không cần ZIP. `.env` dùng để chạy local và đã được ignore; không đưa API key vào báo cáo hoặc screenshot.

Ghi chú trình bày: final answer của renamed_B có token thừa `AppComponent` trước phần Markdown. Các trường nghiệp vụ và nguồn vẫn đúng; giữ nguyên raw answer trong evidence để minh bạch.

---

# Phân tích Block 2: tính giờ và phát hiện quá tải

## Thay đổi

Chỉ mở rộng skill csv-quality, reference và script sẵn có của Stage 04 để làm nghiệp vụ. Không thêm tool; agent.py, prompts.py và các tool Stage 03/04 giữ nguyên. Gemini launcher là lớp tương thích provider; Docker chạy POSIX Bash với repository mount trực tiếp và môi trường Python Linux riêng.

CLI yêu cầu --max-hours hữu hạn, không âm; thiếu/sai tham số trả stderr và exit khác 0. Phân tích hợp lệ exit 0 kể cả khi có dòng lỗi hoặc quá tải. Những lỗi file/schema/parse cũ vẫn exit 1. Script không sửa CSV.

Duyệt mọi dòng không trống; trim ID/owner/hours và giữ owner phân biệt hoa/thường. Mọi ID không trống được giữ tại lần đầu, ngay cả khi dòng đó sai. Chỉ cộng dòng đủ số trường, có ID và owner, hours hữu hạn không âm, không trùng. Mỗi dòng bị loại xuất hiện một lần, chứa mọi lý do theo thứ tự wrong_field_count → missing_task_id → duplicate_id → missing_owner → invalid_hours. Thống kê chất lượng cũ tính trên tất cả dòng, kể cả bị loại. hours_by_owner chỉ có owner có dòng được chấp nhận; overloaded_owners sắp theo owner và dùng tổng > ngưỡng; excluded_rows sắp theo line.

Skill yêu cầu ngưỡng rõ trong câu hỏi hiện tại, không lấy ngưỡng từ lượt trước hoặc đặt mặc định. Reference có ngưỡng, bảng tổng, người quá tải, dòng loại và lý do cùng thống kê chất lượng cũ. Ba file skill/reference/script đồng bộ workspace và fixtures để reset không mất bài làm.

## Kiểm tra trực tiếp và tự động

6/6 CLI checks pass; evidence/block2_direct_results.json giữ stdout/stderr/exit code. Ngưỡng 8: Lan 9, Minh 3; Lan quá tải. Ngưỡng 9: tổng không đổi, không ai quá tải. Loại line 5 T04 invalid_hours, line 6 T02 duplicate_id, line 7 T05 missing_owner. Edge ngưỡng 0: chỉ Minh 0; E01 đầu sai và lần sau vẫn duplicate, không thay thế dòng đầu. Input bytes giữ nguyên.

- stage-03-bash: **48 passed**, exit 0; Linux Python 3.12.15; `evidence/stage-03-bash_pytest.txt`.
- stage-04-script-skill: **73 passed**, exit 0; Linux Python 3.12.15; `evidence/stage-04-script-skill_pytest.txt`.

Tests bao phủ toàn bộ lý do đồng thời, thống kê trên dòng loại, threshold hữu hạn/không âm/thiếu, strict greater-than, zero, trim, blank rows, case-sensitive owners, reordered columns và các lỗi input cũ.

## Model thực tế: Stage 03 và Stage 04

Baseline Stage 03 thực tế: stdout Lan 14, Minh 3, owner rỗng 2. Command chỉ đếm duplicate mà không continue nên cộng cả hai dòng T02; không loại owner rỗng. Nó bắt float('abc') để bỏ hours lỗi ở line 5. Final answer nhầm ID trùng là T03; ID trùng trong CSV thực tế là T02. Có SyntaxWarning do escape \T trong command do model tạo; exit vẫn 0. Giữ nguyên command/stdout/answer dưới đây để chứng minh hạn chế, không chỉnh baseline để làm đẹp kết quả.

### baseline — `evidence/stage-03-bash_baseline.jsonl`

Prompt: Dùng Python qua Bash để tính tổng hours theo owner trong data/workload.csv. Không chỉnh sửa file đầu vào. Cho biết cách xử lý dòng lỗi và task_id trùng.

2 model calls; 1 tool calls; conversation `8d6d60fb880f4c719a57d48b9bab6610`. Input SHA-256 trước/sau: `744832f0d0a96b57046be345240c08064a70929087e8eeb60d8047b38dfe5fde`.

- Event 5, `bash`, tool_call_id `call_884332`. exit=0, timed_out=False.

```bash
python -c "
import csv
from collections import defaultdict

totals = defaultdict(float)
error_lines = 0
seen_task_ids = set()
duplicate_task_ids = 0

with open('data/workload.csv', mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader, start=2):
        try:
            task_id = row.get('task_id', '').strip()
            owner = row.get('owner', '').strip()
            hours_str = row.get('hours', '').strip()
            
            # Kiểm tra task_id trùng
            if task_id in seen_task_ids:
                duplicate_task_ids += 1
            else:
                seen_task_ids.add(task_id)
                
            # Chuyển đổi hours sang float
            hours = float(hours_str)
            totals[owner] += hours
        except Exception as e:
            error_lines += 1
            print(f'Lỗi ở dòng {i}: {row} -> {e}')

print('--- TỔNG KẾT ---')
print(f'Số dòng lỗi / thiếu dữ liệu: {error_lines}')
print(f'Số task_id trùng lặp: {duplicate_task_ids}')
print('\Tổng số giờ (hours) theo owner:')
for owner, total in sorted(totals.items()):
    print(f'  {owner}: {total}')
"
```

```text
Lỗi ở dòng 5: {'task_id': 'T04', 'owner': 'Minh', 'hours': 'abc'} -> could not convert string to float: 'abc'
--- TỔNG KẾT ---
Số dòng lỗi / thiếu dữ liệu: 1
Số task_id trùng lặp: 1
\Tổng số giờ (hours) theo owner:
  : 2.0
  Lan: 14.0
  Minh: 3.0
<string>:34: SyntaxWarning: invalid escape sequence '\T'

```


Câu trả lời model (giữ nguyên):

> Kết quả chạy lệnh Python qua Bash trên file `data/workload.csv`:
> 
> ### 1. Tổng số giờ (`hours`) theo `owner`
> * **(Trống / Không rõ)**: `2.0` giờ (Dòng thiếu owner)
> * **Lan**: `14.0` giờ
> * **Minh**: `3.0` giờ (đã bỏ qua giá trị lỗi ở dòng 5)
> 
> ---
> 
> ### 2. Cách xử lý dòng lỗi và `task_id` trùng
> * **Dòng lỗi (Lỗi định dạng dữ liệu / thiếu trường):** 
>   * Được bắt bằng khối `try...except`.
>   * *Kết quả thực tế:* Dòng 5 có trường `hours = 'abc'` không thể chuyển sang kiểu số (`float`), chương trình đã ghi nhận lỗi dòng 5, bỏ qua giá trị `hours` của dòng đó và tiếp tục xử lý các dòng khác (không làm gián đoạn chương trình).
> * **`task_id` trùng lặp:** 
>   * Sử dụng một tập hợp (`seen_task_ids`) để theo dõi các `task_id` đã gặp.
>   * *Kết quả thực tế:* Phát hiện `1` trường hợp `task_id` bị trùng lặp (ví dụ `T03` xuất hiện 2 lần). Trong đoạn code trên, chương trình vẫn cộng dồn giờ của tất cả các dòng hợp lệ nhưng có đếm và thông báo số lượng `task_id` trùng lặp (nếu cần loại bỏ hoàn toàn task trùng, có thể dùng điều kiện `if task_id in seen_task_ids: continue`).

### threshold8 — `evidence/stage-04-script-skill_threshold8.jsonl`

Prompt: Kiểm tra data/workload.csv, người nào vượt 8 giờ? Ghi báo cáo vào output/workload.md.

5 model calls; 4 tool calls; conversation `b7d181d45fa244579d1b5c12a1289548`. Input SHA-256 trước/sau: `744832f0d0a96b57046be345240c08064a70929087e8eeb60d8047b38dfe5fde`.

- Event 5, `read_file`, tool_call_id `call_688479`. path `skills/csv-quality/SKILL.md`, ok=True.
- Event 9, `read_file`, tool_call_id `call_885440`. path `skills/csv-quality/references/report-template.md`, ok=True.
- Event 13, `bash`, tool_call_id `call_565406`. exit=0, timed_out=False.

```bash
python skills/csv-quality/scripts/check_csv.py --input data/workload.csv --max-hours 8
```

```text
{
  "input": "data/workload.csv",
  "row_count": 6,
  "missing_owner_count": 1,
  "invalid_hours_count": 1,
  "duplicate_id_count": 1,
  "duplicate_ids": [
    "T02"
  ],
  "issues": [
    {
      "line": 5,
      "column": "hours",
      "type": "invalid_hours",
      "task_id": "T04",
      "value": "abc",
      "message": "hours 'abc' không phải số hữu hạn không âm."
    },
    {
      "line": 6,
      "column": "task_id",
      "type": "duplicate_id",
      "task_id": "T02",
      "message": "task_id T02 đã xuất hiện ở line 3."
    },
    {
      "line": 7,
      "column": "owner",
      "type": "missing_owner",
      "task_id": "T05",
      "message": "owner trống."
    }
  ],
  "max_hours": 8.0,
  "hours_by_owner": {
    "Lan": 9.0,
    "Minh": 3.0
  },
  "overloaded_owners": [
    {
      "owner": "Lan",
      "total_hours": 9.0
    }
  ],
  "excluded_rows": [
    {
      "line": 5,
      "task_id": "T04",
      "reasons": [
        "invalid_hours"
      ]
    },
    {
      "line": 6,
      "task_id": "T02",
      "reasons": [
        "duplicate_id"
      ]
    },
    {
      "line": 7,
      "task_id": "T05",
      "reasons": [
        "missing_owner"
      ]
    }
  ]
}

```

- Event 17, `write_file`, tool_call_id `call_887058`. path `output/workload.md`, ok=True.

Câu trả lời model (giữ nguyên):

> Đã kiểm tra `data/workload.csv` với ngưỡng 8 giờ:
> - **Người vượt ngưỡng (> 8 giờ):** **Lan** (9.0 giờ). Minh có 3.0 giờ.
> - **Báo cáo chi tiết:** Đã ghi vào `output/workload.md`.

### threshold9 — `evidence/stage-04-script-skill_threshold9.jsonl`

Prompt: Kiểm tra data/workload.csv, người nào vượt 9 giờ? Ghi báo cáo vào output/workload-9.md.

5 model calls; 4 tool calls; conversation `8f231232443c46bf8febed539ff1c384`. Input SHA-256 trước/sau: `744832f0d0a96b57046be345240c08064a70929087e8eeb60d8047b38dfe5fde`.

- Event 5, `read_file`, tool_call_id `call_784291`. path `skills/csv-quality/SKILL.md`, ok=True.
- Event 9, `read_file`, tool_call_id `call_328544`. path `skills/csv-quality/references/report-template.md`, ok=True.
- Event 13, `bash`, tool_call_id `call_595791`. exit=0, timed_out=False.

```bash
python skills/csv-quality/scripts/check_csv.py --input data/workload.csv --max-hours 9
```

```text
{
  "input": "data/workload.csv",
  "row_count": 6,
  "missing_owner_count": 1,
  "invalid_hours_count": 1,
  "duplicate_id_count": 1,
  "duplicate_ids": [
    "T02"
  ],
  "issues": [
    {
      "line": 5,
      "column": "hours",
      "type": "invalid_hours",
      "task_id": "T04",
      "value": "abc",
      "message": "hours 'abc' không phải số hữu hạn không âm."
    },
    {
      "line": 6,
      "column": "task_id",
      "type": "duplicate_id",
      "task_id": "T02",
      "message": "task_id T02 đã xuất hiện ở line 3."
    },
    {
      "line": 7,
      "column": "owner",
      "type": "missing_owner",
      "task_id": "T05",
      "message": "owner trống."
    }
  ],
  "max_hours": 9.0,
  "hours_by_owner": {
    "Lan": 9.0,
    "Minh": 3.0
  },
  "overloaded_owners": [],
  "excluded_rows": [
    {
      "line": 5,
      "task_id": "T04",
      "reasons": [
        "invalid_hours"
      ]
    },
    {
      "line": 6,
      "task_id": "T02",
      "reasons": [
        "duplicate_id"
      ]
    },
    {
      "line": 7,
      "task_id": "T05",
      "reasons": [
        "missing_owner"
      ]
    }
  ]
}

```

- Event 17, `write_file`, tool_call_id `call_327665`. path `output/workload-9.md`, ok=True.

Câu trả lời model (giữ nguyên):

> Đã kiểm tra xong file `data/workload.csv` với ngưỡng 9 giờ.
> 
> - **Kết quả tổng giờ theo owner**: Lan (9.0 giờ), Minh (3.0 giờ).
> - **Người vượt 9 giờ**: Không có (Lan đạt đúng 9 giờ, Minh đạt 3.0 giờ; lưu ý quy định quá tải là **lớn hơn** ngưỡng).
> - **Báo cáo chi tiết**: Đã được ghi vào file `output/workload-9.md`.

### missing_threshold — `evidence/stage-04-script-skill_missing_threshold.jsonl`

Prompt: Tính tổng giờ theo người trong data/workload.csv và xác định người quá tải.

2 model calls; 1 tool calls; conversation `310e78341f9b40b399561870c10d7e08`. Input SHA-256 trước/sau: `744832f0d0a96b57046be345240c08064a70929087e8eeb60d8047b38dfe5fde`.

- Event 5, `read_file`, tool_call_id `call_603320`. path `skills/csv-quality/SKILL.md`, ok=True.

Câu trả lời model (giữ nguyên):

> Theo quy tắc của skill `csv-quality`, khi kiểm tra workload và xác định người quá tải, bạn cần cung cấp **ngưỡng tối đa giờ** (ví dụ: `--max-hours 40`) vì không có ngưỡng mặc định. 
> 
> Vui lòng cung cấp ngưỡng giờ để tôi có thể chạy phân tích chính xác cho file `data/workload.csv`.

### missing_file — `evidence/stage-04-script-skill_missing_file.jsonl`

Prompt: Kiểm tra data/not-found.csv, người nào vượt 8 giờ? Ghi báo cáo vào output/not-found.md.

3 model calls; 2 tool calls; conversation `cc7146e8241340359e5454707315cce3`. Input SHA-256 trước/sau: `744832f0d0a96b57046be345240c08064a70929087e8eeb60d8047b38dfe5fde`.

- Event 5, `read_file`, tool_call_id `call_525653`. path `skills/csv-quality/SKILL.md`, ok=True.
- Event 9, `bash`, tool_call_id `call_597110`. exit=1, timed_out=False.

```bash
python skills/csv-quality/scripts/check_csv.py --input data/not-found.csv --max-hours 8
```

```text
ERROR: Không đọc được file data/not-found.csv: No such file or directory

```


Câu trả lời model (giữ nguyên):

> Tool `bash` đã chạy lệnh kiểm tra CSV nhưng trả về lỗi với `exit_code: 1`:
> 
> ```
> ERROR: Không đọc được file data/not-found.csv: No such file or directory
> ```
> 
> File `data/not-found.csv` không tồn tại trong workspace, do đó không thể kiểm tra, xác định người vượt ngưỡng 8 giờ hay ghi báo cáo vào `output/not-found.md`. Bạn vui lòng kiểm tra lại đường dẫn file CSV nhé!

## Vì sao cần script, skill và model?

Stage 03 để model tạo Python trong Bash mỗi lần; chính command trong trace quyết định lọc lỗi/trùng thế nào. Nếu cộng cả hai dòng T02 thì Lan thành 14; script Stage 04 áp dụng quy tắc ID đầu tiên nên Lan luôn là 9. Đối chiếu baseline thực tế ở trên, không gán một kết quả cố định cho mọi model.

Bash tool thực thi tiến trình và trả stdout/stderr/exit code. Skill hướng dẫn chọn script, lấy threshold và xử lý lỗi; script quyết định số liệu bằng thuật toán kiểm thử được; model đọc JSON để viết báo cáo. Sửa riêng script chưa đủ: skill cũ thiếu --max-hours khiến CLI thất bại, reference cũ thiếu tổng/quá tải/dòng loại khiến báo cáo thiếu dữ liệu. Nếu history chứa skill/reference cũ thì model còn có thể dùng hướng dẫn lỗi thời: refresh và bắt đầu conversation mới sau khi đồng bộ.

Các báo cáo thành công ở workspace/output/workload.md và workload-9.md, có bản giữ trong evidence/. Missing-threshold chỉ hỏi lại; missing-file ghi nhận stderr/exit khác 0, không tạo báo cáo thành công giả. Traces ghi snapshot ở lớp LangChain, không phải toàn bộ payload wire của provider. Giữ raw trace/answer để kiểm chứng.
