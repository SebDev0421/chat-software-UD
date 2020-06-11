from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, send
from flask_mysqldb import MySQL
from flask_cors import CORS
import json
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

msg = MIMEMultipart('alternative')
msg['Subject'] = "Chat-py"

# setup the parameters of the message

credentials = ("juanse0421@gmail.com","pia042199")
sender , psw = credentials
recived = sender 

context = ssl.create_default_context()
server = smtplib.SMTP_SSL("smtp.gmail.com",port=465, context=context)
server.login(sender,psw)


print('sent email')

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY']='secret'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask_chats'

mysql = MySQL(app)


socketio = SocketIO(app, cors_allowed_origins="*")
@socketio.on('Connect')
def handle_message(msg):
    print(msg)
    socketio.emit('Connect client',msg)

@socketio.on('typing')
def typing_msg(usr):
    print('usr typing: ',usr)


@socketio.on('new message')
def new_message(data):
    dates = json.loads(data)
    print('message into: ',dates['room'])

    cur = mysql.connection.cursor()
    cur.execute('INSERT INTO chats (room,dates) VALUES(%s, %s)',(dates['room'],data))
    mysql.connection.commit()
    socketio.emit('new message client',data)

@socketio.on('send email')
def send_email(data):
    dates = json.loads(data)
    email,room,user = (dates['email'],dates['room'],dates['name'])
    text = "Hi!\nHow are you?\nHere is the link you wanted:\n"
    html = """\
    <html>
     <head></head>
      <body>
       <p>Hi!<br>
        Chat-py?<br>
        Here is the <a href="http://localhost:3000/view/"""+room+"/"+user+""">link</a> you wanted.
       </p>
      </body>
    </html>
    """
    part1 = MIMEText(text,'plain')
    part2 = MIMEText(html,'html')

    msg.attach(part1)
    msg.attach(part2)
    server.sendmail(sender,email,msg.as_string())
   
@app.route('/room', methods = ['POST'])
def get_chat():
    load = json.dumps(request.json)
    room = json.loads(load)
    print(room['room'])
    room = room['room']
    query = 'SELECT * FROM chats WHERE room = \''+room+'\''
    cur = mysql.connection.cursor()
    cur.execute(query)
    data = cur.fetchall()
    return jsonify(data)

if __name__ == '__main__':
    socketio.run(app)