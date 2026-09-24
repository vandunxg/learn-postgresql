# 09 - QA Validation

## QA dimensions

1. Completeness.
2. Semantic fidelity.
3. PostgreSQL/SQL terminology.
4. Code/output fidelity.
5. Boundary continuity.
6. Markdown structure.
7. Terminology consistency.
8. Merge order.

## Severity

### CRITICAL

- đảo meaning;
- mất negation;
- sai SQL/PostgreSQL concept;
- missing paragraph/code/table;
- hallucinated content;
- duplicated content;
- corrupt SQL/query plan/output.

### HIGH

- condition/exception sai;
- recommendation strength sai;
- boundary làm đứt reasoning;
- terminology làm đổi technical meaning;
- table/result relationship sai.

### MEDIUM

- terminology inconsistency;
- câu quá literal/khó hiểu;
- Markdown structure chưa tốt nhưng meaning còn đúng.

### LOW

- stylistic preference không ảnh hưởng meaning.

## Required checks

- input part count == translated part count;
- không có output rỗng;
- natural numeric ordering;
- mọi boundary đã review;
- mọi CRITICAL/HIGH đã resolve hoặc report rõ;
- SQL/code/output không bị translation làm thay đổi;
- final merged file tồn tại và không rỗng;
- không có worker metadata lọt vào book.

## Sampling không đủ

Không được claim toàn bộ sách QA passed nếu chỉ kiểm tra sample. Nếu QA chỉ sampling, report chính xác phạm vi sampling.
