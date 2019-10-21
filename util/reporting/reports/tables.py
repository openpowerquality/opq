import glob
import os
import subprocess
import typing


def make_table(data: typing.List[typing.List],
               caption: str,
               report_dir: str,
               sort_by_col: int = -1,
               sort_reverse: bool = True,
               sum_cols: typing.List[int] = []):

    # Sort data by last column
    header = data[0]
    data = sorted(data[1:], key=lambda row: row[sort_by_col], reverse=sort_reverse)
    data.insert(0, header)

    # Provide any summations
    if len(sum_cols) > 0:
        sum_row = [0 if c in sum_cols else "" for c in range(len(header))]
        for r in range(1, len(data)):
            for c in sum_cols:
                sum_row[c] += data[r][c]
        sum_row[0] = "Total"
        sum_row = list(map(lambda c: "\\textbf{%s}" % str(c), sum_row))
        data.append(sum_row)

    # Make sure everything is a string
    data = list(map(lambda row: list(map(lambda col: str(col), row)), data))

    # First, create a table in tex
    print("Generated latex")
    align = "l" * len(data[0])
    header = " & ".join(map(lambda h: "\\textbf{%s}" % h.replace("_", "\\_"), data[0])) + " \\\\"
    body = ""
    for r in range(1, len(data)):
        body += " & ".join(map(lambda v: v.replace("_", "\\_"),data[r])) + " \\\\ \n"
    out_path = "%s/%s.tex" % (report_dir, caption.replace(" ", "_"))
    with open("tex_template.tex", "r") as fin:
        with open(out_path, "w") as fout:
            fout.write(fin.read()
                       .replace("_ALIGN_", align)
                       .replace("_HEADER_", header)
                       .replace("_BODY_", body)
                       .replace("_CAPTION_", caption))

    # Make the PDF
    subprocess.run(["pdflatex", "-output-directory", report_dir, out_path])
    pdf_path = out_path.replace(".tex", ".pdf")
    print("Generated PDF")

    # Crop the PDF
    subprocess.run(["pdfcrop", pdf_path, pdf_path])
    print("Cropped PDF")

    # Turn it into a PNG
    png_path = pdf_path.replace(".pdf", ".png")
    subprocess.run(["convert",
                    "-background", "white",
                    "-alpha", "remove",
                    "-alpha", "off",
                    "-density", "750",
                    pdf_path,
                    "-quality", "100",
                    png_path])
    print("Converted PDF to PNG")

    # Cleanup
    fs = []
    types = ["aux", "log", "pdf", "tex"]
    for t in types:
        fs.extend(glob.glob("%s/*.%s" % (report_dir, t)))

    for f in fs:
        os.remove(f)
        print("Removed %s" % f)
