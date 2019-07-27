# secure_share
securely share data 

The server is based on Flask with a SQLite Database

the client generates 4096 bit RSA Keys
- private keys are stored on the users' side  
- public keys are uploaded to the server

quering for publickeys based on usernames is possible

- clients will generate new AES keys for all uploaded data
- AES keys are then encrypted by other users public keys 
- encrypted keys and encrypted data is uploaded to the server

TODO:
- use TLS connections
- use certificates to secure the publickeys
- limit the time a file is shared
- select which data to decrypt
- enable authenticated deletion of data