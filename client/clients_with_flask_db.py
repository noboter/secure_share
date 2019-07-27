# -*- coding: utf-8 -*-
"""
Created on Sat Jul 27 09:13:41 2019

@author: norbert
"""

import json
import requests
import random
import string
import base64
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
        if(self.readKeyFromHD()):
            private_key = RSA.import_key(self.privatekey)
        else:
            print("[*] client generating RSA Key for " + name);
            #generate client rsa public/private key
            private_key = RSA.generate(4096)
            self.privatekey = private_key.export_key()
            self.safeKey()

        #encrypted_key = key.export_key(passphrase=secret_code, pkcs=8, protection="scryptAndAES128-CBC")
        self.publickey = private_key.publickey().export_key()
        
    def encKey(self, AESKey, receipientPublicKey):
        recipient_key = RSA.import_key(receipientPublicKey)
        cipher_rsa = PKCS1_OAEP.new(recipient_key)
        return cipher_rsa.encrypt(AESKey)
        
    def decKey(self, encAESkey):
        private_key = RSA.import_key(self.privatekey)
        cipher_rsa = PKCS1_OAEP.new(private_key)
        return cipher_rsa.decrypt(encAESkey)
    
    def safeKeyToHD(self):
        file_out = open("rsa_key_"+self.name+".bin", "wb")
        file_out.write(self.privatekey)
        file_out.close()
        
    def readKeyFromHD(self):
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
            print('[!] Error: private keyfile does not exist')
            return False

    
    def uploadKeyToServer(self):#, phonebook):
        #stores the public key and other relevant data on server 
        #phonebook is the url of the server
        data = {}
        data['publickey'] = self.publickey.decode('utf-8')
        data['name'] = self.name
        j = json.dumps(data)
        #debug
        #print("upload data " + j)
        try:
            res = requests.post('http://localhost:5000/postkey', json=j)
            #print(res)
            if res.ok:
                print("[+] upload of " + self.name + "s key:" + str(res.json()))
        except Exception as e:
            print("[!] Error: cannot connect to server to upload the Pubkey of user: " + self.name)
            
    def queryPkOnServer(self, username):#, phonebook):
        #stores the public key and other relevant data on server 
        #phonebook is the url of the server
        data = {}
        data['name'] = username
        j = json.dumps(data)
        try:
            res = requests.post('http://localhost:5000/queryPK', json=j)
            #print(res)
            if res.ok:
                ret = res.json()
                #print(ret)
                return ret[0][1]
        except Exception as e:
            print("[!] Error: cannot connect to server to query pubkey from user: " + username)
            
    def uploadDataToServer(self, data, keys):
        #data is the AES encrypted data (bytes)
        #keys has alices and bobs public keys and the RSA encrypted AES Key for Bob
        #data gets an id to relate the RSA encrypted AES Key to a blob of data
        try:
            res = requests.post('http://localhost:5000/uploadData', data = str(data))
            #res will now be the dataid or False
            if res.ok:
                ret = res.json()
                print("[+] result of uploading: " + str(ret))
            else:
                return False
        
            maxid = ret['result']

            keysdata = {}
            keysdata['dataid'] = maxid
            keysdata['public_Key_sender'] = str(keys['public_Key_sender'])
            keysdata['public_Key_receiver'] = str(keys['public_Key_receiver'])
            keysdata['enc_Key'] = keys['enc_Key']
            j = json.dumps(keysdata)
        
            res = requests.post('http://localhost:5000/postRelease', json=j)
            if res.ok:
                print("[+] upload of Released Keys:" + str(res.json()))
                #return ret[0][1]
        except Exception as e:
            print("[!] Error: cannot connect to server to upload data from user: " + self.name)
        
    def getDataFromServer(self):
        #try:
        data = {}
        data['pk'] = self.publickey.decode('utf-8')
        j = json.dumps(data)
        res = requests.post('http://localhost:5000/getData', json = j)
        #res will now containt the data and the encrypted key
        #print(res)
        if res.ok:
            ret = res.json()
            print("[+] result of downloading ok ")# + str(ret))
            return ret
        else:
            return False
        
        #except Exception as e:
        #    print("[!] Error: cannot connect to server to upload data from user: " + self.name)

class data:
    
    AESkey = ""
    
    def __init__(self):
        print("[*] client generating AES Key for new data");
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

###############################  run tests ###############################
    

text = """creates two users, a bit of data (like this). Encrypt the Data with 
AES and encrypt the AESkey with RSA from alice for bob, the encrpted key 
and public RSA Keys are stored on a server"""

#two clients:
alice = client("Alice")
alice.uploadKeyToServer()

bob = client("Bob")
bob.uploadKeyToServer()


# now alice has some data to share with bob:
f = data()
#and encrypts it
AESencryptedData = f.enc(text)

#now alice encrypts the key for bob by asking the server for Bobs public key
bobsKey = alice.queryPkOnServer("Bob")
if(bobsKey):
    encAESkey = alice.encKey(f.AESkey, bobsKey)
    print("[+] encrypted data for Bob")

#so alice has the plaintext, the AESencryptedData, the AES Key and the RSAencryptedAESkey for bob
#now upload all this to the server
keys = {}
keys['public_Key_sender'] = alice.publickey.decode('utf-8')
keys['public_Key_receiver'] = bobsKey
keys['enc_Key'] = encAESkey.hex()
alice.uploadDataToServer(AESencryptedData.hex(), keys)


#Now bob can access data on the server and may decrpyt it
try:
    res = bob.getDataFromServer()    
    #now bob has data and keys
    for pair in res['result']:
        encAESkey2 = bytes.fromhex(pair['key'])
        #decrypt the key with own provate key
        decAESkey = bob.decKey(encAESkey2)
        #now decrypt the data
        data = bytes.fromhex(pair['data'])
        print("Data decrypted by Bob")
        print(decrypt(data, decAESkey).decode('utf-8'))
       
except NameError:
    print("[!] cannot decrpyt as the key does not exist")