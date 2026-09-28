from PIL import Image, ImageDraw
import build_course_report_7_chapters as art

def canvas(title, height=1120):
    im=Image.new('RGB',(1800,height),'white'); d=ImageDraw.Draw(im)
    d.text((900,55),title,anchor='mm',font=art.font(38,True),fill='black')
    return im,d

def box(d,rect,text,fill='#EAF2F8'):
    d.rounded_rectangle(rect,radius=15,fill=fill,outline='#365F91',width=3)
    d.multiline_text(((rect[0]+rect[2])/2,(rect[1]+rect[3])/2),text,anchor='mm',align='center',font=art.font(26),fill='black',spacing=8)

def line(d,pts,label=None,pos=None):
    d.line(pts,fill='#365F91',width=3)
    if label:
        x,y=pos
        bb=d.textbbox((x,y),label,anchor='mm',font=art.font(23))
        d.rectangle((bb[0]-8,bb[1]-4,bb[2]+8,bb[3]+4),fill='white')
        d.text((x,y),label,anchor='mm',font=art.font(23),fill='black')

def make_all(folder):
    paths={}
    im,d=canvas('Sơ đồ chức năng chính',1200)
    d.rectangle((440,115,1690,1135),outline='#365F91',width=3)
    for label,y in [('Nhân viên',290),('Quản lý',635),('Hội viên',980)]:
        x=170
        d.ellipse((x-25,y-75,x+25,y-25),outline='black',width=3)
        d.line((x,y-25,x,y+65),fill='black',width=3)
        d.line((x-50,y+10,x+50,y+10),fill='black',width=3)
        d.line((x,y+65,x-40,y+110),fill='black',width=3)
        d.line((x,y+65,x+40,y+110),fill='black',width=3)
        d.text((x,y+145),label,anchor='mm',font=art.font(27,True),fill='black')
    # Generalization: manager can perform staff operations.
    line(d,[(170,555),(170,475)])
    d.polygon([(170,455),(158,479),(182,479)],fill='white',outline='black',width=3)
    groups=[(290,[('Quản lý hội viên',195),('Bán và gia hạn gói',290),('Ghi nhận vào tập',385)]),
            (635,[('Gói tập và nhân viên',535),('Hủy thu và tạm dừng gói',635),('Báo cáo và chi phí',735)]),
            (980,[('Xem mã QR và gói cá nhân',885),('Xem lịch sử cá nhân',985)])]
    for actor_y,cases in groups:
        for label,y in cases:
            line(d,[(225,actor_y),(570,y)])
            d.ellipse((570,y-39,1560,y+39),fill='#EAF2F8',outline='#365F91',width=3)
            d.text((1065,y),label,anchor='mm',font=art.font(27),fill='black')
    d.text((1060,1090),'Các vai trò cần đăng nhập trước khi sử dụng',anchor='mm',font=art.font(24),fill='black')
    paths['usecase']=folder/'usecase_plain.png'; im.save(paths['usecase'])

    for kind,title in [('erd','Quan hệ giữa các nhóm dữ liệu'),('class','Sơ đồ lớp của bài toán')]:
        im,d=canvas(title,1190)
        rects=[(75,180,475,470),(700,180,1100,470),(1325,180,1725,470),
               (75,750,475,1040),(700,750,1100,1040),(1325,750,1725,1040)]
        names=['Tài khoản','Hội viên','Loại gói tập','Khoản thu','Đăng ký gói','Lần vào tập']
        fields=[['Mã tài khoản','Vai trò','Trạng thái'],['Mã hội viên','Thông tin liên hệ','Mã QR'],['Mã loại gói','Tên và giá','Thời hạn và lượt'],['Mã khoản thu','Số tiền','Trạng thái'],['Mã đăng ký','Ngày bắt đầu và hết hạn','Lượt còn lại'],['Mã lần vào','Thời điểm','Người ghi nhận']]
        methods=['Kiểm tra quyền','Cập nhật hồ sơ','Ngừng bán','Hủy có lý do','Tạm dừng và mở lại','Kiểm tra trùng']
        for i,rect in enumerate(rects):
            x1,y1,x2,y2=rect
            box(d,rect,'')
            d.text(((x1+x2)/2,y1+32),names[i],anchor='mm',font=art.font(28,True),fill='black')
            d.line((x1,y1+63,x2,y1+63),fill='#365F91',width=2)
            for j,t in enumerate(fields[i]):
                d.text((x1+20,y1+100+j*42),t,anchor='lm',font=art.font(23),fill='black')
            if kind=='class':
                d.line((x1,y1+215,x2,y1+215),fill='#365F91',width=2)
                d.text(((x1+x2)/2,y1+250),methods[i],anchor='mm',font=art.font(23),fill='black')
        line(d,[(475,325),(700,325)],'0..1 — 0..1',(588,300))
        line(d,[(900,470),(900,750)],'1 — nhiều',(900,580))
        line(d,[(1525,470),(1525,650),(1060,650),(1060,750)],'1 — nhiều',(1310,625))
        line(d,[(475,895),(700,895)],'nhiều — 1',(585,865))
        line(d,[(1100,895),(1325,895)],'1 — nhiều',(1210,865))
        d.text((900,1120),'Mô hình tập trung các đối tượng chính của luồng bán gói và vào tập',anchor='mm',font=art.font(23),fill='black')
        paths[kind]=folder/f'{kind}_plain.png'; im.save(paths[kind])

    im,d=canvas('Sơ đồ trình tự ghi nhận vào tập',1240)
    actors=[(160,'Nhân viên'),(630,'Giao diện'),(1100,'Phần xử lý'),(1620,'Dữ liệu')]
    for x,label in actors:
        box(d,(x-130,120,x+130,195),label)
        for y in range(200,1130,22):
            d.line((x,y,x,y+12),fill='#8798AA',width=2)
    messages=[(160,630,285,'1 Quét hoặc nhập mã'),(630,1100,415,'2 Gửi yêu cầu vào tập'),
              (1100,1620,545,'3 Kiểm tra quyền và gói'),(1620,1100,675,'4 Trả điều kiện hiện tại'),
              (1100,1620,805,'5 Ghi lần vào và cập nhật lượt'),(1620,1100,935,'6 Xác nhận đã lưu'),(1100,630,1065,'7 Hiển thị kết quả')]
    for x1,x2,y,label in messages:
        art.arrow(d,(x1,y),(x2,y))
        d.text(((x1+x2)/2,y-30),label,anchor='mm',font=art.font(22),fill='black')
    d.text((900,1190),'Nếu kiểm tra không đạt, trả lý do từ chối và không thực hiện bước lưu',anchor='mm',font=art.font(24),fill='black')
    paths['sequence']=folder/'sequence_plain.png'; im.save(paths['sequence'])

    im,d=canvas('Sơ đồ hoạt động bán gói',1240)
    d.ellipse((880,115,920,155),fill='black')
    art.arrow(d,(900,160),(900,200))
    box(d,(470,205,1330,295),'Chọn hội viên, gói và cách thanh toán')
    art.arrow(d,(900,300),(900,355))
    d.polygon([(900,355),(1180,475),(900,595),(620,475)],fill='#FFF2CC',outline='#365F91',width=3)
    d.multiline_text((900,475),'Quyền và dữ liệu\nhợp lệ?',anchor='mm',align='center',font=art.font(27),fill='black')
    line(d,[(1180,475),(1520,475),(1520,650)])
    art.arrow(d,(1520,620),(1520,650))
    d.text((1330,445),'Không',anchor='mm',font=art.font(24),fill='black')
    box(d,(1300,655,1740,765),'Thông báo lỗi\nKhông lưu dữ liệu','#FCE4D6')
    art.arrow(d,(900,600),(900,655))
    d.text((935,620),'Có',font=art.font(24),fill='black')
    box(d,(460,660,1230,810),'Lưu đăng ký gói và khoản thu\nGiữ thông tin giá khi bán\nGhi nhật ký thao tác')
    art.arrow(d,(850,815),(850,905))
    box(d,(470,910,1230,1000),'Thông báo kết quả thành công')
    line(d,[(1520,770),(1520,1080),(850,1080)])
    art.arrow(d,(850,1005),(850,1120))
    d.ellipse((824,1120,876,1172),outline='black',width=3)
    d.ellipse((833,1129,867,1163),fill='black')
    paths['activity']=folder/'activity_plain.png'; im.save(paths['activity'])
    return paths
