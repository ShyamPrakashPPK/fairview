from email.mime.multipart import MIMEMultipart

from PIL import Image
from flask import Flask,render_template,request,session,redirect
import random
from DBConnection import Db
import datetime
from email.mime import image
import os
import smtplib
from email.mime.text import MIMEText
from flask_mail import Mail
app = Flask(__name__)
app.secret_key="123"

@app.route('/')
def sample():
    return render_template('login_index.html')


@app.route('/login',methods=['post'])
def login():
    username=request.form['textfield']
    password=request.form['textfield2']
    db=Db()
    result=db.selectOne("select * from login where username='"+ username +"' and password='"+ password +"'")
    if result is not None:
        session['log'] = "lin"
        session['lin']=result['id']
        if result['utype']=='Admin':
            session['log'] = "lin"
            print(session['log'])
            return '''<script>alert('admin login successfull');window.location="/admin_home"</script>'''


        elif result['utype']=='student':
            ss=db.selectOne("select * from student where std_email='"+username+"'")
            session['lid']=result['id']
            session['log'] = 'lin'
            id=result['id']
            qry4=db.selectOne("select * from student WHERE std_id='"+str(id)+"'")
            session['pic']=qry4['std_photo']
            session['name']=qry4['std_name']
            print(session['pic']),(session['name'])
            return '''<script>alert('student login successfull');window.location="/student_home"</script>'''


        elif result['utype']=='staff':
            session['lid']=result['id']
            session['log'] = 'lin'
            id=result['id']

            qry3=db.selectOne("select *  from staff WHERE stf_id='"+str(id)+"'")
            session['pic'] = qry3['stf_photo']
            session['name']=qry3['stf_name']
            return '''<script>alert('staff login successfull');window.location="/staff_home"</script>'''
        else :
            return '''<script>alert('wrong field');window.loaction="/"</script>'''
    else:
        return '''<script>alert('user not found');window.location="/"</script>'''



@app.route('/logout')
def logout():
    session.clear()
    session['log']=""
    return redirect('/')




#------------------------------------------------ADMIN MODULE------------------------------------------------

@app.route('/admin_home')
def admin_home():
    # print("FFFFf   ",session['log'])
    if session['log']== 'lin':
        print(session['log'])
    # print(str(session['lin']),"kkkkkkkkkkkkkkkkkkkkk")
        return render_template('ADMIN/atemp.html')
    else:
        return redirect('/')

@app.route('/view_admin_students')
def view_admin_students():
    if session['log'] == 'lin':
        db=Db()
        aa=db.select("select * from student")
        return render_template('ADMIN/view_students.html',student=aa)
    else:
        return redirect('/')

@app.route('/view_admin_staff')
def view_admin_staff():
    if session['log'] == 'lin':
        db=Db()
        ss=db.select("select * from staff")
        return render_template('ADMIN/view_staff_admin.html', staff=ss)
    else:
        return redirect('/')

@app.route('/vehicle_view_admin', methods=['get', 'post'])
def vehicle_view_admin():
    if session['log'] == 'lin':
        db = Db()
        if request.method=='POST':
            vno=request.form['vno']
            res = db.select("select * from student,vehicle where student.std_id = vehicle.owner_id and vehicle.v_no like '%"+vno+"%' and vehicle.v_id not in (select v_id from blacklist)")
            return render_template('ADMIN/vehicle_view_admin.html', data=res)
        res = db.select("select * from student,vehicle where student.std_id = vehicle.owner_id and vehicle.v_id not in (select v_id from blacklist)")
        return render_template('ADMIN/vehicle_view_admin.html',data = res)
    else:
        return redirect('/')

@app.route('/blacklist/<vid>', methods=['get', 'post'])
def blacklist(vid):
    if session['log'] == 'lin':
        if request.method=='POST':
            reason=request.form['textfield3']
            db=Db()
            db.insert("insert into blacklist(v_id, date, reason) values('"+vid+"', curdate(), '"+reason+"')")
            return "<script>alert('Vehicle blacklisted');window.location='/vehicle_view_admin';</script>"
        return render_template('ADMIN/blacklist.html')
    else:
        return redirect('/')

@app.route('/blacklist_view_admin')
def blacklist_view_admin():
    if session['log'] == 'lin':
        db= Db()
        res=db.select('select * from student,blacklist, vehicle where student.std_id=vehicle.owner_id and vehicle.v_id=blacklist.v_id')
        return render_template('ADMIN/blacklist_view_admin.html', data= res)
    else:
        return redirect('/')

@app.route("/remove_from_blacklist/<blacklist_id>")
def remove_from_blacklist(blacklist_id):
    db=Db()
    db.delete("delete from blacklist where blacklist_id='"+blacklist_id+"'")
    return redirect("/blacklist_view_admin")

@app.route('/camera', methods=['get', 'post'])
def camera():
    if session['log'] == 'lin':
        if request.method=="POST":
            loc=request.form['textfield']
            name=request.form['textfield2']
            db=Db()
            db.insert("insert into camera(loacation, cam_name) values('"+loc+"','"+name+"')")
            return "<script>alert('Camera added');window.location='/camera';</script>"
        return render_template('ADMIN/camera.html')
    else:
        return redirect('/')

@app.route("/view_camera")
def view_camera():
    db=Db()
    res=db.select("select * from camera")
    return render_template("ADMIN/view_camera.html", data=res)

@app.route("/delete_cam/<cid>")
def delete_cam(cid):
    db=Db()
    db.delete("delete from camera where cam_id='"+cid+"'")
    return redirect("/view_camera")

@app.route('/complaint')
def complaint():
    if session['log'] == 'lin':

        return render_template('ADMIN/complaint.html')
    else:
        return redirect('/')

@app.route('/helmet_view_admin')
def helmet_view_admin():
    if session['log'] == 'lin':

        db = Db ()
        res =db.select("select * from helmet, vehicle, student where student.std_id=vehicle.owner_id and vehicle.v_id=helmet.v_id order by date desc")
        return render_template('ADMIN/helmet_view_admin.html', data=res )
    else:
        return redirect('/')
@app.route('/ocr_check/<hid>')
def ocr_check(hid):
    if session['log'] == 'lin':

        db = Db ()
        res =db.selectOne("select * from helmet_violation where helmet_id='"+hid+"'")
        img=res['image']
        import pytesseract
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
        a=pytesseract.image_to_string(Image.open(r'C:\Users\TUF GAMING\PycharmProjects\GLIMPSE\static\helmetpic\bcd.jpg'))
        print("llll", a)

        return "ok"
    else:
        return redirect('/')


@app.route('/triples_view_admin')
def triples_view_admin():
    if session['log'] == 'lin':
        db = Db ()
        res =db.select("select * from student,triples,vehicle where student.std_id = vehicle.owner_id and triples.v_id=vehicle.v_id order by date desc")
        return render_template('ADMIN/triples_view_admin.html', data=res )
    else:
        return redirect('/')


@app.route('/helmet')
def helmet():
    if session['log'] == 'lin':
        return render_template('ADMIN/helmt.html')
    else:
        return redirect('/')

@app.route('/helmet_penalty/<k>')
def helmet_penalty(k):
    if session['log'] == 'lin':
        return render_template('ADMIN/helmet_penalty.html', id=k)
    else:
        return redirect('/')

@app.route('/triples_penalty/<k>')
def triples_penalty(k):
    if session['log'] == 'lin':
        return render_template('ADMIN/triples_penalty.html', id=k)
    else:
        return redirect('/')


@app.route('/helmet_penalty_action/<p>',methods=['post'])
def helmet_penalty_action(p):
    if session['log'] == 'lin':
        db=Db()
        # ss=db.selectOne("select * from helmet where h_id='"+str(p)+"' ")
        # print(ss)
        # res=ss['v_id']
        # print(res)
        # d=db.selectOne("select * from vehicle where v_id='"+str(res)+"'")
        # print(d)
        # s=d['owner_id']
        r=request.form['textfield']
        db.insert("insert into penalty values('',curdate(),'"+r+"','"+str(p)+"','helmet')")
        db.update("update helmet set p_status='penalty added' where h_id='"+str(p)+"' ")
        print(r,p)
        return'''<script>alert('Penalty setted');window.location="/admin_home"</script>'''
    else:
        return redirect('/')


@app.route('/triples_penalty_action/<p>',methods=['post'])
def triples_penalty_action(p):
    if session['log'] == 'lin':
        db=Db()
        # ss=db.selectOne("select * from triples where t_id='"+str(p)+"' ")
        # print(ss)
        # res=ss['v_id']
        # print(res)
        # d=db.selectOne("select * from vehicle where v_id='"+str(res)+"'")
        # print(d)
        # s=d['owner_id']
        r=request.form['textfield']
        db.insert("insert into penalty values('',curdate(),'"+r+"','"+str(p)+"','triples')")
        db.update("update triples set p_status='penalty added' where t_id='" + str(p) + "' ")
        print(r,p)
        return'''<script>alert('Penalty setted');window.location="/admin_home"</script>'''
    else:
        return redirect('/')


@app.route('/send_helmet_penalty')
def send_helmet_penalty():
    if session['log'] == 'lin':
        db=Db()
        res=db.select("select * from student,helmet,vehicle where student.std_id=vehicle.owner_id and helmet.v_id=vehicle.v_id and helmet.p_status='pending'")
        return render_template('ADMIN/send_helmet_penalty_admin.html',data=res)
    else:
        return redirect('/')

@app.route('/send_triples_penalty')
def send_triples_penalty():
    if session['log'] == 'lin':
        db=Db()
        res = db.select("select * from student,triples,vehicle where student.std_id=vehicle.owner_id and triples.v_id=vehicle.v_id and triples.p_status='pending'")
        return render_template('ADMIN/send_triples_penalty_admin.html',data=res)
    else:
        return redirect('/')


@app.route('/send_reply/<k>')
def send_reply(k):
    if session['log'] == 'lin':
        return render_template('ADMIN/send_reply.html',id=k)
    else:
        return redirect('/')

@app.route('/send_reply_action/<p>',methods=['post'])
def send_reply_action(p):
    if session['log'] == 'lin':
        db=Db()
        r=request.form['textfield']
        print(r,p)
        db.update("update complaint set reply='"+r+"' , reply_date=curdate() where c_id='"+p+"'")
        return redirect("/sendreply")
    else:
        return redirect('/')

@app.route('/sendreply')
def sendreply():
    if session['log'] == 'lin':
        db=Db()
        ss=db.select("select * from complaint,staff where complaint.stf_id=staff.stf_id")
        return render_template('ADMIN/view_complaint_send_reply.html',data=ss)
    else:
        return redirect('/')

@app.route('/staffreg')
def staffreg():
    if session['log'] == 'lin':
        return render_template('ADMIN/staff_registration.html')
    else:
        return redirect('/')

@app.route('/staffreg_action',methods=['post'])
def staffreg_action():
    if session['log'] == 'lin':
        name=request.form['textfield']
        type=request.form['select']
        department=request.form['textfield2']
        email=request.form['textfield4']
        phone=request.form['textfield5']
        paswd=random.randint(0000,9999)
        image=request.files['filefield']

        date = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        print(date)
        image.save("C:\\Users\\TUF GAMING\\PycharmProjects\\GLIMPSE\\static\\staff_pic\\"+date+".jpg")
        path = "/static/staff_pic/"+date+".jpg"

        db=Db()
        res=db.insert("insert into login values('','"+email+"','"+str(paswd)+"','staff')")
        db.insert("insert into staff values('"+str(res)+"','"+name+"','"+type+"','"+department+"','"+email+"','"+phone+"','"+path+"')")
        try:
            gmail = smtplib.SMTP('smtp.gmail.com', 587)

            gmail.ehlo()

            gmail.starttls()

            gmail.login('fairviewmorazha@gmail.com', 'sjk9526134639')

        except Exception as e:
            print("Couldn't setup email!!" + str(e))

        msg = MIMEText("YOUR FAIRVIEW ACCOUNT HAS BEEN REGISTERED..  YOUR PASSWORD IS " + str(paswd) + "       YOUR MAIL ID IS YOUR USERNAME")

        msg['Subject'] = 'Verification'

        msg['To'] = email

        msg['From'] = 'fairviewmorazha@gmail.com'

        try:

            gmail.send_message(msg)

        except Exception as e:

            print("COULDN'T SEND EMAIL", str(e))

        return '''<script>alert('Successfuly registered');window.location="/admin_home"</script>'''
    else:
        return redirect('/')


@app.route('/edit_staff/<k>')
def  edit_staff(k):
    if session['log'] == 'lin':
        db=Db()
        ss=db.selectOne("select * from staff where stf_id='"+str(k)+"'")
        print(ss)
        return render_template("ADMIN/edit_staff.html",data=ss,id=k)
    else:
        return redirect('/')

@app.route('/edit_staff_action/<k>',methods=['post'])
def edit_staff_action(k):
    if session['log'] == 'lin':
        db=Db()
        n=request.form['textfield']
        d=request.form['textfield2']
        t=request.form['select']
        e=request.form['textfield4']
        p=request.form['textfield5']
        i=request.files['filefield']
        date = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        print(date)
        i.save("C:\\Users\\TUF GAMING\\PycharmProjects\\GLIMPSE\\static\\staff_pic\\" + date + ".jpg")
        path = "/static/staff_pic/" + date + ".jpg"
        db.update("update staff set stf_name='"+n+"', stf_department='"+d+"',stf_type='"+t+"',stf_email='"+e+"',stf_phone='"+p+"',stf_photo='"+path+"' where stf_id='"+str(k)+"' ")
        return '''<script>alert('Successfuly updated');window.location="/view_admin_staff"</script>'''
    else:
        return redirect('/')


@app.route('/delete_staff/<k>')
def delete_staff(k):
    if session['log'] == 'lin':
        db=Db()
        db.delete(" delete  from staff where stf_id='"+str(k)+"'")
        return '''<script>alert(' Deleted');window.location="/view_admin_staff"</script>'''
    else:
        return redirect('/')


@app.route('/triples')
def triples():
    if session['log'] == 'lin':
        return render_template('ADMIN/triples.html')
    else:
        return redirect('/')

#---------------------------------------------------CAMERA-------------------------------------------------------

@app.route('/cameramain')
def cameramain():
    if session['log'] == 'lin':
        return render_template('CAMERA/camera_main.html')
    else:
        return redirect('/')

@app.route('/helmetcamera')
def helmetcamera():
    if session['log'] == 'lin':
        return render_template('CAMERA/helmet_camera.html')
    else:
        return redirect('/')

@app.route('/triplescamera')
def triplescamera():
    if session['log'] == 'lin':
        return render_template('CAMERA/triples_camera.html')
    else:
        return redirect('/')


@app.route('/vehiclereg')
def vehiclereg():
    if session['log'] == 'lin':
        return render_template('CAMERA/vehicle_registration_camera.html')
    else:
        return redirect('/')


#-------------------------------------------------------------STAFF-----------------------------------------------------

@app.route('/staff_home')
def staff_home():
    if session['log'] == 'lin':
        return render_template('STAFF/stafftemp.html',n=session['name'])
    else:
        return redirect('/')

@app.route('/blackliststaff')
def blackliststaff():
    if session['log']=="lin":

        return render_template('STAFF/blacklist_staff.html')
    else:
        return redirect('/')



@app.route('/complaintstaff')
def complaintstaff():
    if session['log'] == "lin":

        db=Db()
        op=db.select("select * from complaint,staff where complaint.stf_id=staff.stf_id ")
        return render_template('STAFF/complaint_reply_view.html',data=op)
    else:
        return redirect('/')


@app.route('/sendcomplaint')
def sendcomplaint():
    if session['log'] == "lin":
        return render_template('STAFF/sendcomplaint.html')
    else:
        return redirect('/')


@app.route('/complaint_action',methods=['post'])
def complaint_action():
    if session['log'] == "lin":

        complaint=request.form['textarea']
        db=Db()
        db.insert("insert into complaint values ('',2,'"+complaint+"',curdate(),'pending','pending')")
        return '<script>alert("complaint send");window.location="/staff_home"</script>'
    else:
        return redirect('/')


@app.route('/helmetstaff')
def helmetstaff():
    if session['log'] == "lin":
        return render_template('STAFF/helmt_staff.html')
    else:
        return redirect('/')


@app.route('/penaltystaff')
def penaltystaff():
    if session['log'] == "lin":
       return render_template('STAFF/penalty_staff.html')
    else:
       return redirect('/')


@app.route('/student_reg')
def student_reg():
    if session['log'] == "lin":
       return render_template('STAFF/student_registration.html')
    else:
       return redirect('/')


@app.route('/studentsreg',methods=['post'])
def studentsreg():
    if session['log'] == "lin":

        name=request.form['textfield']
        vehno=request.form['textfield2']
        department=request.form['textfield3']
        batch=request.form['textfield4']
        cls=request.form['textfield5']
        email=request.form['textfield6']
        phone=request.form['textfield7']
        place=request.form['textfield8']
        pin=request.form['textfield9']
        paswd=random.randint(0000,9999)

        image = request.files['filefield']

        date = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        print(date)
        image.save("C:\\Users\\TUF GAMING\\PycharmProjects\\GLIMPSE\\static\\stud_pic\\" + date + ".jpg")
        path = "/static/stud_pic/" + date + ".jpg"

        #print(name,email)
        db=Db()
        res=db.insert("insert into login values('','"+email+"','"+str(paswd)+"','student')")
        db.insert("insert into vehicle values('','"+vehno+"','"+str(res)+"')")

        db.insert("insert into student values('"+str(res)+"','"+name+"','"+department+"','"+batch+"','"+cls+"','"+email+"','"+phone+"','"+place+"','"+vehno+"','"+pin+"','"+path+"')")
        try:
            gmail = smtplib.SMTP('smtp.gmail.com', 587)

            gmail.ehlo()

            gmail.starttls()

            gmail.login('fairviewmorazha@gmail.com', 'sjk9526134639')

        except Exception as e:
            print("Couldn't setup email!!" + str(email))

        msg = MIMEText("YOUR FAIRVIEW ACCOUNT HAS BEEN REGISTERED..  YOUR PASSWORD IS " + str(paswd) + "     YOUR MAIL ID IS YOUR USERNAME")

        msg['Subject'] = 'Verification'

        msg['To'] = email

        msg['From'] = 'fairviewmorazha@gmail.com'

        try:

            gmail.send_message(msg)

        except Exception as e:

            print("COULDN'T SEND EMAIL", str(e))
        return '''<script>alert('Successfuly registered');window.location="/staff_home"</script>'''
    else:
        return redirect('/')



@app.route('/edit_student/<k>')
def edit_student(k):
    if session['log'] == "lin":
        db=Db()
        ss=db.selectOne("select * from student where std_id='"+str(k)+"'")
        print(ss)
        return render_template('STAFF/edit_student.html',id=k,data=ss)
    else:
        return redirect('/')

@app.route('/edit_student_action/<k>',methods=['post'])
def edit_student_action(k):
    if session['log'] == "lin":

        db = Db()
        n = request.form['textfield']
        v = request.form['textfield2']
        d = request.form['textfield3']
        b = request.form['textfield4']
        c = request.form['textfield5']
        e = request.form['textfield6']
        p = request.form['textfield7']
        l = request.form['textfield8']
        pn= request.form['textfield9']
        i=request.files['filefield']

        date = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        print(date)
        i.save("C:\\Users\\TUF GAMING\\PycharmProjects\\GLIMPSE\\static\\stud_pic\\" + date + ".jpg")
        path = "/static/stud_pic/" + date + ".jpg"
        db.update(
            "update student set std_name='" + n + "', std_department='" + d + "',std_batch='" + b + "',std_class='"+ c +"',std_email='" + e + "',std_phone='" + p + "',std_place='"+ l +"',vehno='"+ v +"',std_pin='"+ pn +"',std_photo='" + path + "' where std_id='" + str(
                k) + "' ")

        return '''<script>alert('Successfuly updated');window.location="/view_students"</script>'''
    else:
        return redirect('/')

@app.route('/delete_student/<k>')
def delete_student(k):
    if session['log'] == "lin":


        db=Db()
        db.delete(" delete  from student where std_id='"+str(k)+"'")
        return '''<script>alert(' Deleted');window.location="/view_students"</script>'''
    else:
        return redirect('/')

@app.route('/triplesstaff')
def triplesstaff():
    if session['log'] == "lin":
        return render_template('STAFF/triples_staff.html')
    else:
        return redirect('/')

@app.route('/vehicle_view_staff')
def vehicle_view_staff():
    if session['log'] == "lin":

        db = Db()
        res = db.select("select * from student,vehicle where student.std_id = vehicle.owner_id")

        return render_template('STAFF/vehicle_view_staff.html', data=res)
    else:
        return redirect('/')

@app.route('/violations')
def violations():
    if session['log'] == "lin":

        return render_template('ADMIN/violation_home.html')
    else:
        return redirect('/')

@app.route('/view_violations')
def view_violations():
    if session['log'] == "lin":
        return render_template('STAFF/violation_home_staff.html')
    else:
        return redirect('/')


@app.route('/helmet_view_staff')
def helmet_view_staff():
    if session['log'] == "lin":
        db = Db ()
        res =db.select("select * from helmet, vehicle, student where student.std_id=vehicle.owner_id and vehicle.v_id=helmet.v_id order by date desc")
        return render_template('STAFF/helmet_view_staff.html', data=res )
    else:
        return redirect('/')


@app.route('/triples_view_staff')
def triples_view_staff():
    if session['log'] == "lin":
        db = Db ()
        res =db.select("select * from student,triples,vehicle where student.std_id = vehicle.owner_id and vehicle.v_id=triples.v_id order by date desc")
        return render_template('STAFF/triples_view_staff.html', data=res )
    else:
        return redirect('/')


@app.route('/blacklist_view_staff')
def blacklist_view_staff():
     if session['log'] == "lin":
        db= Db()
        res=db.select('select * from student,blacklist where student.vehno=blacklist.v_id')
        return render_template('STAFF/blacklist_view_staff.html', data= res)
     else:
        return redirect('/')


@app.route('/view_penalty')
def view_penalty():
    if session['log'] == "lin":
        db=Db()
        res=db.select('select * from penalty,helmet_violation where penalty.violation_id=helmet_violation.helmet_id')
        return render_template('STAFF/view_penalty_staff.html', data=res)
    else:
        return redirect('/')




@app.route('/view_staff')
def view_staff():
    if session['log'] == "lin":
        db=Db()
        ss=db.select("select * from staff")
        return render_template('STAFF/view_staff.html',staff=ss)
    else:
        return redirect('/')


@app.route('/view_students')
def view_students():
    if session['log'] == "lin":

        db=Db()
        aa=db.select("select * from student")
        return render_template('STAFF/view_students.html',student=aa)
    else:
        return redirect('/')


#-----------------------------------------------------STUDENTS---------------------------------------------------------

@app.route('/student_home')
def student_home():
    if session['log']=='lin':
            return render_template('STUDENT/studtemp.html',n=session['name'])
    else:
        return redirect('/')

@app.route('/view_student_violations')
def view_student_violations():
    if session['log']=="lin":
        sid=session['lid']
        db=Db()
        res=db.select("select * from student,helmet,vehicle where student.std_id=vehicle.owner_id and helmet.v_id=vehicle.v_id and student.std_id='"+str(sid)+"'")
        res1=db.select("select * from student,triples,vehicle where student.std_id =vehicle.owner_id and triples.v_id=vehicle.v_id and student.std_id='"+str(sid)+"'")
        return render_template('STUDENT/student_violations.html',data = res,data1 = res1)
    else:
        return redirect('/')


@app.route('/student_blacklist')
def student_blacklist():
    db=Db()
    res=db.select("select * from vehicle,blacklist where vehicle.v_id=blacklist.v_id and vehicle.owner_id='"+str(session['lid'])+"'")
    return render_template('STUDENT/student_blacklist.html',data=res)

@app.route('/student_helmet_penalty')
def student_helmet_penalty():
    sid = session['lid']
    db=Db()
    res=db.select("select * from helmet,vehicle,penalty where vehicle.owner_id='"+str(sid)+"' and vehicle.v_id=helmet.v_id and penalty.violation_id=helmet.h_id and penalty.type='helmet' and p_status='penalty added'")
    return render_template('STUDENT/student_helmet_penalty.html',data=res)

@app.route('/student_triples_penalty')
def student_triples_penalty():
    sid = session['lid']
    db=Db()
    res=db.select("select * from triples,vehicle,penalty where vehicle.owner_id='"+str(sid)+"' and vehicle.v_id=triples.v_id and penalty.violation_id=triples.t_id and penalty.type='triples' and p_status='penalty added'")
    return render_template('STUDENT/student_triples_penalty.html',data=res)

@app.route('/student_penalty_pay/<j>')
def student_penalty_pay(j):
    # db=Db()


    return render_template('STUDENT/student_penalty_pay.html',id=j)


@app.route('/student_penalty_pay_action/<k>',methods=['GET','POST'])
def student_penalty_pay_action(k):
    if request.method == "POST":
        if session['log'] == "lin":

            db = Db()
            name = request.form['textfield']
            ifsc = request.form['textfield2']
            accno = request.form['textfield3']


            qry=db.selectOne("select * from bankpay WHERE users_id='"+str(session['lid']) +"'")
            if qry is not None:
                db.update("update bankpay set amount=(amount-'"+str(k)+"') where users_id='"+str(session['lid'])+"'")
                db.update("update bankpay set amount=(amount+'"+str(k)+"') where users_id=1")
                ss=db.selectOne("select * from helmet,vehicle where vehicle.v_id=helmet.v_id and vehicle.owner_id='"+str(session['lid'])+"' and p_status='penalty added'")
                s=db.selectOne("select * from triples,vehicle where vehicle.v_id=triples.v_id and vehicle.owner_id='"+str(session['lid'])+"' and p_status='penalty added'")




                if ss is not None:
                    h = ss['h_id']
                    db.update("update helmet set p_status='payed' where h_id='"+str(h)+"'")
                else:
                    return '''<script>alert('no  penalty');window.location="/student_home"</script>'''




                if s is not None:
                    t = s['t_id']
                    db.update("update triples set p_status='payed' where t_id='"+str(t)+"'")
                    return '''<script>alert('Successfully payed');window.location="/student_home"</script>'''
                else:
                    return '''<script>alert(' no penalty');window.location="/student_home"</script>'''


            else:
                 return '''<script>alert('invalid bank details');window.location="/view_students"</script>'''

        else:
            return redirect('/')
    else:
        return render_template('STUDENT/student_penalty_pay.html')



@app.route("/a")
def a():
    return render_template("ADMIN/index.html")


@app.route("/forgot_pswd",methods=['get','post'])
def forgot_pswd():
    if request.method=="POST":

        email = request.form['textfield']

        db = Db()
        res = db.selectOne("select * from  login where username ='"+str(email)+"'")
        pswd = res['password']

        try:
            gmail = smtplib.SMTP('smtp.gmail.com', 587)

            gmail.ehlo()

            gmail.starttls()

            gmail.login('fairviewmorazha@gmail.com', 'sjk9526134639')

        except Exception as e:
            print("Couldn't setup email!!" + str(email))

        msg = MIMEText(" YOUR PASSWORD IS " + str(
            pswd) + "")

        msg['Subject'] = 'Verification'

        msg['To'] = email

        msg['From'] = 'fairviewmorazha@gmail.com'

        try:

            gmail.send_message(msg)

        except Exception as e:

            print("COULDN'T SEND EMAIL", str(e))
        return '''<script>alert('Password send sucessfuly');window.location="/"</script>'''

    else:
        return render_template("forgot_pswd.html")

if __name__ == '__main__':
    app.run(port=4000)
