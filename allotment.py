from sys import meta_path
from time import localtime, strftime
from flask import Flask,render_template,url_for,session,request,redirect,session
import mysql.connector
import os
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from werkzeug import debug

'''render_template is used to directly render html, css etc pages'''
'''templates folder me saare render wale file hone chahiye'''

app = Flask(__name__)
app.secret_key=os.urandom(24)
conn = mysql.connector.connect(host = 'remotemysql.com', user = 'kQhIm4uPaN',password = '72DY2MaG9o', database = 'kQhIm4uPaN')
cur = conn.cursor()

ROOMS=["Allotment","Room-Query","Mess","Roomate"]

socketio = SocketIO(app)




@app.route('/')
def home():
    if 'user_id' in session:
        return redirect('/studentdash')
    elif 'ward_id' in session:
        return redirect('/warddash')
    else:
        return render_template('index.html')

@app.route('/login', methods = ['POST'])
def login():
     email = request.form.get('email')
     passw = request.form.get('password')
     cur.execute("""SELECT * FROM `studentlogin` WHERE `Email` LIKE '{}' AND `Pass` LIKE '{}'""".format(email,passw))
     users = cur.fetchall()
     dot=users
     if len(users) > 0:
         session['user_id'] = users[0][0]
         return redirect('/studentdash')
     else:
         return redirect('/')
     

@app.route('/wardlogin', methods = ['POST'])
def wardlogin():
     wemail = request.form.get('wemail')
     wpassw = request.form.get('wpassword')
     cur.execute("""SELECT * FROM `wardens` WHERE `email` LIKE '{}' AND `pass` LIKE '{}'""".format(wemail,wpassw))
     users = cur.fetchall()
     if len(users) > 0:
         session['ward_id']=1
         return redirect('/warddash')
     else:
         return redirect('/')
     

@app.route('/register')
def register():
    return render_template('registation.html')

@app.route('/add_user', methods=['POST'])
def add_user():
    rname = request.form.get('rname')
    remail = request.form.get('remail')
    rpass = request.form.get('rpass')
    phone = request.form.get('phone')
    rreg = request.form.get('rreg')

    cur.execute("""INSERT INTO `studentlogin` (`id`,`Name`,`Email`,`Pass`,`Phone`,`register_no`) VALUES (NULL,'{}','{}','{}','{}','{}')""".format(rname,remail,rpass,phone,rreg))
    conn.commit()

    cur.execute("""SELECT * FROM `studentlogin` WHERE `Email` LIKE '{}'""".format(remail))
    myuser=cur.fetchall()
    dot=myuser
    session['user_id']=myuser[0][0]

    return redirect('/studentdash')


@app.route('/warddash')
def warddash():
    if 'ward_id' in session:
        cur.execute("""SELECT * FROM `allotrooms`""")
        wdr=cur.fetchall()
        return render_template('warddash.html',dr=wdr)
    else:
        return redirect('/')

@app.route('/studentdash')
def studentdash():
    if 'user_id' in session:
        cur.execute("""SELECT * FROM `studentlogin` WHERE `id` LIKE '{}'""".format(session['user_id']))
        data=cur.fetchall()
        cur.execute("""SELECT * FROM `allotrooms`""")
        dr=cur.fetchall()
        return render_template('studentdash.html',data=data,dr=dr)
        
    else:
        return redirect('/')

@app.route('/allotrooms', methods=['POST'])
def allotrooms():
    if 'user_id' in session:
        cur.execute("""SELECT * FROM `studentlogin` WHERE `id` LIKE '{}'""".format(session['user_id']))
        st=cur.fetchall()
        roomno=request.form.get("roomno")
        cur.execute("""UPDATE `allotrooms` SET st_id=%s, Name=%s, reg=%s, alloted=%s WHERE r_id=%s""",(st[0][0],st[0][1],st[0][5],'Yes',roomno))
        conn.commit()
        return redirect('/studentdash')
    else:
        return redirect('/')
    
@app.route('/studentdash/profile')
def profile():
    if 'user_id' in session:
        cur.execute("""SELECT * FROM `studentlogin` WHERE `id` LIKE '{}'""".format(session['user_id']))
        datap=cur.fetchall()
        return render_template('profile.html',data=datap)
        
    else:
        return redirect('/')

@app.route('/studentdash/booking')
def booking():
    if 'user_id' in session:
        cur.execute("""SELECT * FROM `studentlogin` WHERE `id` LIKE '{}'""".format(session['user_id']))
        datab=cur.fetchall()
        return render_template('booking.html',data=datab)
        
    else:
        return redirect('/')

@app.route('/book_stud', methods=['POST'])
def book_stud():
    bname = request.form.get('bname')
    bemail = request.form.get('bemail')
    bbranch = request.form.get('bbranch')
    bphone = request.form.get('bphone')
    breg = request.form.get('breg')
    slot = request.form.get('slot')
    mess = request.form.get('bmess')

    cur.execute("""INSERT INTO `bookedstud` (`id`,`Name`,`Email`,`Branch`,`Phone`,`Reg_no`,`Slot`,`Mess`) VALUES (NULL,'{}','{}','{}','{}','{}','{}','{}')""".format(bname,bemail,bbranch,bphone,breg,slot,mess))
    conn.commit()
    return redirect('/studentdash')
    
@app.route('/studentdash/contact')
def wcontact():
    if 'user_id' in session:
        cur.execute("""SELECT * FROM `studentlogin` WHERE `id` LIKE '{}'""".format(session['user_id']))
        cdata=cur.fetchall()
        return render_template('scontact.html',data=cdata)
    else:
        return redirect('/')

@app.route('/studentdash/guide')
def sguide():
    if 'user_id' in session:
        cur.execute("""SELECT * FROM `studentlogin` WHERE `id` LIKE '{}'""".format(session['user_id']))
        gdata=cur.fetchall()
        return render_template('sguide.html',data=gdata)
    else:
        return redirect('/')


@app.route('/warddash/profile')
def wprofile():
    if 'ward_id' in session:
        
        
        return render_template('wprofile.html')
        
    else:
        return redirect('/')

@app.route('/warddash/booking')
def wbooking():
    if 'ward_id' in session:
        cur.execute("""SELECT * FROM `bookedstud`""")
        booked=cur.fetchall()
        return render_template('wbooking.html',data=booked)
        
    else:
        return redirect('/')

@app.route("/chat",methods=['GET','POST'])
def chat():
    if 'user_id' in session:
        cur.execute("""SELECT * FROM `studentlogin` WHERE `id` LIKE '{}'""".format(session['user_id']))
        datac=cur.fetchall()
        return render_template('schat.html',username=datac[0][1], rooms=ROOMS)
    elif 'ward_id' in session:
        cur.execute("""SELECT * FROM `wardens` WHERE `id` LIKE '{}'""".format(session['ward_id']))
        datac=cur.fetchall()
        return render_template('wchat.html',username=datac[0][1],rooms=ROOMS)
    else:
        return redirect('/')


    
     

@app.route('/logout')
def logout():
    if 'user_id' in session:
        session.pop('user_id')
    elif 'ward_id'in session:
        session.pop('ward_id')
    return redirect('/')

@socketio.on('message')
def message(data):
    print(f"\n\n{data}\n\n")
    
    
    send({'msg': data['msg'],'username': data['username'],'time_stamp': strftime('%b-%d %I:%M%p', localtime())}, room=data['room'])
    #emit('some-event','This is the message')

@socketio.on('join')
def join(data):
    join_room(data['room'])
    send({'msg': data['username']+" has joined the "+data['room']+" room."},room=data['room'])

@socketio.on('leave')

def leave(data):
    leave_room(data['room'])
    send({'msg': data['username']+" has left the "+data['room']+" room."},room=data['room'])


if __name__ == "__main__":
    socketio.run(app,debug=True)
       