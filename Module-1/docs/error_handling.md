# Error Handling Strategy

## Objective

Handle partial failures gracefully and continue processing.

## Implemented Logging

Centralized logger:

scripts/logger.py

Log File:

output/logs/error_log.txt

## Failure Scenarios Covered

1. Corrupt PDF files
2. CSV read failures
3. CSV write failures
4. JSON normalization failures
5. Database insertion failures

## Recovery Strategy

- Log error with timestamp
- Skip problematic file
- Continue processing remaining files
- Rollback database transactions when required