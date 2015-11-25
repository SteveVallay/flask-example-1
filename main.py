import sqlite3,datetime
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

DATABASE = '/tmp/myapp.db'
DEBUG = 'true'
SECRET_KEY = 'development key'
g_date=''

app = Flask(__name__)
app.config.from_object(__name__)

@app.before_request
def before_request():
    g.db = con_db()
@app.teardown_request
def teardown_request(exception):
    db = getattr(g,'db',None)
    if db is not None:
        db.close()
@app.route('/<pdate>')
@app.route('/',methods=['GET','POST'])
def index(pdate=None):
    print 'inside'
    if request.method == 'POST':
        print 'form'
        data = request.form
        print 'data:',data
        try:
            db_update_data(data)
        except Exception as e:
            flash("Some worms has been taken")

        print 'request index'
        pd=data['data-add']
        return redirect(url_for('index')+pd)
    else:
        if "logged_in" not in session:
            flash("Login to catch the worms")
        args = request.args
        print "args:" ,args
        if args:
            try:
                dt=datetime.date(int(args['year']),int(args['month']),int(args['day']))
                pdate=dt.strftime('%Y%m%d')
            except ValueError as e:
                print e
        date=datetime.datetime.now()
        #verify pdate format
        if not pdate:
            pdate = date.strftime('%Y%m%d')
            print pdate
        if not check_date(pdate):
            flash('your date format ' + pdate + ' not correct')
            pdate = date.strftime('%Y%m%d')
        else:
            date = datetime.date(int(pdate[0:4]),int(pdate[4:6]),int(pdate[6:8]))
        users=[]
        for row in db_get_user():
            users.append(row[1])
        otmap={}
        otdata = db_get_otdata(pdate)
        if otdata:
            for row in db_get_otdata(pdate):
                otmap[row[1]]=row[0]
        print users
        print otmap
        for user in users:
            if user in otmap:
                print user
            else:
                print user ,'not exist in map'
        return render_template('index.html',pdate=pdate,year=date.year,month=date.month,day=date.day,users=users,otmap=otmap)

@app.route('/login',methods=['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
        name=request.form['username']
        password=request.form['password']
        if db_check_user(name,password):
            flash(' you were logged in')
            session['logged_in'] = True
            session['user_name'] = name
            return redirect(url_for('index'))
        else:
          error='invalid username or password'
    else:
        if 'logged_in' in session and session['logged_in'] == True:
            flash("you have logged in")
            return redirect(url_for('index'))
    return render_template('login.html',error=error)
@app.route('/logout')
def logout():
    session.pop('logged_in',None)
    session.pop('user_name',None)
    flash('You were logged out')
    return redirect(url_for('index'))
def check_date(d):
    if len(d) != 8:
        return False
    y = d[0:4]
    m = d[4:6]
    d = d[6:8]
    try:
        dt=datetime.date(int(y),int(m),int(d))
        print dt
    except ValueError as e:
        print e
        return False
    return True
def db_check_user(username,password):
    sql='select * from user where username=\''+ username+'\'and  password=\'' + password + '\''
    print sql
    cur = g.db.execute(sql)
    rv = cur.fetchall()
    print 'rv:',rv
    cur.close()
    return (True if rv else False)
def db_get_user():
    cur = g.db.execute('select id,username from user order by username')
    rv = cur.fetchall()
    print rv
    cur.close()
    return (rv if rv else None)
def db_update_data(data):
    '''year = data['year']
    month = data['month']
    day= data['day']
    dt=datetime.date(int(year),int(month),int(day))
    ymd = dt.strftime('%Y%m%d')
    print 'ymd',ymd
    '''
    ymd=data['data-add']
    sql='insert into  otmap values '
    for row in db_get_user():
        if row[1] in data:
            print row[1]
            s= sql + '('+ymd+',\''+session['user_name'] +'\'' +',\''+row[1]+'\')'
            print s
            g.db.execute(s)
        else:
            pass
    g.db.commit()

def db_get_otdata(date):
    sql_get_otdata="select otsrc,otdst from otmap where date="+'\''+date+'\''
    cur = g.db.execute(sql_get_otdata)
    rv = cur.fetchall()
    print rv
    cur.close()
    return (rv if rv else None)


def con_db():
    return sqlite3.connect(app.config['DATABASE'])


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=2015)
