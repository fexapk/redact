from __future__ import annotations

from pathlib import Path

import fitz


OUTPUT_DIR = Path("output/pdf/mock-redaction-tests")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    _create_payslip(OUTPUT_DIR / "01_mock_payslip_sensitive.pdf")
    _create_bank_statement(OUTPUT_DIR / "02_mock_bank_statement_sensitive.pdf")
    _create_medical_form(OUTPUT_DIR / "03_mock_medical_intake_sensitive.pdf")


def _new_doc() -> fitz.Document:
    doc = fitz.open()
    doc.set_metadata(
        {
            "title": "Mock redaction test PDF",
            "author": "Ava",
            "subject": "Synthetic sensitive data for local redaction testing",
        }
    )
    return doc


def _add_header(page: fitz.Page, title: str) -> None:
    page.insert_text((50, 42), title, fontsize=18, fontname="helv")
    page.insert_text(
        (50, 65),
        "Synthetic test document. Contains fake sensitive data.",
        fontsize=8,
        color=(0.35, 0.35, 0.35),
    )
    page.draw_line((50, 80), (545, 80), color=(0, 0, 0), width=0.8)


def _label_value(page: fitz.Page, x: int, y: int, label: str, value: str) -> None:
    page.insert_text((x, y), label, fontsize=8, fontname="helv", color=(0.2, 0.2, 0.2))
    page.insert_text((x + 120, y), value, fontsize=10, fontname="cour")


def _section_box(page: fitz.Page, rect: fitz.Rect, title: str) -> None:
    page.draw_rect(rect, color=(0, 0, 0), width=0.8)
    page.insert_text((rect.x0 + 10, rect.y0 + 18), title, fontsize=11, fontname="helv")
    page.draw_line(
        (rect.x0, rect.y0 + 26),
        (rect.x1, rect.y0 + 26),
        color=(0, 0, 0),
        width=0.6,
    )


def _create_payslip(path: Path) -> None:
    doc = _new_doc()
    page = doc.new_page(width=595, height=842)
    _add_header(page, "Mock Payroll Statement")

    _section_box(page, fitz.Rect(50, 105, 545, 250), "Employee Details")
    fields = [
        ("Employee", "Marina Holt"),
        ("Home Address", "418 North Cedar Ave, Dayton, OH 45402"),
        ("SSN", "493-28-1845"),
        ("Employee ID", "EMP-78421"),
        ("Payroll Email", "marina.holt@example.test"),
        ("Bank Account", "US91 0001 9876 5432 1010 42"),
    ]
    for index, (label, value) in enumerate(fields):
        _label_value(page, 70, 145 + index * 17, label, value)

    _section_box(page, fitz.Rect(50, 280, 545, 500), "Earnings and Deductions")
    rows = [
        ("Base Salary", "80.00", "42.50", "3400.00", ""),
        ("Overtime", "6.00", "63.75", "382.50", ""),
        ("Federal Tax", "", "", "", "612.44"),
        ("State Tax", "", "", "", "184.19"),
        ("Retirement", "", "", "", "226.95"),
    ]
    x_positions = [70, 245, 315, 390, 480]
    headers = ["Concept", "Units", "Rate", "Earnings", "Deductions"]
    for x, header in zip(x_positions, headers):
        page.insert_text((x, 320), header, fontsize=8, fontname="helv")
    page.draw_line((65, 328), (530, 328), color=(0, 0, 0), width=0.6)
    for row_index, row in enumerate(rows):
        y = 350 + row_index * 24
        for x, value in zip(x_positions, row):
            page.insert_text((x, y), value, fontsize=9, fontname="cour")

    _section_box(page, fitz.Rect(50, 530, 545, 665), "Payment Summary")
    _label_value(page, 70, 570, "Gross Pay", "3782.50 USD")
    _label_value(page, 70, 592, "Total Deductions", "1023.58 USD")
    _label_value(page, 70, 614, "Net Pay", "2758.92 USD")
    _label_value(page, 70, 636, "Deposit Account", "**** **** **** 1042")

    doc.save(path)
    doc.close()


def _create_bank_statement(path: Path) -> None:
    doc = _new_doc()
    page = doc.new_page(width=595, height=842)
    _add_header(page, "Mock Bank Statement")

    _section_box(page, fitz.Rect(50, 105, 545, 240), "Account Holder")
    fields = [
        ("Name", "Owen Vargas"),
        ("Address", "77 Lake View Road, Albany, NY 12207"),
        ("Account Number", "102938475610"),
        ("Routing Number", "021000021"),
        ("Debit Card", "4111 1111 1111 4242"),
    ]
    for index, (label, value) in enumerate(fields):
        _label_value(page, 70, 145 + index * 17, label, value)

    _section_box(page, fitz.Rect(50, 270, 545, 705), "Transactions")
    headers = ["Date", "Description", "Amount", "Balance"]
    x_positions = [70, 140, 390, 470]
    for x, header in zip(x_positions, headers):
        page.insert_text((x, 310), header, fontsize=8, fontname="helv")
    page.draw_line((65, 318), (530, 318), color=(0, 0, 0), width=0.6)
    rows = [
        ("2026-05-03", "Payroll Deposit - Northwind", "+2950.00", "6502.91"),
        ("2026-05-05", "Rent Payment", "-1450.00", "5052.91"),
        ("2026-05-07", "Pharmacy #1182", "-43.87", "5009.04"),
        ("2026-05-10", "Utility Payment", "-126.19", "4882.85"),
        ("2026-05-12", "Transfer to Mia Vargas", "-300.00", "4582.85"),
        ("2026-05-15", "Card Purchase - Market", "-88.42", "4494.43"),
        ("2026-05-18", "Loan Payment Ref LN-4509-7721", "-411.20", "4083.23"),
        ("2026-05-20", "ATM Withdrawal", "-120.00", "3963.23"),
        ("2026-05-24", "Insurance Autopay", "-219.75", "3743.48"),
        ("2026-05-28", "Interest Credit", "+2.14", "3745.62"),
    ]
    for row_index, row in enumerate(rows):
        y = 345 + row_index * 28
        for x, value in zip(x_positions, row):
            page.insert_text((x, y), value, fontsize=8.5, fontname="cour")

    page2 = doc.new_page(width=595, height=842)
    _add_header(page2, "Mock Bank Statement - Page 2")
    _section_box(page2, fitz.Rect(50, 105, 545, 260), "Security Notes")
    _label_value(page2, 70, 145, "Online Banking ID", "OVARGAS-2207")
    _label_value(page2, 70, 170, "Support PIN", "8841")
    _label_value(page2, 70, 195, "Statement Code", "STMT-MOCK-2026-05-OV")
    page2.insert_textbox(
        fitz.Rect(70, 300, 520, 390),
        "This mock second page ensures the redaction app is tested with "
        "multi-page documents and scrollable pages.",
        fontsize=10,
        fontname="helv",
    )

    doc.save(path)
    doc.close()


def _create_medical_form(path: Path) -> None:
    doc = _new_doc()
    page = doc.new_page(width=595, height=842)
    _add_header(page, "Mock Medical Intake Form")

    _section_box(page, fitz.Rect(50, 105, 545, 315), "Patient Information")
    fields = [
        ("Patient", "Leah Kim"),
        ("DOB", "1988-11-24"),
        ("Phone", "+1 614 555 0198"),
        ("Email", "leah.kim@example.test"),
        ("Medical Record No.", "MRN-77-2049-A"),
        ("Insurance ID", "HLTH-5520-9918-AX"),
        ("Emergency Contact", "Noah Kim, +1 614 555 0112"),
    ]
    for index, (label, value) in enumerate(fields):
        _label_value(page, 70, 145 + index * 20, label, value)

    _section_box(page, fitz.Rect(50, 345, 545, 560), "Health History")
    notes = [
        "Current medications: metformin 500mg, lisinopril 10mg.",
        "Allergies: penicillin.",
        "Prior diagnosis: Type 2 diabetes, hypertension.",
        "Preferred pharmacy: Riverbend Pharmacy, account RX-4419-20.",
        "Primary physician: Dr. Elena Park, NPI 1841299001.",
    ]
    for index, note in enumerate(notes):
        page.insert_text((70, 390 + index * 28), note, fontsize=9, fontname="cour")

    _section_box(page, fitz.Rect(50, 590, 545, 710), "Consent")
    page.insert_textbox(
        fitz.Rect(70, 630, 525, 685),
        "I authorize this mock clinic to use this synthetic information "
        "for local redaction software testing only.",
        fontsize=10,
        fontname="helv",
    )
    page.insert_text((70, 725), "Signature: Leah Kim", fontsize=10, fontname="cour")

    doc.save(path)
    doc.close()


if __name__ == "__main__":
    main()
