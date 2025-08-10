from io import BytesIO
from flask import send_file
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas


def add_footer(canvas, doc):
    footer_text = "Powered by Spark-by-Sanasana"
    canvas.saveState()
    canvas.setFont('Helvetica-Oblique', 9)
    width, height = landscape(A4)
    canvas.drawCentredString(width / 2, 20, footer_text)
    canvas.restoreState()


def export_to_pdf(data, filename="report.pdf", title="Report"):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph(title, styles['Title']))

    if not data:
        elements.append(Paragraph("No data available.", styles['Normal']))
    else:
        headers = list(data[0].keys())
        table_data = [headers]
        for row in data:
            table_data.append([row.get(h, "") for h in headers])

        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#01947A")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 11),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ]))
        elements.append(table)

    doc.build(elements, onFirstPage=add_footer, onLaterPages=add_footer)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )
