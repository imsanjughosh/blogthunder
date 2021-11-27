from flask import Flask,render_template,request,redirect,url_for,session,g
from flask_sqlalchemy import SQLAlchemy
import json
from flask_mail import Mail
from datetime import datetime
import os

# from werkzeug import secure_filename




#Database Connection
with open('config.json','r') as c:
    params=json.load(c) ["params"]
local_server=True
app = Flask(__name__)
app.secret_key='super-secrte-key'
app.config['UPLOAD_FOLDER'] = params['upload_location']
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD = params['gmail-password']
)
mail = Mail(app)
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_url']
else:
     app.config['SQLALCHEMY_DATABASE_URI'] = params['prop_url']
db = SQLAlchemy(app)
#End of Database Connection


#DATABASE TABLE CONTACTS
class Contacts(db.Model):      #CLASS CONTACTS IS SAME THE TABLE NAME   
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
#/DATABASE TABLE CONTACTS

#DATABASE TABLE LOGIN
class Login(db.Model):      #CLASS Login IS SAME THE TABLE NAME   
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    def __init__(self,name,email,password,phone) -> str:
        self.name=name,
        self.email=email,
        self.password=password,
        self.phone=phone
#/DATABASE TABLE LOGIN


#DATABASE TABLE POSTS
class Posts(db.Model):      #CLASS Posts IS SAME THE TABLE NAME   
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(20), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    slug = db.Column(db.String(20), nullable=False)
    tagline = db.Column(db.String(20), nullable=False)
    file1 = db.Column(db.String(70), nullable=False)
    def __init__(self,title,content,date,slug,tagline,file1) -> str:
        self.title=title,
        self.content=content,
        self.date=date,
        self.slug=slug
        self.tagline=tagline,
        self.file1=file1            
#DATABASE TABLE LOGIN


#INDEX PAGE
@app.route("/")
def home():
    posts = Posts.query.filter_by().all()[0:params['no_of_posts']]
    return render_template('index.html', params=params, posts=posts)


#BLOG ADD
@app.route("/about",methods = ['GET', 'POST'])
def about():
    if(request.method=='POST'):
        '''Add entry to the database'''
        file1=request.files['file1']
        #file1.save(os.path.join(app.config['UPLOAD_FOLDER']))
        file1.save(os.path.join(app.config['UPLOAD_FOLDER'],file1.filename))
        title = request.form.get('title')          
        slug = request.form.get('slug')
        content = request.form.get('content')
        tagline = request.form.get('tagline')
        entry = Posts(title=title,content = content, date= datetime.now(),slug = slug,tagline=tagline,file1=file1)
        db.session.add(entry)
        db.session.commit()
    if g.user:
        return render_template("about.html",params=params,user=session['user'])
    # return "<p>Hello, World!</p>"
    return redirect(url_for('login'))

#CONTACT
@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if(request.method=='POST'):
        '''Add entry to the database'''
        name = request.form.get('name')          #left=variable as class as database ;right=form value
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contacts(name=name, phone = phone, email = email, msg = message, date= datetime.now())
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from ' + name,
                          sender="email",
                          recipients = [params['gmail-user']],
                          body = message + "\n" + phone +"\n" + email
                          )
    return render_template('contact.html',params=params)


#TO SHOW A PARTICULAR BLOG USING SLUG
@app.route("/post/<string:post_slug>",methods=['GET'])
def postroute(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template("post.html",params=params,post=post)

#SIGN IN
@app.route("/sign" , methods = ['GET', 'POST'])
def sign():
    if g.user:
       return redirect(url_for('show'))   
    if(request.method=='POST'):
        '''Add entry to the database'''
        name = request.form.get('name')          #left=variable as class as database ;right=form value
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        entry = Login(name=name,email = email,password=password, phone = phone)
        db.session.add(entry)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('sign.html',params=params)

#LOGIN 
@app.route("/login", methods = ['GET', 'POST'])
def login():
        if g.user:
         return redirect(url_for('show'))
        if(request.method=='POST'):
            session.pop('user',None)

        email = request.form.get('email1')
        password = request.form.get('password1')
        if email =="sanju" and password=="admin":
            session['user']=email
            return redirect(url_for('about'))
        return render_template('login.html',params=params)


#EDIT A BLOG
@app.route("/edit/<string:sno>",methods=['GET','POST'])
def edit(sno):
    if g.user:
        posts = Posts.query.filter_by(sno=sno).first()
        if sno!='0':
            if(request.method=='POST'):
                title = request.form.get('title')          
                slug = request.form.get('slug')
                content = request.form.get('content')
                tagline = request.form.get('tagline')
                posts = Posts.query.filter_by(sno=sno).first()
                posts.title=title
                posts.slug=slug
                posts.content=content
                posts.tagline=tagline
                db.session.add(posts)
                db.session.commit()
                return redirect('/post/'+slug)
                

            return render_template("edit.html",params=params,user=session['user'],posts=posts)
    return redirect(url_for('login'))
#DELETE
@app.route("/delete/<string:sno>",methods=['GET','POST'])
def delete(sno):
    if g.user:
        posts = Posts.query.filter_by(sno=sno).first()
        db.session.delete(posts)
        db.session.commit()
        return redirect(url_for('show'))
    return redirect(url_for('login'))



#TO SHOW ALL THE BLOGS WITH A SAME PAGE EDIT/DELETE BUTTON
# @app.route("/show")
# def show():
#     posts = Posts.query.all()
#     if g.user:
#         return render_template("show.html",params=params,user=session['user'],posts=posts)
#     else:
#         return render_template('show.html', params=params, posts=posts)

#[BOTH SHOW METHODS ARE SAME JUST STOP 2ND SHOW AND ACTIVE 1ST !!..OR OPPOSITE]
#TO SHOW ALL THE BLOGS BEFORE LOGIN WE JUST SEE AND AFTER LOGIN WE HAVE THAT EDIT/DELETE BUTTON
@app.route("/show")
def show():
    posts = Posts.query.all()
    if g.user:
        return render_template("show.html",params=params,user=session['user'],posts=posts)
    else:
        return render_template('showall.html', params=params, posts=posts)







#SESSION CREATION AND USE IN ANY PAGE
@app.before_request
def before_request():
    g.user=None

    if 'user' in session:
        g.user = session['user']

#LOGOUT SESSION
@app.route("/dropsession")
def dropsession():
    session.pop('user',None)
    return render_template('login.html',params=params)

#Login with db try
# @app.route("/login")
# def login():
#     login=Login.query.all()
#     semail=login.name
#     spass=login.password
#     print(semail)
#     # if g.user:
#     #              return redirect(url_for('show'))
#     #         if(request.method=='POST'):
#     #             session.pop('user',None)

#     #         email = request.form.get('email')
#     #         password = request.form.get('password')
#     #         if email =="email" and password=="password":
#     #             session['user']=email
#     #         return redirect(url_for('about'))
#         # return render_template('login.html',params=params)
   




    # posts = Posts.query.all()
    # return render_template('show.html', params=params, posts=posts)
    # if g.user:
    #     return render_template("show.html",params=params,user=session['user'])
    # return redirect(url_for('show'))





if __name__=="__main__":
    app.run(debug=True,port=8000)