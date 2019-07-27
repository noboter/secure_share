# secure_share
securely share data 

The server is based on Flask and manages users

the client generates 4096 bit RSA Keys
- private keys are stored on the users' side  
- public keys are uploaded to the server

quering for publickeys based on usernames is possible

TODO:
- upload encrypted data with AES Keys file 
- share RSA encrypted AES keys to securely share data
- use TLS connections
- use certificates to secure the publickeys
