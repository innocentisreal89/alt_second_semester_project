from flask import Flask, redirect, url_for, render_template, request,flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user,login_user, LoginManager, UserMixin, logout_user, login_required
from datetime import datetime
import os


base_dir = os.path.dirname(os.path.realpath(__file__))

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'iziWriter.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = '026b0eb800ec2934fb5cf2e7'

db = SQLAlchemy(app)
login_manager= LoginManager(app)


class UserBlog(db.Model):
    __tablename__ = 'userblog'
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(100), nullable=False, unique=True)
    content = db.Column(db.Text, nullable=False)
    posted_by = db.Column(db.String(20), nullable=False, default='N/A')
    posted_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    
    



    def __repr__(self) -> str:
        return self.content


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    firstname = db.Column(db.String(30), nullable=False)
    lastname = db.Column(db.String(30), nullable=False)
    phoneNumber = db.Column(db.Integer(), nullable=False)
    username=db.Column(db.String(30), nullable=False, unique=True)
    email = db.Column(db.String(30), nullable=False, unique=True)
    password_hash = db.Column(db.Text(), nullable=False)
    blogs = db.relationship('UserBlog',  backref=db.backref('users', lazy='joined',uselist=False))

    def __repr__(self) -> str:
        return f'User<{self.username}>'


db.create_all()
db.session.commit()

@login_manager.user_loader
def user_loader(id):
    return User.query.get(int(id))


@app.route('/')
def Welcome():
    post=UserBlog.query.order_by(UserBlog.posted_on).all()
    
    return render_template('index.html',posts=post,users=current_user)


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user =User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            flash('Login successful')
            login_user(user)
            return redirect(url_for('Welcome'))

        flash('Login unsuccessful, please try again')
        return render_template('login.html')
    else:
        return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        phone_number=request.form.get('phone_number')
        username = request.form.get('username')
        password = request.form.get('password')
        cornfirm_password = request.form.get('confirm_password')


        user = User.query.filter_by(username= username).first()
        if user:
            flash('Username already exist')
            return redirect(url_for('register'))
        email_exist = User.query.filter_by(email=email).first()
        if email_exist:
            return redirect(url_for('register'))
        
        password_hash = generate_password_hash(password)

        new_user = User(firstname=firstname, lastname=lastname, phoneNumber=phone_number,
         email=email,username=username, password_hash=password_hash)
        
        db.session.add(new_user)
        db.session.commit()
        flash('SignUp Successful')

        return redirect('login')

    
    return render_template('sign_up.html')



@app.route('/posts',  methods=['GET', 'POST'])
def posts():
    if request.method == 'POST':
        post_title = request.form.get('title')
        post_content = request.form.get('post')
        
        new_post = UserBlog(title=post_title, content=post_content, users=current_user)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/posts')
    else:
        all_posts = UserBlog.query.order_by(UserBlog.posted_on).all()
        return render_template('posts.html', posts=all_posts)


@app.route('/posts/new', methods=['GET', 'POST'])
@login_required
def new_post():
    if request.method == 'POST':
        post_title = request.form.get('title')
        post_content = request.form.get('post')
        
        new_post = UserBlog(title=post_title,content=post_content,users=current_user)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/posts')
    else:
        return render_template('new_post.html')

@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    to_edit = UserBlog.query.get_or_404(id)
    if request.method == 'POST':
        to_edit.title = request.form.get('title')
        to_edit.content = request.form.get('post')
        db.session.commit()
        return redirect('/posts')
    else:
        return render_template('editPost.html', post=to_edit)


@app.route('/posts/delete/<int:id>')
@login_required
def delete(id):
    to_delete = UserBlog.query.get_or_404(id)
    db.session.delete(to_delete)
    db.session.commit()
    return redirect('/posts')

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('Welcome'))




if __name__ == "__main__":
    app.run(debug=True)