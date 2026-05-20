import os
import pathlib
import weasyprint

DATA_DIR = os.environ.get("DATA_DIR", "/data")


def render_invoice_pdf(invoice, items, business_snapshot: dict, client_snapshot: dict, template_env) -> bytes:
    """
    Render invoice_pdf.html template → WeasyPrint → bytes.
    Writes to disk at DATA_DIR/pdfs/YYYY/invoice.number.pdf and updates invoice.pdf_path.
    """
    template = template_env.get_template("invoice_pdf.html")
    html_string = template.render(
        invoice=invoice,
        items=items,
        business=business_snapshot,
        client=client_snapshot,
    )

    pdf_bytes = weasyprint.HTML(string=html_string).write_pdf()

    year = str(invoice.issue_date.year)
    out_dir = pathlib.Path(DATA_DIR) / "pdfs" / year
    out_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{invoice.number}.pdf"
    full_path = out_dir / filename
    full_path.write_bytes(pdf_bytes)

    # Store relative path
    invoice.pdf_path = str(pathlib.Path("pdfs") / year / filename)

    return pdf_bytes


def render_receipt_pdf(invoice, business_snapshot: dict, client_snapshot: dict, template_env) -> bytes:
    """
    Render receipt_pdf.html template → WeasyPrint → bytes.
    Writes to disk at DATA_DIR/receipts/YYYY/receipt.pdf and updates invoice.receipt_pdf_path.
    """
    template = template_env.get_template("receipt_pdf.html")
    html_string = template.render(
        invoice=invoice,
        business=business_snapshot,
        client=client_snapshot,
    )

    pdf_bytes = weasyprint.HTML(string=html_string).write_pdf()

    year = str(invoice.paid_at.year)
    out_dir = pathlib.Path(DATA_DIR) / "receipts" / year
    out_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{invoice.receipt_number}.pdf"
    full_path = out_dir / filename
    full_path.write_bytes(pdf_bytes)

    # Store relative path
    invoice.receipt_pdf_path = str(pathlib.Path("receipts") / year / filename)

    return pdf_bytes
