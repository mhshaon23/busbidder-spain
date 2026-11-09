"""
generate_pdf.py
Exports report/BusBidder_Spain_Final_Report.docx to PDF using Microsoft Word,
so the submitted PDF is exactly what Word shows. It also refreshes the table of
contents and saves it in the .docx. Windows with Microsoft Word is required.

    python report/generate_pdf.py

Alternative without this script: open the .docx in Word, right-click the table
of contents > Update Field, then File > Save As > PDF.
"""

import subprocess
from pathlib import Path

REPORT_DIR = Path(__file__).resolve().parent
DOCX_PATH = REPORT_DIR / "BusBidder_Spain_Final_Report.docx"
PDF_PATH = REPORT_DIR / "BusBidder_Spain_Final_Report.pdf"

POWERSHELL = r"""
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open('{docx}')
    foreach ($toc in $doc.TablesOfContents) {{ $toc.Update() }}
    $doc.Fields.Update() | Out-Null
    $doc.Save()
    $doc.SaveAs2('{pdf}', 17)
    $doc.Close($false)
}} finally {{
    $word.Quit()
}}
"""


def export_pdf() -> None:
    script = POWERSHELL.replace("{docx}", str(DOCX_PATH)).replace("{pdf}", str(PDF_PATH))
    script = script.replace("{{", "{").replace("}}", "}")
    subprocess.run(["powershell", "-NoProfile", "-Command", script], check=True)
    print(f"Saved: {PDF_PATH}")


if __name__ == "__main__":
    export_pdf()
