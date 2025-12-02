import os
import re
import argparse

def run(input_file: str, output_dir: str, threshold_mm: int = 5, excel_file: str = "ec_alerts.xml") -> None:
    with open(input_file, "r", encoding="utf-8", errors="ignore") as f:
        lines = [ln.strip() for ln in f.readlines() if ln and ln.strip()]

    voie01 = []
    voie02 = []
    voie01_ec = []
    voie02_dv = []
    voie02_ec = []
    voie01_dv = []

    for line in lines:
        tokens = re.split(r"\s+", line)
        if not tokens:
            continue
        idp = tokens[0]
        last = tokens[-1]
        code = last if last in ("EC", "DV") else None

        if re.match(r"^VO0*1_", idp):
            voie01.append(line)
            if code == "EC":
                voie01_ec.append(line)
            elif code == "DV":
                voie01_dv.append(line)
        elif re.match(r"^VO0*2_", idp):
            voie02.append(line)
            if code == "DV":
                voie02_dv.append(line)
            elif code == "EC":
                voie02_ec.append(line)

    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "voie01.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(voie01) + ("\n" if voie01 else ""))
    with open(os.path.join(output_dir, "voie02.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(voie02) + ("\n" if voie02 else ""))
    with open(os.path.join(output_dir, "voie01_ec.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(voie01_ec) + ("\n" if voie01_ec else ""))
    with open(os.path.join(output_dir, "voie02_dv.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(voie02_dv) + ("\n" if voie02_dv else ""))
    with open(os.path.join(output_dir, "voie02_ec.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(voie02_ec) + ("\n" if voie02_ec else ""))
    with open(os.path.join(output_dir, "voie01_dv.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(voie01_dv) + ("\n" if voie01_dv else ""))

    def analyze_ec(lines_ec):
        pairs = []
        pts = []
        for ln in lines_ec:
            tk = re.split(r"\s+", ln)
            if len(tk) >= 3:
                pts.append((tk[0], float(tk[1]), float(tk[2])))
        for i in range(0, len(pts) - 1, 2):
            p0, x0, y0 = pts[i]
            p1, x1, y1 = pts[i+1]
            dx = x1 - x0
            dy = y1 - y0
            d = (dx*dx + dy*dy) ** 0.5
            diff_mm = round((d - 1.435) * 1000)
            pairs.append((p0, p1, d, diff_mm))
        return pairs

    voie01_pairs = analyze_ec(voie01_ec)
    voie02_pairs = analyze_ec(voie02_ec)

    def fmt_line(p0, p1, d, diff_mm):
        sign = "+" if diff_mm > 0 else ("-" if diff_mm < 0 else "0")
        return f"{p0}\t{p1}\t{d:.3f}\t{sign}{abs(diff_mm)} mm"

    with open(os.path.join(output_dir, "voie01_ec_analysis.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(fmt_line(*t) for t in voie01_pairs) + ("\n" if voie01_pairs else ""))
    with open(os.path.join(output_dir, "voie02_ec_analysis.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(fmt_line(*t) for t in voie02_pairs) + ("\n" if voie02_pairs else ""))

    def write_csv(pairs, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write("point_a,point_b,distance_m,diff_mm,flag\n")
            for p0, p1, d, diff_mm in pairs:
                flag = "ALERT" if abs(diff_mm) > threshold_mm else "OK"
                f.write(f"{p0},{p1},{d:.3f},{diff_mm},{flag}\n")

    write_csv(voie01_pairs, os.path.join(output_dir, "voie01_ec_analysis.csv"))
    write_csv(voie02_pairs, os.path.join(output_dir, "voie02_ec_analysis.csv"))

    alerts01 = [p for p in voie01_pairs if abs(p[3]) > threshold_mm]
    alerts02 = [p for p in voie02_pairs if abs(p[3]) > threshold_mm]

    def write_excel_xml(path, sheet1, sheet2):
        header = (
            "<?xml version=\"1.0\"?>\n"
            "<?mso-application progid=\"Excel.Sheet\"?>\n"
            "<Workbook xmlns=\"urn:schemas-microsoft-com:office:spreadsheet\" "
            "xmlns:o=\"urn:schemas-microsoft-com:office:office\" "
            "xmlns:x=\"urn:schemas-microsoft-com:office:excel\" "
            "xmlns:ss=\"urn:schemas-microsoft-com:office:spreadsheet\">\n"
        )
        def sheet_xml(name, rows):
            s = [f"<Worksheet ss:Name=\"{name}\">", "<Table>"]
            s.append("<Row>"
                     "<Cell><Data ss:Type=\"String\">point_a</Data></Cell>"
                     "<Cell><Data ss:Type=\"String\">point_b</Data></Cell>"
                     "<Cell><Data ss:Type=\"String\">distance_m</Data></Cell>"
                     "<Cell><Data ss:Type=\"String\">diff_mm</Data></Cell>")
            for p0, p1, d, diff_mm in rows:
                s.append("<Row>"
                         f"<Cell><Data ss:Type=\"String\">{p0}</Data></Cell>"
                         f"<Cell><Data ss:Type=\"String\">{p1}</Data></Cell>"
                         f"<Cell><Data ss:Type=\"Number\">{d:.3f}</Data></Cell>"
                         f"<Cell><Data ss:Type=\"Number\">{diff_mm}</Data></Cell>")
            s.append("</Table>")
            s.append("</Worksheet>")
            return "\n".join(s)
        content = header + sheet_xml("VOIE01_ALERTS", alerts01) + "\n" + sheet_xml("VOIE02_ALERTS", alerts02) + "\n" + "</Workbook>\n"
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    write_excel_xml(os.path.join(output_dir, excel_file), alerts01, alerts02)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="levéRaildemo.txt")
    parser.add_argument("--output", default=".")
    parser.add_argument("--threshold-mm", type=int, default=5)
    parser.add_argument("--excel-file", default="ec_alerts.xml")
    args = parser.parse_args()
    run(args.input, args.output, args.threshold_mm, args.excel_file)
