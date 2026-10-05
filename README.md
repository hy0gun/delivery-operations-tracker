# Delivery Operations Tracker

Run tracker.py in PyCharm. Menu options cover add, view, search, update, summary, CSV export, history, HTML report, and status filter. JSON is saved beside the code; sample addresses are fictional.

## Data and functions
A dictionary maps package IDs to address/status/history dictionaries. Each history event has a UTC timestamp and status. Existing sample records may have no history; history starts with future changes. add_package rejects duplicates and blanks. update_status checks the ID and status and rejects a repeated status. load validates required fields and event timestamps.

save keeps one previous version as packages.backup.json, writes a temporary file, then replaces packages.json. The menu copies state before an operation and restores it on handled errors. This is intended for one local process, not concurrent writers. The history is editable JSON, not a tamper-proof audit log.

html_report escapes values before inserting them into HTML; export_csv correctly quotes commas. Generated HTML shows counts, delivery percentage, and package rows. To reset, back up your data and replace packages.json with {}.

## Files
tracker.py = program; packages.json = sample/current data; delivery_report.html = generated example. Backup/report files are generated locally when running. No customer data should be used.

## Walkthrough
Read validate/load/save first, then add_package/update_status/statistics, then main. New concepts beyond basic lists/functions: dictionary comprehensions, datetime timestamps, deepcopy for rollback, and HTML escaping. See DEMO_GUIDE.md for an example presentation.

## Limits
No live GPS, delivery service integration, authentication, routing optimization, or concurrency. Backups are one prior version and power-loss durability is not guaranteed. CSV formula-like external values are not sanitized; use fictional data.

