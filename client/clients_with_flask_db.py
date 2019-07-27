# -*- coding: utf-8 -*-
"""
Created on Sat Jul 27 09:13:41 2019

@author: norbert
"""

import json
import requests
import random
import string
from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome import Random
from Cryptodome.PublicKey import RSA

BLOCK_SIZE = 16  # Bytes
PAD = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)

class client:
    
    privatekey = ""
    publickey = ""
    name = ""
    
    def __init__(self, name):
        self.name = name
        #check if key exists, otherwise create one
        if(self.readKey()):
            private_key = RSA.import_key(self.privatekey)
        else:
            print("client generating RSA Key for " + name);
            #generate client rsa public/private key
            private_key = RSA.generate(4096)
            self.privatekey = private_key.export_key()
            self.safeKey()

        #encrypted_key = key.export_key(passphrase=secret_code, pkcs=8, protection="scryptAndAES128-CBC")
        self.publickey = private_key.export_key()
        
    def encKey(self, AESKey, receipientPublicKey):
        recipient_key = RSA.import_key(receipientPublicKey)
        cipher_rsa = PKCS1_OAEP.new(recipient_key)
        return cipher_rsa.encrypt(AESKey)
        
    def decKey(self, encAESkey):
        private_key = RSA.import_key(self.privatekey)
        cipher_rsa = PKCS1_OAEP.new(private_key)
        return cipher_rsa.decrypt(encAESkey)
    
    def safeKey(self):
        file_out = open("rsa_key_"+self.name+".bin", "wb")
        file_out.write(self.privatekey)
        file_out.close()
        
    def readKey(self):
        try:
            f = open("rsa_key_"+self.name+".bin", "rb")
            key = f.read()
            f.close()
            if(len(key)<2):
                return False
            self.privatekey = key
            #close the file?
            return True
        except FileNotFoundError:
            print('File does not exist')
            return False

    
    def upload(self):#, phonebook):
        #stores the public key and other relevant data on server 
        #phonebook is the url of the server
        data = {}
        data['publickey'] = self.publickey.decode('utf-8')
        data['name'] = self.name
        j = json.dumps(data)
        #debug
        #print("upload data " + j)
        res = requests.post('http://localhost:5000/postkey', json=j)
        #print(res)
        if res.ok:
            print("upload of " + self.name + "s key:" + str(res.json()))
            
    def queryOnServer(self, username):#, phonebook):
        #stores the public key and other relevant data on server 
        #phonebook is the url of the server
        data = {}
        data['name'] = username
        j = json.dumps(data)
        res = requests.post('http://localhost:5000/queryPK', json=j)
        #print(res)
        if res.ok:
            ret = res.json()
            #print(ret)
            return ret[0][1]
           

class data:
    
    AESkey = ""
    
    def __init__(self):
        print("client generating AES Key");
        #generate client symmetric AES key
        key = "".join(random.choice(string.ascii_uppercase+
                         string.ascii_lowercase+string.digits) \
                         for _ in range(32))
        self.AESkey=bytes(key, 'utf-8')
        
    def enc(self, text):
        iv = Random.new().read(BLOCK_SIZE)
        aesobj = AES.new(self.AESkey, AES.MODE_CFB, iv)
        plaintext = bytes(PAD(str(text)), 'utf-8')
        return iv + aesobj.encrypt(plaintext)

def decrypt(enc, key):
    iv = enc[:16]
    cipher = AES.new(key, AES.MODE_CFB, iv )
    return cipher.decrypt( enc[16:] )


text = """create two users, a file with this data and encrypt the AESkey
        with RSA from first user for the second"""

#two clients:
alice = client("Alice")
alice.upload()

bob = client("Bob")
bob.upload()

#a bit of data
f = data()
AESencryptedText = f.enc(text)
#print("encrypted data: ")
#print(AESencryptedText)

#now alice encrypts the key for bob by asking the server for Bobs public key
bobsKey = alice.queryOnServer("Bob")
encAESkey = alice.encKey(f.AESkey, bobsKey)
#print("Key from Alice encrypted for Bob: ")
#print(encAESkey)

#bob decrypts the key 
decAESkey = bob.decKey(encAESkey)
#now bob can decrypt the data
print("Data decrypted by Bob")
print(decrypt(AESencryptedText, decAESkey))

#doll