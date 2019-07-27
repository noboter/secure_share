#!flask/bin/python
from app import app

# set the secret key.  keep this really secret:
app.secret_key = 'KZb5CZgbyzsFh&BT%NMTP@YN^&5F'

app.run(host='0.0.0.0',port=5000,debug=True)