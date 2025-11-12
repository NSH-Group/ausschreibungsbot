IMAP email parser:
- Connect via IMAP using env vars
- Parse daily tender alert emails (HTML/text), extract links & fields using rules
- Normalize and insert into DB, deduplicate by external_id/url hash
- Unit tests with sample .eml fixtures 