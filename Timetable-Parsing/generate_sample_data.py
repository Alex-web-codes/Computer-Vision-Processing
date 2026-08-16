import os
import matplotlib.pyplot as plt
import pandas as pd

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
except ImportError:
    reportlab = None

DIR = os.path.dirname(__file__)

SAMPLE_DATA = [
    ["Time / Day", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
    ["09:00 - 10:00 AM", "Mathematics", "Physics", "Chemistry", "English", "Computer Sci"],
    ["10:00 - 11:00 AM", "Physics", "Mathematics", "Computer Sci", "Mathematics", "Biology"],
    ["11:00 - 11:30 AM", "BREAK", "BREAK", "BREAK", "BREAK", "BREAK"],
    ["11:30 - 12:30 PM", "Chemistry", "English", "Mathematics", "Physics", "History"],
    ["12:30 - 01:30 PM", "LUNCH", "LUNCH", "LUNCH", "LUNCH", "LUNCH"],
    ["01:30 - 02:30 PM", "Computer Sci", "Biology", "History", "Chemistry", "Art & Design"]
]

def generate_sample_pdf(pdf_path=None):
    if pdf_path is None:
        pdf_path = os.path.join(DIR, "sample_timetable.pdf")

    print(f"[Sample Gen] Creating sample PDF timetable: {pdf_path}")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    title = Paragraph("<b>UNIVERSITY CLASS TIMETABLE</b>", styles["Title"])
    elements.append(title)
    elements.append(Spacer(1, 20))

    t = Table(SAMPLE_DATA)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2C3E50')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 10),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#ECF0F1')),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#7F8C8D')),
    ]))
    elements.append(t)
    doc.build(elements)
    print(f"  [OK] PDF Timetable generated: {pdf_path}")
    return pdf_path

def generate_sample_png(png_path=None):
    if png_path is None:
        png_path = os.path.join(DIR, "sample_timetable.png")

    print(f"[Sample Gen] Creating sample PNG timetable image: {png_path}")
    df = pd.DataFrame(SAMPLE_DATA[1:], columns=SAMPLE_DATA[0])

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.axis("tight")
    ax.axis("off")
    
    table = ax.table(cellText=df.values, colLabels=df.columns, loc="center", cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.8)

    # Style header and borders
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_facecolor("#2C3E50")
            cell.get_text().set_color("white")
            cell.get_text().set_weight("bold")
        else:
            cell.set_facecolor("#F8F9F9")

    plt.title("WEEKLY LECTURE TIMETABLE", fontsize=14, fontweight="bold", pad=20)
    plt.savefig(png_path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"  [OK] PNG Timetable generated: {png_path}")
    return png_path

if __name__ == "__main__":
    generate_sample_pdf()
    generate_sample_png()
