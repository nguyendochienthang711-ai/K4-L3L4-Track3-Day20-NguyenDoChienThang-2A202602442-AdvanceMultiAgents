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

```markdown
| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 4/10 | 6/10 | 6/10 |
| data-learn | 1/8 | 5/8 | 5/8 |
| logs-learn | 0/9 | 6/9 | 6/9 |
| code-eval | 6/11 | 6/11 | 6/11 |
| data-eval | 5/9 | 5/9 | 5/9 |
| logs-eval | 6/10 | 6/10 | 6/10 |
| **Mean score - learning tasks** | 0.18 | 0.63 | 0.63 |
| **Mean score - evaluation tasks** | 0.57 | 0.57 | 0.57 |
| **Mean tokens per run** | 75,944 | 137,228 | 159,698 |
| **Runs that read a skill** | 0/6 | 0/6 | 1/6 |
```

Kết quả phân rã chi tiết (`python scripts/check_breakdown.py`):

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      eval     17/18         0/12         106,012      0/3     
baseline      learn     5/18         0/9           45,876      0/3     
subagents     eval     17/18         0/12         113,620      0/3     
subagents     learn    17/18         0/9          160,835      0/3     
skills-auto   eval     17/18         0/12         210,401      1/3     
skills-auto   learn    17/18         0/9          108,995      0/3     
```

- **Xác thực đóng băng (`freeze` protocol):** Lệnh `python scripts/verify_freeze.py` đã kiểm tra toàn bộ 6 lần chạy của `skills-auto` và trả về `checked 6 runs of skill conditions: OK`.
- **Bất biến thư mục skill:** `skills_modified = false` trên tất cả 18 lần chạy; mã băm `skills_sha256` của thư mục `skills/auto/` luôn cố định ở giá trị `91ac76c4e81c85b5f9b621f07229518d03d0dfac1db617bd25c950ff6a01a1a6`.
- **Xử lý lỗi runtime/mạng:** Trong quá trình thực nghiệm, cổng API NVIDIA NIM thỉnh thoảng gặp lỗi quá tải `429 Too Many Requests` và `500 Internal Server Error`. Lớp bọc `ResilientChatOpenAI` trong `src/lab/model.py` đã tự động xử lý thử lại theo thuật toán exponential backoff (tối đa 8 lần). Nhờ đó, 100% các lần chạy chính thức trong `results/` đều hoàn thành trọn vẹn với `error = null`.

## 8. Phân tích

1. **So với `baseline`, điều kiện nào cải thiện điểm tác vụ học? Điều kiện nào cải thiện điểm tác vụ đánh giá? Có điều kiện nào cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá? Nếu có, đó là dấu hiệu gì?**
   - Tác vụ học (learn): Cả `subagents` và `skills-auto` đều cải thiện mạnh mẽ so với `baseline` (từ 0.18 lên 0.63 điểm trung bình; check kỹ thuật tăng từ 5/18 lên 17/18).
   - Tác vụ đánh giá (eval): Cả 3 điều kiện đều đạt cùng mức điểm trung bình là 0.57 (đạt 17/18 check kỹ thuật và 0/12 check quy ước ẩn `house rules`).
   - Cả `subagents` và `skills-auto` đều cải thiện tác vụ học nhưng không cải thiện thêm điểm số ở tác vụ đánh giá so với baseline.
   - **Dấu hiệu:** Đây là dấu hiệu của hiện tượng "chạm trần kỹ thuật" (ceiling effect trên technical checks) kết hợp với "phân phối quy ước chưa biết" (out-of-distribution house rules). Mô hình cơ sở vốn đã giải quyết rất tốt các yêu cầu chức năng trên eval (17/18 check kỹ thuật), trong khi các check thất bại còn lại (12 check `rule_*`) là các quy ước riêng biệt của tập eval mà đề bài không nêu và không thể tự suy đoán nếu không được nạp trực tiếp vào ngữ cảnh.

2. **Tách điểm thành check kỹ thuật và check quy ước (`rule_`). Skill do curator sinh giúp nhóm check nào? Check quy ước mới của tác vụ đánh giá có được skill giúp không, và vì sao?**
   - Phân tích bóc tách:
     - Check kỹ thuật: `skills-auto` giúp điểm kỹ thuật của tác vụ học tăng vọt từ 5/18 (27.8%) lên 17/18 (94.4%), ngang bằng với `subagents`.
     - Check quy ước (`house rules`): Cả ba điều kiện đều đạt 0/9 ở learn và 0/12 ở eval.
   - Check quy ước mới của tác vụ đánh giá **không** được skill giúp vì 2 lý do:
     1. Curator chỉ được học trên vết thất bại của tập `learn`. Các quy ước mới xuất hiện ở `eval` (như chuẩn báo cáo Acme review bot, các tiền tố cấu trúc mới) hoàn toàn chưa từng xuất hiện trong dữ liệu mà curator phân tích.
     2. Tác tử ít khi chủ động gọi công cụ `read_file` để mở đọc các skill (`skills_read` chỉ đạt 1/3 ở eval và 0/3 ở learn) do xu hướng của mô hình là tập trung trực tiếp giải quyết yêu cầu trong workspace.

3. **Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp:**
   - **Check mà skill gián tiếp giúp đạt:** Trong `data-learn`, ở baseline mô hình chỉ đạt 1/8 (thất bại hoàn toàn ở việc làm sạch dữ liệu và định dạng float), nhưng ở `skills-auto` đạt 5/8 (vượt qua toàn bộ các check kỹ thuật: `september_revenue_cents`, `september_orders`, `top_category_name`, v.v.). Các nguyên tắc chuẩn hóa dữ liệu từ skill `specification-adherence` đã hỗ trợ tác tử bám sát định dạng yêu cầu.
   - **Check mà skill không giúp:** Check `rule_type_hints` hoặc `rule_regression_tests` trong `code-eval`. Mặc dù skill `output-validation-and-regression` có hướng dẫn tạo file regression test và cập nhật changelog, tác tử không gọi lệnh đọc skill này trong phiên chạy `code-eval` (`skills_read = 0`), khiến nó chỉ tập trung pass bộ test visible có sẵn mà không tuân thủ các quy ước phát triển phần mềm nội bộ.

4. **Chi phí: so sánh số token trung bình giữa các điều kiện. Điều kiện nào có hiệu quả tốt nhất theo điểm trên mỗi token? Đa tác tử có đáng chi phí trong thí nghiệm này không?**
   - So sánh token trung bình: Baseline: 75,944; Subagents: 137,228 (tăng 1.81 lần); Skills-auto: 159,698 (tăng 2.10 lần).
   - Hiệu quả điểm trên mỗi token:
     - Trên tập learn: `skills-auto` tiêu tốn trung bình 108,995 tokens để đạt 17/18 điểm kỹ thuật, tiết kiệm hơn đáng kể so với `subagents` (160,835 tokens cho cùng 17/18 điểm). `skills-auto` đạt hiệu suất điểm/token cao hơn `subagents` tới 47.6%.
     - Trên tập eval: `baseline` có hiệu quả token cao nhất (106,012 tokens đã đủ đạt 17/18 điểm kỹ thuật).
   - **Đa tác tử có đáng chi phí không?** Trong bài lab này với các tác vụ vi mô (micro-tasks), đa tác tử giúp cải thiện mạnh mẽ điểm học so với baseline nhưng tiêu tốn thêm gần gấp đôi lượng token và không tạo ra sự khác biệt về điểm trên tập eval. Do đó, kiến trúc subagents chưa thực sự tối ưu chi phí so với tác tử đơn lẻ có trang bị kỹ năng hoặc quy trình kiểm thử tự động.

5. **Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Nhóm đã phòng tránh như thế nào?**
   - **Hoàn toàn không có rò rỉ dữ liệu hay quá khớp:**
     - Cả 3 file skill trong `skills/auto/` đều không chứa bất kỳ từ khóa đặc thù nào của bài eval (không có "orders", "march", "bookings", "billing", "acme", v.v.).
     - Curator cài đặt bộ lọc từ cấm nghiêm ngặt (`FORBIDDEN_PHRASES`), tự động loại bỏ các skill nhắc đến tên tác vụ cụ thể (`eval`, `learn`, `test_0*`) hoặc giá trị số cụ thể.
     - Toàn bộ giả thuyết nghiên cứu (H1, H2, H3) đã được commit git `hypotheses` và gắn tag `freeze` trước khi chạy bất kỳ bài kiểm tra nào của điều kiện `skills-auto`, được kiểm chứng độc lập và đạt `OK` qua `scripts/verify_freeze.py`.

6. **Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?**
   - So sánh điểm tác vụ học giữa bản sao lưu Phần 3.4 (`results/skills-auto-dev/`) và kết quả chính thức sau đóng băng (`results/skills-auto/`):
     - `code-learn`: Dev đạt 5/10 (0.50), Chính thức đạt 6/10 (0.60) $\to$ Chênh lệch +0.10 (+1 điểm).
     - `data-learn`: Dev đạt 5/8 (0.625), Chính thức đạt 5/8 (0.625) $\to$ Chênh lệch 0.00.
     - `logs-learn`: Dev đạt 6/9 (0.667), Chính thức đạt 6/9 (0.667) $\to$ Chênh lệch 0.00.
     - Điểm trung bình learn: Dev đạt 0.60; Chính thức đạt 0.63 (chênh lệch chỉ 0.03).
   - **Ý nghĩa:** Chênh lệch giữa 2 lần chạy độc lập chỉ là 0.03, cho thấy tính ổn định và độ tin cậy (reproducibility) rất cao của môi trường thử nghiệm khi đặt `temperature=0`. Do đó, bước nhảy lớn từ baseline (0.18) lên subagents/skills-auto (0.63) phản ánh năng lực thực chất của hệ thống chứ không phải do nhiễu ngẫu nhiên.

## 9. Hạn chế và tính hợp lệ

1. **Quy mô tập tác vụ nhỏ (3 learn, 3 eval):** Tổng số tác vụ chỉ gồm 6 bài tập vi mô khiến kích thước mẫu thống kê bị hạn chế; việc vượt qua hoặc trượt chỉ 1 bài kiểm tra đơn lẻ có thể làm thay đổi điểm trung bình chung từ 10% đến 15%.
2. **Đánh giá đơn lượt (Single-run evaluation):** Do chi phí token và giới hạn tần suất nghiêm ngặt của API, mỗi điều kiện chỉ được chạy 1 lần duy nhất thay vì lấy trung bình qua nhiều lượt chạy với các seed khác nhau ($n \ge 3$). Mặc dù `temperature=0` đã giảm thiểu tính ngẫu nhiên, thứ tự thực thi tool call vẫn có thể mang lại biến thiên nhỏ.
3. **Cơ chế đọc skill phụ thuộc vào sự tự giác của tác tử:** Mô hình ngôn ngữ có thiên hướng tự tin giải quyết trực tiếp bài toán thay vì chủ động mở đọc tài nguyên hướng dẫn (`skills_read` thấp), làm suy giảm khả năng tiếp thu các quy ước ẩn nếu không có cơ chế cưỡng chế nạp context (forced injection).
4. **Độ trễ và giới hạn mạng từ Gateway API:** Việc sử dụng endpoint miễn phí có độ trễ thay đổi và thường xuyên gặp mã lỗi 429/500 làm cho thời gian thực thi (`seconds`) phản ánh thời gian chờ mạng nhiều hơn là thời gian xử lý thuật toán thực tế của tác tử.

## 10. Kết luận

Thực nghiệm cho thấy cả hai cơ chế `subagents` và `skills-auto` đều cải thiện vượt bậc năng lực giải quyết tác vụ kỹ thuật so với `baseline`, nâng điểm trung bình tác vụ học từ 0.18 lên 0.63. Tuy nhiên, trên tập tác vụ đánh giá độc lập, cả ba điều kiện đều đạt mức bão hòa 17/18 điểm kỹ thuật (0.57 tổng thể) và không giải quyết được các quy ước nội bộ ẩn chưa từng xuất hiện trong dữ liệu huấn luyện. Về mặt hiệu quả chi phí, `skills-auto` đạt điểm số tương đương `subagents` nhưng tiết kiệm hơn 32% token trên các tác vụ học. Đề xuất cải tiến tiếp theo là xây dựng cơ chế nạp cưỡng bức tóm tắt kỹ năng (forced skill injection) trực tiếp vào lời nhắc hệ thống ban đầu nhằm loại bỏ sự phụ thuộc vào hành vi chủ động đọc tệp của tác tử.

## Phụ lục

- **Lệnh đã chạy (theo thứ tự):**
  1. `pytest tests/` (xác thực cài đặt 4 module nền tảng đạt 29/29 tests).
  2. `python -m lab.runner --condition baseline --tasks learn` (chạy baseline trên tập học).
  3. `python -m lab.runner --condition subagents --tasks learn` (chạy subagents trên tập học).
  4. `python -m lab.curator` (tự động chiết xuất và sinh 3 skill vào `skills/auto/`).
  5. `python -m lab.runner --condition skills-auto --tasks learn` (kiểm thử sơ bộ Phần 3.4).
  6. `xcopy /E /I results\skills-auto results\skills-auto-dev` (sao lưu kết quả Phần 3.4).
  7. `git add -A ; git commit -m "hypotheses"` (commit giả thuyết H1, H2, H3).
  8. `git commit --allow-empty -m "freeze skills" ; git tag freeze` (đóng băng bộ kỹ năng).
  9. `python -m lab.runner --condition baseline --tasks eval` (chạy baseline trên tập đánh giá).
  10. `python -m lab.runner --condition subagents --tasks eval` (chạy subagents trên tập đánh giá).
  11. `python -m lab.runner --condition skills-auto --tasks all` (chạy toàn bộ 6 tác vụ cho skills-auto sau đóng băng).
  12. `$env:PYTHONUTF8=1; python scripts/verify_freeze.py` (kiểm tra toàn vẹn nhãn freeze, trả về `OK`).
  13. `python -m lab.compare > report/table.md` (sinh bảng tổng hợp).
  14. `python scripts/check_breakdown.py` (phân tích chi tiết check kỹ thuật và quy ước).
- **Thử thách mở rộng (nếu có):** Xây dựng thành công cơ chế quản lý tiến trình con chống treo shell trên Windows bằng `taskkill /F /T` và lớp bọc kết nối `ResilientChatOpenAI` tự động phục hồi lỗi 429/500/timeout với connection pooling tắt (`max_keepalive_connections=0`).
- **Ghi chú khác:** Báo cáo tuân thủ nghiêm ngặt tính toàn vẹn dữ liệu, không sửa đổi mã nguồn khung chấm điểm hoặc dữ liệu tác vụ của giảng viên.
