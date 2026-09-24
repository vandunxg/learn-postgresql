# PostgreSQL Glossary Baseline

Glossary này là baseline, không phải whitelist. Giữ English khi technical term chưa có trong bảng nhưng đó là cách viết tự nhiên và chính xác hơn.

| Nhóm | Thuật ngữ ưu tiên giữ nguyên |
| --- | --- |
| Nền tảng | PostgreSQL, Postgres, SQL, database, database cluster, server, instance, backend process, client, session, connection |
| Data model | schema, table, row, column, tuple, relation, data type, domain, enum, array, composite type, range type |
| SQL | query, statement, clause, expression, predicate, subquery, CTE, recursive CTE, window function, aggregate, GROUP BY, HAVING, ORDER BY, LIMIT, OFFSET |
| DDL/DML | DDL, DML, SELECT, INSERT, UPDATE, DELETE, MERGE, CREATE, ALTER, DROP, TRUNCATE, COPY |
| Constraints | constraint, primary key, foreign key, unique constraint, CHECK constraint, NOT NULL, DEFAULT, identity column, generated column |
| Transaction | transaction, commit, rollback, savepoint, isolation level, read committed, repeatable read, serializable, lock, deadlock, snapshot, MVCC |
| Storage | heap, page, block, tuple, TOAST, tablespace, relation fork, free space map, visibility map |
| Maintenance | VACUUM, autovacuum, ANALYZE, REINDEX, CLUSTER, statistics, bloat |
| WAL/Recovery | WAL, write-ahead log, WAL record, checkpoint, crash recovery, archive, point-in-time recovery, PITR |
| Index | index, B-tree, Hash, GiST, SP-GiST, GIN, BRIN, expression index, partial index, covering index, index-only scan |
| Planner | query planner, optimizer, plan, execution plan, cost, cardinality, selectivity, sequential scan, index scan, bitmap scan, nested loop, hash join, merge join |
| Concurrency | lock, row-level lock, table-level lock, advisory lock, blocking, wait event, deadlock |
| Security | role, user, privilege, ownership, GRANT, REVOKE, authentication, authorization, `pg_hba.conf` |
| Replication | replication, physical replication, streaming replication, logical replication, publisher, subscriber, primary, standby, replica, replication slot, failover, switchover |
| Backup | backup, logical backup, physical backup, `pg_dump`, `pg_restore`, `pg_basebackup` |
| Tooling | `psql`, meta-command, `EXPLAIN`, `EXPLAIN ANALYZE`, `pg_ctl`, `initdb`, `createdb`, `createuser` |
| Programmability | function, procedure, trigger, PL/pgSQL, extension, operator, cast |
| JSON | JSON, JSONB, JSON path, operator, containment |
| Monitoring | `pg_stat_*`, statistics collector, activity, wait event, metrics, logging |
| Configuration | parameter, configuration, GUC, `postgresql.conf`, `pg_hba.conf`, `search_path`, `work_mem`, `shared_buffers` |

## Identifier và casing

Giữ nguyên chính tả/casing của SQL keyword trong code, function/operator/type name, catalog name, configuration parameter, command, file name, schema/table/column identifier, extension name và executable/tool.
