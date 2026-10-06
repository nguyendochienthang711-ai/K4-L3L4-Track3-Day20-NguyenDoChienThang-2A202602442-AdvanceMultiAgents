# Báo cáo Lab: Self evolving Agentic

> Sao chép tệp này thành `report/REPORT.md` (đã làm ở Phần 0) và điền dần qua các Phần của lab. Xóa các dòng hướng dẫn dạng trích dẫn (bắt đầu bằng `>`). Văn phong kỹ thuật, ngắn gọn, mọi nhận định đi kèm số liệu hoặc bằng chứng. Trong buổi học: điền mục 1 đến 7 (bản nháp). Sau buổi học: hoàn thiện mục 8 đến 10.

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Nguyễn Đỗ Chiến Thắng | 2A202602442 | Toàn bộ bài lab (harness, subagents, curator, thực nghiệm, báo cáo) |

- Mô hình (tên deployment hoặc `LAB_MODEL`), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: `nvidia/nemotron-3-ultra-550b-a55b` (NVIDIA NIM Gateway), `LAB_TEMPERATURE=0`, `LAB_MAX_TOKENS=4096`, `recursion_limit=60`
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: `deepagents 0.7.21`, Windows 11 (Python 3.11, PosixShellBackend qua Git Bash), chạy trực tiếp trong môi trường Conda
- Số lần chạy tác vụ đã dùng / ngân sách: 9 lần chạy tác vụ học (3 baseline + 3 subagents + 3 skills-auto)
- Commit của tag `freeze`: (sẽ cập nhật sau khi tạo tag)

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

> Dự đoán điều kiện nào đạt điểm cao nhất trên **tác vụ đánh giá** và vì sao. Nêu căn cứ từ phân loại lỗi (mục 4) và từ tài liệu tham khảo. Điền cả ba dòng; `verify_freeze.py` kiểm tra điều này.

- H1 (subagents so với baseline): Điều kiện subagents sẽ đạt điểm kỹ thuật cao hơn đáng kể so với baseline trên các tác vụ đánh giá (cải thiện từ 30% đến 40% điểm kỹ thuật) nhờ cơ chế kiểm tra chéo và phân tích kỹ lưỡng, nhưng chi phí token sẽ cao gấp 2 đến 3.5 lần. Đối với các check quy ước mới (ẩn), subagents vẫn không thể đạt điểm do đề bài không cung cấp.
- H2 (skills-auto so với baseline): Điều kiện skills-auto sẽ vượt trội hơn baseline ở các check quy ước và kỹ thuật đã đúc kết từ tác vụ học (như không sửa file test cũ, chuyển tiền sang cents, format UTC ISO-8601, cấu trúc json/csv). Tuy nhiên, đối với các quy ước MỚI chỉ xuất hiện ở tác vụ đánh giá, skills-auto sẽ không giải quyết được (hiện tượng overfitting/thiếu tính chuyển giao như công bố SkillEvolBench).
- H3 (tác vụ học so với tác vụ đánh giá): Điểm số trung bình trên tác vụ đánh giá của cả ba điều kiện sẽ thấp hơn so với tác vụ học (chênh lệch dự kiến giảm 15-25%), nguyên nhân do tác vụ đánh giá đưa vào các quy ước tổ chức mới cùng bộ dữ liệu kiểm thử biên phức tạp hơn mà mô hình chưa từng được phản hồi.

## 3. Làm quen Deep Agents (Phần 0.3)

1. **Harness & Backend**: Tác tử tương tác với môi trường qua `LocalShellBackend` kết hợp `CompositeBackend`. Mọi đường dẫn trong sandbox đều là tương đối (`workspace/...`, `skills/...`), đảm bảo cô lập sandbox an toàn, không lộ đường dẫn thực tế hay biến môi trường nhạy cảm.
2. **Bộ công cụ (Tools)**: Gồm các công cụ tệp (`read_file`, `write_file`, `list_dir`), công cụ thực thi lệnh shell (`execute`), và công cụ giao việc đa tác tử (`task`). Shell tool thực thi lệnh dưới quyền POSIX shell nhằm đảm bảo tính tương thích của các lệnh CLI/Python.
3. **Subagent & Context Isolation**: Tác tử con hoạt động trong không gian hội thoại riêng biệt, chỉ nhận các chỉ dẫn và ngữ cảnh được tác tử chính truyền qua lời giao việc. Khi kết thúc, subagent trả về kết quả tóm tắt cho tác tử chính, giúp cô lập ngữ cảnh và tránh làm phình to context window chính.

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

> Chỉ dùng tác vụ học. Mỗi dòng là một check thất bại.

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| `code-learn` | `tests_not_modified` | C | "the original files in tests/ must not be modified" - sửa test thay vì sửa tận gốc code |
| `code-learn` | `parse_price_all_formats` | D | "wrong for: ['(12.00)']" - bỏ sót định dạng kế toán số âm trong ngoặc đơn |
| `code-learn` | `csv_quoting_follows_docstring` | A | "to_csv_row returned 'Desk, large "oak",10.00,2'" - bỏ qua docstring yêu cầu RFC 4180 escaping |
| `code-learn` | `rule_type_hints` | E | "RULE: every public function... has type annotations on all parameters and return value" |
| `code-learn` | `rule_regression_tests` | E | "RULE: add tests/test_regressions.py with one test function per bug you fixed" |
| `code-learn` | `rule_changelog` | E | "RULE: record each fix in CHANGELOG.md under '## Unreleased'" |
| `data-learn` | `north_q1_revenue` | D | "north_q1_revenue: wrong value (got 245.28)" - tính sai do chưa khử duplicate và lệch múi giờ |
| `data-learn` | `north_q1_orders` | D | "north_q1_orders: wrong value (got 2)" - đếm sai do chưa khử trùng lặp |
| `data-learn` | `missing_amount_orders` | D | "missing_amount_orders: wrong value (got 0)" - bỏ sót đơn hàng thiếu trường amount |
| `data-learn` | `duplicate_rows_removed` | D | "duplicate_rows_removed: wrong value (got 0)" - không phát hiện và loại bỏ các bản ghi trùng |
| `data-learn` | `rule_money_in_cents` | E | "RULE: money values in answer.json are integer cents" |
| `data-learn` | `rule_meta_block` | E | "RULE: answer.json has an object `meta` = {...}" |
| `data-learn` | `rule_clean_csv` | E | "RULE: write workspace/clean.csv with the header order_id,timestamp_utc,region,amount_cents" |
| `logs-learn` | `valid_structure` | F | "FileNotFoundError: workspace/errors.json" - kết thúc mà chưa tạo file kết quả |
| `logs-learn` | `entry_count` | F | "FileNotFoundError: workspace/errors.json" |
| `logs-learn` | `timestamps_utc` | F | "FileNotFoundError: workspace/errors.json" |
| `logs-learn` | `exception_fields` | F | "FileNotFoundError: workspace/errors.json" |
| `logs-learn` | `repeat_counts` | F | "FileNotFoundError: workspace/errors.json" |
| `logs-learn` | `counts_by_service` | F | "FileNotFoundError: workspace/errors.json" |
| `logs-learn` | `rule_service_names` | E | "FileNotFoundError: workspace/errors.json (RULE: canonical service names)" |
| `logs-learn` | `rule_sorted_errors` | E | "FileNotFoundError: workspace/errors.json (RULE: sorted errors)" |
| `logs-learn` | `rule_schema_header` | E | "FileNotFoundError: workspace/errors.json (RULE: schema header)" |

Nhận xét: nhóm lỗi nào chiếm đa số? Skill có thể phòng ngừa nhóm đó không?
- Lỗi nhóm E (Vi phạm quy ước tổ chức `rule_*`) chiếm đa số tuyệt đối (9/22 check thất bại, tức 100% các quy ước ẩn đều thất bại vì đề bài không nói trước).
- Tiếp theo là nhóm D (Bỏ sót dữ liệu bẩn / dị biệt) và F (Chưa hoàn thành tạo file kết quả trước khi kết thúc).
- **Skill hoàn toàn có thể phòng ngừa nhóm E**: Curator có thể trích xuất các quy ước ẩn (`RULE:...`) từ phản hồi thất bại của bài test và tổng hợp thành skill hướng dẫn tổ chức, giúp tác tử tự động tuân thủ toàn bộ các quy ước này ở các lần chạy sau.

## 5. Điều kiện `subagents` (Phần 2.3)

- Các subagent đã định nghĩa (tên, vai trò, lý do thiết kế):
  1. `explorer`: Đọc đề, duyệt cây thư mục, kiểm tra các file dữ liệu/log bẩn hoặc chạy test ban đầu để khoanh vùng lỗi.
  2. `implementer`: Chỉnh sửa code, xử lý làm sạch dữ liệu, chuẩn hóa log và chạy lệnh giải quyết bài toán.
  3. `reviewer`: Chạy lại toàn bộ test suite, đối chiếu kết quả với các yêu cầu kỹ thuật và docstring trước khi bàn giao.
- `subagent_calls` ở từng tác vụ và nhận xét (kể cả trường hợp bằng 0):
  - `code-learn`: 0; `data-learn`: 0; `logs-learn`: 0.
  - Tác tử chính (`agent`) ưu tiên sử dụng trực tiếp các tool bash/shell để xử lý tập tin một cách tuần tự nhằm tiết kiệm context và thời gian, thay vì chia nhỏ và giao quyền cho subagent khi bối cảnh tác vụ còn đơn lẻ.
- Thông tin thiếu hoặc thừa khi giao việc (nếu có giao việc):
  - Khi tác tử chính tự làm trực tiếp, tác tử có toàn quyền kiểm soát môi trường cục bộ, tránh được hiện tượng mất ngữ cảnh (context loss) giữa tác tử chính và tác tử con.
- Ảnh hưởng đến token và thời gian:
  - Token trung bình tăng từ 45,876 (baseline) lên 160,835 (subagents), tức tăng khoảng 3.5 lần.
  - Thời gian thực thi tăng tương ứng từ 20–60s lên 110–220s do tác tử cân nhắc kỹ lưỡng hơn và thực hiện nhiều lượt suy luận/kiểm tra cẩn thận hơn, giúp điểm kỹ thuật tăng vọt từ 5/18 (27.8%) lên 17/18 (94.4%).

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Số lần chạy curator, số skill bị xóa và lý do:
  - Curator chạy 1 lần chính thức, sinh ra đúng 3 skills hợp lệ theo chuẩn định dạng YAML frontmatter và checklist.
  - Số skill bị xóa: 0. Cả 3 skill đều đạt yêu cầu về độ tổng quát, độ an toàn và không bị rò rỉ dữ liệu đánh giá.

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `module-integrity-test-safety` | Tổng quát cho mọi bài kiểm tra module và test suite | Đúng: hướng dẫn không sửa test gốc, chỉ thêm test mới, kiểm tra import path | 10 dòng; Description: "WHEN working on a codebase with existing tests..."; skills_read: 0 |
| `specification-adherence` | Tổng quát cho việc đọc docstring, tuân thủ định dạng đặc tả | Đúng: hướng dẫn đọc kỹ docstring, kiểm tra rule về kiểu dữ liệu (cents, UTC) | 10 dòng; Description: "WHEN implementing or modifying functions that have docstrings..."; skills_read: 0 |
| `output-validation-and-regression` | Tổng quát cho việc tạo file output, test hồi quy và changelog | Đúng: hướng dẫn cấu trúc JSON/CSV, test hồi quy (`test_regressions.py`), cập nhật CHANGELOG.md | 11 dòng; Description: "WHEN generating output files or fixing bugs..."; skills_read: 0 |

## 7. Kết quả so sánh (Phần 4.3, 4.4)

> Dán nội dung `report/table.md` và kết quả `python scripts/check_breakdown.py`. Nêu các lần chạy có `error` hoặc `skills_modified = true` (nếu có) và cách xử lý.

```text
(dán bảng ở đây)
```

## 8. Phân tích

> Trả lời từng câu bằng số liệu từ mục 7 và bằng chứng từ vết. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.

1. So với `baseline`, điều kiện nào cải thiện điểm tác vụ **học**? Điều kiện nào cải thiện điểm tác vụ **đánh giá**? Có điều kiện nào cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá? Nếu có, đó là dấu hiệu gì?
2. Tách điểm thành check kỹ thuật và check quy ước (`rule_`). Skill do curator sinh giúp nhóm check nào? Check quy ước **mới** của tác vụ đánh giá có được skill giúp không, và vì sao?
3. Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp (skill chưa được đọc, đọc nhưng không làm theo, skill thiếu hoặc sai).
4. Chi phí: so sánh số token trung bình giữa các điều kiện. Điều kiện nào có hiệu quả tốt nhất theo điểm trên mỗi token? Đa tác tử có đáng chi phí trong thí nghiệm này không?
5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Nhóm đã phòng tránh như thế nào?
6. Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?

## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1.
2.
3.

## 10. Kết luận

> Tối đa 5 câu. Chỉ khẳng định điều số liệu hỗ trợ. Nêu một đề xuất cải tiến tiếp theo.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
- Thử thách mở rộng (nếu có): hướng chọn, kết quả, nhận xét.
- Ghi chú khác:
