from flask import Flask, render_template,request, redirect,flash,session
from datetime import datetime
from models import db,User,Todo
from sqlalchemy import or_
from dotenv import load_dotenv
import os

load_dotenv()


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
app.secret_key = os.environ.get("SECRET_KEY")



with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        title    = request.form['title']
        desc     = request.form['desc']
        priority = request.form.get('priority', 'Medium')
        due_str  = request.form.get('due_date', '')
        due_date = datetime.strptime(due_str, '%Y-%m-%d').date() if due_str else None

        todo = Todo(title=title, desc=desc, priority=priority,due_date=due_date, user_id=session['user_id'])
        db.session.add(todo)
        db.session.commit()
        return redirect('/')

    # Search & Filter — only runs on GET
    search      = request.args.get('search', '')
    sel_priority = request.args.get('priority', '')

    query = Todo.query.filter_by(user_id=session['user_id'])

    if search:
        query = query.filter(or_(Todo.title.ilike(f'%{search}%'), Todo.desc.ilike(f'%{search}%')))
    if sel_priority:
        query = query.filter_by(priority=sel_priority)

    allTodo = query.all()
    return render_template('index.html', allTodo=allTodo,search=search, sel_priority=sel_priority)


@app.route('/update/<int:SNo>',methods = ['GET','POST'])
def update(SNo):
    if 'user_id' not in session:
        return redirect('/login')
    
    if request.method=='POST':
        title = request.form['title']
        desc = request.form['desc']

        todo = Todo.query.filter_by(SNo=SNo).first()

        todo.title = title
        todo.desc = desc
        todo.priority = request.form.get('priority', 'Medium')
        due_str = request.form.get('due_date', '')
        todo.due_date = datetime.strptime(due_str, '%Y-%m-%d').date() if due_str else None

        db.session.add(todo)
        db.session.commit()
        return redirect("/")
    todo = Todo.query.filter_by(SNo=SNo).first()

    return render_template('update.html',todo=todo)


@app.route('/delete/<int:SNo>')
def delete(SNo):
    if 'user_id' not in session:
        return redirect('/login')
    
    todo = Todo.query.filter_by(SNo=SNo).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect("/")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing = User.query.filter_by(username=username).first()
        if existing:
            flash('Username already taken!', 'error')
            return redirect('/signup')

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created! Please login.', 'success')
        return redirect('/login')

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect('/')
        else:
            flash('Wrong username or password!', 'error')
            return redirect('/login')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/toggle/<int:SNo>')
def toggle(SNo):
    if 'user_id' not in session:
        return redirect('/login')
    todo = Todo.query.filter_by(SNo=SNo, user_id=session['user_id']).first()
    todo.status = 'Complete' if todo.status == 'Pending' else 'Pending'
    db.session.commit()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)