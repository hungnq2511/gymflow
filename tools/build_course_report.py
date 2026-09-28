from __future__ import annotations

from pathlib import Path
from textwrap import dedent

from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts"
ASSETS = OUT / "report_assets"
DOCX = OUT / "Bao_cao_Cong_nghe_phan_mem_GymFlow.docx"
OUT.mkdir(exist_ok=True)
ASSETS.mkdir(exist_ok=True)

NAVY = "17365D"
BLUE = "DCE6F1"
PALE = "F3F6FA"
GRAY = "D9D9D9"
TEXT = "111111"


def set_cell_shading(cell, fill: str):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=90, start=100, bottom=90, end=100):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for m, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{m}"))
        if node is None:
            node = OxmlElement(f"w:{m}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_table_borders(table, color=GRAY, size="6"):
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.first_child_found_in("w:tblBorders")
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = borders.find(qn(f"w:{edge}"))
        if tag is None:
            tag = OxmlElement(f"w:{edge}")
            borders.append(tag)
        tag.set(qn("w:val"), "single")
        tag.set(qn("w:sz"), size)
        tag.set(qn("w:color"), color)


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def set_repeat_heading(row):
    set_repeat_table_header(row)


def add_field(run, instruction: str):
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = instruction
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instr, separate, end])


def add_page_number(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run()
    add_field(run, "PAGE")


def set_font(run, name="Times New Roman", size=12, bold=False, italic=False, color=TEXT):
    run.font.name = name
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), name)
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), name)
    run._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), name)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = RGBColor.from_string(color)


def style_document(doc: Document):
    sec = doc.sections[0]
    sec.page_width = Inches(8.5)
    sec.page_height = Inches(11)
    sec.top_margin = Inches(0.72)
    sec.bottom_margin = Inches(0.68)
    sec.left_margin = Inches(0.9)
    sec.right_margin = Inches(0.72)
    sec.header_distance = Inches(0.3)
    sec.footer_distance = Inches(0.3)

    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    normal.font.size = Pt(12)
    pf = normal.paragraph_format
    pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    pf.first_line_indent = Inches(0.3)
    pf.space_after = Pt(5)
    pf.line_spacing = 1.25

    for name, size, before, after in [
        ("Title", 21, 0, 10),
        ("Heading 1", 17, 14, 8),
        ("Heading 2", 14, 11, 6),
        ("Heading 3", 12, 8, 4),
    ]:
        st = doc.styles[name]
        st.font.name = "Times New Roman"
        st._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
        st.font.size = Pt(size)
        st.font.bold = True
        st.font.color.rgb = RGBColor(0, 0, 0)
        st.paragraph_format.space_before = Pt(before)
        st.paragraph_format.space_after = Pt(after)
        st.paragraph_format.keep_with_next = True
        p_pr = st._element.get_or_add_pPr()
        p_bdr = p_pr.find(qn("w:pBdr"))
        if p_bdr is not None:
            p_pr.remove(p_bdr)

    for section in doc.sections:
        header = section.header
        p = header.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run("BÁO CÁO CÔNG NGHỆ PHẦN MỀM   |   GYMFLOW")
        set_font(r, size=8, bold=True, color="555555")
        add_page_number(section.footer.paragraphs[0])

    settings = doc.settings._element
    update = OxmlElement("w:updateFields")
    update.set(qn("w:val"), "true")
    settings.append(update)


def add_para(doc, text: str, bold_lead: str | None = None, align=None, indent=True):
    p = doc.add_paragraph()
    if align is not None:
        p.alignment = align
    if not indent:
        p.paragraph_format.first_line_indent = Inches(0)
    if bold_lead and text.startswith(bold_lead):
        r1 = p.add_run(bold_lead)
        set_font(r1, bold=True)
        r2 = p.add_run(text[len(bold_lead):])
        set_font(r2)
    else:
        r = p.add_run(text)
        set_font(r)
    return p


def add_bullets(doc, items, level=0):
    for item in items:
        p = doc.add_paragraph(style="List Bullet" if level == 0 else "List Bullet 2")
        p.paragraph_format.first_line_indent = Inches(0)
        p.paragraph_format.left_indent = Inches(0.25 + level * 0.2)
        p.paragraph_format.space_after = Pt(3)
        r = p.add_run(item)
        set_font(r)


def add_numbered(doc, items):
    for index, item in enumerate(items, 1):
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Inches(0)
        p.paragraph_format.left_indent = Inches(0.3)
        p.paragraph_format.space_after = Pt(3)
        set_font(p.add_run(f"{index}. {item}"))


def add_toc_line(doc, label, page, major=False):
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Inches(0)
    p.paragraph_format.left_indent = Inches(0 if major else 0.25)
    p.paragraph_format.space_after = Pt(3 if major else 2)
    p.paragraph_format.tab_stops.add_tab_stop(Inches(6.15), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
    r = p.add_run(f"{label}\t{page}")
    set_font(r, size=10.5 if major else 10, bold=major)


def add_table(doc, headers, rows, widths=None, font_size=9):
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_table_borders(table)
    hdr = table.rows[0]
    set_repeat_heading(hdr)
    for i, h in enumerate(headers):
        cell = hdr.cells[i]
        set_cell_shading(cell, NAVY)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        set_cell_margins(cell)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Inches(0)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(str(h))
        set_font(r, size=font_size, bold=True, color="FFFFFF")
        if widths:
            cell.width = Inches(widths[i])
    for ridx, row in enumerate(rows):
        cells = table.add_row().cells
        for i, value in enumerate(row):
            cell = cells[i]
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            set_cell_margins(cell)
            if ridx % 2 == 1:
                set_cell_shading(cell, PALE)
            p = cell.paragraphs[0]
            p.paragraph_format.first_line_indent = Inches(0)
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if len(str(value)) < 24 and i != len(row) - 1 else WD_ALIGN_PARAGRAPH.LEFT
            set_font(p.add_run(str(value)), size=font_size)
            if widths:
                cell.width = Inches(widths[i])
    doc.add_paragraph().paragraph_format.space_after = Pt(0)
    return table


def caption(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Inches(0)
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(7)
    set_font(p.add_run(text), size=10, italic=True)


def new_page(doc, heading=None, level=2):
    doc.add_page_break()
    if heading:
        doc.add_heading(heading, level=level)


def add_picture(doc, path, width=6.25, cap=None):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Inches(0)
    shape = p.add_run().add_picture(str(path), width=Inches(width))
    alt = cap or Path(path).stem.replace("_", " ")
    shape._inline.docPr.set("descr", alt)
    shape._inline.docPr.set("title", alt)
    if cap:
        caption(doc, cap)


def diagram(path, title, boxes, arrows, footer=None):
    width, height = 1800, 1044
    scale = width / 10
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    font_path = "/System/Library/Fonts/Supplemental/Arial.ttf"
    bold_path = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
    regular = ImageFont.truetype(font_path, 29)
    small = ImageFont.truetype(font_path, 23)
    title_font = ImageFont.truetype(bold_path, 43)
    draw.text((width / 2, 54), title, anchor="mm", font=title_font, fill="#111111")
    centers = {}
    for key, x, y, w, h, label, fill in boxes:
        left = int(x * scale)
        top = int(height - (y + h) * scale)
        right = int((x + w) * scale)
        bottom = int(height - y * scale)
        draw.rounded_rectangle((left, top, right, bottom), radius=16, fill=fill, outline="#17365D", width=3)
        draw.multiline_text(((left + right) / 2, (top + bottom) / 2), label, anchor="mm", align="center", font=regular, fill="#111111", spacing=5)
        centers[key] = ((left + right) / 2, (top + bottom) / 2)
    for a, b, label in arrows:
        x1, y1 = centers[a]
        x2, y2 = centers[b]
        import math
        dx, dy = x2 - x1, y2 - y1
        distance = max(math.hypot(dx, dy), 1)
        ux, uy = dx / distance, dy / distance
        start = (x1 + ux * 68, y1 + uy * 48)
        end = (x2 - ux * 70, y2 - uy * 48)
        draw.line((start, end), fill="#365F91", width=4)
        px, py = -uy, ux
        tip = end
        base = (end[0] - ux * 22, end[1] - uy * 22)
        draw.polygon([tip, (base[0] + px * 10, base[1] + py * 10), (base[0] - px * 10, base[1] - py * 10)], fill="#365F91")
        if label:
            mx, my = (start[0] + end[0]) / 2, (start[1] + end[1]) / 2 - 16
            bbox = draw.textbbox((mx, my), label, anchor="mm", font=small)
            draw.rectangle((bbox[0] - 5, bbox[1] - 3, bbox[2] + 5, bbox[3] + 3), fill="white")
            draw.text((mx, my), label, anchor="mm", font=small, fill="#555555")
    if footer:
        draw.text((width / 2, height - 28), footer, anchor="ms", font=small, fill="#555555")
    image.save(path)


def make_diagrams():
    diagram(
        ASSETS / "scrum.png", "Chu trình Scrum áp dụng cho GymFlow",
        [
            ("pb", .4, 3.4, 1.5, .8, "Product\nBacklog", "#DCE6F1"),
            ("plan", 2.3, 3.4, 1.5, .8, "Sprint\nPlanning", "#EAF2F8"),
            ("sprint", 4.2, 3.2, 1.8, 1.2, "Sprint\n1 đến 2 tuần", "#FFF2CC"),
            ("daily", 4.35, 1.55, 1.5, .75, "Daily Scrum", "#E2F0D9"),
            ("inc", 6.45, 3.4, 1.4, .8, "Increment", "#DDEBF7"),
            ("review", 8.2, 3.8, 1.3, .7, "Review", "#FCE4D6"),
            ("retro", 8.2, 2.35, 1.3, .7, "Retro", "#F4CCCC"),
        ],
        [("pb","plan","chọn ưu tiên"),("plan","sprint","Sprint Backlog"),("daily","sprint","đồng bộ"),("sprint","inc","hoàn thành"),("inc","review","phản hồi"),("inc","retro","cải tiến"),("review","pb","điều chỉnh")],
        "Mỗi Increment phải đáp ứng Definition of Done trước khi trình diễn",
    )
    diagram(
        ASSETS / "architecture.png", "Kiến trúc tổng thể của hệ thống GymFlow",
        [
            ("browser", .3, 2.45, 1.5, .9, "Trình duyệt\nManager Staff Member", "#DCE6F1"),
            ("ui", 2.25, 3.45, 1.7, .9, "Next.js App Router\nReact UI", "#EAF2F8"),
            ("api", 2.25, 1.45, 1.7, .9, "Route Handlers\nZod RBAC", "#EAF2F8"),
            ("auth", 4.55, 3.45, 1.7, .9, "Supabase Auth\nSession JWT", "#E2F0D9"),
            ("db", 4.55, 1.45, 1.7, .9, "PostgreSQL\nRLS Index", "#FFF2CC"),
            ("rpc", 7.0, 1.45, 1.8, .9, "PL pgSQL RPC\nGiao dịch nguyên tử", "#FCE4D6"),
            ("audit", 7.0, 3.45, 1.8, .9, "Audit Logs\nTruy vết", "#F4CCCC"),
        ],
        [("browser","ui","HTTPS"),("ui","api","fetch JSON"),("api","auth","xác thực"),("api","db","truy vấn"),("db","rpc","thực thi"),("api","audit","ghi nhật ký"),("auth","db","profile role")],
        "Service role chỉ tồn tại ở phía máy chủ và không được gửi xuống trình duyệt",
    )
    diagram(
        ASSETS / "checkin.png", "Luồng xử lý check in",
        [
            ("scan", .3, 3.6, 1.4, .8, "Quét QR hoặc\nnhập mã", "#DCE6F1"),
            ("api", 2.15, 3.6, 1.5, .8, "API kiểm tra\nquyền staff", "#EAF2F8"),
            ("lock", 4.15, 3.6, 1.6, .8, "Khóa bản ghi\nhội viên gói", "#FFF2CC"),
            ("rules", 6.25, 3.3, 1.65, 1.4, "Kiểm tra trạng thái\nthời hạn đóng băng\nlượt và trùng 10 phút", "#FCE4D6"),
            ("ok", 8.35, 4.15, 1.3, .7, "Ghi check in", "#E2F0D9"),
            ("deny", 8.35, 2.75, 1.3, .7, "Từ chối có lý do", "#F4CCCC"),
            ("visit", 6.35, 1.35, 1.45, .75, "Trừ một lượt", "#E2F0D9"),
            ("log", 8.35, 1.35, 1.3, .75, "Ghi audit log", "#DDEBF7"),
        ],
        [("scan","api","token"),("api","lock","RPC"),("lock","rules","FOR UPDATE"),("rules","ok","hợp lệ"),("rules","deny","không hợp lệ"),("ok","visit","gói theo lượt"),("visit","log","cùng giao dịch"),("ok","log","")],
        "Toàn bộ thay đổi dữ liệu thành công hoặc thất bại cùng nhau",
    )
    diagram(
        ASSETS / "subscription.png", "Vòng đời đăng ký gói tập",
        [
            ("scheduled", .6, 3.4, 1.55, .8, "Scheduled\nchờ hiệu lực", "#DCE6F1"),
            ("active", 3.0, 3.4, 1.45, .8, "Active\nđang sử dụng", "#E2F0D9"),
            ("frozen", 5.35, 3.4, 1.45, .8, "Frozen\ntạm dừng", "#FFF2CC"),
            ("expired", 7.75, 3.4, 1.45, .8, "Expired\nhết hạn", "#E7E6E6"),
            ("cancel", 4.15, 1.55, 1.7, .8, "Cancelled\nđã hủy", "#F4CCCC"),
        ],
        [("scheduled","active","đến ngày bắt đầu"),("active","frozen","đóng băng"),("frozen","active","mở lại và gia hạn"),("active","expired","qua ngày kết thúc"),("scheduled","cancel","hủy"),("active","cancel","hủy quản trị")],
        "Snapshot tên gói giá thời hạn và số lượt bảo toàn lịch sử giao dịch",
    )
    diagram(
        ASSETS / "deployment.png", "Mô hình triển khai đề xuất",
        [
            ("user", .4, 2.7, 1.3, .8, "Người dùng\nHTTPS", "#DCE6F1"),
            ("web", 2.25, 2.7, 1.55, .8, "Next.js\nWeb runtime", "#EAF2F8"),
            ("env", 4.25, 4.0, 1.55, .75, "Biến môi trường\nbí mật", "#FFF2CC"),
            ("auth", 4.25, 2.7, 1.55, .8, "Supabase Auth", "#E2F0D9"),
            ("db", 6.35, 2.7, 1.55, .8, "Supabase\nPostgreSQL", "#FFF2CC"),
            ("backup", 8.35, 3.8, 1.2, .75, "Sao lưu", "#E7E6E6"),
            ("monitor", 8.35, 1.65, 1.2, .75, "Giám sát", "#FCE4D6"),
        ],
        [("user","web","request"),("web","auth","session"),("auth","db","profile"),("web","db","server API"),("env","web","inject"),("db","backup","schedule"),("web","monitor","log")],
        "Môi trường development staging production dùng cấu hình và dữ liệu tách biệt",
    )


def add_cover(doc):
    section = doc.sections[0]
    section.header.is_linked_to_previous = False
    section.footer.is_linked_to_previous = False
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Inches(0)
    for text, size, bold, space in [
        ("TRƯỜNG ĐẠI HỌC .................................", 13, True, 2),
        ("KHOA CÔNG NGHỆ THÔNG TIN", 13, True, 28),
        ("BÁO CÁO MÔN HỌC", 16, True, 6),
        ("CÔNG NGHỆ PHẦN MỀM", 16, True, 26),
    ]:
        run = p.add_run(text)
        set_font(run, size=size, bold=bold)
        run.add_break()
        p.paragraph_format.space_after = Pt(space)
    title = doc.add_paragraph(style="Title")
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.paragraph_format.first_line_indent = Inches(0)
    set_font(title.add_run("XÂY DỰNG HỆ THỐNG QUẢN LÝ PHÒNG GYM TRÊN NỀN TẢNG WEB THEO PHƯƠNG PHÁP AGILE SCRUM"), size=21, bold=True)
    p_pr = title._p.get_or_add_pPr()
    p_bdr = p_pr.find(qn("w:pBdr"))
    if p_bdr is not None:
        p_pr.remove(p_bdr)
    doc.add_paragraph()
    info = [
        ("Giảng viên hướng dẫn", "[HỌ VÀ TÊN GIẢNG VIÊN]"),
        ("Sinh viên thực hiện", "[HỌ VÀ TÊN SINH VIÊN]"),
        ("Mã số sinh viên", "[MÃ SỐ SINH VIÊN]"),
        ("Lớp", "[TÊN LỚP]"),
        ("Nhóm", "[SỐ NHÓM]"),
    ]
    table = doc.add_table(rows=len(info), cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_repeat_table_header(table.rows[0])
    for i, (a, b) in enumerate(info):
        table.rows[i].cells[0].width = Inches(2.0)
        table.rows[i].cells[1].width = Inches(3.8)
        for j, value in enumerate((a, b)):
            cell = table.rows[i].cells[j]
            p2 = cell.paragraphs[0]
            p2.paragraph_format.first_line_indent = Inches(0)
            set_font(p2.add_run(value), size=12, bold=(j == 0))
            set_cell_margins(cell, top=70, bottom=70)
    tbl_pr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{edge}")
        e.set(qn("w:val"), "nil")
        borders.append(e)
    tbl_pr.append(borders)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Inches(0)
    p.paragraph_format.space_before = Pt(54)
    set_font(p.add_run("Thành phố Hồ Chí Minh năm 2026"), size=12, bold=True)


def add_front_matter(doc):
    new_page(doc, "Lời cam đoan", 1)
    add_para(doc, "Tôi cam đoan báo cáo này trình bày kết quả phân tích và xây dựng hệ thống GymFlow trong phạm vi môn học Công nghệ phần mềm. Các nội dung tham khảo về Agile, Scrum và công nghệ nền tảng đều được ghi nguồn ở cuối báo cáo. Mã nguồn, cấu trúc cơ sở dữ liệu, ca kiểm thử và kết quả build được đối chiếu trực tiếp từ project tại thời điểm lập báo cáo.")
    add_para(doc, "Những thông tin nhận diện sinh viên, lớp và giảng viên trên trang bìa cần được bổ sung trước khi nộp. Người thực hiện chịu trách nhiệm kiểm tra lại quy định trình bày riêng của cơ sở đào tạo, tính chính xác của thông tin cá nhân và phạm vi đóng góp của từng thành viên nếu đây là bài làm nhóm.")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.paragraph_format.first_line_indent = Inches(0)
    p.paragraph_format.space_before = Pt(28)
    set_font(p.add_run("Sinh viên thực hiện\n\n\n[HỌ VÀ TÊN]"), bold=True)

    new_page(doc, "Lời cảm ơn", 1)
    add_para(doc, "Tôi xin cảm ơn giảng viên môn Công nghệ phần mềm đã cung cấp nền tảng về quy trình phát triển, quản lý yêu cầu, thiết kế, kiểm thử và cải tiến sản phẩm. Những kiến thức đó được vận dụng để tổ chức đề tài GymFlow theo cách tiếp cận Agile Scrum, từ việc hình thành Product Backlog đến đánh giá Increment sau mỗi sprint.")
    add_para(doc, "Tôi cũng ghi nhận các tài liệu chính thức của Scrum, Next.js, TypeScript, Supabase, PostgreSQL, Zod và Vitest đã hỗ trợ quá trình lựa chọn kỹ thuật. Báo cáo tập trung vào khả năng áp dụng kiến thức vào một bài toán quản lý phòng gym có dữ liệu, vai trò người dùng và giao dịch tài chính cụ thể.")

    new_page(doc, "Tóm tắt", 1)
    add_para(doc, "Đề tài xây dựng một hệ thống quản lý phòng gym trên nền tảng web nhằm số hóa các hoạt động thường xuyên của một chi nhánh. Hệ thống GymFlow hỗ trợ đăng nhập và phân quyền, quản lý hội viên, quản lý gói tập, bán và gia hạn gói, thanh toán, check in bằng mã QR hoặc mã hội viên, đóng băng gói, báo cáo, chăm sóc hội viên và theo dõi chi phí. Cổng hội viên cho phép người dùng xem mã QR, gói hiện tại, lịch sử thanh toán, lịch sử check in và cập nhật thông tin liên hệ.")
    add_para(doc, "Giải pháp sử dụng Next.js 16 và React 19 cho lớp giao diện và Route Handler, TypeScript cho kiểm tra kiểu, Zod cho xác thực đầu vào, Supabase Auth cho phiên đăng nhập và PostgreSQL cho dữ liệu. Các nghiệp vụ có nguy cơ phát sinh sai lệch như bán gói, check in, đóng băng và hủy thanh toán được đặt trong hàm cơ sở dữ liệu để thực thi nguyên tử. Phân quyền được kiểm tra tại API, đồng thời Row Level Security bảo vệ dữ liệu ở lớp cơ sở dữ liệu.")
    add_para(doc, "Quy trình phát triển được tổ chức theo Scrum với Product Backlog ưu tiên theo giá trị nghiệp vụ và rủi ro. Mỗi sprint tạo ra một Increment có thể kiểm thử. Kết quả kiểm chứng tại thời điểm lập báo cáo gồm 16 ca kiểm thử tự động đều đạt, kiểm tra lint không phát hiện lỗi và bản build production hoàn thành với 23 route. Báo cáo kết luận rằng hệ thống đáp ứng phạm vi MVP của một phòng gym đơn chi nhánh và có nền tảng để mở rộng theo hướng đa chi nhánh, thanh toán trực tuyến, thông báo tự động và quan sát vận hành.")
    add_para(doc, "Từ khóa Agile Scrum Next.js Supabase PostgreSQL quản lý phòng gym", bold_lead="Từ khóa ", indent=False)

    new_page(doc, "Abstract", 1)
    add_para(doc, "This report presents GymFlow, a web based management system for a single branch gym. The product covers authentication and role based access, member records, membership plans, subscription sales and renewals, payments, QR or member code check in, subscription freezing, reports, retention follow ups, expenses, and a self service member portal.")
    add_para(doc, "The system uses Next.js 16, React 19, TypeScript, Zod, Supabase Auth, and PostgreSQL. Business critical operations are implemented as database functions so related changes are committed atomically. Server side authorization is combined with database Row Level Security. Development is organized with Scrum artifacts and events, and the report traces requirements from backlog items to design and test evidence.")
    add_para(doc, "At the reporting checkpoint, all 16 automated tests pass, lint completes without findings, and the optimized production build succeeds with 23 application and API routes. The implementation therefore satisfies the defined MVP scope while leaving clear increments for multi branch operation, online payment, automated notifications, and production observability.")
    add_para(doc, "Keywords Agile Scrum Next.js Supabase PostgreSQL gym management", bold_lead="Keywords ", indent=False)

    new_page(doc, "Mục lục", 1)
    for label, page, major in [
        ("Lời cam đoan", 2, False),
        ("Lời cảm ơn", 3, False),
        ("Tóm tắt", 4, False),
        ("Abstract", 5, False),
        ("Danh mục bảng và hình", 7, False),
        ("Danh mục từ viết tắt", 8, False),
        ("1 Tổng quan đề tài", 9, True),
        ("2 Cơ sở phương pháp Agile Scrum", 14, True),
        ("3 Phân tích yêu cầu", 21, True),
        ("4 Phân tích và thiết kế hệ thống", 29, True),
        ("5 Hiện thực hệ thống", 39, True),
        ("6 Kiểm thử và đánh giá", 50, True),
        ("7 Triển khai và vận hành", 57, True),
        ("8 Kết luận và hướng phát triển", 64, True),
        ("Tài liệu tham khảo", 68, True),
        ("Phụ lục A đến H", "69 đến 76", True),
    ]:
        add_toc_line(doc, label, page, major)

    new_page(doc, "Danh mục bảng và hình", 1)
    add_table(doc, ["Ký hiệu", "Nội dung"], [
        ("Hình 2.1", "Chu trình Scrum áp dụng cho GymFlow"),
        ("Hình 4.1", "Kiến trúc tổng thể của hệ thống"),
        ("Hình 4.2", "Luồng xử lý check in"),
        ("Hình 4.3", "Vòng đời đăng ký gói tập"),
        ("Hình 7.1", "Mô hình triển khai đề xuất"),
        ("Bảng 2.1", "Vai trò và trách nhiệm Scrum"),
        ("Bảng 2.2", "Kế hoạch sprint"),
        ("Bảng 3.1", "Product Backlog rút gọn"),
        ("Bảng 3.2", "Ma trận phân quyền"),
        ("Bảng 4.1", "Từ điển dữ liệu mức bảng"),
        ("Bảng 5.1", "Danh mục API"),
        ("Bảng 6.1", "Kết quả kiểm thử"),
        ("Bảng 7.1", "Rủi ro triển khai"),
    ], widths=[1.2, 5.2], font_size=10)

    new_page(doc, "Danh mục từ viết tắt", 1)
    add_table(doc, ["Từ viết tắt", "Diễn giải"], [
        ("API", "Application Programming Interface"),
        ("CRUD", "Create Read Update Delete"),
        ("DoD", "Definition of Done"),
        ("JWT", "JSON Web Token"),
        ("MVP", "Minimum Viable Product"),
        ("QR", "Quick Response code"),
        ("RBAC", "Role Based Access Control"),
        ("RLS", "Row Level Security"),
        ("RPC", "Remote Procedure Call"),
        ("UI", "User Interface"),
    ], widths=[1.6, 4.8], font_size=10)


def chapter1(doc):
    new_page(doc, "1 Tổng quan đề tài", 1)
    doc.add_heading("1.1 Bối cảnh và lý do chọn đề tài", level=2)
    add_para(doc, "Một phòng gym quy mô nhỏ hoặc vừa thường bắt đầu bằng sổ ghi chép, bảng tính và các nhóm nhắn tin. Cách làm này đáp ứng giai đoạn đầu nhưng nhanh chóng bộc lộ hạn chế khi số hội viên, gói tập và giao dịch tăng lên. Lễ tân phải kiểm tra nhiều nguồn để xác định thời hạn gói; quản lý khó đối chiếu doanh thu và chi phí; hội viên không chủ động xem lịch sử sử dụng. Dữ liệu trùng lặp còn làm tăng rủi ro thu sai tiền, trừ sai lượt hoặc cho phép một tài khoản xem thông tin không thuộc phạm vi của mình.")
    add_para(doc, "Đề tài chọn bài toán quản lý phòng gym vì đây là một miền nghiệp vụ đủ rõ để áp dụng trọn vẹn chu trình công nghệ phần mềm. Hệ thống phải xử lý dữ liệu chủ, giao dịch, phân quyền, báo cáo và các quy tắc có tính thời gian. Một thao tác check in tưởng như đơn giản nhưng thực tế phải kiểm tra trạng thái hội viên, ngày bắt đầu, ngày hết hạn, trạng thái đóng băng, số lượt còn lại và lần quét gần nhất. Điều đó tạo điều kiện để đánh giá chất lượng phân tích yêu cầu, thiết kế dữ liệu và kiểm thử.")
    add_para(doc, "GymFlow được định hướng là ứng dụng web cho một chi nhánh, dùng được trên máy tính quầy lễ tân và thiết bị di động. Mục tiêu của phiên bản MVP không phải thay thế mọi hệ thống vận hành của doanh nghiệp lớn. Mục tiêu là tạo một luồng nghiệp vụ nhất quán từ tiếp nhận hội viên, bán gói, ghi nhận thanh toán đến kiểm soát ra vào và theo dõi tình hình kinh doanh.")

    new_page(doc, "1.2 Mục tiêu của hệ thống", 2)
    add_para(doc, "Mục tiêu tổng quát là xây dựng một hệ thống web giúp phòng gym quản lý dữ liệu tập trung, giảm thao tác thủ công và cung cấp thông tin kịp thời cho ba nhóm người dùng là quản lý, nhân viên và hội viên. Hệ thống phải bảo đảm rằng mỗi chức năng chỉ được sử dụng bởi vai trò phù hợp và các giao dịch liên quan đến tiền hoặc lượt tập không tạo ra trạng thái dở dang.")
    add_bullets(doc, [
        "Quản lý hồ sơ hội viên, mã hội viên, mã QR, trạng thái hoạt động và thông tin liên hệ.",
        "Quản lý gói tập theo giá, thời hạn, giới hạn lượt, mô tả, điều khoản và trạng thái kinh doanh.",
        "Hỗ trợ bán mới, gia hạn nối tiếp, thanh toán tiền mặt hoặc chuyển khoản, sinh phiếu thu và hủy giao dịch có lý do.",
        "Kiểm soát check in, ngăn quét trùng trong mười phút và trừ lượt trong cùng giao dịch dữ liệu.",
        "Cung cấp số liệu doanh thu, check in, hội viên, chi phí và lợi nhuận phục vụ quyết định vận hành.",
        "Cho phép hội viên tự xem dữ liệu cá nhân và lịch sử sử dụng trong phạm vi của chính mình.",
    ])
    add_para(doc, "Tiêu chí thành công của MVP gồm bốn nhóm. Nhóm chức năng yêu cầu các luồng chính có thể hoàn thành từ giao diện. Nhóm dữ liệu yêu cầu ràng buộc và lịch sử giao dịch được bảo toàn. Nhóm bảo mật yêu cầu phiên đăng nhập, RBAC và RLS hoạt động đồng thời. Nhóm chất lượng yêu cầu kiểm thử tự động, lint và build production đều hoàn thành.")

    new_page(doc, "1.3 Phạm vi và giới hạn", 2)
    add_para(doc, "Phạm vi hiện tại tập trung vào một cơ sở và các giao dịch thanh toán đủ một lần. Nhân viên quản lý hội viên, bán gói và check in; quản lý có thêm quyền cấu hình gói, quản lý nhân viên, hủy thanh toán, đóng băng và xem báo cáo tài chính; hội viên truy cập cổng cá nhân. Các chức năng chăm sóc hội viên và chi phí được đưa vào để phản ánh công việc sau bán hàng và kiểm soát lợi nhuận.")
    add_table(doc, ["Trong phạm vi", "Ngoài phạm vi MVP"], [
        ("Một chi nhánh phòng gym", "Quản lý chuỗi nhiều chi nhánh"),
        ("Thanh toán tiền mặt và chuyển khoản ghi nhận thủ công", "Cổng thanh toán và đối soát ngân hàng tự động"),
        ("QR chứa token ngẫu nhiên", "Thiết bị kiểm soát cửa chuyên dụng"),
        ("Báo cáo vận hành và tài chính cơ bản", "Kho dữ liệu và dự báo nâng cao"),
        ("Thông báo trong dữ liệu hệ thống", "SMS email push đa kênh hoàn chỉnh"),
        ("Tài khoản được mời", "Đăng ký công khai và xác minh danh tính điện tử"),
    ], widths=[3.2, 3.2], font_size=9)
    add_para(doc, "Giới hạn này giữ cho Product Backlog phù hợp với thời lượng môn học. Các hạng mục ngoài phạm vi không bị loại bỏ vĩnh viễn; chúng được lưu như đề xuất cho các release tiếp theo. Cách quản lý phạm vi như vậy phù hợp với tư duy Agile vì nhóm ưu tiên phần tạo giá trị sớm và giữ khả năng phản hồi khi có thêm dữ liệu sử dụng.")

    new_page(doc, "1.4 Phương pháp thực hiện", 2)
    add_para(doc, "Báo cáo kết hợp phương pháp phát triển lặp với kỹ thuật phân tích và kiểm chứng mã nguồn. Yêu cầu được diễn đạt thành user story và tiêu chí chấp nhận. Thiết kế được mô tả qua kiến trúc phân lớp, mô hình dữ liệu, trạng thái nghiệp vụ và luồng tương tác. Việc hiện thực được đánh giá bằng cấu trúc source code, migration SQL và các route đang tồn tại trong project.")
    add_numbered(doc, [
        "Khảo sát bài toán và xác định nhóm người dùng cùng các điểm đau vận hành.",
        "Tạo Product Backlog, ước lượng tương đối và sắp xếp ưu tiên theo giá trị cùng rủi ro.",
        "Chia Increment thành các sprint, xác định Sprint Goal và Definition of Done.",
        "Thiết kế kiến trúc, cơ sở dữ liệu, phân quyền, giao diện và hợp đồng API.",
        "Hiện thực chức năng theo lát cắt dọc để mỗi sprint có luồng chạy được.",
        "Kiểm thử quy tắc nghiệp vụ, kiểm tra tĩnh và build production trước khi đánh giá.",
    ])
    add_para(doc, "Bằng chứng đánh giá tại thời điểm báo cáo gồm 113 tệp TypeScript hoặc TSX với khoảng 12.258 dòng, 20 Route Handler, 6 migration SQL, 16 bảng dữ liệu, 14 hàm cơ sở dữ liệu và 22 chính sách RLS. Các con số chỉ phản ánh kích thước kỹ thuật, không thay thế đánh giá về tính đúng đắn. Vì vậy chương kiểm thử tập trung vào các quy tắc có khả năng gây tổn thất nghiệp vụ.")

    new_page(doc, "1.5 Cấu trúc báo cáo", 2)
    add_para(doc, "Sau chương tổng quan, Chương 2 trình bày cách áp dụng Agile Scrum và tổ chức Product Backlog. Chương 3 phân tích yêu cầu chức năng, phi chức năng, vai trò và các trường hợp sử dụng quan trọng. Chương 4 mô tả kiến trúc, dữ liệu, phân quyền và các quyết định thiết kế. Chương 5 liên hệ thiết kế với mã nguồn, API và giao diện đã triển khai.")
    add_para(doc, "Chương 6 trình bày chiến lược kiểm thử, dữ liệu kiểm thử và kết quả thực thi. Chương 7 đề xuất quy trình triển khai, vận hành, bảo mật và quản trị rủi ro. Chương 8 tổng kết mức độ đáp ứng mục tiêu và lộ trình phát triển tiếp theo. Phần phụ lục cung cấp hướng dẫn cài đặt, đặc tả API rút gọn, bảng truy vết yêu cầu và checklist nghiệm thu.")
    add_para(doc, "Cấu trúc này tạo chuỗi truy vết từ nhu cầu đến bằng chứng. Một yêu cầu không chỉ xuất hiện trong danh sách chức năng mà còn phải liên hệ với thiết kế dữ liệu, điểm kiểm soát quyền, API và ca kiểm thử. Đây là cơ sở để giảng viên hoặc người đánh giá kiểm tra tính nhất quán của sản phẩm.")


def chapter2(doc):
    new_page(doc, "2 Cơ sở phương pháp Agile Scrum", 1)
    doc.add_heading("2.1 Tư tưởng Agile", level=2)
    add_para(doc, "Tuyên ngôn Agile ưu tiên con người và tương tác, phần mềm chạy được, cộng tác với khách hàng và phản hồi trước thay đổi, đồng thời vẫn thừa nhận giá trị của quy trình, tài liệu, hợp đồng và kế hoạch [1]. Đối với GymFlow, tư tưởng này được chuyển thành cách giao hàng theo lát cắt nghiệp vụ. Thay vì hoàn thành toàn bộ cơ sở dữ liệu rồi mới làm giao diện, nhóm xây từng luồng có thể trình diễn như tạo hội viên, bán gói và check in.")
    add_para(doc, "Phần mềm chạy được là thước đo tiến độ quan trọng, nhưng báo cáo môn học vẫn cần tài liệu. Tài liệu ở đây phục vụ quyết định và truy vết: user story nêu giá trị; tiêu chí chấp nhận xác định điều kiện hoàn thành; sơ đồ làm rõ ranh giới; ca kiểm thử cung cấp bằng chứng. Những nội dung không giúp phát triển, kiểm thử hoặc vận hành được giữ ngắn để giảm chi phí bảo trì.")
    add_para(doc, "Khả năng phản hồi thay đổi thể hiện ở việc dùng snapshot dữ liệu gói trong subscription. Nếu tên hoặc giá gói thay đổi, giao dịch cũ vẫn giữ bối cảnh ban đầu. Thiết kế này cho phép phòng gym thay đổi chính sách kinh doanh mà không làm sai lịch sử. Tương tự, trạng thái gói được mở rộng từ active và cancelled thành scheduled, active, frozen, expired và cancelled khi yêu cầu nghiệp vụ trưởng thành.")

    new_page(doc, "2.2 Khung Scrum", 2)
    add_para(doc, "Scrum là một khung làm việc gọn nhẹ để tạo giá trị trong các vấn đề phức tạp. Hướng dẫn Scrum 2020 mô tả một Scrum Team gồm Product Owner, Scrum Master và Developers; các sự kiện gồm Sprint, Sprint Planning, Daily Scrum, Sprint Review và Sprint Retrospective; các tạo tác gồm Product Backlog, Sprint Backlog và Increment [2]. Khung này không quy định chi tiết kỹ thuật, vì vậy nhóm vẫn cần lựa chọn cách phân tích, thiết kế, kiểm thử và quản lý mã nguồn.")
    add_picture(doc, ASSETS / "scrum.png", 6.35, "Hình 2.1 Chu trình Scrum áp dụng cho GymFlow")
    add_para(doc, "Trong đồ án cá nhân, một người có thể thực hiện nhiều trách nhiệm nhưng vẫn cần phân biệt vai trò khi ra quyết định. Khi ưu tiên Product Backlog, người thực hiện đứng ở góc nhìn Product Owner. Khi gỡ trở ngại và cải tiến cách làm, người thực hiện đứng ở góc nhìn Scrum Master. Khi thiết kế, lập trình và kiểm thử, người thực hiện đóng vai Developers. Sự phân biệt này giúp tránh việc đánh đồng mong muốn sản phẩm với giải pháp kỹ thuật.")

    new_page(doc, "2.3 Vai trò và trách nhiệm", 2)
    add_table(doc, ["Vai trò", "Trách nhiệm trong đề tài", "Sản phẩm đầu ra"], [
        ("Product Owner", "Làm rõ giá trị, sắp xếp Product Backlog, chấp nhận Increment", "Product Goal, backlog ưu tiên, tiêu chí chấp nhận"),
        ("Scrum Master", "Duy trì nhịp sprint, nhận diện trở ngại, hướng dẫn cải tiến", "Lịch sự kiện, impediment log, hành động retrospective"),
        ("Developers", "Phân tích, thiết kế, lập trình, migration, kiểm thử và build", "Sprint Backlog, mã nguồn, test, Increment"),
        ("Stakeholder", "Cung cấp quy tắc vận hành và phản hồi khi review", "Phản hồi về quy trình lễ tân, tài chính và hội viên"),
    ], widths=[1.25, 3.1, 2.05], font_size=9)
    caption(doc, "Bảng 2.1 Vai trò và trách nhiệm Scrum")
    add_para(doc, "Product Owner chịu trách nhiệm tối đa hóa giá trị chứ không chỉ ghi yêu cầu. Chẳng hạn, check in QR được ưu tiên trước đặt lịch lớp vì nó tác động trực tiếp đến luồng ra vào hằng ngày. Developers chịu trách nhiệm về chất lượng của Increment, do đó không được coi kiểm thử hoặc migration là công việc phụ sau sprint.")
    add_para(doc, "Scrum Master theo dõi những trở ngại như thiếu môi trường Supabase, quy tắc gia hạn chưa rõ hoặc dữ liệu mẫu không đủ trường hợp biên. Mỗi trở ngại phải có hành động cụ thể: tạo dữ liệu fixture, tách quy tắc thành hàm thuần để kiểm thử hoặc đưa quyết định chưa rõ trở lại Product Backlog refinement.")

    new_page(doc, "2.4 Product Goal và Definition of Done", 2)
    add_para(doc, "Product Goal của GymFlow là cung cấp một hệ thống web thống nhất để một chi nhánh quản lý hội viên, gói tập, thanh toán và check in, đồng thời cho phép quản lý theo dõi tình hình kinh doanh và hội viên tự xem dữ liệu của mình. Goal này đủ ổn định để định hướng nhiều sprint nhưng không khóa cứng cách hiện thực.")
    add_para(doc, "Definition of Done được áp dụng cho từng Product Backlog Item trước khi đưa vào Increment. Một hạng mục chỉ được xem là hoàn thành khi mã nguồn đã tích hợp, đầu vào được xác thực, quyền truy cập được kiểm tra, thay đổi cơ sở dữ liệu có migration, tình huống lỗi chính có thông báo, ca kiểm thử liên quan đạt, lint không có lỗi và build production thành công.")
    add_bullets(doc, [
        "Chức năng đáp ứng tiêu chí chấp nhận và có thể trình diễn từ giao diện hoặc API.",
        "Không để service role key hoặc dữ liệu nhạy cảm trong mã phía trình duyệt.",
        "Giao dịch nhiều bước phải nguyên tử hoặc có cơ chế bù trừ rõ ràng.",
        "Các thay đổi quan trọng tạo audit log để truy vết người thực hiện và đối tượng.",
        "Tên, trạng thái, lỗi và nội dung giao diện được dùng nhất quán bằng tiếng Việt.",
        "Tài liệu README hoặc báo cáo được cập nhật nếu cách cài đặt hay hành vi thay đổi.",
    ])

    new_page(doc, "2.5 Kế hoạch sprint", 2)
    add_table(doc, ["Sprint", "Sprint Goal", "Phạm vi chính", "Increment"], [
        ("Sprint 1", "Thiết lập nền tảng", "Next.js, Supabase, schema lõi, đăng nhập, vai trò", "Người dùng đăng nhập và được điều hướng theo vai trò"),
        ("Sprint 2", "Quản lý hội viên và gói", "CRUD hội viên, mã QR, gói tập, tìm kiếm", "Nhân viên quản lý dữ liệu chủ"),
        ("Sprint 3", "Bán gói và tài chính đầu vào", "Subscription, gia hạn, thanh toán, phiếu thu", "Luồng bán hàng chạy xuyên suốt"),
        ("Sprint 4", "Kiểm soát sử dụng", "Check in, chống trùng, trừ lượt, đóng băng", "Lễ tân xử lý lượt vào an toàn"),
        ("Sprint 5", "Tự phục vụ và báo cáo", "Portal, dashboard, CSV, báo cáo", "Hội viên và quản lý có góc nhìn riêng"),
        ("Sprint 6", "Hoàn thiện vận hành", "Follow up, chi phí, bảo mật, test, build", "MVP sẵn sàng nghiệm thu"),
    ], widths=[.7, 1.55, 2.25, 1.9], font_size=8.5)
    caption(doc, "Bảng 2.2 Kế hoạch sprint")
    add_para(doc, "Mỗi sprint được đề xuất trong khoảng một đến hai tuần tùy thời lượng học phần. Sprint Review dùng dữ liệu mẫu để trình diễn luồng nghiệp vụ hoàn chỉnh. Sprint Retrospective tập trung vào một hoặc hai cải tiến có thể thực hiện ngay, ví dụ chuẩn hóa hàm xử lý lỗi, tách logic tài chính thành hàm thuần hoặc bổ sung migration thay vì sửa trực tiếp cơ sở dữ liệu.")

    new_page(doc, "2.6 Quản lý và ước lượng backlog", 2)
    add_para(doc, "Product Backlog được sắp xếp theo bốn yếu tố: tần suất sử dụng, ảnh hưởng tài chính, rủi ro dữ liệu và phụ thuộc kỹ thuật. Check in và bán gói có độ ưu tiên cao vì diễn ra thường xuyên và tác động trực tiếp đến doanh thu hoặc quyền sử dụng. Báo cáo nâng cao có thể thực hiện sau khi dữ liệu giao dịch đã ổn định.")
    add_para(doc, "Ước lượng dùng story point theo dãy Fibonacci 1, 2, 3, 5, 8 và 13. Điểm không quy đổi trực tiếp thành giờ; nó phản ánh độ phức tạp, lượng chưa biết và công sức kiểm thử tương đối. User story có điểm 13 phải được xem xét tách nhỏ để giảm rủi ro. Ví dụ quản lý đăng ký gói được tách thành bán mới, gia hạn, đóng băng và hủy thanh toán.")
    add_para(doc, "Backlog refinement diễn ra giữa sprint để làm rõ tiêu chí chấp nhận, xác định phụ thuộc và chuẩn bị dữ liệu kiểm thử. Một story được coi là sẵn sàng khi nêu rõ người dùng, giá trị, điều kiện đầu vào, kết quả mong đợi, trường hợp lỗi chính và những bảng hoặc API bị ảnh hưởng. Quy tắc này giảm việc bắt đầu một hạng mục khi câu hỏi nghiệp vụ cơ bản vẫn chưa có câu trả lời.")

    new_page(doc, "2.7 Theo dõi tiến độ và cải tiến", 2)
    add_para(doc, "Sprint Backlog nên được theo dõi trên bảng To do, In progress, Review và Done. Giới hạn công việc đang làm giúp người thực hiện hoàn tất một lát cắt trước khi mở thêm việc. Với đồ án cá nhân, bảng công việc vẫn có giá trị vì nó làm lộ các hạng mục bị mắc ở khâu kiểm thử hoặc dữ liệu thay vì tạo cảm giác tiến độ từ số lượng tệp đã sửa.")
    add_para(doc, "Các chỉ số phù hợp gồm số story hoàn thành theo DoD, số lỗi phát hiện sau review, thời gian từ bắt đầu đến Done, số lần build thất bại và tỷ lệ ca kiểm thử đạt. Velocity chỉ dùng để dự báo cho chính nhóm, không dùng làm chỉ tiêu so sánh. Khi phạm vi thay đổi, Product Owner điều chỉnh backlog và Sprint Goal thay vì buộc nhóm hoàn thành mọi việc đã hình dung từ đầu.")
    add_para(doc, "Retrospective của GymFlow tập trung vào chất lượng dòng chảy. Một cải tiến điển hình là đưa nghiệp vụ check in từ thao tác rời rạc ở API xuống hàm PostgreSQL có khóa bản ghi. Thay đổi này giảm nguy cơ hai request đồng thời cùng trừ lượt. Một cải tiến khác là tách `decideCheckIn` và `calculateFinancialSummary` thành hàm thuần để kiểm thử nhanh mà không phụ thuộc cơ sở dữ liệu.")


def chapter3(doc):
    new_page(doc, "3 Phân tích yêu cầu", 1)
    doc.add_heading("3.1 Các bên liên quan", level=2)
    add_para(doc, "Bên liên quan trực tiếp gồm chủ hoặc quản lý phòng gym, nhân viên lễ tân và hội viên. Quản lý quan tâm đến doanh thu, chi phí, hiệu suất gói, tính đúng của giao dịch và khả năng kiểm soát nhân viên. Lễ tân cần thao tác nhanh trong giờ cao điểm, tìm đúng hội viên và nhận phản hồi rõ khi check in thất bại. Hội viên cần biết gói nào đang có hiệu lực, còn bao nhiêu lượt và lịch sử sử dụng của mình.")
    add_para(doc, "Bên liên quan gián tiếp gồm kế toán, người vận hành hạ tầng và giảng viên đánh giá. Kế toán cần phiếu thu và khả năng truy vết giao dịch bị hủy. Người vận hành cần quy trình cấu hình bí mật, migration và sao lưu. Giảng viên cần thấy mối liên hệ giữa phương pháp phát triển, thiết kế, mã nguồn và bằng chứng kiểm thử.")
    add_table(doc, ["Bên liên quan", "Nhu cầu chính", "Rủi ro cần kiểm soát"], [
        ("Quản lý", "Số liệu tổng hợp, cấu hình, nhân sự", "Giao dịch sai, lộ dữ liệu, mất truy vết"),
        ("Nhân viên", "Tìm kiếm và xử lý nhanh", "Nhầm hội viên, thao tác trùng, quyền quá rộng"),
        ("Hội viên", "Tự xem gói và lịch sử", "Xem dữ liệu người khác, QR lộ thông tin"),
        ("Kế toán", "Đối chiếu thu chi", "Xóa cứng giao dịch, thiếu lý do hủy"),
        ("Vận hành", "Cấu hình và khôi phục", "Lộ khóa bí mật, migration không đồng bộ"),
    ], widths=[1.2, 2.5, 2.7], font_size=9)

    new_page(doc, "3.2 Yêu cầu chức năng", 2)
    add_para(doc, "Yêu cầu chức năng được nhóm theo năng lực nghiệp vụ thay vì theo màn hình. Cách nhóm này giúp tránh việc một màn hình chứa nhiều quy tắc nhưng không có chủ sở hữu rõ ràng. Mỗi nhóm chức năng phải xác định tác nhân, dữ liệu đầu vào, tiền điều kiện, luồng thành công và phản hồi khi thất bại.")
    add_bullets(doc, [
        "Xác thực và tài khoản gồm đăng nhập, đăng xuất, quên mật khẩu, xác nhận email mời và bắt buộc đổi mật khẩu tạm.",
        "Hội viên gồm tạo, tìm kiếm, lọc, cập nhật, đổi trạng thái, mời tài khoản và xuất danh sách.",
        "Gói tập gồm tạo, sửa, bật tắt kinh doanh, giá, thời hạn, lượt, mô tả và điều khoản.",
        "Đăng ký và thanh toán gồm bán mới, gia hạn, ngày bắt đầu, snapshot gói, phiếu thu, hủy giao dịch và đóng băng.",
        "Check in gồm quét QR hoặc nhập mã, kiểm tra điều kiện, chống trùng, ghi lịch sử và trừ lượt.",
        "Báo cáo gồm doanh thu, hội viên, check in, gói bán chạy, chi phí và lợi nhuận.",
        "Cổng hội viên gồm QR, thông tin liên hệ, gói hiện tại và kế tiếp, thanh toán và lịch sử check in.",
        "Chăm sóc và tài chính gồm danh sách sắp hết hạn hoặc hết lượt, phân công liên hệ, ghi chú, chi phí và danh mục chi phí.",
    ])
    add_para(doc, "Các yêu cầu trên được triển khai thông qua 20 Route Handler dưới `app/api`, các trang đăng nhập, quản trị, cổng hội viên và các component giao diện. Quy tắc trọng yếu được lặp lại ở nhiều lớp chỉ khi có mục đích phòng vệ, ví dụ kiểm tra vai trò ở server và chính sách RLS ở database.")

    new_page(doc, "3.3 Product Backlog rút gọn", 2)
    backlog = [
        ("US01", "Là người dùng tôi muốn đăng nhập để truy cập đúng khu vực", "Must", 5),
        ("US02", "Là quản lý tôi muốn tạo tài khoản nhân viên", "Should", 5),
        ("US03", "Là nhân viên tôi muốn tạo và tìm hội viên", "Must", 5),
        ("US04", "Là nhân viên tôi muốn cập nhật trạng thái hội viên", "Must", 3),
        ("US05", "Là quản lý tôi muốn cấu hình gói tập", "Must", 5),
        ("US06", "Là nhân viên tôi muốn bán gói và ghi nhận tiền", "Must", 8),
        ("US07", "Là nhân viên tôi muốn gia hạn nối tiếp", "Must", 5),
        ("US08", "Là quản lý tôi muốn đóng băng gói", "Should", 5),
        ("US09", "Là nhân viên tôi muốn check in bằng QR", "Must", 8),
        ("US10", "Là quản lý tôi muốn hủy thanh toán có lý do", "Must", 5),
        ("US11", "Là quản lý tôi muốn xem dashboard", "Should", 5),
        ("US12", "Là hội viên tôi muốn xem QR và gói của mình", "Should", 5),
        ("US13", "Là nhân viên tôi muốn theo dõi khách sắp hết hạn", "Could", 5),
        ("US14", "Là quản lý tôi muốn ghi nhận chi phí", "Should", 5),
        ("US15", "Là quản lý tôi muốn xuất CSV hội viên", "Could", 3),
    ]
    add_table(doc, ["ID", "User story", "Ưu tiên", "SP"], backlog, widths=[.55, 4.55, .85, .45], font_size=8.5)
    caption(doc, "Bảng 3.1 Product Backlog rút gọn")
    add_para(doc, "Mức Must đại diện cho năng lực thiết yếu để vận hành luồng chính. Should tạo giá trị lớn nhưng có thể dùng phương án thủ công ngắn hạn. Could được thực hiện khi năng lực sprint cho phép. Cách phân loại này hỗ trợ Product Owner bảo vệ Sprint Goal khi xuất hiện yêu cầu mới.")

    new_page(doc, "3.4 Ma trận phân quyền", 2)
    add_table(doc, ["Chức năng", "Manager", "Staff", "Member"], [
        ("Xem dashboard vận hành", "Có", "Có", "Không"),
        ("Quản lý hội viên", "Có", "Có", "Chỉ hồ sơ mình"),
        ("Quản lý gói tập", "Có", "Chỉ xem", "Chỉ xem gói liên quan"),
        ("Bán và gia hạn gói", "Có", "Có", "Không"),
        ("Check in", "Có", "Có", "Không"),
        ("Đóng băng gói", "Có", "Không", "Không"),
        ("Hủy thanh toán", "Có", "Không", "Không"),
        ("Quản lý nhân viên", "Có", "Không", "Không"),
        ("Báo cáo và chi phí", "Có", "Không", "Không"),
        ("Xem portal cá nhân", "Không", "Không", "Có"),
    ], widths=[3.0, 1.1, 1.1, 1.2], font_size=9)
    caption(doc, "Bảng 3.2 Ma trận phân quyền")
    add_para(doc, "Ma trận dùng nguyên tắc quyền tối thiểu. Staff được phép thực hiện nghiệp vụ quầy nhưng không được quản lý nhân viên, hủy thanh toán hoặc xem tài chính tổng hợp. Member chỉ đọc dữ liệu thuộc hồ sơ liên kết với tài khoản và chỉ cập nhật một số trường liên hệ. Manager có quyền cao nhất nhưng vẫn bị chặn tự vô hiệu hóa hoặc hạ quyền nếu đó là quản lý hoạt động cuối cùng.")

    new_page(doc, "3.5 Đặc tả trường hợp sử dụng bán gói", 2)
    add_para(doc, "Tên trường hợp sử dụng là bán mới hoặc gia hạn gói. Tác nhân chính là manager hoặc staff. Tiền điều kiện gồm phiên đăng nhập hợp lệ, tài khoản không bị buộc đổi mật khẩu, hội viên đang hoạt động và gói đang kinh doanh. Đầu vào gồm hội viên, gói, phương thức thanh toán và ngày bắt đầu tùy chọn.")
    add_numbered(doc, [
        "Nhân viên mở hồ sơ hội viên và chọn thao tác bán hoặc gia hạn.",
        "Hệ thống tải danh sách gói đang hoạt động và hiển thị giá, thời hạn, giới hạn lượt.",
        "Nhân viên chọn phương thức thanh toán và xác nhận ngày bắt đầu.",
        "API xác thực đầu vào, phiên và vai trò rồi gọi hàm `sell_membership`.",
        "Cơ sở dữ liệu xác định ngày kết thúc, tạo subscription cùng snapshot và tạo payment.",
        "Hệ thống sinh mã phiếu thu, ghi audit log và trả kết quả cho giao diện.",
    ])
    add_para(doc, "Nếu gia hạn khi gói hiện tại còn hiệu lực, subscription mới có trạng thái scheduled và bắt đầu sau ngày kết thúc gần nhất. Nếu gói hoặc hội viên không hợp lệ, toàn bộ giao dịch bị từ chối. Không được tạo subscription mà thiếu payment hợp lệ trong luồng bán đủ tiền. Kết quả thành công phải hiển thị đủ tên hội viên, tên gói, số tiền và mã phiếu để nhân viên đối chiếu.")

    new_page(doc, "3.6 Đặc tả trường hợp sử dụng check in", 2)
    add_para(doc, "Tên trường hợp sử dụng là ghi nhận lượt vào phòng tập. Tác nhân chính là manager hoặc staff. Hệ thống nhận một token có thể là QR UUID hoặc mã hội viên. Tiền điều kiện là người thực hiện đã đăng nhập và không bị yêu cầu đổi mật khẩu.")
    add_numbered(doc, [
        "Nhân viên quét QR hoặc nhập mã hội viên tại màn hình check in.",
        "API loại bỏ khoảng trắng, kiểm tra token không rỗng và xác thực vai trò.",
        "Hàm cơ sở dữ liệu khóa bản ghi liên quan để tránh hai request cập nhật đồng thời.",
        "Hệ thống kiểm tra trạng thái hội viên, gói, ngày hiệu lực, đóng băng, số lượt và quét trùng.",
        "Nếu hợp lệ, hệ thống ghi check in, trừ một lượt khi cần và ghi audit log.",
        "Giao diện hiển thị thành công hoặc lý do từ chối bằng thông điệp dễ hiểu.",
    ])
    add_para(doc, "Các nhánh lỗi có mã riêng như INVALID QR, MEMBER INACTIVE, NO VALID SUBSCRIPTION, NOT STARTED, FROZEN, EXPIRED, NO VISITS LEFT và DUPLICATE. Việc trả lý do cụ thể giúp lễ tân xử lý đúng thay vì cho rằng mọi lỗi đều do máy quét. Dữ liệu cá nhân không được mã hóa trực tiếp trong QR; token ngẫu nhiên chỉ đóng vai trò khóa tra cứu.")

    new_page(doc, "3.7 Yêu cầu phi chức năng", 2)
    add_table(doc, ["Nhóm", "Yêu cầu", "Cách kiểm chứng"], [
        ("Bảo mật", "Xác thực session, RBAC server, RLS database, giữ bí mật service role", "Kiểm tra route, policy và cấu hình env"),
        ("Toàn vẹn", "Giao dịch bán gói, check in, freeze, cancel phải nguyên tử", "Kiểm tra hàm SQL và tình huống lỗi"),
        ("Hiệu năng", "Tra cứu và dashboard phù hợp quy mô một chi nhánh", "Index, giới hạn bản ghi, build production"),
        ("Khả dụng", "Giao diện tiếng Việt, phản hồi lỗi rõ, dùng được trên mobile", "Review UI và kiểm thử chấp nhận"),
        ("Bảo trì", "TypeScript, module tách biệt, migration có thứ tự", "Lint, test, cấu trúc source"),
        ("Truy vết", "Thao tác quan trọng có actor, entity và thời điểm", "Đối chiếu audit logs"),
        ("Khôi phục", "Có seed, migration và kế hoạch sao lưu", "Diễn tập trên môi trường staging"),
    ], widths=[1.05, 3.25, 2.1], font_size=8.5)
    add_para(doc, "Yêu cầu phi chức năng phải được kiểm tra cùng chức năng. Một API trả đúng dữ liệu nhưng bỏ qua kiểm tra quyền vẫn không đạt. Tương tự, giao diện check in đẹp nhưng hai request đồng thời có thể trừ sai lượt thì Increment chưa đáp ứng Definition of Done.")

    new_page(doc, "3.8 Quy tắc nghiệp vụ", 2)
    add_bullets(doc, [
        "Mỗi hội viên có mã hội viên và QR token duy nhất.",
        "Chỉ hội viên active mới được bán gói hoặc check in.",
        "Gói có giá không âm, thời hạn dương và số lượt dương nếu không phải gói unlimited.",
        "Gia hạn bắt đầu sau gói active hoặc scheduled cuối cùng để tránh chồng thời gian.",
        "Một subscription chỉ có tối đa một payment hợp lệ.",
        "Check in trong vòng mười phút kể từ lần gần nhất bị từ chối là trùng.",
        "Gói theo lượt giảm đúng một lượt sau check in thành công; gói unlimited không thay đổi lượt.",
        "Một subscription chỉ có một kỳ đóng băng active tại một thời điểm.",
        "Hủy payment yêu cầu manager và lý do; dữ liệu được đổi trạng thái thay vì xóa cứng.",
        "Không được vô hiệu hóa quản lý active cuối cùng.",
    ])
    add_para(doc, "Các quy tắc trên được đặt ở lớp phù hợp. Quy tắc định dạng được kiểm tra bằng Zod tại biên API. Quy tắc cần tính nguyên tử hoặc khóa đồng thời được đặt trong PostgreSQL. Ràng buộc duy nhất và check constraint bảo vệ dữ liệu ngay cả khi có một đường ghi mới trong tương lai. Giao diện chỉ hỗ trợ người dùng nhập đúng chứ không được xem là ranh giới bảo mật.")


def chapter4(doc):
    new_page(doc, "4 Phân tích và thiết kế hệ thống", 1)
    doc.add_heading("4.1 Kiến trúc tổng thể", level=2)
    add_para(doc, "GymFlow sử dụng kiến trúc web ba lớp có tăng cường logic nghiệp vụ tại cơ sở dữ liệu. Lớp trình bày gồm trang Next.js và React component. Lớp ứng dụng gồm Route Handler, kiểm tra phiên, vai trò, xác thực Zod và chuyển đổi lỗi. Lớp dữ liệu gồm PostgreSQL, các bảng, ràng buộc, index, RLS, trigger và hàm PL pgSQL.")
    add_picture(doc, ASSETS / "architecture.png", 6.35, "Hình 4.1 Kiến trúc tổng thể của hệ thống")
    add_para(doc, "Thiết kế này phù hợp với phạm vi một ứng dụng web đơn khối có module. Next.js xử lý cả giao diện và API nên giảm chi phí triển khai. Supabase cung cấp Auth và PostgreSQL, trong khi các hàm RPC giữ giao dịch quan trọng gần dữ liệu. Điểm cần kiểm soát là service role bỏ qua RLS; vì vậy khóa này chỉ được khởi tạo trong module server và mọi route sử dụng admin client phải gọi `requireActor` trước khi truy vấn.")

    new_page(doc, "4.2 Thiết kế thành phần", 2)
    add_table(doc, ["Thành phần", "Trách nhiệm", "Tệp đại diện"], [
        ("Trang và layout", "Điều hướng theo phiên và vai trò", "app/page.tsx app/admin app/portal"),
        ("Giao diện quản trị", "Dashboard, hội viên, gói, check in, thanh toán, báo cáo", "components/gym-app.tsx"),
        ("Mô đun vận hành", "Chăm sóc hội viên và chi phí", "components/operations-modules.tsx"),
        ("Cổng hội viên", "QR, gói, thanh toán, check in, liên hệ", "components/member-portal.tsx"),
        ("API", "Xác thực request, phân quyền, điều phối dữ liệu", "app/api/*/route.ts"),
        ("Xác thực", "Đọc session, nạp profile, kiểm tra role", "lib/authz.ts"),
        ("Nghiệp vụ thuần", "Quy tắc check in và tính tài chính", "lib/check-in.ts lib/operations.ts"),
        ("Dữ liệu", "Schema, policy, RPC, seed", "supabase/migrations supabase/seed.sql"),
    ], widths=[1.35, 3.15, 1.9], font_size=8.5)
    add_para(doc, "Ranh giới module dựa trên trách nhiệm thay vì công nghệ đơn thuần. `lib/authz.ts` là điểm dùng chung cho mọi API có bảo vệ. `lib/http.ts` chuẩn hóa cách xử lý kết quả PostgREST. Những quy tắc có thể kiểm thử độc lập được giữ trong hàm thuần, còn nghiệp vụ cần đồng thời dữ liệu được đặt trong RPC.")
    add_para(doc, "Giao diện quản trị hiện tập trung trong component lớn `gym-app.tsx`. Cách này giúp hoàn thành MVP nhanh nhưng làm tăng chi phí thay đổi khi số module tiếp tục mở rộng. Hướng cải tiến là tách theo feature gồm members, plans, subscriptions, checkins, payments và reports, đồng thời giữ kiểu dữ liệu dùng chung trong một lớp domain hoặc generated types từ Supabase.")

    new_page(doc, "4.3 Thiết kế dữ liệu mức khái niệm", 2)
    add_para(doc, "Mô hình dữ liệu đặt member là thực thể nghiệp vụ trung tâm nhưng tách khỏi profile xác thực. Một hội viên có thể tồn tại trước khi được mời tài khoản; khi chấp nhận lời mời, member liên kết với profile. Cách tách này phù hợp quy trình tại quầy, nơi phòng gym có thể đăng ký khách trước khi khách dùng portal.")
    add_table(doc, ["Nhóm dữ liệu", "Bảng", "Quan hệ chính"], [
        ("Danh tính", "profiles members", "Profile có thể liên kết một member"),
        ("Sản phẩm", "membership_plans", "Plan có nhiều subscription"),
        ("Giao dịch", "subscriptions payments subscription_freezes", "Member có nhiều subscription và payment"),
        ("Sử dụng", "check_ins", "Check in thuộc member và subscription"),
        ("Chăm sóc", "member_follow_ups notifications", "Follow up và thông báo theo member"),
        ("Lớp học", "class_types trainers class_sessions class_bookings", "Session thuộc loại lớp và trainer"),
        ("Tài chính", "expense_categories expenses", "Chi phí thuộc danh mục"),
        ("Kiểm soát", "audit_logs", "Lưu actor hành động entity và chi tiết"),
    ], widths=[1.2, 2.8, 2.4], font_size=8.5)
    caption(doc, "Bảng 4.1 Từ điển dữ liệu mức bảng")
    add_para(doc, "Tổng cộng các migration tạo hoặc mở rộng 16 bảng. Nhóm bảng lớp học vẫn tồn tại ở migration lịch sử nhưng chức năng đặt lớp đã được loại khỏi giao diện ở migration sau. Chi tiết này thể hiện nhu cầu quản lý thay đổi schema có kiểm soát: xóa một module sản phẩm không đồng nghĩa được phép xóa ngay dữ liệu lịch sử mà chưa đánh giá tác động.")

    new_page(doc, "4.4 Thiết kế dữ liệu giao dịch", 2)
    add_para(doc, "Subscription lưu khóa plan và đồng thời lưu snapshot tên, giá, thời hạn và số lượt. Nếu quản lý sửa giá gói, báo cáo giao dịch cũ vẫn dùng giá tại thời điểm bán. Trường sale type phân biệt new và renewal; trạng thái scheduled cho phép xếp gói kế tiếp mà không làm mất gói đang dùng.")
    add_para(doc, "Payment tham chiếu subscription và member, có receipt code duy nhất, phương thức, trạng thái, người ghi nhận, thời điểm và thông tin hủy. Unique index có điều kiện bảo đảm một subscription chỉ có một payment valid. Khi hủy, hệ thống cập nhật trạng thái thay vì xóa bản ghi, nhờ vậy tổng doanh thu có thể loại giao dịch hủy nhưng vẫn giữ bằng chứng kiểm toán.")
    add_para(doc, "Check in tham chiếu đúng subscription đã sử dụng. Với gói theo lượt, cập nhật remaining visits nằm trong cùng hàm với insert check in. Việc khóa bản ghi bằng `FOR UPDATE` ngăn hai request đồng thời cùng đọc một số lượt và ghi kết quả mâu thuẫn. Index theo member và thời gian hỗ trợ truy vấn lần gần nhất để phát hiện quét trùng.")
    add_para(doc, "Audit log dùng cấu trúc chung actor, action, entity type, entity id, details và created at. Trường JSONB details giữ dữ liệu phụ theo từng hành động mà không phải thay đổi schema cho mọi loại sự kiện. Tuy nhiên không nên đưa mật khẩu, token phiên hoặc khóa bí mật vào details.")

    new_page(doc, "4.5 Thiết kế luồng check in", 2)
    add_picture(doc, ASSETS / "checkin.png", 6.35, "Hình 4.2 Luồng xử lý check in")
    add_para(doc, "Luồng check in được thiết kế theo nguyên tắc fail fast và giao dịch nguyên tử. Các kiểm tra rẻ và rõ ràng được thực hiện trước; chỉ khi mọi điều kiện đạt, hệ thống mới ghi dữ liệu. Thứ tự kiểm tra còn giúp trả về lý do hữu ích. Ví dụ một hội viên inactive bị từ chối trước khi hệ thống tìm gói.")
    add_para(doc, "Bài toán đồng thời được giải quyết ở database thay vì phụ thuộc trạng thái giao diện. Nếu hai thiết bị gửi cùng token gần như đồng thời, khóa bản ghi và kiểm tra lần check in gần nhất khiến chỉ một giao dịch có thể hoàn tất. Cơ chế mười phút chống quét trùng là quy tắc nghiệp vụ có thể cấu hình trong tương lai, nhưng ở MVP nó được mã hóa thống nhất trong logic và test.")

    new_page(doc, "4.6 Thiết kế vòng đời gói", 2)
    add_picture(doc, ASSETS / "subscription.png", 6.35, "Hình 4.3 Vòng đời đăng ký gói tập")
    add_para(doc, "Trạng thái scheduled được dùng cho gia hạn có ngày bắt đầu trong tương lai. Khi đến ngày bắt đầu, gói có thể được coi là active trong truy vấn hoặc được cập nhật bởi tác vụ định kỳ. Frozen biểu thị quyền sử dụng tạm dừng. Khi mở lại, ngày kết thúc được kéo dài theo số ngày đóng băng thực tế để bảo toàn quyền lợi.")
    add_para(doc, "Expired là trạng thái kết thúc tự nhiên khi qua ngày end date, còn cancelled là quyết định hành chính hoặc hệ quả của hủy giao dịch. Hai trạng thái phải được phân biệt vì báo cáo giữ chân và hoàn tiền có cách xử lý khác nhau. Chuyển trạng thái cần ghi audit log; không cho phép cập nhật tùy ý từ giao diện nếu không có nghiệp vụ tương ứng.")

    new_page(doc, "4.7 Thiết kế xác thực và phân quyền", 2)
    add_para(doc, "Supabase Auth quản lý người dùng và phiên. Bảng profiles mở rộng thông tin nghiệp vụ gồm role, status, username và cờ must change password. Hàm `currentActor` đọc người dùng từ session, sau đó tra profile bằng admin client và chỉ trả actor khi profile active. `requireActor` tiếp tục kiểm tra cờ đổi mật khẩu và danh sách role được phép.")
    add_para(doc, "RLS tạo lớp bảo vệ thứ hai. Staff được đọc các bảng phục vụ quầy; member chỉ đọc dữ liệu có member id liên kết profile của chính mình; audit log chỉ cho manager. Tài liệu Supabase khuyến nghị bật RLS trên bảng được phơi bày và giữ service role ở backend vì khóa này có thể bỏ qua RLS [5][6]. GymFlow tuân theo nguyên tắc đó ở kiến trúc server API.")
    add_para(doc, "Tài khoản nhân viên được tạo từ username và email nội bộ, nhận mật khẩu tạm `admin123`, sau đó bắt buộc đổi mật khẩu. API đổi mật khẩu yêu cầu tối thiểu tám ký tự và từ chối dùng lại mật khẩu tạm. Quản lý không thể tự hạ quyền hoặc tự vô hiệu hóa, đồng thời hệ thống bảo vệ quản lý active cuối cùng để tránh mất khả năng quản trị.")

    new_page(doc, "4.8 Thiết kế API và xử lý lỗi", 2)
    add_para(doc, "Route Handler của Next.js được dùng như lớp ứng dụng. Mỗi route thực hiện chuỗi trách nhiệm gồm xác thực, parse request, kiểm tra role, gọi database và ánh xạ kết quả thành HTTP response. App Router và Route Handler cho phép đặt UI và endpoint trong cùng cấu trúc project [3], phù hợp với một nhóm nhỏ và MVP.")
    add_para(doc, "Zod kiểm tra dữ liệu không tin cậy tại biên. Các schema xác định độ dài tên, định dạng email, số dương, enum phương thức thanh toán và UUID. `safeParse` trả kết quả có thể phân nhánh mà không cần bắt ngoại lệ; cách dùng này phù hợp hướng dẫn Zod [8]. Sau validation, API chuyển tên trường camelCase sang snake case của database.")
    add_para(doc, "Hàm `apiError` chuẩn hóa một số lỗi thành mã trạng thái 401, 403, 409, 503 hoặc 500. Các lỗi nghiệp vụ dự kiến như DUPLICATE hoặc NO VALID SUBSCRIPTION thường được RPC trả trong JSON với cờ ok và API trả 409. Hướng cải tiến là xây danh mục error code tập trung để UI, API và test không lệch thông điệp.")

    new_page(doc, "4.9 Thiết kế giao diện", 2)
    add_para(doc, "Giao diện quản trị dùng thanh điều hướng theo module, phần tiêu đề trang, thẻ chỉ số, bảng dữ liệu và hộp thoại thao tác. Dashboard ưu tiên số liệu cần đọc nhanh như doanh thu, số hội viên, lượt check in và gói bán nhiều. Màn hình check in dành diện tích lớn cho ô quét và phản hồi thành công hoặc thất bại để phù hợp thao tác tại quầy.")
    add_para(doc, "Cổng hội viên tách khỏi khu vực quản trị. Hội viên thấy mã QR của mình, thông tin liên hệ, gói đang dùng, gói kế tiếp, lịch sử thanh toán và check in. Việc tách trải nghiệm giảm nguy cơ hiển thị nhầm chức năng quản trị và làm cho giao diện trên điện thoại gọn hơn.")
    add_para(doc, "Các nguyên tắc khả dụng gồm dùng nhãn tiếng Việt rõ ràng, xác nhận thao tác có hậu quả, không dùng màu làm tín hiệu duy nhất, giữ target bấm đủ lớn và hiển thị trạng thái tải. Dữ liệu rỗng cần có thông điệp hướng dẫn thay vì bảng trắng. Khi lỗi xảy ra, thông báo phải nêu điều gì không hợp lệ và bước khắc phục phù hợp.")

    new_page(doc, "4.10 Quyết định thiết kế và đánh đổi", 2)
    add_table(doc, ["Quyết định", "Lợi ích", "Đánh đổi"], [
        ("Next.js full stack", "Một project cho UI và API, triển khai đơn giản", "Component có thể lớn nếu không tách feature"),
        ("Supabase", "Auth và PostgreSQL tích hợp nhanh", "Phụ thuộc dịch vụ và cần hiểu RLS"),
        ("RPC cho giao dịch", "Nguyên tử, khóa đồng thời gần dữ liệu", "Logic chia giữa TypeScript và SQL"),
        ("Service role ở server", "Điều phối truy vấn linh hoạt", "Mọi route phải kiểm tra quyền chặt"),
        ("Snapshot gói", "Lịch sử ổn định", "Dữ liệu lặp có chủ đích"),
        ("Soft state thay xóa", "Truy vết và đối chiếu", "Câu truy vấn phải lọc trạng thái"),
    ], widths=[1.8, 2.5, 2.1], font_size=8.5)
    add_para(doc, "Các đánh đổi được chấp nhận trong phạm vi MVP nhưng phải được theo dõi. Khi hệ thống tăng tải hoặc mở rộng đa chi nhánh, có thể cần tách read model cho báo cáo, hàng đợi cho thông báo và policy theo branch id. Việc mở rộng không nên phá hợp đồng hiện tại mà cần migration, thử nghiệm hồi quy và kế hoạch chuyển dữ liệu.")


def chapter5(doc):
    new_page(doc, "5 Hiện thực hệ thống", 1)
    doc.add_heading("5.1 Môi trường và công nghệ", level=2)
    add_para(doc, "Project sử dụng Next.js 16.3.4, React 19.2.6, TypeScript 5.9.3 và Node.js từ phiên bản 22.13.0. Tailwind CSS và hệ component hỗ trợ xây giao diện. Supabase JavaScript cùng gói SSR cung cấp client cho browser và server. PostgreSQL lưu dữ liệu và thực thi hàm nghiệp vụ. Zod 4 xác thực đầu vào, Vitest 5 chạy unit test, oxlint kiểm tra chất lượng tĩnh và Next build tạo gói production.")
    add_para(doc, "TypeScript giúp phát hiện sai lệch kiểu trước khi chạy, đặc biệt hữu ích khi dữ liệu API có nhiều trạng thái [4]. Tuy vậy, kiểu tĩnh không xác thực dữ liệu từ HTTP, nên Zod được dùng tại biên. Sự kết hợp này tạo hai lớp: TypeScript hỗ trợ lập trình viên trong quá trình phát triển, còn Zod bảo vệ ứng dụng trước dữ liệu runtime không hợp lệ.")
    add_table(doc, ["Công nghệ", "Phiên bản trong project", "Vai trò"], [
        ("Next.js", "16.3.4", "Framework web và Route Handler"),
        ("React", "19.2.6", "Giao diện thành phần"),
        ("TypeScript", "5.9.3", "Kiểm tra kiểu tĩnh"),
        ("Supabase JS", "2.116.0", "Auth và truy cập dữ liệu"),
        ("Zod", "4.6.1", "Validation request"),
        ("Vitest", "5.0.0", "Kiểm thử tự động"),
        ("Tailwind CSS", "4.2.1", "Thiết kế giao diện"),
    ], widths=[1.45, 1.45, 3.5], font_size=9)

    new_page(doc, "5.2 Cấu trúc mã nguồn", 2)
    add_para(doc, "Thư mục `app` chứa page, layout, route xác thực và Route Handler. `components` chứa ứng dụng quản trị, cổng hội viên, module vận hành và các component giao diện tái sử dụng. `lib` chứa xác thực, Supabase client, HTTP helper, validation và logic nghiệp vụ có thể kiểm thử. `supabase/migrations` chứa lịch sử schema, còn `supabase/seed.sql` tạo dữ liệu trình diễn có UUID cố định.")
    add_table(doc, ["Đường dẫn", "Nội dung", "Nguyên tắc thay đổi"], [
        ("app/api", "Endpoint nghiệp vụ", "Mỗi route phải xác thực và validate"),
        ("components", "UI theo vai trò", "Không chứa service role hoặc bí mật"),
        ("lib/supabase", "Client browser server admin", "Tách rõ phạm vi chạy"),
        ("lib/*.test.ts", "Unit test logic", "Không phụ thuộc dữ liệu production"),
        ("supabase/migrations", "DDL policy RPC", "Chỉ thêm migration có thứ tự"),
        ("supabase/seed.sql", "Dữ liệu demo", "Chạy lại an toàn không xóa dữ liệu thật"),
    ], widths=[1.7, 2.35, 2.35], font_size=9)
    add_para(doc, "Mã nguồn hiện có 113 tệp TypeScript và TSX, khoảng 12.258 dòng. `gym-app.tsx` chứa nhiều màn hình và là ứng viên cần tách khi phát triển tiếp. Việc tách nên theo chức năng và giữ giao diện API ổn định để tránh một đợt refactor lớn khó kiểm thử.")

    new_page(doc, "5.3 Hiện thực xác thực", 2)
    add_para(doc, "Trang gốc đọc actor rồi điều hướng manager và staff tới khu vực admin, member tới portal, còn người chưa đăng nhập tới login. Route callback xử lý phiên sau xác thực. Route confirm xác minh token hash cho luồng mời và khôi phục mật khẩu trước khi mở trang đặt mật khẩu mới.")
    add_para(doc, "Ở server, `currentActor` gọi Supabase Auth để lấy user, sau đó tra bảng profiles theo auth user id. Profile inactive bị coi là không hợp lệ. `requireActor` nhận danh sách vai trò được phép, từ chối tài khoản chưa xác thực, sai vai trò hoặc đang bắt buộc đổi mật khẩu. Mọi API nghiệp vụ dùng hàm này trước khi tạo admin client cho truy vấn có đặc quyền.")
    add_para(doc, "Nhân viên được tạo bằng username. Hệ thống tạo email nội bộ dạng username tại miền dành cho staff, tạo profile trước rồi gọi API quản trị để tạo Auth user. Nếu bước tạo Auth user thất bại, profile vừa tạo được xóa để bù trừ. Đây là một ví dụ cần transaction phân tán; do Auth và database không cùng giao dịch PostgreSQL, ứng dụng sử dụng thao tác bù và audit log.")

    new_page(doc, "5.4 Hiện thực quản lý hội viên", 2)
    add_para(doc, "API hội viên hỗ trợ GET với tìm kiếm và lọc trạng thái, POST để tạo, PATCH theo id để cập nhật và endpoint invite để mời tài khoản. Khi tạo, schema yêu cầu họ tên tối thiểu hai ký tự, số điện thoại tối thiểu tám ký tự và kiểm tra định dạng email hoặc URL ảnh nếu có. API tra trùng số điện thoại và email trước khi insert.")
    add_para(doc, "Mã hội viên được sinh theo quy ước của ứng dụng và QR token dùng UUID ngẫu nhiên. QR không chứa tên, số điện thoại hay thông tin gói. Khi nhân viên cập nhật hồ sơ, API chỉ ánh xạ những trường thực sự xuất hiện trong request và ghi changes vào audit log. Việc chuyển status sang inactive không xóa lịch sử thanh toán và check in.")
    add_para(doc, "Báo cáo hội viên có endpoint riêng để xuất dữ liệu. Khi xuất CSV hoặc bảng tính, hệ thống cần tránh đưa trường nhạy cảm không cần thiết. Một cải tiến tiếp theo là cho phép chọn cột, ghi người xuất và áp dụng thời hạn lưu tệp tạm.")

    new_page(doc, "5.5 Hiện thực gói tập và đăng ký", 2)
    add_para(doc, "Gói tập có tên, giá, số ngày, giới hạn lượt tùy chọn, mô tả, điều khoản và cờ active. Manager tạo hoặc sửa gói; staff chỉ dùng danh sách gói active khi bán. Việc ngừng kinh doanh không xóa gói vì subscription lịch sử vẫn tham chiếu.")
    add_para(doc, "API subscription nhận member id, plan id, method và start date, sau đó gọi RPC `sell_membership`. Hàm đọc plan đang active, kiểm tra member, xác định ngày bắt đầu và kết thúc, tạo snapshot, subscription, payment, receipt code và audit log. Nếu có gói đang hoạt động hoặc chờ hiệu lực, luồng gia hạn xác định ngày nối tiếp thay vì hủy gói hiện tại.")
    add_para(doc, "Đóng băng dùng RPC riêng và chỉ manager được gọi. Hàm kiểm tra khoảng ngày, trạng thái gói và kỳ freeze đang tồn tại. Khi mở lại, hệ thống tính thời gian thực tế và dời end date. Việc đặt quy tắc này ở database bảo đảm giao diện và API khác trong tương lai không thể tạo hai freeze active cho cùng subscription.")

    new_page(doc, "5.6 Hiện thực thanh toán", 2)
    add_para(doc, "Payment được tạo cùng lúc với subscription trong luồng bán gói. Mã phiếu thu giúp nhân viên đối chiếu. Danh sách thanh toán có thể lọc theo status và method. Doanh thu chỉ cộng những bản ghi valid; giao dịch cancelled được giữ lại nhưng loại khỏi tổng.")
    add_para(doc, "Hủy thanh toán là thao tác đặc quyền của manager và yêu cầu lý do tối thiểu ba ký tự. RPC `cancel_payment` khóa payment, kiểm tra trạng thái, cập nhật cancelled at, cancelled by, cancelled reason và xử lý subscription liên quan theo quy tắc. Audit log ghi hành động để phục vụ kiểm tra sau này.")
    add_para(doc, "MVP giả định thanh toán đủ một lần bằng tiền mặt hoặc chuyển khoản. Nếu bổ sung trả góp hoặc cổng thanh toán, quan hệ một payment valid cho mỗi subscription phải được thiết kế lại thành nhiều payment hoặc invoice và allocation. Thay đổi đó ảnh hưởng báo cáo, hoàn tiền, webhook và đối soát nên cần một Epic riêng.")

    new_page(doc, "5.7 Hiện thực check in", 2)
    add_para(doc, "Màn hình check in hỗ trợ máy quét camera qua thư viện HTML5 QR code và ô nhập mã thủ công. Khi nhận token, client gửi POST tới `/api/check-ins`. API xác thực manager hoặc staff, loại bỏ khoảng trắng, từ chối token rỗng rồi gọi RPC.")
    add_para(doc, "RPC tra member theo QR token hoặc member code không phân biệt hoa thường. Sau đó hàm kiểm tra member active, subscription có hiệu lực, ngày, trạng thái freeze, lượt còn lại và lần check in gần nhất. Với gói có giới hạn, remaining visits giảm một. Insert check in, cập nhật lượt và audit log nằm trong cùng transaction.")
    add_para(doc, "Logic tương đương được mô hình hóa trong hàm TypeScript `decideCheckIn` để unit test các nhánh mà không cần kết nối database. Hàm trả union type gồm thành công với cờ decrement visit hoặc thất bại với reason xác định. Cách này tăng tốc vòng phản hồi, nhưng test tích hợp database vẫn cần bổ sung để chứng minh RPC và ràng buộc SQL đúng.")

    new_page(doc, "5.8 Hiện thực dashboard và báo cáo", 2)
    add_para(doc, "Endpoint bootstrap tải song song hội viên, gói, thanh toán trong tháng và check in gần đây. Giao diện tính các chỉ số và biểu đồ bảy ngày từ dữ liệu trả về. Truy vấn giới hạn 500 payment và 1.000 check in để tránh tải không giới hạn trong MVP.")
    add_para(doc, "Dashboard hiển thị xu hướng doanh thu, check in và gói được mua nhiều nhất. Báo cáo hội viên cho phép xuất dữ liệu phục vụ xử lý bên ngoài. Module chi phí tải expense, category và payment theo khoảng ngày rồi dùng `calculateFinancialSummary` để tính doanh thu, chi phí và lợi nhuận; các bản ghi cancelled bị loại.")
    add_para(doc, "Cách tính ở client phù hợp quy mô nhỏ, nhưng khi dữ liệu tăng cần chuyển phép tổng hợp về database hoặc materialized view. API cũng nên nhận khoảng ngày, timezone và phân trang rõ ràng. Việc chốt timezone Asia Ho Chi Minh là cần thiết vì doanh thu theo ngày và check in phụ thuộc ranh giới lịch địa phương.")

    new_page(doc, "5.9 Hiện thực cổng hội viên", 2)
    add_para(doc, "Endpoint portal chỉ chấp nhận role member và tra member có profile id bằng actor hiện tại. Truy vấn nạp subscription, freeze, payment và check in của đúng hội viên. PATCH portal chỉ cho sửa điện thoại, địa chỉ, liên hệ khẩn cấp và avatar; hội viên không thể tự đổi mã, trạng thái hoặc quyền.")
    add_para(doc, "Giao diện hiển thị QR, thông tin liên hệ, gói đang dùng, gói kế tiếp và lịch sử. Việc cho hội viên tự kiểm tra giảm số câu hỏi tại quầy và giúp phát hiện sai lệch sớm. Tuy nhiên QR nên được xem là thông tin xác thực mức thấp; ảnh chụp QR có thể được chia sẻ, vì vậy check in giá trị cao có thể cần xác minh bổ sung.")
    add_para(doc, "RLS bảo vệ dữ liệu ngay cả khi truy vấn trực tiếp bằng client authenticated. Chính sách member dùng profile id hiện tại để giới hạn rows. Khi thêm dữ liệu mới cho portal, nhà phát triển phải cập nhật cả truy vấn, chính sách và test quyền; chỉ thêm component hiển thị là chưa đủ.")

    new_page(doc, "5.10 Hiện thực chăm sóc và chi phí", 2)
    add_para(doc, "Module chăm sóc chọn ứng viên có gói sắp hết hạn trong cửa sổ cảnh báo hoặc còn không quá ba lượt. Nhân viên có thể tạo lịch follow up, phân công, ghi chú, thời điểm liên hệ tiếp theo và cập nhật trạng thái. Mọi thay đổi quan trọng được ghi audit log.")
    add_para(doc, "Module chi phí chỉ dành cho manager. Chi phí có danh mục, mô tả, số tiền, ngày, số hóa đơn, cờ lặp và trạng thái. Hủy chi phí đổi trạng thái thay vì xóa. Tổng lợi nhuận bằng payment valid trừ expense valid trong khoảng thời gian đã chọn.")
    add_para(doc, "Hai module này cho thấy Increment được mở rộng từ vận hành quầy sang quản trị quan hệ và tài chính. Chúng cũng đặt ra yêu cầu dữ liệu dài hạn. Follow up cần chính sách lưu trữ ghi chú phù hợp, còn chứng từ chi phí có thể cần file đính kèm và quy trình phê duyệt ở phiên bản sau.")

    new_page(doc, "5.11 Danh mục API", 2)
    rows = [
        ("GET", "/api/bootstrap", "manager staff", "Dữ liệu dashboard"),
        ("GET POST", "/api/members", "manager staff", "Danh sách và tạo hội viên"),
        ("PATCH", "/api/members id", "manager staff", "Cập nhật hội viên"),
        ("POST", "/api/members id invite", "manager staff", "Mời tài khoản"),
        ("GET POST", "/api/plans", "manager staff", "Danh sách và tạo gói"),
        ("PATCH", "/api/plans id", "manager", "Sửa gói"),
        ("POST", "/api/subscriptions", "manager staff", "Bán hoặc gia hạn"),
        ("POST DELETE", "/api/subscriptions id freeze", "manager", "Đóng băng hoặc mở lại"),
        ("GET POST", "/api/check-ins", "manager staff", "Lịch sử và check in"),
        ("GET", "/api/payments", "manager staff", "Danh sách thanh toán"),
        ("POST", "/api/payments id cancel", "manager", "Hủy thanh toán"),
        ("GET PATCH", "/api/portal", "member", "Dữ liệu và cập nhật portal"),
        ("GET POST", "/api/follow-ups", "manager staff", "Chăm sóc hội viên"),
        ("GET POST", "/api/expenses", "manager", "Chi phí và tài chính"),
        ("GET POST", "/api/staff", "manager", "Quản lý nhân viên"),
    ]
    add_table(doc, ["Phương thức", "Endpoint", "Vai trò", "Mục đích"], rows, widths=[.9, 2.35, 1.15, 2.0], font_size=7.8)
    caption(doc, "Bảng 5.1 Danh mục API chính")


def chapter6(doc):
    new_page(doc, "6 Kiểm thử và đánh giá", 1)
    doc.add_heading("6.1 Chiến lược kiểm thử", level=2)
    add_para(doc, "Chiến lược kiểm thử ưu tiên quy tắc có ảnh hưởng trực tiếp đến quyền sử dụng và số liệu tài chính. Unit test kiểm tra hàm thuần nhanh và cô lập. Kiểm thử API cần xác minh validation, mã trạng thái và phân quyền. Kiểm thử tích hợp database cần xác minh transaction, khóa đồng thời, constraint và RLS. Kiểm thử chấp nhận đi theo user story từ giao diện.")
    add_para(doc, "Kim tự tháp kiểm thử được áp dụng theo hướng có nhiều test đơn vị, số lượng vừa phải test tích hợp và một số ít luồng end to end quan trọng. Với project hiện tại, bằng chứng tự động tập trung ở unit test, lint và build. Đây là nền tảng tốt nhưng chưa thay thế test tích hợp Supabase và test trình duyệt.")
    add_bullets(doc, [
        "Unit test cho check in, nhận diện khách cần chăm sóc, tính doanh thu chi phí và validation UUID.",
        "API test cho unauthenticated, forbidden, invalid input, conflict và success.",
        "Database test cho bán gói, gia hạn, freeze, unfreeze, cancel payment và đồng thời check in.",
        "RLS test cho manager, staff, member và anon trên từng bảng được phơi bày.",
        "End to end test cho đăng nhập, tạo hội viên, bán gói, check in và xem portal.",
    ])

    new_page(doc, "6.2 Kiểm thử logic check in", 2)
    add_table(doc, ["Mã", "Điều kiện", "Kết quả mong đợi"], [
        ("CI01", "Hội viên active gói active còn 5 lượt", "Cho phép và trừ một lượt"),
        ("CI02", "Gói unlimited", "Cho phép và không trừ lượt"),
        ("CI03", "Hội viên inactive", "MEMBER INACTIVE"),
        ("CI04", "Không có gói active", "NO ACTIVE SUBSCRIPTION"),
        ("CI05", "Ngày bắt đầu trong tương lai", "NOT STARTED"),
        ("CI06", "Gói đang frozen", "FROZEN"),
        ("CI07", "Đã qua ngày kết thúc", "EXPIRED"),
        ("CI08", "Remaining visits bằng 0", "NO VISITS LEFT"),
        ("CI09", "Lần gần nhất cách 5 phút", "DUPLICATE"),
    ], widths=[.65, 3.25, 2.5], font_size=8.5)
    add_para(doc, "Các trường hợp trên được kiểm thử với thời điểm cố định để tránh phụ thuộc đồng hồ máy chạy test. Cách truyền `now` vào hàm giúp test tái lập. Gói theo lượt và unlimited được tách thành hai nhánh vì cùng là check in thành công nhưng khác hiệu ứng dữ liệu.")
    add_para(doc, "Khoảng trống còn lại là kiểm thử hai request đồng thời tại PostgreSQL. Unit test không thể chứng minh `FOR UPDATE` hoạt động. Một integration test cần mở hai transaction hoặc gửi hai RPC song song với cùng token, sau đó xác nhận chỉ có một check in và số lượt chỉ giảm một.")

    new_page(doc, "6.3 Kiểm thử chăm sóc và tài chính", 2)
    add_para(doc, "Hàm `isRetentionCandidate` nhận ngày giới hạn và xác định subscription cần chăm sóc nếu end date nằm trong cửa sổ hoặc remaining visits không quá ba. Test bao phủ gói sắp hết hạn, gói ít lượt và gói còn khỏe. Việc truyền ngày giới hạn từ ngoài giúp logic không phụ thuộc múi giờ runtime.")
    add_para(doc, "Hàm `calculateFinancialSummary` cộng payment valid, cộng expense valid rồi tính profit. Test đưa cả bản ghi cancelled và xác nhận chúng không tham gia tổng. Trường hợp chuẩn cho kết quả doanh thu 1.000.000 đồng, chi phí 250.000 đồng và lợi nhuận 750.000 đồng.")
    add_para(doc, "Các test tiếp theo nên bao phủ số âm bị chặn ở API hoặc database, giá trị numeric trả về dạng chuỗi, khoảng ngày rỗng, dữ liệu lớn và timezone tại ranh giới ngày. Báo cáo tài chính phải thống nhất giữa dashboard, file xuất và truy vấn đối chiếu.")

    new_page(doc, "6.4 Kiểm thử validation và phân quyền", 2)
    add_para(doc, "Validation test hiện xác nhận schema database id chấp nhận UUID sinh ngẫu nhiên, chấp nhận UUID fixture cố định và từ chối chuỗi không phải UUID. Các Route Handler còn dùng schema cho email, URL, số dương, enum trạng thái và độ dài chuỗi. Test API nên gửi dữ liệu thiếu, thừa, sai kiểu và sát biên để xác minh cả response body lẫn mã trạng thái.")
    add_table(doc, ["Tình huống", "Actor", "Kỳ vọng HTTP"], [
        ("Không có phiên gọi API hội viên", "Không xác thực", "401"),
        ("Member gọi API nhân viên", "member", "403"),
        ("Staff hủy payment", "staff", "403"),
        ("Manager gửi reason quá ngắn", "manager", "400"),
        ("Check in token rỗng", "staff", "400"),
        ("Check in bị trùng", "staff", "409"),
        ("Supabase chưa cấu hình", "manager", "503"),
    ], widths=[3.3, 1.35, 1.3], font_size=9)
    add_para(doc, "Kiểm thử RLS phải dùng client với JWT của từng vai trò thay vì admin client. Member A không được đọc member B, payment B hoặc check in B. Staff không được đọc audit log hoặc expenses nếu policy chỉ cho manager. Anon chỉ được đọc gói active theo policy công khai, không được đọc bảng khác.")

    new_page(doc, "6.5 Kết quả kiểm chứng tự động", 2)
    add_table(doc, ["Hạng mục", "Kết quả", "Bằng chứng"], [
        ("Unit test", "Đạt", "3 tệp test và 16 test đều pass"),
        ("Lint", "Đạt", "oxlint hoàn thành không có finding"),
        ("TypeScript", "Đạt", "Next build hoàn thành bước type checking"),
        ("Production build", "Đạt", "Compiled successfully và sinh 23 route"),
        ("Migration review", "Đạt có lưu ý", "6 migration có schema policy RPC và lịch sử loại module lớp học"),
        ("Integration test Supabase", "Chưa tự động hóa đầy đủ", "Cần pipeline database riêng"),
        ("End to end browser", "Chưa tự động hóa đầy đủ", "Cần Playwright hoặc tương đương"),
    ], widths=[1.45, 1.5, 3.45], font_size=9)
    caption(doc, "Bảng 6.1 Kết quả kiểm thử tại thời điểm báo cáo")
    add_para(doc, "Kết quả được chạy trực tiếp trên project: Vitest báo 3 tệp test đạt với 16 test; oxlint kết thúc thành công; Next.js build biên dịch, kiểm tra TypeScript, tạo 23 trang hoặc route và hoàn tất tối ưu hóa. Kết quả chứng minh source hiện tại có thể build, nhưng không tự động chứng minh kết nối production hoặc dữ liệu Supabase thật.")

    new_page(doc, "6.6 Kiểm thử chấp nhận người dùng", 2)
    add_table(doc, ["Kịch bản", "Bước chính", "Tiêu chí chấp nhận"], [
        ("Tiếp nhận hội viên mới", "Đăng nhập staff tạo hồ sơ tìm theo tên", "Mã và QR duy nhất hồ sơ xuất hiện trong danh sách"),
        ("Bán gói", "Chọn member plan method xác nhận", "Có subscription payment receipt và audit"),
        ("Gia hạn", "Bán gói khi gói cũ còn hiệu lực", "Gói mới scheduled bắt đầu nối tiếp"),
        ("Check in", "Quét token hợp lệ hai lần trong 10 phút", "Lần đầu đạt lần hai bị từ chối trùng"),
        ("Đóng băng", "Manager chọn khoảng ngày và lý do", "Gói frozen check in bị chặn"),
        ("Portal", "Member đăng nhập và xem lịch sử", "Chỉ thấy dữ liệu của chính mình"),
        ("Tài chính", "Manager chọn khoảng ngày", "Tổng bỏ qua payment và expense cancelled"),
    ], widths=[1.45, 2.65, 2.3], font_size=8.5)
    add_para(doc, "Buổi Sprint Review nên dùng seed data vì dữ liệu này bao phủ hội viên active, sắp hết hạn, frozen, expired, inactive và chưa mua gói. Gói mẫu có cả unlimited, theo lượt, sinh viên và gói ngừng bán. Việc chuẩn bị sẵn trạng thái giúp người đánh giá quan sát nhánh nghiệp vụ mà không phải chờ thời gian thực.")

    new_page(doc, "6.7 Đánh giá chất lượng", 2)
    add_para(doc, "Về chức năng, hệ thống bao phủ chuỗi giá trị chính từ hồ sơ đến sử dụng và báo cáo. Về bảo mật, project có session, phân quyền server, RLS và tách service role. Về toàn vẹn, các nghiệp vụ chính sử dụng constraint và RPC. Về bảo trì, TypeScript, validation, migration và test tạo nền tảng tốt.")
    add_para(doc, "Các điểm cần cải tiến gồm component quản trị lớn, thiếu test tích hợp database, thiếu end to end test, quan sát production chưa đầy đủ và một số logic báo cáo còn tính ở client. Lịch sử migration có module lớp học rồi loại bỏ, do đó cần tài liệu rõ hơn về trạng thái schema cuối cùng và kiểm tra migration từ database trống.")
    add_para(doc, "Đánh giá chung là MVP phù hợp trình diễn và nghiệm thu học phần khi được cấu hình Supabase đúng. Trước khi dùng cho vận hành thật, dự án cần hoàn thành test quyền tự động, backup restore drill, chính sách dữ liệu cá nhân, monitoring và quy trình xử lý sự cố.")


def chapter7(doc):
    new_page(doc, "7 Triển khai và vận hành", 1)
    doc.add_heading("7.1 Mô hình triển khai", level=2)
    add_picture(doc, ASSETS / "deployment.png", 6.35, "Hình 7.1 Mô hình triển khai đề xuất")
    add_para(doc, "Ứng dụng Next.js được triển khai trên runtime hỗ trợ Node.js phù hợp, kết nối tới một project Supabase riêng cho từng môi trường. Biến `NEXT_PUBLIC_SUPABASE_URL` và publishable key có thể dùng ở client theo mô hình Supabase, còn `SUPABASE_SERVICE_ROLE_KEY` chỉ tồn tại ở server. Domain sử dụng HTTPS và redirect URL trong Supabase phải khớp môi trường.")
    add_para(doc, "Ba môi trường development, staging và production dùng database tách biệt. Migration được áp dụng theo thứ tự tên, sau đó smoke test xác thực đăng nhập, đọc dữ liệu, bán gói và check in. Seed chỉ dùng cho development hoặc staging; không chạy dữ liệu demo vào production.")

    new_page(doc, "7.2 Quy trình phát hành", 2)
    add_numbered(doc, [
        "Tạo nhánh hoặc pull request cho Product Backlog Item và mô tả tiêu chí chấp nhận.",
        "Chạy unit test, lint và production build trong pipeline.",
        "Khởi tạo database tạm, áp dụng toàn bộ migration và chạy integration test.",
        "Triển khai staging, chạy smoke test theo vai trò và kiểm tra log.",
        "Phê duyệt release, sao lưu production và áp dụng migration tương thích ngược.",
        "Triển khai ứng dụng, theo dõi lỗi, latency và giao dịch trong cửa sổ giám sát.",
        "Nếu có sự cố, rollback ứng dụng; migration dữ liệu dùng kế hoạch phục hồi riêng thay vì hạ cấp mù quáng.",
    ])
    add_para(doc, "Mỗi release cần release note ghi chức năng, migration, thay đổi cấu hình và rủi ro. Thao tác ảnh hưởng dữ liệu phải có truy vấn kiểm tra trước và sau. Với migration lớn, phương pháp expand and contract giúp ứng dụng cũ và mới cùng hoạt động trong thời gian chuyển đổi.")

    new_page(doc, "7.3 Quản lý cấu hình và bí mật", 2)
    add_para(doc, "Tệp `.env` và `.env.local` không được commit. `.env.example` chỉ chứa tên biến và giá trị giả. Service role có quyền cao và bỏ qua RLS nên cần lưu trong kho bí mật của nền tảng triển khai, giới hạn người xem và xoay vòng khi nghi ngờ lộ. Log không được in toàn bộ biến môi trường hoặc Authorization header.")
    add_para(doc, "URL redirect của login, invite và recovery phải được cấu hình cho từng domain. Public signup nên tắt vì tài khoản được tạo qua lời mời. Mật khẩu tạm cần thay đổi ở lần đăng nhập đầu; production nên bổ sung chính sách mật khẩu, giới hạn thử đăng nhập và MFA cho manager.")
    add_para(doc, "Quyền database cần rà soát cùng RLS. Theo tài liệu Supabase, grant và policy là hai lớp khác nhau; policy không tự thu hồi quyền đã grant [5]. Vì vậy quy trình bảo mật phải kiểm tra cả privilege, policy, function grant và search path của security definer.")

    new_page(doc, "7.4 Sao lưu và khôi phục", 2)
    add_para(doc, "Dữ liệu hội viên và giao dịch là tài sản chính. Kế hoạch sao lưu xác định tần suất, thời gian lưu, người chịu trách nhiệm và mục tiêu khôi phục. Sao lưu chỉ có giá trị khi đã thử restore. Staging nên định kỳ nhận bản sao đã ẩn danh để diễn tập migration và khôi phục.")
    add_bullets(doc, [
        "Sao lưu tự động database theo khả năng của gói dịch vụ và lưu bản xuất trước migration rủi ro cao.",
        "Xác định RPO cho dữ liệu giao dịch và RTO cho hoạt động quầy.",
        "Lưu migration trong Git và kiểm tra có thể dựng database mới từ đầu.",
        "Kiểm tra ngẫu nhiên payment, subscription và check in sau restore.",
        "Không dùng seed demo trong quy trình khôi phục production.",
        "Ghi biên bản restore drill và cập nhật runbook sau mỗi lần diễn tập.",
    ])
    add_para(doc, "Khi hệ thống tạm ngừng, quầy có thể dùng danh sách offline tối thiểu để ghi thời điểm, mã hội viên và nhân viên xử lý. Sau khi dịch vụ khôi phục, dữ liệu phải được nhập có kiểm soát và đánh dấu nguồn để tránh tạo check in trùng.")

    new_page(doc, "7.5 Giám sát và xử lý sự cố", 2)
    add_para(doc, "Giám sát cần theo dõi availability, thời gian phản hồi API, tỷ lệ lỗi 5xx, lỗi Auth, số check in bị từ chối theo reason, thất bại RPC và độ trễ database. Chỉ số nghiệp vụ như doanh thu giảm đột ngột hoặc số payment không khớp subscription cũng có thể phát hiện lỗi mà metric kỹ thuật bỏ sót.")
    add_para(doc, "Log ứng dụng cần có request id, route, actor id đã làm mờ khi phù hợp, status và thời gian xử lý. Audit log phục vụ truy vết nghiệp vụ nhưng không thay log kỹ thuật. Cả hai loại log cần thời hạn lưu và quyền truy cập. Dữ liệu cá nhân không nên xuất hiện tự do trong thông báo lỗi.")
    add_para(doc, "Runbook sự cố xác định cách phân loại mức độ, người liên hệ, biện pháp cô lập và điều kiện khôi phục. Sau sự cố quan trọng, nhóm thực hiện post incident review tập trung vào nguyên nhân hệ thống và hành động phòng ngừa, sau đó đưa hành động vào Product Backlog.")

    new_page(doc, "7.6 Phân tích rủi ro", 2)
    add_table(doc, ["Rủi ro", "Khả năng", "Tác động", "Biện pháp"], [
        ("Lộ service role key", "Thấp", "Rất cao", "Secret store, xoay khóa, không log"),
        ("Sai lệch giao dịch đồng thời", "Trung bình", "Cao", "RPC, khóa bản ghi, integration test"),
        ("Migration lỗi", "Trung bình", "Cao", "Staging, backup, expand contract"),
        ("Member xem dữ liệu người khác", "Thấp", "Rất cao", "RLS test theo vai trò"),
        ("Quét QR chia sẻ", "Trung bình", "Trung bình", "Token ngẫu nhiên, chống trùng, xác minh bổ sung"),
        ("Báo cáo sai timezone", "Trung bình", "Trung bình", "Chuẩn hóa Asia Ho Chi Minh"),
        ("Mất kết nối tại quầy", "Trung bình", "Cao", "Runbook offline và đồng bộ có kiểm soát"),
        ("Component khó bảo trì", "Cao", "Trung bình", "Tách feature và regression test"),
    ], widths=[2.0, .85, .85, 2.7], font_size=8.2)
    caption(doc, "Bảng 7.1 Rủi ro triển khai")
    add_para(doc, "Rủi ro được xem xét trong Sprint Planning và cập nhật tại Review hoặc Retrospective. Hạng mục giảm rủi ro có thể được ưu tiên dù không tạo chức năng nhìn thấy ngay, vì nó bảo vệ giá trị đã phát hành.")

    new_page(doc, "7.7 Bảo vệ dữ liệu cá nhân", 2)
    add_para(doc, "Hồ sơ hội viên chứa họ tên, số điện thoại, email, ngày sinh, địa chỉ, liên hệ khẩn cấp và lịch sử sử dụng. Hệ thống cần thu thập đúng mục đích, giới hạn người truy cập và xác định thời hạn lưu. Trường không cần thiết cho vận hành không nên bắt buộc.")
    add_para(doc, "Bản xuất báo cáo phải giới hạn cột và được lưu an toàn. Dữ liệu staging hoặc dùng cho phân tích cần ẩn danh. Khi hội viên yêu cầu chỉnh sửa, hệ thống giữ lịch sử giao dịch nhưng cập nhật thông tin liên hệ theo quy trình. Quyền xóa phải cân bằng với nghĩa vụ lưu chứng từ và audit.")
    add_para(doc, "QR chỉ chứa UUID ngẫu nhiên là quyết định đúng cho giảm lộ thông tin trực tiếp. Tuy nhiên URL, log và ảnh chụp vẫn có thể làm lộ token. Phiên bản sau có thể dùng QR luân phiên hoặc nonce ngắn hạn nếu mô hình đe dọa yêu cầu mức bảo vệ cao hơn.")


def chapter8(doc):
    new_page(doc, "8 Kết luận và hướng phát triển", 1)
    doc.add_heading("8.1 Kết quả đạt được", level=2)
    add_para(doc, "Đề tài đã xây dựng một hệ thống web quản lý phòng gym với phạm vi MVP rõ ràng. Luồng cốt lõi từ đăng nhập, tạo hội viên, cấu hình gói, bán hoặc gia hạn, thanh toán, check in đến báo cáo đã có cấu trúc dữ liệu và API tương ứng. Cổng hội viên, chăm sóc và chi phí mở rộng sản phẩm ra ngoài thao tác quầy.")
    add_para(doc, "Về kỹ thuật, hệ thống kết hợp Next.js, TypeScript, Supabase Auth và PostgreSQL trong một kiến trúc phù hợp nhóm nhỏ. Validation, RBAC, RLS, constraint, RPC và audit log tạo nhiều lớp bảo vệ. Các giao dịch dễ sai lệch được xử lý nguyên tử ở database. Snapshot bảo toàn lịch sử khi gói thay đổi.")
    add_para(doc, "Về quy trình, Agile Scrum được dùng để chia sản phẩm thành Increment, ưu tiên backlog theo giá trị và rủi ro, đồng thời gắn Definition of Done với kiểm thử và build. Bằng chứng hiện tại gồm 16 test tự động đạt, lint sạch và production build thành công với 23 route.")

    new_page(doc, "8.2 Hạn chế", 2)
    add_para(doc, "Hệ thống hiện hướng tới một chi nhánh và thanh toán đủ một lần. Chưa có cổng thanh toán, đa chi nhánh, kiểm soát cửa vật lý, thông báo đa kênh hoặc phân tích dự báo. Module lớp học từng xuất hiện trong schema nhưng đã rời phạm vi sản phẩm hiện tại, cho thấy backlog và database cần tiếp tục được đồng bộ.")
    add_para(doc, "Bộ test tự động chưa bao phủ đầy đủ API, RLS và trình duyệt. Unit test chứng minh một số quy tắc nhưng không chứng minh toàn bộ transaction PostgreSQL. Quan sát production, sao lưu khôi phục, accessibility và kiểm thử tải cần được thực hiện trước khi phục vụ vận hành thực.")
    add_para(doc, "Một số component giao diện còn lớn và các kiểu dữ liệu response được khai báo tại chỗ. Khi sản phẩm mở rộng, cấu trúc này có thể gây lặp và khó refactor. Báo cáo cũng dùng dữ liệu mẫu thay vì số liệu hoạt động dài hạn, nên chưa thể kết luận về tải, tỷ lệ giữ chân hoặc tác động kinh doanh thực tế.")

    new_page(doc, "8.3 Hướng phát triển", 2)
    add_bullets(doc, [
        "Tự động hóa integration test cho migration, RPC và RLS bằng database tạm trong CI.",
        "Bổ sung end to end test cho năm luồng quan trọng và kiểm thử accessibility.",
        "Tách `gym-app.tsx` theo feature, sinh TypeScript type từ schema và chuẩn hóa error catalog.",
        "Phát triển đa chi nhánh với branch id, policy theo chi nhánh và báo cáo hợp nhất.",
        "Tích hợp cổng thanh toán, webhook idempotent, hóa đơn và đối soát.",
        "Bổ sung email hoặc SMS cho hết hạn, thanh toán và chăm sóc theo consent.",
        "Đưa tổng hợp báo cáo về database, thêm phân trang và bộ lọc thời gian chuẩn.",
        "Thiết lập monitoring, alert, backup restore drill và quy trình ứng phó sự cố.",
    ])
    add_para(doc, "Các hạng mục nên được đưa vào Product Backlog và đánh giá theo giá trị, chi phí cùng rủi ro. Ưu tiên gần nhất là test tích hợp và quan sát vận hành vì chúng giảm rủi ro cho toàn bộ chức năng hiện có. Sau đó mới mở rộng thanh toán hoặc đa chi nhánh, tránh tăng phạm vi trên một nền tảng chưa được kiểm chứng đầy đủ.")

    new_page(doc, "8.4 Bài học kinh nghiệm", 2)
    add_para(doc, "Bài học quan trọng nhất là quy tắc nghiệp vụ phải được đặt ở nơi có thể bảo đảm tính đúng. Kiểm tra ở giao diện giúp trải nghiệm tốt nhưng không chống được request cạnh tranh hoặc client khác. Constraint và transaction tại database là cần thiết cho tiền, lượt và trạng thái.")
    add_para(doc, "Scrum mang lại giá trị khi mỗi sprint có Goal và Increment dùng được, không phải khi nhóm tạo nhiều cuộc họp hoặc biểu mẫu. Product Backlog cần thể hiện giá trị và rủi ro; Definition of Done cần bao gồm migration, quyền và test. Retrospective chỉ hữu ích khi tạo ra hành động nhỏ có thể theo dõi ở sprint tiếp theo.")
    add_para(doc, "Cuối cùng, tài liệu có chất lượng phải kết nối yêu cầu với thiết kế và bằng chứng. Báo cáo không chỉ mô tả công nghệ đã dùng mà phải giải thích vì sao quyết định đó phù hợp, đánh đổi nào được chấp nhận và điều gì vẫn chưa được chứng minh.")


def references_and_appendices(doc):
    new_page(doc, "Tài liệu tham khảo", 1)
    refs = [
        "[1] Agile Alliance. Manifesto for Agile Software Development và Principles behind the Agile Manifesto. https://agilemanifesto.org/ và https://agilemanifesto.org/principles. Truy cập ngày 19 tháng 9 năm 2026.",
        "[2] Ken Schwaber và Jeff Sutherland. Hướng dẫn Scrum 2020 bản tiếng Việt. https://scrumguides.org/docs/scrumguide/v2020/2020-Scrum-Guide-Vietnamese.pdf. Truy cập ngày 19 tháng 9 năm 2026.",
        "[3] Vercel. Next.js Documentation App Router Getting Started. https://nextjs.org/docs/app/getting-started. Truy cập ngày 19 tháng 9 năm 2026.",
        "[4] Microsoft. TypeScript Handbook. https://www.typescriptlang.org/docs/handbook/. Truy cập ngày 19 tháng 9 năm 2026.",
        "[5] Supabase. Row Level Security. https://supabase.com/docs/guides/database/postgres/row-level-security. Truy cập ngày 19 tháng 9 năm 2026.",
        "[6] Supabase. Securing your data. https://supabase.com/docs/guides/database/secure-data. Truy cập ngày 19 tháng 9 năm 2026.",
        "[7] Supabase. Database Functions. https://supabase.com/docs/guides/database/functions. Truy cập ngày 19 tháng 9 năm 2026.",
        "[8] Zod. Documentation. https://zod.dev/. Truy cập ngày 19 tháng 9 năm 2026.",
        "[9] Vitest. Getting Started. https://vitest.dev/guide/. Truy cập ngày 19 tháng 9 năm 2026.",
        "[10] GymFlow project. README, package manifest, source code, migration SQL, seed data và test trong workspace của đề tài. Đối chiếu ngày 19 tháng 9 năm 2026.",
    ]
    for ref in refs:
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Inches(-0.3)
        p.paragraph_format.left_indent = Inches(0.3)
        p.paragraph_format.space_after = Pt(8)
        set_font(p.add_run(ref), size=11)

    new_page(doc, "Phụ lục A Hướng dẫn cài đặt", 1)
    add_numbered(doc, [
        "Cài Node.js phiên bản từ 22.13.0 và tải source code của project.",
        "Tạo project Supabase riêng cho môi trường và lấy URL, publishable key cùng service role key.",
        "Tạo `.env.local` từ `.env.example`; không commit khóa thật vào Git.",
        "Chạy các tệp trong `supabase/migrations` theo thứ tự tên trên database mới.",
        "Cấu hình Site URL và redirect cho login, invite, recovery theo domain.",
        "Tắt public signup nếu chỉ dùng lời mời tài khoản.",
        "Cài dependencies bằng `npm install`, sau đó chạy `npm test`, `npm run lint` và `npm run build`.",
        "Chỉ ở development hoặc staging, chạy `supabase/seed.sql` để tạo dữ liệu mẫu.",
        "Chạy `npm run dev` và mở địa chỉ local của Next.js.",
    ])
    add_para(doc, "Thứ tự migration là một phần của sản phẩm. Không gộp hoặc sửa migration đã áp dụng trên môi trường dùng chung nếu không có kế hoạch. Khi thay đổi schema, tạo migration mới, kiểm tra từ database trống và kiểm tra nâng cấp từ phiên bản gần nhất.")

    new_page(doc, "Phụ lục B Dữ liệu mẫu", 1)
    add_para(doc, "Seed data dùng UUID cố định và thao tác upsert để có thể chạy lại mà không xóa dữ liệu thật. Bộ dữ liệu gồm bốn profile, sáu hội viên, năm loại gói, sáu subscription, sáu payment, năm check in, một kỳ freeze, một follow up, một chi phí và các audit log mẫu.")
    add_table(doc, ["Mã mẫu", "Trạng thái", "Mục đích kiểm thử"], [
        ("GF DEMO01", "Active và đã gia hạn", "Gói active cùng gói scheduled"),
        ("GF DEMO02", "Sắp hết hạn còn 3 lượt", "Retention và gói theo lượt"),
        ("GF DEMO03", "Frozen", "Từ chối check in và unfreeze"),
        ("GF DEMO04", "Expired", "Lịch sử hết hạn"),
        ("GF DEMO05", "Inactive và cancelled", "Chặn nghiệp vụ và lịch sử hủy"),
        ("GF DEMO06", "Chưa mua gói", "Bán mới"),
    ], widths=[1.45, 2.0, 2.95], font_size=9)
    add_para(doc, "Khi demo, cần tạo Auth user bằng email mẫu tương ứng để trigger liên kết profile. Dữ liệu mẫu không phải dữ liệu cá nhân thật và không được dùng làm tài khoản production.")

    new_page(doc, "Phụ lục C Ma trận truy vết yêu cầu", 1)
    add_table(doc, ["Yêu cầu", "Thiết kế", "Hiện thực", "Kiểm thử"], [
        ("US01 đăng nhập", "Auth và profile role", "auth routes lib authz", "API auth và redirect"),
        ("US03 hội viên", "members profile QR", "members routes GymApp", "Validation và UAT"),
        ("US06 bán gói", "RPC và snapshot", "subscriptions route sell membership", "Integration và UAT"),
        ("US09 check in", "Lock rule và audit", "check ins route RPC", "CI01 đến CI09"),
        ("US10 hủy tiền", "Soft cancel", "cancel payment RPC", "Role conflict audit"),
        ("US12 portal", "RLS member scope", "portal route component", "Cross member denial"),
        ("US14 chi phí", "expenses categories", "expenses route module", "Financial summary"),
    ], widths=[1.3, 1.65, 2.15, 1.3], font_size=8.2)
    add_para(doc, "Ma trận truy vết giúp phát hiện yêu cầu chưa có test hoặc thiết kế chưa có hiện thực. Trong CI, các mã user story có thể được dùng trong tên test hoặc pull request để liên kết bằng chứng tự động.")

    new_page(doc, "Phụ lục D Checklist nghiệm thu", 1)
    add_bullets(doc, [
        "Thông tin sinh viên, lớp, nhóm và giảng viên đã được điền đúng.",
        "Mục lục và số trang đã được cập nhật trong Word sau lần chỉnh sửa cuối.",
        "Môi trường demo dùng database staging và không chứa dữ liệu cá nhân thật.",
        "Có tài khoản manager, staff, member để trình diễn phân quyền.",
        "Luồng tạo hội viên, bán gói, check in, hủy thanh toán và portal đã được chạy thử.",
        "Tất cả unit test, lint và production build đều đạt trên commit nộp bài.",
        "Migration có thể dựng database mới và seed chạy lại an toàn.",
        "Service role key không xuất hiện trong Git, ảnh chụp hoặc log báo cáo.",
        "Giới hạn của MVP và các hạng mục chưa tự động hóa được trình bày trung thực.",
        "File nộp mở được, font tiếng Việt hiển thị đúng và bảng hình không tràn trang.",
    ])
    add_para(doc, "Checklist này nên được thực hiện trên đúng tệp và commit cuối cùng. Nếu có thay đổi sau nghiệm thu thử, nhóm phải chạy lại các bước bị ảnh hưởng thay vì dựa trên kết quả cũ.")

    new_page(doc, "Phụ lục E Biên bản kiểm chứng kỹ thuật", 1)
    add_table(doc, ["Lệnh kiểm chứng", "Kết quả", "Ghi chú"], [
        ("npm test", "Pass", "3 test files và 16 tests"),
        ("npm run lint", "Pass", "oxlint không báo lỗi"),
        ("npm run build", "Pass", "Biên dịch production thành công"),
        ("Next route inventory", "23", "Trang và API động cùng một trang tĩnh not found"),
        ("TypeScript TSX files", "113", "Khoảng 12.258 dòng"),
        ("SQL migrations", "6", "Khoảng 710 dòng SQL kể cả seed khi thống kê"),
        ("Database objects", "16 bảng 14 hàm 22 policy", "Đếm từ migration"),
    ], widths=[2.1, 1.2, 3.1], font_size=9)
    add_para(doc, "Biên bản phản ánh trạng thái project ngày 19 tháng 9 năm 2026. Sau khi chỉnh sửa mã nguồn, cần chạy lại toàn bộ kiểm chứng và cập nhật số liệu nếu khác.")

    new_page(doc, "Phụ lục F Nhật ký retrospective đề xuất", 1)
    add_table(doc, ["Sprint", "Điều hiệu quả", "Vấn đề", "Hành động kế tiếp"], [
        ("1", "Khởi tạo auth và schema sớm", "Thiếu fixture vai trò", "Tạo seed manager staff member"),
        ("2", "CRUD tạo giá trị nhìn thấy", "Component tăng nhanh", "Tách form và table dùng chung"),
        ("3", "RPC giữ bán gói nguyên tử", "Quy tắc gia hạn phức tạp", "Bổ sung state model và test"),
        ("4", "Check in có reason rõ", "Chưa test đồng thời", "Thêm database integration test"),
        ("5", "Portal giảm tải lễ tân", "RLS khó kiểm tra thủ công", "Tạo test role matrix"),
        ("6", "Build và lint ổn định", "Thiếu E2E và monitoring", "Đưa vào release backlog"),
    ], widths=[.55, 2.05, 1.85, 2.05], font_size=8.2)
    add_para(doc, "Retrospective không dùng để đánh giá cá nhân. Mỗi hành động phải có người chịu trách nhiệm, tiêu chí hoàn thành và vị trí trong backlog. Hành động chưa hoàn thành được xem lại ở retrospective tiếp theo.")

    new_page(doc, "Phụ lục G Mẫu Sprint Review", 1)
    add_numbered(doc, [
        "Nhắc lại Sprint Goal và các Product Backlog Item đã chọn.",
        "Trình diễn Increment trên staging bằng dữ liệu mẫu, không dùng slide thay cho phần mềm.",
        "Đối chiếu từng tiêu chí chấp nhận và ghi nhận hạng mục chưa Done.",
        "Trình bày test, lint, build và thay đổi migration liên quan.",
        "Thu phản hồi của quản lý, lễ tân và hội viên theo giá trị và khả dụng.",
        "Cập nhật Product Backlog, ưu tiên và dự báo release dựa trên thông tin mới.",
    ])
    add_para(doc, "Đối với Sprint có check in, kịch bản demo nên gồm một QR hợp lệ, một hội viên inactive, một gói hết lượt và một lần quét trùng. Đối với Sprint thanh toán, demo cả giao dịch valid và cancelled để chứng minh số liệu tổng hợp đúng.")

    new_page(doc, "Phụ lục H Thuật ngữ nghiệp vụ", 1)
    add_table(doc, ["Thuật ngữ", "Định nghĩa trong hệ thống"], [
        ("Hội viên", "Người có hồ sơ tại phòng gym, có thể có hoặc chưa có tài khoản portal"),
        ("Gói tập", "Sản phẩm có giá, thời hạn và giới hạn lượt tùy chọn"),
        ("Đăng ký gói", "Quyền sử dụng một gói của một hội viên trong khoảng ngày"),
        ("Gia hạn", "Đăng ký mới bắt đầu nối tiếp quyền hiện có"),
        ("Đóng băng", "Tạm dừng quyền sử dụng trong khoảng thời gian được phê duyệt"),
        ("Check in", "Bản ghi hội viên vào tập và sử dụng quyền từ một subscription"),
        ("Phiếu thu", "Mã chứng từ gắn với payment"),
        ("Chăm sóc", "Hoạt động liên hệ hội viên sắp hết hạn hoặc gần hết lượt"),
        ("Audit log", "Nhật ký actor thực hiện action trên entity tại thời điểm xác định"),
    ], widths=[1.5, 4.9], font_size=9)


def finalize(doc):
    # Keep title/headings black and normalize all table borders/padding.
    for p in doc.paragraphs:
        if p.style and p.style.name in {"Title", "Heading 1", "Heading 2", "Heading 3"}:
            for r in p.runs:
                r.font.color.rgb = RGBColor(0, 0, 0)
    for table in doc.tables:
        set_table_borders(table)
        for row in table.rows:
            for cell in row.cells:
                set_cell_margins(cell)
    doc.core_properties.title = "Xây dựng hệ thống quản lý phòng gym trên nền tảng web theo phương pháp Agile Scrum"
    doc.core_properties.subject = "Báo cáo môn học Công nghệ phần mềm"
    doc.core_properties.keywords = "GymFlow, Agile, Scrum, Next.js, Supabase, PostgreSQL"
    doc.core_properties.author = "[HỌ VÀ TÊN SINH VIÊN]"
    doc.save(DOCX)


def main():
    make_diagrams()
    doc = Document()
    style_document(doc)
    add_cover(doc)
    add_front_matter(doc)
    chapter1(doc)
    chapter2(doc)
    chapter3(doc)
    chapter4(doc)
    chapter5(doc)
    chapter6(doc)
    chapter7(doc)
    chapter8(doc)
    references_and_appendices(doc)
    finalize(doc)
    print(DOCX)


if __name__ == "__main__":
    main()
