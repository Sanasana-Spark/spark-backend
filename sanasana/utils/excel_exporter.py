from io import BytesIO
import openpyxl
from flask import send_file


def export_to_excel(data, filename="report.xlsx", sheet_name="Report"):
    """
    Generates an Excel file from a list of dictionaries and sends it as a download.

    :param data: List of dicts, each dict = row
    :param filename: Download file name
    :param sheet_name: Excel sheet title
    :return: Flask send_file response
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet_name

    if not data:
        ws.append(["No data"])
    else:
        # Write header
        headers = list(data[0].keys())
        ws.append(headers)

        # Write rows
        for row in data:
            ws.append([row.get(h) for h in headers])

    # Save to BytesIO
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    # Send as downloadable file
    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
