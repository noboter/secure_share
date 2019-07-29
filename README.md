# secure_share
securely share data 

The server is based on Flask with a SQLite Database

the client generates 4096 bit RSA Keys
- private keys are stored on the users' side  
- public keys are uploaded to the server

quering for publickeys based on usernames is possible

- clients will generate new AES keys for all uploaded data
- AES keys are then encrypted by other users RSA public keys
- the AES encrypted data is signed with the senders private key
- RSA encrypted AESkey and AES encrypted data is uploaded to the server

TODO:
- TLS connections, so the clients know with which server they are talking
- select which data to decrypt (not always all like now)
- enable deletion of data