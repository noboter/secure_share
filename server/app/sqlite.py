import sqlite3
import time
from passlib.hash import pbkdf2_sha256

class Db:
    def __init__(self, file):
        self.file = file
        self.conn = sqlite3.connect(file)
        self.c = self.conn.cursor()
        self.create_db()

    def create_db(self):
        # Create table
        self.c.execute('''CREATE TABLE IF NOT EXISTS users
             (name text, password text, email text, registered real, lastlogin real)''')
        
        #only one key per username
        self.c.execute('''CREATE TABLE IF NOT EXISTS public_keys
             (username text, public_Key text, signed text, primary key(username))''')
        
        self.c.execute('''CREATE TABLE IF NOT EXISTS keys
             (public_Key_sender text, public_Key_receiver text, encKey text, dataid INTEGER, epoch INTEGER, primary key(public_Key_sender, public_Key_receiver, epoch))''')
        
        self.c.execute('''CREATE TABLE IF NOT EXISTS data
             (dataid INTEGER, data blob, epoch INTEGER, primary key(dataid, epoch))''')
        
        self.conn.commit()
    
    def insert(self,name,password,email):
        # check if username exists
        hash = pbkdf2_sha256.encrypt(password, rounds=200000, salt_size=16)
        t = (name,)
        self.c.execute('SELECT * FROM users WHERE name=?', t)
        data=self.c.fetchall()
        if len(data)>0:
            return False
        else:
            # Insert a row of data
            epoch=int(time.time())
            query="INSERT INTO users VALUES ('"+name+"','"+hash+"','"+email+"',"+str(epoch)+","+str(epoch)+")"
            self.c.execute(query)
            # Save (commit) the changes
            self.conn.commit()
            return True
    
    def login(self, name, password):
        t = (name,)
        self.c.execute('SELECT password FROM users WHERE name=?', t)
        data = self.c.fetchone()
        if(data==None):
            return False # user is not existing
        test=pbkdf2_sha256.verify(password, data[0])
        if(test):
            self.update(name)
            return True
        else:
            return False
        
    def update(self,name):
        epoch=int(time.time())
        self.c.execute("UPDATE users SET lastlogin="+str(epoch)+" WHERE name='"+name+"'")
        # Save (commit) the changes
        self.conn.commit()
        
    def close(self):
        self.conn.close()
        
    def get_pubkeys(self):
        self.c.execute('SELECT * FROM public_keys')
        data = self.c.fetchall()
        result = []
        if(data==None):
            return "" # user is not existing
        for row in data:
            result.append(row)
        return result
    
    def insert_pubkey(self, data):
        epoch=int(time.time())
        sql = "INSERT OR REPLACE INTO public_keys (username,public_Key,signed) values (?, ?, ?)"
        self.c.execute(sql, (data['name'], data['publickey'], str(int(epoch))))
        self.conn.commit()
        return True
        #print(query)
        #print("executed")
    
    def findPk(self, name):
        sql = "SELECT * FROM public_keys where username = ?"
        self.c.execute(sql, (name,))
        data = self.c.fetchall()
        result=[]
        if(data==None):
            return "" # user is not existing
        for row in data:
            result.append(row)
        return result
        #print(query)
        #print("executed")
    