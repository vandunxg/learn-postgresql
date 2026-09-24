# 07 - Table, Diagram, Result Set và Query Plan

## Tables

Preserve:

- số cột;
- thứ tự cột;
- thứ tự row;
- header meaning;
- cell code/identifier;
- NULL/boolean/numeric value;
- relationship giữa caption và table.

Dịch natural-language cell nếu đó là prose, nhưng không dịch identifiers/literals/output values có technical meaning.

## Query result tables

Nếu table là output trực tiếp từ SQL/`psql`, coi là technical output và giữ nguyên toàn bộ thay vì dịch cell.

## Diagram

Không tự vẽ lại diagram dựa trên suy đoán. Nếu asset có thể extract, giữ asset. Dịch caption/alt text từ source nếu có.

Nếu text nằm trong image và không có source text đáng tin cậy, không hallucinate. Ghi issue cho QA nếu hình là bắt buộc để hiểu content.

## Schema/ER diagram

Table name, column name, data type, constraint và relationship label mang technical identifier phải giữ nguyên.

## Query plan

Query plan là structured technical output, không phải prose table. Không chuyển thành prose hoặc markdown table nếu làm mất tree structure.
