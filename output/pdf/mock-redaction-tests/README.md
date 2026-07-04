# Mock Redaction Test PDFs

These PDFs contain synthetic sensitive data for testing the Redact app.

Suggested workflow:

1. Open each `*_sensitive.pdf` file in Redact.
2. Draw redaction boxes over the fake sensitive fields.
3. Export the redacted copy back into this directory.
4. Use a clear suffix such as `_redacted.pdf`.

Example:

```text
01_mock_payslip_sensitive.pdf
01_mock_payslip_redacted.pdf
```

After redacted copies are saved here, Ava can inspect the PDFs visually and
attempt text extraction to check whether sensitive content remains recoverable.

