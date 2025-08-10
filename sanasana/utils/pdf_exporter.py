from io import BytesIO
from flask import send_file
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

def export_to_pdf(data, filename="report.pdf", title="Report"):
    """
    Generates a PDF table from a list of dicts and sends it as a download.

    :param data: List of dicts, each dict = row
    :param filename: Download file name
    :param title: Report title
    :return: Flask send_file response
    """
    buffer = BytesIO()

    # PDF document
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    elements = []
    styles = getSampleStyleSheet()

    # Title
    elements.append(Paragraph(title, styles['Title']))

    if not data:
        elements.append(Paragraph("No data available.", styles['Normal']))
    else:
        # Prepare table data
        headers = list(data[0].keys())
        table_data = [headers]
        for row in data:
            table_data.append([row.get(h, "") for h in headers])

        # Table
        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#4F81BD")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 11),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ]))
        elements.append(table)

    # Build PDF
    doc.build(elements)
    buffer.seek(0)

    # Send as downloadable file
    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )
