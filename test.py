# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 18:45:29 2019

@author: norbert
"""

from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome import Random
from Cryptodome.PublicKey import RSA


BLOCK_SIZE = 16  # Bytes
PAD = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)

class client:
    
    privatekey = ""
    publickey = ""
    
    def __init__(self):
        print("client generating RSA Key");
        #generate client rsa public/private key
        privkey = RSA.generate(2048)
        self.privatekey = privkey.export_key()#4096)
        #encrypted_key = key.export_key(passphrase=secret_code, pkcs=8, protection="scryptAndAES128-CBC")
        self.publickey = privkey.export_key();
        
    def encKey(self, AESKey, receipientPublicKey):
        recipient_key = RSA.import_key(receipientPublicKey)
        cipher_rsa = PKCS1_OAEP.new(recipient_key)
        return cipher_rsa.encrypt(AESKey)
        
    def decKey(self, encAESkey):
        private_key = RSA.import_key(self.privatekey)
        cipher_rsa = PKCS1_OAEP.new(private_key)
        return cipher_rsa.decrypt(encAESkey)

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


text = "create two users, a file with this data and encrypt the AESkey \
        with RSA from first user for the second"

#two clients:
print("Alice")
alice = client()
print("Bob")
bob = client()

#a bit of data
f = data()
AESencryptedText = f.enc(text)
print("encrypted data: ")
print(AESencryptedText)

#now alice encrypts the key for bob
encAESkey = alice.encKey(f.AESkey, bob.publickey)
print("Key from Alice encrypted for Bob: ")
print(encAESkey)

#bob decrypts the key 
decAESkey = bob.decKey(encAESkey)
#now bob can decrypt the data
print("Data decrypted by Bob")
print(decrypt(AESencryptedText, decAESkey))

#doll