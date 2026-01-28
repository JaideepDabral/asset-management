# Database Performance & Scalability Report

This document outlines the optimizations implemented to ensure the ITSM platform remains high-performing as data scales from hundreds to hundreds of thousands of records.

## 1. Audit Log & Search Indexing

**Problem**: As the `audit_logs` and `assets` tables grow, queries like "find all logs for Asset X" or "list assets by status" would require a Full Table Scan (O(N)), leading to slow dashboard loads.

**Implemented Solutions**:

- **B-Tree Indices**: Added to high-frequency filtering columns:
  - `AuditLog`: `timestamp`, `entity_id`, `entity_type`, `action`, `performed_by`.
  - `Asset`: Already indexed on `serial_number`, `status`, `name`, and `id`.
- **Unique Constraints**: Ensured `Asset.serial_number` is unique and indexed for O(1) lookups during data ingestion/sync.

## 2. JSONB & GIN Indices (PostgreSQL Optimized)

**Problem**: The platform uses JSON to store complex specifications and audit details. Standard JSON in Postgres is stored as text, making deep searches (e.g., finding assets with "CPU: M3") very slow.

**Implemented Solutions**:

- **Conversion to JSONB**: Switched specifications and audit details to the `JSONB` (Binary JSON) format. JSONB is slightly slower to write but significantly faster to read and process.
- **GIN Indexing**: Implemented **Generalized Inverted Indexes (GIN)** on:
  - `assets.specifications`
  - `audit_logs.details`
- **Benefit**: This allows the database to index the internal keys and values of the JSON objects, enabling sub-millisecond searches even for nested data.

## 3. High-Performance Pagination

**Problem**: Standard `LIMIT/OFFSET` pagination (e.g., `OFFSET 10000`) forces the database to scan and discard 10,000 rows before returning results. This becomes exponentially slower as you navigate to later pages.

**Implemented Solutions**:

- **Keyset Pagination (Preferred)**: Added support for the `after_id` parameter in the Audit Log API.
  - **Logic**: Instead of "skipping 100 rows", the system asks for "the next 100 rows after ID X".
  - **Performance**: Since it filters by an indexed anchor (`timestamp` + `id`), the query time remains constant (O(log N)) regardless of how deep the user paginates.
- **Compatibility**: Maintained support for standard `offset` for simple small-scale uses while providing the high-performance path for large-scale audit browsing.

## Summary of Optimization Methods Used

| Method                | Target                    | Complexity Improvement     |
| :-------------------- | :------------------------ | :------------------------- |
| **B-Tree Indexing**   | IDs, Statuses, Timestamps | O(N) → O(log N)            |
| **GIN Indexing**      | Nested JSON Data          | Full Scan → Indexed Hash   |
| **Keyset Pagination** | High-Volume Logs          | O(N) → O(1/log N) anchor   |
| **JSONB Storage**     | Specs & Audit Metadata    | Faster parsing & filtering |
