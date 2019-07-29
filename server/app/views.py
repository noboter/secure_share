from app import app
from app.sqlite import Db
from flask import render_template, redirect, request, Markup, session, escape, jsonify
import json


@app.route('/login', methods=['GET', 'POST'])
def login():
    db = Db('database.db')
    
    error = None
    if request.method == 'POST':
        name = request.form['username']
        passw = request.form['password']
        if(db.login(name,passw)):
            #set the user as active
            session['username'] = name
            #global u
            #u = User(request.form['username'],True)
            return redirect('/protected')
        else:
            error = "That didn't work"

    return render_template('login.html', error=error)
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    db = Db('database.db')
    #db.create_db()

    error = None
    if request.method == 'POST':
        name = request.form['username']
        passw = request.form['password']
        email = request.form['email']
        if(db.insert(name,passw,email)):
            #set the user as active            
            #u = User(request.form['username'],True)
            session['username'] = name
            return redirect('/protected')
        else:
            error = "Name exists, please chose a different one"

    return render_template('register.html', error=error)

@app.route('/protected', methods=['GET', 'POST'])
def prot():
    if 'username' in session:
        return 'logged in </br></br><a href="/">home</a>'
    else:
        return redirect('/')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    return redirect('/')
    
@app.route('/', methods=['GET', 'POST'])
def index():
    title  = 'welcome'
    content = ''

    if 'username' in session:
        content+='Logged in as %s' % escape(session['username'])
        content+= Markup('''</br><a href="/logout">logout</a></br>
                        <a href="/protected">protected</a></br>
                        <a href="/dict">phonebook</a></br>''')
    else:
        content+='You are not logged in'
        content+= Markup('''</br><a href="/login">login</a> &nbsp 
                        <a href="/register">register</a></br>''')
    content+=Markup("</br>");
    
    return render_template('index.html', title=title,content=content)
        
@app.route('/dict', methods=['GET', 'POST'])
def listkeys():
    if 'username' in session:
        db = Db('database.db')
        #anti scraping gibberisch, just return random suff
        body = Markup("<a href='/'>home</a></br>")
        body += Markup("</br>")
        pks = db.get_pubkeys();
        body+=Markup("<table><th>name</th><th>pubkey</th><th>signed</th><tbody>")
        for i in pks:
            body+=Markup("<tr>")
            for j in i:
                body += Markup("<td>")+str(j)+Markup("</td>")
            body+=Markup("</tr>")
        body+=Markup("</tbody></table>")
        body += Markup("</br>")
        return render_template('index.html', content=body)
    else:
        return redirect('/')

@app.route('/postkey', methods=['POST'])
def postkey():
    #add keys or files or .. to the db through client
    db = Db('database.db')
    if(request.is_json):
        ##get parameters
        content = request.get_json()
        data = json.loads(content)
        #return(jsonify(data['name']))
        res = db.insert_pubkey(data)

        return jsonify(result=res)
    else:
        return jsonify(result=False)

@app.route('/uploadData', methods=['POST'])
def uploadData():
    #add keys or files or .. to the db through client
    db = Db('database.db')

    chunk_size = 4096
    while True:
        chunk = request.stream.read(chunk_size)
        if len(chunk) == 0:
            return
        
        res = db.insert_data(chunk) #should return an id 
        return jsonify(result=res)
    else:
        return jsonify(result=False)

@app.route('/postRelease', methods=['POST'])
def postRelease():
    #add keys or files or .. to the db through client
    db = Db('database.db')
    if(request.is_json):
        ##get parameters
        content = request.get_json()
        data = json.loads(content)
        res = db.insert_Release(data)
        return jsonify(result=res)
    else:
        return jsonify(result=False)

@app.route('/getData', methods=['POST'])
def getData():
    #add keys or files or .. to the db through client
    db = Db('database.db')
    if(request.is_json):
        ##get parameters
        content = request.get_json()
        data = json.loads(content)
        
        res = db.get_Data(data['pk'])
        
        return jsonify(result=res)
    else:
        return jsonify(result=False)

@app.route('/queryPK', methods=['POST'])
def queryPK():
    #add keys or files or .. to the db through client
    db = Db('database.db')
    if(request.is_json):
        ##get parameters
        content = request.get_json()
        data = json.loads(content)
        res = db.findPk(data['name'])

        return jsonify(res)
    else:
        return jsonify(result=False)
