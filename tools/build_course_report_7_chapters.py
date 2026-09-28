from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

import build_course_report as b


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts"
ASSETS = OUT / "report_7_chapters_assets"
DOCX = OUT / "Bao_cao_GymFlow_theo_khung_7_chuong.docx"
ASSETS.mkdir(parents=True, exist_ok=True)

FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"


def font(size=28, bold=False):
    return ImageFont.truetype(BOLD if bold else FONT, size)


def arrow(draw, start, end, color="#365F91", width=4):
    import math
    x1, y1 = start
    x2, y2 = end
    draw.line((x1, y1, x2, y2), fill=color, width=width)
    dx, dy = x2 - x1, y2 - y1
    length = max(math.hypot(dx, dy), 1)
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    bx, by = x2 - ux * 22, y2 - uy * 22
    draw.polygon([(x2, y2), (bx + px * 10, by + py * 10), (bx - px * 10, by - py * 10)], fill=color)


def title(draw, text):
    draw.text((900, 55), text, anchor="mm", font=font(42, True), fill="#111111")


def save(img, name):
    path = ASSETS / name
    img.save(path)
    return path


def make_use_case():
    img = Image.new("RGB", (1800, 1080), "white")
    d = ImageDraw.Draw(img)
    title(d, "Use Case Diagram của hệ thống GymFlow")
    d.rounded_rectangle((350, 120, 1450, 1010), radius=24, outline="#17365D", width=4, fill="#FBFCFE")
    d.text((900, 150), "Hệ thống quản lý phòng gym", anchor="mm", font=font(30, True), fill="#17365D")

    actors = {"Quản lý": (150, 320), "Nhân viên": (150, 650), "Hội viên": (1650, 520)}
    for name, (x, y) in actors.items():
        d.ellipse((x-22, y-75, x+22, y-31), outline="#111111", width=4)
        d.line((x, y-31, x, y+55), fill="#111111", width=4)
        d.line((x-45, y, x+45, y), fill="#111111", width=4)
        d.line((x, y+55, x-38, y+110), fill="#111111", width=4)
        d.line((x, y+55, x+38, y+110), fill="#111111", width=4)
        d.text((x, y+145), name, anchor="mm", font=font(27, True), fill="#111111")

    cases = [
        ("Đăng nhập", 550, 245), ("Quản lý hội viên", 820, 245), ("Quản lý gói tập", 1120, 245),
        ("Bán và gia hạn gói", 610, 440), ("Check in", 940, 440), ("Quản lý thanh toán", 1250, 440),
        ("Theo dõi báo cáo", 600, 650), ("Quản lý nhân viên", 940, 650), ("Quản lý chi phí", 1250, 650),
        ("Xem QR và gói cá nhân", 720, 850), ("Xem lịch sử cá nhân", 1120, 850),
    ]
    centers = {}
    for label, x, y in cases:
        d.ellipse((x-165, y-58, x+165, y+58), outline="#365F91", width=3, fill="#EAF2F8")
        d.text((x, y), label, anchor="mm", font=font(23), fill="#111111")
        centers[label] = (x, y)

    manager = ["Đăng nhập", "Quản lý hội viên", "Quản lý gói tập", "Bán và gia hạn gói", "Check in", "Quản lý thanh toán", "Theo dõi báo cáo", "Quản lý nhân viên", "Quản lý chi phí"]
    staff = ["Đăng nhập", "Quản lý hội viên", "Bán và gia hạn gói", "Check in"]
    member = ["Đăng nhập", "Xem QR và gói cá nhân", "Xem lịch sử cá nhân"]
    for label in manager:
        d.line((195, 320, centers[label][0]-165, centers[label][1]), fill="#78909C", width=2)
    for label in staff:
        d.line((195, 650, centers[label][0]-165, centers[label][1]), fill="#5C6BC0", width=2)
    for label in member:
        d.line((1605, 520, centers[label][0]+165, centers[label][1]), fill="#43A047", width=2)
    return save(img, "use_case.png")


def class_box(draw, x, y, w, name, attrs, methods, fill="#EAF2F8"):
    line_h = 31
    h = 58 + (len(attrs)+len(methods)+1)*line_h
    draw.rounded_rectangle((x, y, x+w, y+h), radius=12, outline="#17365D", width=3, fill=fill)
    draw.rectangle((x, y, x+w, y+55), fill="#17365D")
    draw.text((x+w/2, y+28), name, anchor="mm", font=font(25, True), fill="white")
    yy = y+70
    for a in attrs:
        draw.text((x+14, yy), a, anchor="lm", font=font(19), fill="#111111")
        yy += line_h
    draw.line((x, yy-10, x+w, yy-10), fill="#AAB7C4", width=2)
    for m in methods:
        draw.text((x+14, yy), m, anchor="lm", font=font(19), fill="#111111")
        yy += line_h
    return (x, y, x+w, y+h)


def make_class_diagram():
    img = Image.new("RGB", (1800, 1220), "white")
    d = ImageDraw.Draw(img)
    title(d, "Class Diagram miền nghiệp vụ GymFlow")
    boxes = {}
    boxes["Profile"] = class_box(d, 70, 140, 380, "Profile", ["id UUID", "fullName string", "role Role", "status Status"], ["canAccess role"], "#EAF2F8")
    boxes["Member"] = class_box(d, 550, 140, 400, "Member", ["id UUID", "memberCode string", "qrToken UUID", "status Status"], ["updateProfile", "isActive"], "#E2F0D9")
    boxes["Plan"] = class_box(d, 1120, 140, 420, "MembershipPlan", ["id UUID", "name string", "price decimal", "durationDays int", "visitLimit int"], ["activate", "deactivate"], "#FFF2CC")
    boxes["Subscription"] = class_box(d, 180, 600, 430, "Subscription", ["id UUID", "startDate date", "endDate date", "remainingVisits int", "status string"], ["freeze", "unfreeze", "expire"], "#FCE4D6")
    boxes["Payment"] = class_box(d, 710, 650, 390, "Payment", ["id UUID", "receiptCode string", "amount decimal", "method string", "status string"], ["cancel reason"], "#F4CCCC")
    boxes["CheckIn"] = class_box(d, 1230, 650, 390, "CheckIn", ["id UUID", "checkedInAt datetime", "checkedInBy UUID"], ["validateDuplicate"], "#DDEBF7")

    def center(name, side):
        x1,y1,x2,y2 = boxes[name]
        return {"left":(x1,(y1+y2)/2),"right":(x2,(y1+y2)/2),"top":((x1+x2)/2,y1),"bottom":((x1+x2)/2,y2)}[side]
    links = [
        (center("Profile","right"), center("Member","left"), "0..1       1"),
        (center("Member","bottom"), center("Subscription","top"), "1       0..*"),
        (center("Plan","bottom"), center("Subscription","right"), "1       0..*"),
        (center("Subscription","right"), center("Payment","left"), "1       1"),
        (center("Subscription","right"), center("CheckIn","left"), "1       0..*"),
    ]
    for p1,p2,label in links:
        d.line((*p1,*p2), fill="#365F91", width=3)
        d.text(((p1[0]+p2[0])/2,(p1[1]+p2[1])/2-14), label, anchor="mm", font=font(19), fill="#555555", stroke_width=4, stroke_fill="white")
    d.text((900, 1175), "Sơ đồ tập trung các lớp nghiệp vụ chính và không liệt kê toàn bộ bảng hỗ trợ", anchor="mm", font=font(21), fill="#555555")
    return save(img, "class_diagram.png")


def make_erd():
    img = Image.new("RGB", (1800, 1100), "white")
    d = ImageDraw.Draw(img)
    title(d, "Mô hình quan hệ dữ liệu chính")
    nodes = {
        "profiles": (80,150,390,300), "members": (510,150,820,330), "plans": (1020,150,1350,330),
        "subscriptions": (520,500,900,720), "payments": (1050,500,1380,700), "check_ins": (1400,780,1720,970),
        "freezes": (120,550,430,730), "follow_ups": (90,830,430,1000), "audit_logs": (630,830,980,1010),
    }
    texts = {
        "profiles":["PK id","auth_user_id","role","status"], "members":["PK id","FK profile_id","member_code","qr_token"],
        "plans":["PK id","name","price","duration_days"], "subscriptions":["PK id","FK member_id","FK plan_id","status","remaining_visits"],
        "payments":["PK id","FK subscription_id","amount","status"], "check_ins":["PK id","FK member_id","FK subscription_id","checked_in_at"],
        "freezes":["PK id","FK subscription_id","start_date","status"], "follow_ups":["PK id","FK member_id","assigned_to","status"],
        "audit_logs":["PK id","FK actor_id","action","entity_id"],
    }
    for name, (x1,y1,x2,y2) in nodes.items():
        d.rounded_rectangle((x1,y1,x2,y2), radius=10, outline="#17365D", width=3, fill="#F7FAFD")
        d.rectangle((x1,y1,x2,y1+48), fill="#17365D")
        d.text(((x1+x2)/2,y1+25), name, anchor="mm", font=font(23,True), fill="white")
        y=y1+66
        for item in texts[name]:
            d.text((x1+14,y), item, anchor="lm", font=font(19), fill="#111111"); y+=29
    conns = [("profiles","members"),("members","subscriptions"),("plans","subscriptions"),("subscriptions","payments"),("subscriptions","check_ins"),("subscriptions","freezes"),("members","follow_ups"),("profiles","audit_logs")]
    for a,c in conns:
        ax1,ay1,ax2,ay2=nodes[a]; bx1,by1,bx2,by2=nodes[c]
        p1=((ax1+ax2)/2,(ay1+ay2)/2); p2=((bx1+bx2)/2,(by1+by2)/2)
        d.line((*p1,*p2), fill="#7A8DA0", width=3)
    return save(img, "erd.png")


def make_sequence():
    img = Image.new("RGB", (1800, 1120), "white")
    d = ImageDraw.Draw(img)
    title(d, "Sequence Diagram cho luồng check in")
    actors = [(170,"Nhân viên"),(530,"Giao diện"),(900,"API"),(1270,"RPC"),(1610,"PostgreSQL")]
    for x,label in actors:
        d.rounded_rectangle((x-125,120,x+125,190),radius=10,outline="#17365D",width=3,fill="#EAF2F8")
        d.text((x,155),label,anchor="mm",font=font(24,True),fill="#111111")
        d.line((x,190,x,1040),fill="#9E9E9E",width=2)
    messages = [
        (170,530,260,"1 Quét QR hoặc nhập mã"),(530,900,350,"2 POST api check ins"),(900,900,430,"3 Xác thực session và role"),
        (900,1270,510,"4 Gọi check_in_member"),(1270,1610,590,"5 Khóa và đọc member subscription"),(1610,1270,680,"6 Trả dữ liệu hiện tại"),
        (1270,1610,760,"7 Ghi check in trừ lượt audit"),(1610,1270,840,"8 Commit kết quả"),(1270,900,920,"9 JSON ok hoặc reason"),(900,530,990,"10 HTTP 201 hoặc 409"),
    ]
    for x1,x2,y,label in messages:
        if x1==x2:
            d.line((x1,y,x1+120,y),fill="#365F91",width=3); d.line((x1+120,y,x1+120,y+35),fill="#365F91",width=3); arrow(d,(x1+120,y+35),(x1,y+35))
            d.text((x1+10,y-17),label,anchor="lm",font=font(20),fill="#111111")
        else:
            arrow(d,(x1,y),(x2,y)); d.text(((x1+x2)/2,y-17),label,anchor="mm",font=font(20),fill="#111111",stroke_width=4,stroke_fill="white")
    return save(img, "sequence_checkin.png")


def make_activity():
    b.diagram(
        ASSETS / "activity_sell.png", "Activity Diagram bán và gia hạn gói",
        [
            ("start",.4,4.05,1.15,.65,"Bắt đầu","#E2F0D9"),("select",2.0,3.85,1.55,1.0,"Chọn hội viên\ngói và phương thức","#DCE6F1"),
            ("valid",4.05,3.85,1.45,1.0,"Kiểm tra quyền\nvà đầu vào","#FFF2CC"),("rpc",6.05,3.85,1.45,1.0,"Gọi RPC\nbán gói","#EAF2F8"),
            ("decision",8.1,3.85,1.35,1.0,"Dữ liệu\nhợp lệ","#FCE4D6"),("error",8.1,2.0,1.35,.75,"Trả lỗi\nkhông ghi dữ liệu","#F4CCCC"),
            ("sub",5.9,1.6,1.6,.85,"Tạo subscription\nvà snapshot","#E2F0D9"),("pay",3.65,1.6,1.55,.85,"Tạo payment\nphiếu thu","#E2F0D9"),
            ("audit",1.55,1.6,1.35,.85,"Ghi audit log","#DDEBF7"),("end",.25,.35,1.2,.65,"Kết thúc","#E7E6E6"),
        ],
        [("start","select",""),("select","valid",""),("valid","rpc",""),("rpc","decision",""),("decision","error","Không"),("decision","sub","Có"),("sub","pay","cùng giao dịch"),("pay","audit",""),("audit","end","")],
        "Giao dịch chỉ commit khi subscription payment và audit log đều được tạo thành công",
    )
    return ASSETS / "activity_sell.png"


def ui_frame(name, screen_title, cards, table_headers=None, rows=None, accent="#17365D"):
    img = Image.new("RGB", (1800, 1050), "#EEF2F6")
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((80,70,1720,980),radius=24,fill="white",outline="#C7D2DE",width=3)
    d.rectangle((80,70,1720,125),fill="#F7F8FA")
    for i,c in enumerate(["#FF5F57","#FFBD2E","#28C840"]): d.ellipse((110+i*36,88,130+i*36,108),fill=c)
    d.text((900,98),"GymFlow",anchor="mm",font=font(25,True),fill="#333333")
    d.rectangle((80,125,380,980),fill=accent)
    d.text((120,180),"GYMFLOW",font=font(30,True),fill="white")
    nav=["Tổng quan","Hội viên","Gói tập","Check in","Thanh toán","Báo cáo"]
    for i,n in enumerate(nav):
        y=270+i*70
        if n==screen_title: d.rounded_rectangle((105,y-25,350,y+25),radius=10,fill="#2D5684")
        d.text((130,y),n,anchor="lm",font=font(23),fill="white")
    d.text((430,185),screen_title,anchor="lm",font=font(38,True),fill="#111111")
    x=430
    for label,value in cards:
        d.rounded_rectangle((x,235,x+280,355),radius=14,fill="#F7FAFD",outline="#D9E2EC",width=2)
        d.text((x+22,270),label,anchor="lm",font=font(20),fill="#617080")
        d.text((x+22,320),value,anchor="lm",font=font(31,True),fill=accent)
        x+=310
    if table_headers:
        left, top, right = 430, 420, 1650
        colw=(right-left)/len(table_headers)
        d.rectangle((left,top,right,top+60),fill=accent)
        for i,h in enumerate(table_headers): d.text((left+colw*(i+.5),top+30),h,anchor="mm",font=font(20,True),fill="white")
        for r_idx,row in enumerate(rows or []):
            y=top+60+r_idx*68
            d.rectangle((left,y,right,y+68),fill="#F7FAFD" if r_idx%2 else "white",outline="#E1E6EB",width=1)
            for i,val in enumerate(row): d.text((left+colw*i+14,y+34),str(val),anchor="lm",font=font(19),fill="#222222")
    return save(img, name)


def make_ui_images():
    dashboard = ui_frame("ui_dashboard.png","Tổng quan",[("Doanh thu tháng","5.120.000 đ"),("Hội viên active","5"),("Check in hôm nay","2")],["Thời gian","Hội viên","Mã"],[("08:30","Nguyễn Văn An","GF DEMO01"),("06:45","Trần Thị Bình","GF DEMO02"),("Hôm qua","Nguyễn Văn An","GF DEMO01")])
    members = ui_frame("ui_members.png","Hội viên",[("Tổng hội viên","6"),("Đang hoạt động","5"),("Sắp hết hạn","1")],["Mã","Họ tên","Điện thoại","Trạng thái"],[("GF DEMO01","Nguyễn Văn An","0902000001","Hoạt động"),("GF DEMO02","Trần Thị Bình","0902000002","Sắp hết hạn"),("GF DEMO05","Võ Quốc Em","0902000005","Ngừng hoạt động")])
    checkin = ui_frame("ui_checkin.png","Check in",[("Trạng thái máy quét","Sẵn sàng"),("Lượt hôm nay","2"),("Chống trùng","10 phút")],["Kết quả","Hội viên","Gói","Thời gian"],[("Thành công","Nguyễn Văn An","Tháng Unlimited","08:30"),("Từ chối","Trần Thị Bình","Quét trùng","08:35")])
    portal = ui_frame("ui_portal.png","Cổng hội viên",[("Mã hội viên","GF DEMO01"),("Gói hiện tại","Còn 19 ngày"),("Lượt còn lại","Không giới hạn")],["Ngày","Hoạt động","Chi tiết"],[("Hôm nay","Check in","08:30"),("10 ngày trước","Thanh toán","PT DEMO 0001"),("Hôm qua","Gia hạn","Gói quý Unlimited")],accent="#286A5A")
    return dashboard,members,checkin,portal


def make_visuals():
    b.make_diagrams()
    return {
        "usecase": make_use_case(), "class": make_class_diagram(), "erd": make_erd(),
        "sequence": make_sequence(), "activity": make_activity(),
        "architecture": b.ASSETS / "architecture.png", "checkin": b.ASSETS / "checkin.png",
        "subscription": b.ASSETS / "subscription.png", "scrum": b.ASSETS / "scrum.png",
        "ui": make_ui_images(),
    }


def page(doc, heading, level=2):
    b.new_page(doc, heading, level)


def intro_pages(doc):
    b.add_cover(doc)
    page(doc,"Lời cam đoan",1)
    b.add_para(doc,"Tôi cam đoan báo cáo này trình bày kết quả phân tích, thiết kế, xây dựng và kiểm thử hệ thống GymFlow trong phạm vi môn học Công nghệ phần mềm. Các số liệu kỹ thuật được đối chiếu từ mã nguồn, migration và kết quả chạy kiểm thử của project. Tài liệu tham khảo được liệt kê ở cuối báo cáo.")
    b.add_para(doc,"Các trường thông tin trên trang bìa cần được hoàn thiện trước khi nộp. Nếu đề tài được thực hiện theo nhóm, phần phân công phải phản ánh đúng đóng góp của từng thành viên.")
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.RIGHT; p.paragraph_format.first_line_indent=Inches(0); p.paragraph_format.space_before=Pt(30); b.set_font(p.add_run("Sinh viên thực hiện\n\n\n[HỌ VÀ TÊN]"),bold=True)
    page(doc,"Lời cảm ơn",1)
    b.add_para(doc,"Tôi xin cảm ơn giảng viên môn Công nghệ phần mềm đã hướng dẫn cách xác định yêu cầu, thiết kế hệ thống, tổ chức kiểm thử và quản lý quá trình phát triển. Những nội dung này được vận dụng trực tiếp vào đề tài quản lý phòng gym trên nền tảng web.")
    b.add_para(doc,"Tôi cũng tham khảo tài liệu chính thức của Next.js, TypeScript, Supabase, PostgreSQL, Zod, Vitest và Scrum để lựa chọn giải pháp kỹ thuật phù hợp. Báo cáo tập trung vào sản phẩm thực tế và bằng chứng kiểm chứng thay vì trình bày dài về lý thuyết.")
    page(doc,"Tóm tắt",1)
    b.add_para(doc,"GymFlow là hệ thống web hỗ trợ một chi nhánh phòng gym quản lý hội viên, gói tập, đăng ký gói, thanh toán, check in, chăm sóc hội viên, chi phí và báo cáo. Hệ thống có ba vai trò quản lý, nhân viên và hội viên; mỗi vai trò chỉ được truy cập đúng chức năng và dữ liệu cần thiết.")
    b.add_para(doc,"Giải pháp sử dụng Next.js 16, React 19, TypeScript, Zod, Supabase Auth và PostgreSQL. Các nghiệp vụ có nguy cơ sai lệch như bán gói, check in, đóng băng và hủy thanh toán được hiện thực bằng hàm cơ sở dữ liệu để bảo đảm tính nguyên tử. Phân quyền được kiểm tra tại API và Row Level Security.")
    b.add_para(doc,"Báo cáo được tổ chức theo bảy chương: giới thiệu; khảo sát và yêu cầu; thiết kế; xây dựng; kiểm thử; áp dụng Agile Scrum; kết luận. Kết quả kiểm chứng ngày 22 tháng 9 năm 2026 gồm 16 kiểm thử đạt, lint không có lỗi và build production thành công với 23 route.")
    b.add_para(doc,"Từ khóa quản lý phòng gym Next.js Supabase PostgreSQL Agile Scrum",bold_lead="Từ khóa ",indent=False)
    page(doc,"Abstract",1)
    b.add_para(doc,"GymFlow is a web based management system for a single branch gym. It supports member records, membership plans, subscription sales and renewals, payments, QR or member code check in, retention follow ups, expenses, reports, and a member self service portal.")
    b.add_para(doc,"The application uses Next.js 16, React 19, TypeScript, Zod, Supabase Auth, and PostgreSQL. Critical operations are implemented as database functions to keep related changes atomic. Server side role checks are combined with Row Level Security. The report follows seven chapters and limits the Scrum chapter to product backlog, sprint planning, sprint execution, and sprint results.")
    b.add_para(doc,"At the verification checkpoint on 22 September 2026, all 16 automated tests pass, lint reports no findings, and the optimized production build succeeds with 23 routes.")
    page(doc,"Mục lục",1)
    entries=[("1 Giới thiệu đề tài",9),("2 Khảo sát và phân tích yêu cầu",14),("3 Thiết kế hệ thống",24),("4 Xây dựng hệ thống",34),("5 Kiểm thử hệ thống",44),("6 Áp dụng Agile Scrum",50),("7 Kết luận",56),("Tài liệu tham khảo",59),("Phụ lục",60)]
    for label,num in entries: b.add_toc_line(doc,label,num,True)
    page(doc,"Danh mục hình và bảng",1)
    b.add_table(doc,["Ký hiệu","Nội dung"],[("Hình 2.1","Use Case Diagram"),("Hình 3.1","Kiến trúc hệ thống"),("Hình 3.2","Mô hình quan hệ dữ liệu"),("Hình 3.3","Class Diagram"),("Hình 3.4","Sequence Diagram check in"),("Hình 3.5","Activity Diagram bán gói"),("Hình 4.1 đến 4.5","Giao diện kết quả"),("Bảng 2.1","Ma trận phân quyền"),("Bảng 5.1","Test Case tiêu biểu"),("Bảng 6.1","Product Backlog")],widths=[1.5,4.9],font_size=9.5)
    page(doc,"Danh mục từ viết tắt",1)
    b.add_table(doc,["Từ viết tắt","Diễn giải"],[("API","Application Programming Interface"),("CRUD","Create Read Update Delete"),("MVP","Minimum Viable Product"),("QR","Quick Response code"),("RBAC","Role Based Access Control"),("RLS","Row Level Security"),("RPC","Remote Procedure Call"),("UAT","User Acceptance Testing")],widths=[1.5,4.9],font_size=10)


def chapter1(doc):
    page(doc,"1 Giới thiệu đề tài",1)
    doc.add_heading("1.1 Lý do chọn đề tài",level=2)
    b.add_para(doc,"Hoạt động của phòng gym phát sinh dữ liệu liên tục tại quầy lễ tân: hồ sơ hội viên, thời hạn gói, lượt tập, thanh toán và lịch sử check in. Khi các dữ liệu này được lưu ở sổ, bảng tính hoặc nhiều nhóm nhắn tin, nhân viên mất thời gian đối chiếu và dễ xử lý sai. Quản lý cũng khó biết doanh thu thực, chi phí và số hội viên cần chăm sóc.")
    b.add_para(doc,"Bài toán phù hợp môn Công nghệ phần mềm vì có nhiều vai trò, trạng thái, giao dịch và yêu cầu bảo mật. Một lượt check in phải kiểm tra hội viên, gói, ngày hiệu lực, trạng thái đóng băng, số lượt và lần quét gần nhất. Một giao dịch bán gói phải tạo subscription, payment, phiếu thu và nhật ký trong cùng một luồng nhất quán.")
    b.add_para(doc,"Đề tài GymFlow được chọn để xây dựng một sản phẩm có thể chạy được, đồng thời thể hiện đầy đủ quá trình khảo sát, phân tích, thiết kế, hiện thực, kiểm thử và quản lý sprint.")
    page(doc,"1.2 Mục tiêu",2)
    b.add_para(doc,"Mục tiêu tổng quát là xây dựng hệ thống web quản lý tập trung cho một chi nhánh phòng gym, giúp giảm thao tác thủ công, bảo đảm dữ liệu giao dịch và cung cấp thông tin đúng cho quản lý, nhân viên cùng hội viên.")
    b.add_bullets(doc,["Quản lý hồ sơ hội viên, trạng thái, mã hội viên và QR token.","Quản lý gói tập, bán mới, gia hạn, đóng băng và lịch sử subscription.","Ghi nhận payment, phiếu thu, phương thức thanh toán và hủy có lý do.","Check in bằng QR hoặc mã hội viên, chống quét trùng và trừ lượt nguyên tử.","Cung cấp dashboard, báo cáo hội viên, doanh thu, chi phí và lợi nhuận.","Cho phép hội viên xem QR, gói, thanh toán và lịch sử của chính mình."])
    b.add_para(doc,"Mục tiêu chất lượng là kiểm soát quyền theo vai trò, bảo vệ dữ liệu bằng RLS, giữ khóa service role ở server, kiểm thử các quy tắc quan trọng và tạo được bản build production.")
    page(doc,"1.3 Phạm vi",2)
    b.add_table(doc,["Trong phạm vi","Ngoài phạm vi MVP"],[("Một chi nhánh","Chuỗi nhiều chi nhánh"),("Tiền mặt và chuyển khoản ghi nhận thủ công","Cổng thanh toán và đối soát tự động"),("QR token ngẫu nhiên","Thiết bị cửa kiểm soát chuyên dụng"),("Báo cáo vận hành và tài chính cơ bản","Dự báo kinh doanh nâng cao"),("Tài khoản theo lời mời","Đăng ký công khai"),("Portal hội viên","Ứng dụng di động native")],widths=[3.2,3.2],font_size=9)
    b.add_para(doc,"Phạm vi được giữ ở mức MVP để hoàn thiện chuỗi nghiệp vụ cốt lõi trong thời lượng môn học. Các hạng mục ngoài phạm vi được xem là hướng phát triển chứ không được đưa vào sprint hiện tại.")
    page(doc,"1.4 Đối tượng sử dụng",2)
    b.add_table(doc,["Đối tượng","Mục đích sử dụng","Quyền nổi bật"],[("Quản lý","Điều hành và kiểm soát","Gói tập, nhân viên, hủy payment, báo cáo, chi phí"),("Nhân viên","Vận hành quầy","Hội viên, bán gói, check in, chăm sóc"),("Hội viên","Tự phục vụ","Xem QR, gói, payment, check in và cập nhật liên hệ")],widths=[1.2,2.4,2.8],font_size=9)
    b.add_para(doc,"Quyền được cấp theo nguyên tắc tối thiểu. Staff không xem báo cáo tài chính hoặc quản lý nhân viên. Member chỉ truy cập dữ liệu liên kết với profile của chính mình.")
    page(doc,"1.5 Công nghệ và phương pháp phát triển",2)
    b.add_para(doc,"Hệ thống dùng Next.js App Router cho trang và Route Handler, React cho giao diện, TypeScript cho kiểm tra kiểu, Zod cho validation, Supabase Auth cho phiên đăng nhập và PostgreSQL cho lưu trữ. Tailwind CSS hỗ trợ responsive; Vitest và oxlint hỗ trợ kiểm thử cùng kiểm tra chất lượng.")
    b.add_para(doc,"Quá trình phát triển áp dụng Scrum theo hướng thực dụng. Product Backlog được chia thành sáu sprint, mỗi sprint có mục tiêu và Increment chạy được. Phần Agile Scrum của báo cáo chỉ trình bày backlog, sprint plan và kết quả, không lặp lại lý thuyết chung.")
    b.add_para(doc,"Mã nguồn được quản lý theo migration và kiểm chứng bằng ba bước `npm test`, `npm run lint` và `npm run build`. Những nghiệp vụ cần nguyên tử được đưa xuống PostgreSQL function.")


def chapter2(doc,v):
    page(doc,"2 Khảo sát và phân tích yêu cầu",1)
    doc.add_heading("2.1 Mô tả bài toán",level=2)
    b.add_para(doc,"Phòng gym cần quản lý toàn bộ vòng đời hội viên từ tiếp nhận thông tin, bán gói, thu tiền, sử dụng dịch vụ đến gia hạn hoặc ngừng hoạt động. Dữ liệu phải phản ánh trạng thái theo thời gian và giữ được lịch sử. Một hội viên có thể có gói đang dùng và gói gia hạn chờ hiệu lực; payment có thể bị hủy nhưng không được xóa; gói có thể tạm đóng băng rồi được kéo dài ngày kết thúc.")
    b.add_para(doc,"Tại quầy, tốc độ và phản hồi rõ là yêu cầu quan trọng. Nhân viên phải tìm hội viên nhanh, quét QR và biết ngay vì sao một lượt vào bị từ chối. Ở góc nhìn quản lý, hệ thống phải cho phép đối chiếu doanh thu, chi phí, trạng thái giao dịch và người đã thao tác.")
    b.add_para(doc,"Hội viên cần một khu vực riêng để xem dữ liệu của mình mà không gọi lễ tân. Điều này đặt ra yêu cầu phân quyền ở cả API và database, vì chỉ ẩn menu trên giao diện không đủ bảo vệ dữ liệu.")
    page(doc,"2.2 Các đối tượng sử dụng hệ thống",2)
    b.add_para(doc,"Quản lý chịu trách nhiệm cấu hình và kiểm soát. Nhân viên xử lý nghiệp vụ hằng ngày. Hội viên là người nhận dịch vụ và tự xem dữ liệu. Ngoài ba tác nhân trực tiếp, kế toán và người vận hành là bên liên quan gián tiếp vì cần đối chiếu chứng từ, migration, sao lưu và khôi phục.")
    b.add_table(doc,["Tác nhân","Nhu cầu","Rủi ro"],[("Quản lý","Số liệu chính xác và quyền kiểm soát","Hủy nhầm giao dịch hoặc mất audit"),("Nhân viên","Thao tác nhanh và thông báo rõ","Nhầm hội viên hoặc thao tác trùng"),("Hội viên","Xem dữ liệu cá nhân","Lộ dữ liệu của người khác"),("Kế toán","Đối chiếu thu chi","Xóa cứng hoặc thiếu lý do hủy"),("Vận hành","Triển khai ổn định","Lộ khóa hoặc migration lỗi")],widths=[1.1,2.7,2.6],font_size=9)
    page(doc,"2.3 Yêu cầu chức năng",2)
    b.add_bullets(doc,["Đăng nhập, quên mật khẩu, xác nhận lời mời và bắt buộc đổi mật khẩu tạm.","Tạo, tìm kiếm, lọc, cập nhật, đổi trạng thái và mời tài khoản hội viên.","Tạo, sửa, bật tắt kinh doanh gói tập với giá, thời hạn và giới hạn lượt.","Bán mới, gia hạn nối tiếp, đóng băng và mở lại subscription.","Ghi nhận payment, phiếu thu, danh sách và hủy payment có lý do.","Check in bằng QR hoặc mã hội viên, kiểm tra điều kiện và chống trùng.","Dashboard, báo cáo hội viên, doanh thu, check in, chi phí và lợi nhuận.","Portal hội viên và module chăm sóc khách sắp hết hạn hoặc gần hết lượt."])
    b.add_para(doc,"Mỗi chức năng phải xác định tác nhân, tiền điều kiện, đầu vào, kết quả và nhánh lỗi. Những chức năng thay đổi tiền, lượt hoặc trạng thái không được thực hiện bằng nhiều request độc lập nếu có thể tạo dữ liệu dở dang.")
    page(doc,"2.4 Yêu cầu phi chức năng",2)
    b.add_table(doc,["Nhóm","Yêu cầu","Cách kiểm chứng"],[("Bảo mật","Session, RBAC, RLS và giữ bí mật service role","Test theo vai trò và rà soát cấu hình"),("Toàn vẹn","Giao dịch trọng yếu nguyên tử","Integration test RPC"),("Hiệu năng","Phản hồi phù hợp một chi nhánh","Index, giới hạn dữ liệu và đo API"),("Khả dụng","Tiếng Việt, responsive, lỗi rõ","UAT desktop và mobile"),("Bảo trì","TypeScript, module, migration","Lint, build và review source"),("Truy vết","Thao tác quan trọng có audit","Đối chiếu actor action entity")],widths=[1.1,3.0,2.3],font_size=8.7)
    b.add_para(doc,"Yêu cầu phi chức năng được xem là điều kiện hoàn thành, không phải phần bổ sung sau khi giao diện chạy. Một chức năng đúng nghiệp vụ nhưng cho sai vai trò truy cập vẫn bị xem là chưa đạt.")
    page(doc,"2.5 Ma trận phân quyền",2)
    b.add_table(doc,["Chức năng","Manager","Staff","Member"],[("Dashboard","Có","Có","Không"),("Hội viên","Có","Có","Hồ sơ mình"),("Gói tập","Quản lý","Chỉ xem","Xem liên quan"),("Bán và gia hạn","Có","Có","Không"),("Check in","Có","Có","Không"),("Đóng băng","Có","Không","Không"),("Hủy payment","Có","Không","Không"),("Nhân viên và chi phí","Có","Không","Không"),("Portal cá nhân","Không","Không","Có")],widths=[3.0,1.1,1.1,1.2],font_size=9)
    b.caption(doc,"Bảng 2.1 Ma trận phân quyền")
    b.add_para(doc,"API sử dụng `requireActor` để kiểm tra role. RLS tiếp tục giới hạn row tại database. Hai lớp này bảo vệ các đường truy cập khác nhau và không thay thế cho nhau.")
    page(doc,"2.6 Use Case Diagram",2)
    b.add_picture(doc,v["usecase"],6.35,"Hình 2.1 Use Case Diagram của hệ thống GymFlow")
    b.add_para(doc,"Use Case Diagram thể hiện ba tác nhân chính. Manager kế thừa phần lớn nghiệp vụ quầy và có thêm quyền quản trị. Staff tập trung vào hội viên, bán gói và check in. Member sử dụng cổng cá nhân.")
    page(doc,"2.7 Đặc tả Use Case đăng nhập",2)
    b.add_table(doc,["Mục","Nội dung"],[("Tác nhân","Manager Staff Member"),("Tiền điều kiện","Tài khoản tồn tại và active"),("Đầu vào","Email hoặc username và mật khẩu"),("Luồng chính","Xác thực session nạp profile điều hướng theo role"),("Ngoại lệ","Sai thông tin tài khoản inactive hoặc phải đổi mật khẩu"),("Hậu điều kiện","Phiên hợp lệ và truy cập đúng khu vực")],widths=[1.45,4.95],font_size=9)
    b.add_para(doc,"Nhân viên mới dùng mật khẩu tạm và bị chuyển tới màn hình đổi mật khẩu. Member đi vào portal; manager và staff đi vào admin. Route được bảo vệ lại ở server nên nhập URL trực tiếp không vượt quyền.")
    page(doc,"2.8 Đặc tả Use Case bán và gia hạn gói",2)
    b.add_numbered(doc,["Nhân viên chọn hội viên đang active.","Hệ thống hiển thị gói đang kinh doanh.","Nhân viên chọn gói, phương thức và ngày bắt đầu.","API xác thực dữ liệu và vai trò.","RPC xác định bán mới hoặc gia hạn nối tiếp.","Hệ thống tạo subscription, snapshot, payment, phiếu thu và audit log.","Giao diện hiển thị kết quả để đối chiếu."])
    b.add_para(doc,"Nếu dữ liệu không hợp lệ, giao dịch không ghi một phần. Gói gia hạn bắt đầu sau ngày kết thúc gần nhất và có trạng thái scheduled khi chưa đến ngày hiệu lực.")
    page(doc,"2.9 Đặc tả Use Case check in",2)
    b.add_table(doc,["Mục","Nội dung"],[("Tác nhân","Manager hoặc Staff"),("Đầu vào","QR token hoặc member code"),("Kiểm tra","Member active gói hiệu lực không frozen còn lượt không trùng 10 phút"),("Thành công","Tạo check in trừ lượt nếu cần và ghi audit"),("Thất bại","Trả reason cụ thể và không đổi dữ liệu")],widths=[1.35,5.05],font_size=9)
    b.add_para(doc,"Các reason chính gồm INVALID QR, MEMBER INACTIVE, NO VALID SUBSCRIPTION, NOT STARTED, FROZEN, EXPIRED, NO VISITS LEFT và DUPLICATE. Giao diện ánh xạ reason thành thông báo tiếng Việt.")
    page(doc,"2.10 Đặc tả Use Case hủy thanh toán",2)
    b.add_para(doc,"Manager chọn một payment valid và nhập lý do. API từ chối role khác hoặc lý do quá ngắn. RPC khóa payment, đổi status thành cancelled, lưu thời điểm, người hủy và lý do, sau đó cập nhật subscription theo quy tắc. Audit log ghi lại hành động.")
    b.add_para(doc,"Use Case không xóa payment vì lịch sử cần cho đối chiếu. Tổng doanh thu chỉ cộng payment valid. Nếu payment đã cancelled, yêu cầu lặp lại trả conflict thay vì thay đổi lần nữa.")


def chapter3(doc,v):
    page(doc,"3 Thiết kế hệ thống",1)
    doc.add_heading("3.1 Kiến trúc hệ thống",level=2)
    b.add_picture(doc,v["architecture"],6.35,"Hình 3.1 Kiến trúc tổng thể GymFlow")
    b.add_para(doc,"Kiến trúc gồm lớp giao diện Next.js và React, lớp ứng dụng là Route Handler cùng RBAC và Zod, lớp dữ liệu là PostgreSQL với RLS, index và RPC. Supabase Auth quản lý phiên. Service role chỉ chạy ở server.")
    page(doc,"3.2 Thiết kế các thành phần",2)
    b.add_table(doc,["Thành phần","Trách nhiệm","Tệp đại diện"],[("Trang","Điều hướng theo role","app page admin portal"),("Giao diện quản trị","Dashboard và nghiệp vụ quầy","components gym-app"),("Portal","Dữ liệu hội viên","components member-portal"),("API","Xác thực validate điều phối","app api"),("Authz","Nạp actor và role","lib authz"),("Nghiệp vụ","Check in và tài chính","lib check-in operations"),("Database","Schema policy RPC seed","supabase migrations")],widths=[1.35,2.85,2.2],font_size=8.7)
    b.add_para(doc,"Các module dùng hợp đồng JSON và kiểu TypeScript. Logic thuần được tách để unit test; nghiệp vụ cần transaction được đặt trong RPC.")
    page(doc,"3.3 Thiết kế cơ sở dữ liệu",2)
    b.add_picture(doc,v["erd"],6.35,"Hình 3.2 Mô hình quan hệ dữ liệu chính")
    b.add_para(doc,"Member tách khỏi profile để phòng gym có thể tạo hồ sơ trước khi mời tài khoản. Subscription liên kết member và plan, đồng thời lưu snapshot tên, giá, thời hạn và lượt để lịch sử không thay đổi khi plan được sửa.")
    page(doc,"3.4 Từ điển dữ liệu",2)
    b.add_table(doc,["Bảng","Mục đích","Ràng buộc quan trọng"],[("profiles","Danh tính và role","auth user unique status active inactive"),("members","Hồ sơ hội viên","member code và QR unique"),("membership_plans","Sản phẩm gói","price không âm duration dương"),("subscriptions","Quyền sử dụng","status date remaining visits"),("payments","Giao dịch thu","receipt unique một valid mỗi subscription"),("check_ins","Lịch sử vào tập","member subscription actor time"),("subscription_freezes","Kỳ đóng băng","một active mỗi subscription"),("audit_logs","Truy vết","actor action entity details")],widths=[1.7,2.5,2.2],font_size=8.5)
    b.add_para(doc,"Migration còn có follow up, notification, expense và các bảng lớp học trong lịch sử. Module đặt lớp đã được loại khỏi phạm vi giao diện ở migration sau và không được xem là chức năng MVP hiện tại.")
    page(doc,"3.5 Class Diagram",2)
    b.add_picture(doc,v["class"],6.35,"Hình 3.3 Class Diagram miền nghiệp vụ")
    b.add_para(doc,"Class Diagram mô tả các đối tượng nghiệp vụ thay vì ánh xạ một một toàn bộ bảng. Profile cung cấp role, Member đại diện khách hàng, Subscription thể hiện quyền sử dụng, còn Payment và CheckIn là giao dịch phát sinh.")
    page(doc,"3.6 Sequence Diagram check in",2)
    b.add_picture(doc,v["sequence"],6.35,"Hình 3.4 Sequence Diagram cho luồng check in")
    b.add_para(doc,"Sequence cho thấy validation quyền diễn ra trước RPC. PostgreSQL khóa và kiểm tra dữ liệu, sau đó ghi check in, trừ lượt và audit trong một transaction. API trả 201 khi thành công hoặc 409 cho xung đột nghiệp vụ.")
    page(doc,"3.7 Activity Diagram bán gói",2)
    b.add_picture(doc,v["activity"],6.35,"Hình 3.5 Activity Diagram bán và gia hạn gói")
    b.add_para(doc,"Activity Diagram nhấn mạnh nhánh dữ liệu không hợp lệ và ranh giới transaction. Không có trạng thái subscription đã tạo nhưng thiếu payment trong luồng bán đủ tiền.")
    page(doc,"3.8 Thiết kế trạng thái đăng ký gói",2)
    b.add_picture(doc,v["subscription"],6.35,"Hình 3.6 Vòng đời đăng ký gói tập")
    b.add_para(doc,"Scheduled dành cho gói kế tiếp, active dành cho quyền đang dùng, frozen là tạm dừng, expired là hết hạn tự nhiên và cancelled là hủy hành chính hoặc giao dịch. Mỗi chuyển trạng thái phải có nghiệp vụ và audit tương ứng.")
    page(doc,"3.9 Thiết kế phân quyền và bảo mật",2)
    b.add_para(doc,"Supabase Auth xác thực user. `currentActor` nạp profile active và `requireActor` kiểm tra role cùng cờ đổi mật khẩu. Route dùng admin client chỉ sau bước này. RLS tiếp tục giới hạn row đối với client authenticated.")
    b.add_bullets(doc,["Không đưa service role key xuống browser.","QR chỉ chứa UUID ngẫu nhiên, không chứa thông tin cá nhân.","Function security definer giới hạn quyền execute và đặt search path.","Payment, check in và audit không bị xóa cứng.","Manager cuối cùng không thể bị vô hiệu hóa hoặc hạ quyền."])
    page(doc,"3.10 Thiết kế giao diện",2)
    b.add_para(doc,"Giao diện quản trị dùng sidebar theo module, tiêu đề trang, thẻ số liệu, bảng dữ liệu và dialog. Màn hình check in ưu tiên ô quét cùng phản hồi lớn. Portal hội viên tách khỏi khu vực admin và tối ưu cho điện thoại.")
    b.add_table(doc,["Nguyên tắc","Áp dụng"],[("Nhất quán","Tên module trạng thái màu và thông báo dùng thống nhất"),("Phản hồi","Có loading success error và reason cụ thể"),("Responsive","Bảng và điều hướng thích ứng màn hình nhỏ"),("An toàn","Xác nhận thao tác hủy và yêu cầu lý do"),("Khả dụng","Nhãn tiếng Việt target bấm rõ dữ liệu rỗng có hướng dẫn")],widths=[1.5,4.9],font_size=9)


def chapter4(doc,v):
    page(doc,"4 Xây dựng hệ thống",1)
    doc.add_heading("4.1 Công nghệ sử dụng",level=2)
    b.add_table(doc,["Công nghệ","Phiên bản","Vai trò"],[("Next.js","16.3.4","Framework web và Route Handler"),("React","19.2.6","Giao diện component"),("TypeScript","5.9.3","Kiểm tra kiểu"),("Supabase JS","2.116.0","Auth và truy cập database"),("Zod","4.6.1","Validation runtime"),("Vitest","5.0.0","Unit test"),("Tailwind CSS","4.2.1","Responsive UI")],widths=[1.5,1.3,3.6],font_size=9)
    b.add_para(doc,"Project yêu cầu Node.js từ 22.13.0. Next.js App Router cho phép đặt trang và API trong cùng project. PostgreSQL function xử lý giao dịch dữ liệu chuyên sâu.")
    page(doc,"4.2 Cấu trúc mã nguồn",2)
    b.add_table(doc,["Thư mục","Nội dung"],[("app","Page layout auth route và API"),("components","Ứng dụng quản trị portal và UI component"),("lib","Authz HTTP validation nghiệp vụ Supabase client"),("supabase migrations","Schema constraint policy function"),("supabase seed","Dữ liệu mẫu có UUID cố định"),("lib test","Test check in tài chính validation")],widths=[2.0,4.4],font_size=9)
    b.add_para(doc,"Source có 113 tệp TypeScript hoặc TSX với khoảng 12.258 dòng, 20 Route Handler và 6 migration. `gym-app.tsx` là component lớn cần tách theo feature khi mở rộng.")
    page(doc,"4.3 Các chức năng xác thực và tài khoản",2)
    b.add_para(doc,"Trang gốc điều hướng theo actor. Login, forgot password, callback, confirm và update password tạo chuỗi xác thực hoàn chỉnh. Tài khoản staff dùng username và mật khẩu tạm, sau đó buộc đổi mật khẩu. Member được mời từ hồ sơ có email.")
    b.add_para(doc,"API đổi mật khẩu yêu cầu tối thiểu tám ký tự và từ chối dùng `admin123`. Profile inactive bị coi như không có quyền. Manager không thể tự khóa hoặc làm mất manager active cuối cùng.")
    page(doc,"4.4 Các chức năng hội viên và gói tập",2)
    b.add_para(doc,"Hội viên hỗ trợ tạo, tìm kiếm, lọc, cập nhật, đổi trạng thái, mời tài khoản và xuất báo cáo. API kiểm tra trùng điện thoại hoặc email, sinh mã hội viên và QR token. Mọi cập nhật quan trọng được ghi audit.")
    b.add_para(doc,"Gói tập có tên, giá, số ngày, lượt tùy chọn, mô tả, điều khoản và trạng thái kinh doanh. Manager quản lý gói; staff chỉ đọc để bán. Việc ngừng bán không xóa plan cũ.")
    page(doc,"4.5 Các chức năng đăng ký và thanh toán",2)
    b.add_para(doc,"RPC `sell_membership` xác định ngày bắt đầu, ngày kết thúc, sale type và status, sau đó tạo snapshot, subscription, payment, receipt code cùng audit. Gia hạn nối tiếp tránh chồng thời gian. Unique index ngăn nhiều payment valid cho một subscription.")
    b.add_para(doc,"Freeze và unfreeze chỉ dành cho manager. Hủy payment yêu cầu lý do và dùng soft cancel. Doanh thu chỉ cộng payment valid.")
    page(doc,"4.6 Chức năng check in",2)
    b.add_picture(doc,v["checkin"],6.35,"Hình 4.1 Luồng xử lý check in đã hiện thực")
    b.add_para(doc,"Giao diện hỗ trợ camera QR và nhập mã thủ công. API xác thực role rồi gọi RPC. Hàm database dùng khóa bản ghi để ngăn hai request cùng trừ lượt. Nhánh lỗi được trả bằng reason có thể hiển thị cho lễ tân.")
    page(doc,"4.7 Chức năng báo cáo chăm sóc và chi phí",2)
    b.add_para(doc,"Dashboard tổng hợp doanh thu tháng, hội viên, check in và gói bán nhiều. Module chăm sóc tìm subscription sắp hết hạn hoặc còn không quá ba lượt, cho phép phân công và ghi lịch liên hệ. Module chi phí ghi danh mục, số tiền, ngày, chứng từ và trạng thái.")
    b.add_para(doc,"Lợi nhuận được tính bằng payment valid trừ expense valid trong khoảng ngày. Khi dữ liệu tăng, phần tổng hợp nên chuyển về database và bổ sung phân trang.")
    page(doc,"4.8 Giao diện kết quả tổng quan",2)
    b.add_picture(doc,v["ui"][0],6.35,"Hình 4.2 Giao diện tổng quan được dựng theo cấu trúc UI của project")
    b.add_para(doc,"Màn hình tổng quan đặt chỉ số ở đầu và lịch sử gần đây bên dưới. Các số trong hình dùng dữ liệu demo để minh họa bố cục.")
    page(doc,"4.9 Giao diện kết quả quản lý hội viên",2)
    b.add_picture(doc,v["ui"][1],6.35,"Hình 4.3 Giao diện quản lý hội viên")
    b.add_para(doc,"Danh sách hiển thị mã, tên, điện thoại và trạng thái. Bộ lọc và tìm kiếm hỗ trợ thao tác tại quầy; các form tạo và cập nhật nằm trong dialog.")
    page(doc,"4.10 Giao diện kết quả check in và portal",2)
    b.add_picture(doc,v["ui"][2],6.1,"Hình 4.4 Giao diện check in")
    b.add_picture(doc,v["ui"][3],6.1,"Hình 4.5 Giao diện cổng hội viên")


def chapter5(doc):
    page(doc,"5 Kiểm thử hệ thống",1)
    doc.add_heading("5.1 Phương pháp kiểm thử",level=2)
    b.add_para(doc,"Kiểm thử được tổ chức theo nhiều lớp. Unit test kiểm tra hàm thuần và quy tắc biên. API test cần kiểm tra validation, phân quyền và mã trạng thái. Integration test xác minh RPC, constraint, RLS và transaction. UAT đi theo user story trên giao diện.")
    b.add_para(doc,"Project hiện có bằng chứng tự động cho unit test, lint, TypeScript và production build. Integration test Supabase cùng end to end browser là hạng mục cần hoàn thiện trước khi vận hành thật.")
    page(doc,"5.2 Test Case check in",2)
    b.add_table(doc,["Mã","Dữ liệu","Kết quả mong đợi"],[("CI01","Member active gói active còn lượt","Cho phép và trừ một lượt"),("CI02","Gói unlimited","Cho phép không trừ lượt"),("CI03","Member inactive","MEMBER INACTIVE"),("CI04","Không có gói active","NO ACTIVE SUBSCRIPTION"),("CI05","Gói chưa bắt đầu","NOT STARTED"),("CI06","Gói frozen","FROZEN"),("CI07","Gói hết hạn","EXPIRED"),("CI08","Còn 0 lượt","NO VISITS LEFT"),("CI09","Quét lại sau 5 phút","DUPLICATE")],widths=[.7,3.2,2.5],font_size=8.7)
    b.caption(doc,"Bảng 5.1 Test Case check in")
    page(doc,"5.3 Test Case chức năng nghiệp vụ",2)
    b.add_table(doc,["Mã","Kịch bản","Kết quả"],[("MB01","Tạo hội viên trùng điện thoại","409 và không tạo"),("PL01","Staff tạo gói","403"),("SB01","Gia hạn khi gói cũ còn hiệu lực","Tạo scheduled nối tiếp"),("PM01","Staff hủy payment","403"),("PM02","Manager hủy với lý do hợp lệ","Cancelled và có audit"),("PT01","Member A đọc member B","Bị RLS từ chối"),("EX01","Tổng tài chính có bản ghi cancelled","Bỏ qua bản ghi cancelled")],widths=[.7,3.4,2.3],font_size=8.7)
    b.add_para(doc,"Các test API và RLS trong bảng là bộ tiêu chí cần tự động hóa thêm. Chúng không được ghi là đạt nếu chưa chạy trên database test.")
    page(doc,"5.4 Dữ liệu kiểm thử",2)
    b.add_para(doc,"Seed data có bốn profile, sáu hội viên, năm gói, sáu subscription, sáu payment, năm check in, một freeze, một follow up, một expense và audit log. Các trạng thái gồm active, scheduled, frozen, expired, cancelled, inactive và chưa mua gói.")
    b.add_table(doc,["Mã","Trạng thái","Mục đích"],[("GF DEMO01","Active và scheduled","Bán gia hạn"),("GF DEMO02","Còn 3 lượt sắp hết hạn","Retention và theo lượt"),("GF DEMO03","Frozen","Từ chối check in"),("GF DEMO04","Expired","Lịch sử hết hạn"),("GF DEMO05","Inactive cancelled","Chặn nghiệp vụ"),("GF DEMO06","Chưa có gói","Bán mới")],widths=[1.4,2.3,2.7],font_size=9)
    page(doc,"5.5 Kết quả kiểm thử tự động",2)
    b.add_table(doc,["Hạng mục","Kết quả ngày 22 tháng 9 năm 2026","Bằng chứng"],[("Vitest","Đạt","3 tệp test 16 test pass"),("oxlint","Đạt","Không có finding"),("TypeScript","Đạt","Next build hoàn thành type checking"),("Production build","Đạt","Compiled successfully 23 route"),("Integration Supabase","Chưa đầy đủ","Cần pipeline database"),("End to end","Chưa đầy đủ","Cần Playwright hoặc tương đương")],widths=[1.55,2.4,2.45],font_size=8.7)
    b.add_para(doc,"Kết quả chứng minh source có thể build và các quy tắc đã viết test hoạt động. Kết quả không thay thế kiểm thử kết nối production, tải hoặc khôi phục dữ liệu.")
    page(doc,"5.6 Kiểm thử chấp nhận",2)
    b.add_numbered(doc,["Đăng nhập bằng ba vai trò và kiểm tra điều hướng.","Tạo hội viên mới rồi tìm lại theo mã và số điện thoại.","Bán gói và xác nhận subscription payment receipt audit.","Gia hạn và xác nhận gói mới scheduled nối tiếp.","Check in hợp lệ rồi quét lại trong mười phút.","Đóng băng và xác nhận check in bị từ chối.","Member đăng nhập portal và chỉ thấy dữ liệu của mình.","Manager xem báo cáo và đối chiếu bản ghi cancelled."])
    b.add_para(doc,"Sprint Review nên dùng cùng một checklist UAT để các kết quả có thể so sánh giữa các phiên bản.")


def chapter6(doc,v):
    page(doc,"6 Áp dụng Agile Scrum",1)
    doc.add_heading("6.1 Product Backlog",level=2)
    backlog=[("US01","Đăng nhập và phân quyền","Must",5),("US02","Quản lý nhân viên","Should",5),("US03","CRUD hội viên","Must",5),("US04","Quản lý gói","Must",5),("US05","Bán gói","Must",8),("US06","Gia hạn nối tiếp","Must",5),("US07","Check in QR","Must",8),("US08","Đóng băng gói","Should",5),("US09","Hủy payment","Must",5),("US10","Dashboard và báo cáo","Should",5),("US11","Portal hội viên","Should",5),("US12","Chăm sóc hội viên","Could",5),("US13","Chi phí và lợi nhuận","Should",5)]
    b.add_table(doc,["ID","User story rút gọn","Ưu tiên","SP"],backlog,widths=[.55,4.7,.75,.4],font_size=8.5)
    b.caption(doc,"Bảng 6.1 Product Backlog")
    b.add_para(doc,"Backlog được ưu tiên theo tần suất sử dụng, ảnh hưởng tài chính, rủi ro dữ liệu và phụ thuộc. Story point phản ánh độ phức tạp tương đối.")
    page(doc,"6.2 Chia Sprint",2)
    b.add_table(doc,["Sprint","Mục tiêu","Story chính"],[("Sprint 1","Nền tảng xác thực và dữ liệu","US01 US02"),("Sprint 2","Quản lý dữ liệu chủ","US03 US04"),("Sprint 3","Luồng bán hàng","US05 US06 US09"),("Sprint 4","Kiểm soát sử dụng","US07 US08"),("Sprint 5","Tự phục vụ và báo cáo","US10 US11"),("Sprint 6","Hoàn thiện vận hành","US12 US13 test build")],widths=[.9,2.45,3.05],font_size=9)
    b.add_para(doc,"Mỗi sprint tạo một Increment có thể chạy. Các hạng mục chưa đạt tiêu chí chấp nhận không được tính Done và quay lại Product Backlog.")
    page(doc,"6.3 Kế hoạch Sprint 1 và Sprint 2",2)
    b.add_table(doc,["Sprint","Công việc","Tiêu chí hoàn thành"],[("1","Khởi tạo Next.js Supabase schema profiles auth route role","Ba vai trò đăng nhập và điều hướng đúng"),("1","Migration và seed nền tảng","Dựng database mới thành công"),("2","CRUD hội viên QR tìm kiếm lọc","Tạo sửa tìm và đổi trạng thái"),("2","CRUD gói tập","Manager tạo sửa bật tắt; staff chỉ xem")],widths=[.7,3.2,2.5],font_size=8.7)
    b.add_para(doc,"Rủi ro chính là thiếu dữ liệu vai trò và component tăng nhanh. Hành động giảm rủi ro là tạo seed sớm và tách helper xác thực dùng chung.")
    page(doc,"6.4 Kế hoạch Sprint 3 và Sprint 4",2)
    b.add_table(doc,["Sprint","Công việc","Tiêu chí hoàn thành"],[("3","RPC bán gói gia hạn payment receipt","Tạo dữ liệu nguyên tử và có audit"),("3","Hủy payment","Chỉ manager và bắt buộc lý do"),("4","Check in QR mã hội viên","Bao phủ các reason và chống trùng"),("4","Freeze unfreeze","Không check in khi frozen và kéo dài end date")],widths=[.7,3.2,2.5],font_size=8.7)
    b.add_para(doc,"Sprint 3 và 4 ưu tiên transaction cùng khóa đồng thời. Unit test được viết cho quyết định check in; integration test database được ghi vào backlog chất lượng.")
    page(doc,"6.5 Kế hoạch Sprint 5 và Sprint 6",2)
    b.add_table(doc,["Sprint","Công việc","Tiêu chí hoàn thành"],[("5","Dashboard báo cáo portal","Mỗi role thấy đúng dữ liệu"),("5","Xuất hội viên và lịch sử","Dữ liệu đúng bộ lọc"),("6","Follow up chi phí lợi nhuận","Tính đúng và có audit"),("6","Test lint build tài liệu","16 test pass lint sạch build thành công")],widths=[.7,3.2,2.5],font_size=8.7)
    b.add_para(doc,"Sprint 6 tập trung hoàn thiện, không mở thêm Epic lớn. Những hạng mục như đa chi nhánh và thanh toán trực tuyến được giữ cho release sau.")
    page(doc,"6.6 Kết quả từng Sprint",2)
    b.add_table(doc,["Sprint","Increment đạt được","Điểm cần cải tiến"],[("1","Đăng nhập role schema và seed","Bổ sung test redirect"),("2","Hội viên và gói chạy từ UI đến database","Tách component theo feature"),("3","Bán gia hạn payment và hủy","Thêm integration test RPC"),("4","Check in freeze chống trùng","Test hai request đồng thời"),("5","Dashboard portal và export","Đưa tổng hợp lớn về database"),("6","Follow up chi phí 16 test lint build","Bổ sung E2E monitoring")],widths=[.75,3.2,2.45],font_size=8.7)
    b.add_para(doc,"Kết quả sprint được đánh giá bằng Increment và tiêu chí chấp nhận, không bằng số lượng tệp sửa. Các điểm cần cải tiến trở thành backlog cho vòng tiếp theo.")


def chapter7(doc):
    page(doc,"7 Kết luận",1)
    doc.add_heading("7.1 Kết quả đạt được",level=2)
    b.add_para(doc,"Đề tài đã xây dựng được MVP quản lý phòng gym trên nền tảng web với ba vai trò và chuỗi nghiệp vụ từ hội viên, gói, bán hàng, thanh toán đến check in, báo cáo, portal, chăm sóc và chi phí. Dữ liệu giao dịch có snapshot, constraint và audit.")
    b.add_para(doc,"Kiến trúc Next.js và Supabase phù hợp quy mô đồ án. RBAC, RLS và server only service role tạo nhiều lớp bảo vệ. Các nghiệp vụ trọng yếu dùng RPC để thực thi nguyên tử. Source đã vượt qua 16 test, lint và production build.")
    page(doc,"7.2 Hạn chế",2)
    b.add_para(doc,"Hệ thống hiện chỉ phục vụ một chi nhánh, thanh toán đủ một lần và ghi nhận chuyển khoản thủ công. Chưa có cổng thanh toán, thiết bị kiểm soát cửa, thông báo đa kênh hoặc phân tích dự báo. Module lớp học không còn trong phạm vi giao diện hiện tại.")
    b.add_para(doc,"Bộ kiểm thử tự động chưa bao phủ đầy đủ API, RLS, transaction PostgreSQL và trình duyệt. Component quản trị còn lớn; monitoring, backup restore drill và accessibility cần được hoàn thiện trước khi vận hành thật.")
    page(doc,"7.3 Hướng phát triển",2)
    b.add_bullets(doc,["Tự động hóa integration test cho migration RPC và RLS.","Bổ sung end to end test và kiểm thử accessibility.","Tách giao diện theo feature và sinh type từ schema.","Phát triển đa chi nhánh với policy theo branch.","Tích hợp thanh toán trực tuyến và webhook idempotent.","Bổ sung thông báo email SMS theo consent.","Thiết lập monitoring alert backup và runbook sự cố."])
    b.add_para(doc,"Ưu tiên gần nhất là kiểm thử tích hợp và quan sát vận hành vì chúng giảm rủi ro cho toàn bộ chức năng hiện có. Mở rộng sản phẩm chỉ nên thực hiện sau khi nền tảng chất lượng được củng cố.")


def back_matter(doc):
    page(doc,"Tài liệu tham khảo",1)
    refs=["[1] Agile Manifesto. Manifesto for Agile Software Development. https://agilemanifesto.org/. Truy cập ngày 22 tháng 9 năm 2026.","[2] Ken Schwaber và Jeff Sutherland. Hướng dẫn Scrum 2020 bản tiếng Việt. https://scrumguides.org/docs/scrumguide/v2020/2020-Scrum-Guide-Vietnamese.pdf.","[3] Vercel. Next.js Documentation. https://nextjs.org/docs/app/getting-started.","[4] Microsoft. TypeScript Handbook. https://www.typescriptlang.org/docs/handbook/.","[5] Supabase. Row Level Security. https://supabase.com/docs/guides/database/postgres/row-level-security.","[6] Supabase. Securing your data. https://supabase.com/docs/guides/database/secure-data.","[7] Supabase. Database Functions. https://supabase.com/docs/guides/database/functions.","[8] Zod Documentation. https://zod.dev/.","[9] Vitest Documentation. https://vitest.dev/guide/.","[10] GymFlow project. README, source code, migration, seed và test trong workspace. Đối chiếu ngày 22 tháng 9 năm 2026."]
    for ref in refs:
        p=doc.add_paragraph(); p.paragraph_format.first_line_indent=Inches(-.3); p.paragraph_format.left_indent=Inches(.3); p.paragraph_format.space_after=Pt(8); b.set_font(p.add_run(ref),size=11)
    page(doc,"Phụ lục A Hướng dẫn cài đặt",1)
    b.add_numbered(doc,["Cài Node.js từ phiên bản 22.13.0.","Tạo project Supabase cho môi trường development.","Tạo `.env.local` từ `.env.example` và điền URL publishable key service role key.","Chạy migration theo thứ tự tên.","Cấu hình Site URL redirect invite và recovery.","Tắt public signup nếu chỉ dùng lời mời.","Chạy `npm install`, `npm test`, `npm run lint`, `npm run build`.","Chạy seed chỉ ở development hoặc staging.","Chạy `npm run dev` và mở ứng dụng local."])
    page(doc,"Phụ lục B Danh mục API",1)
    rows=[("GET","api bootstrap","manager staff"),("GET POST","api members","manager staff"),("PATCH","api members id","manager staff"),("GET POST","api plans","manager staff"),("POST","api subscriptions","manager staff"),("POST DELETE","api subscriptions id freeze","manager"),("GET POST","api check ins","manager staff"),("GET","api payments","manager staff"),("POST","api payments id cancel","manager"),("GET PATCH","api portal","member"),("GET POST","api follow ups","manager staff"),("GET POST","api expenses","manager"),("GET POST","api staff","manager")]
    b.add_table(doc,["Phương thức","Endpoint","Vai trò"],rows,widths=[1.2,3.4,1.8],font_size=8.7)
    page(doc,"Phụ lục C Ma trận truy vết",1)
    b.add_table(doc,["Yêu cầu","Thiết kế","Hiện thực","Kiểm thử"],[("Đăng nhập","Auth role","auth routes authz","Redirect role"),("Hội viên","Member QR","members API UI","Validation UAT"),("Bán gói","RPC snapshot","subscriptions API","Integration UAT"),("Check in","Lock rules","check ins RPC","CI01 đến CI09"),("Hủy payment","Soft cancel","cancel RPC","Role conflict audit"),("Portal","RLS scope","portal API UI","Cross member denial"),("Chi phí","Expense status","expenses API","Financial summary")],widths=[1.25,1.55,2.15,1.45],font_size=8.2)
    page(doc,"Phụ lục D Checklist nghiệm thu",1)
    b.add_bullets(doc,["Đã điền thông tin trang bìa.","Mục lục và số trang khớp bản cuối.","Có tài khoản demo cho ba vai trò.","Luồng tạo hội viên bán gói check in portal đã chạy thử.","Test lint build đều đạt trên commit nộp.","Migration dựng được database mới.","Service role key không có trong Git hoặc ảnh chụp.","File Word mở được và không tràn bảng hình."])


def main():
    visuals=make_visuals()
    doc=Document(); b.style_document(doc)
    intro_pages(doc); chapter1(doc); chapter2(doc,visuals); chapter3(doc,visuals); chapter4(doc,visuals); chapter5(doc); chapter6(doc,visuals); chapter7(doc); back_matter(doc)
    doc.core_properties.title="Xây dựng hệ thống quản lý phòng gym trên nền tảng web theo phương pháp Agile Scrum"
    doc.core_properties.subject="Báo cáo môn học Công nghệ phần mềm theo khung 7 chương"
    doc.core_properties.author="[HỌ VÀ TÊN SINH VIÊN]"
    for table in doc.tables:
        b.set_table_borders(table)
        for row in table.rows:
            for cell in row.cells:
                b.set_cell_margins(cell)
    doc.save(DOCX)
    print(DOCX)


if __name__=="__main__":
    main()
