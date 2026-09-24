# 08 - Semantic Review

Semantic review diễn ra sau translation/boundary reconciliation và phải đối chiếu trực tiếp source.

## Review theo context

Không review từng sentence cô lập. Đọc ít nhất paragraph trước, paragraph hiện tại, paragraph sau và example/code liên quan.

## Kiểm tra meaning

- subject/action/object;
- condition và exception;
- negation;
- cause/effect;
- comparison/contrast;
- recommendation strength;
- scope/qualifier;
- temporal/version context;
- technical relationship.

## PostgreSQL-specific semantic traps

Chủ động kiểm tra các cặp/concept dễ dịch sai:

- database vs database cluster;
- role vs user;
- schema vs database;
- row vs tuple;
- snapshot vs backup;
- transaction isolation vs locking;
- MVCC visibility vs physical row existence;
- VACUUM vs ANALYZE;
- WAL vs transaction log theo meaning source;
- primary/standby vs generic master/slave wording của source cũ;
- logical vs physical replication;
- index scan vs index-only scan;
- sequential scan vs bitmap heap scan;
- planner estimate vs actual runtime;
- function vs procedure;
- view vs materialized view;
- NULL semantics;
- SQL three-valued logic;
- `SERIAL`/sequence/identity distinctions;
- constraint vs index;
- connection vs session vs process.

Không "sửa" source dựa trên PostgreSQL knowledge hiện đại. Dùng knowledge để hiểu đúng source, không để thay source.

## Minimal edit

Nếu translation đã đúng meaning, tự nhiên và nhất quán thì giữ nguyên. Chỉ sửa khi có evidence cụ thể.
