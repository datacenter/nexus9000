'''
http://www.tylerlesmann.com/2008/dec/19/encrypting-database-data-django/
'''

#!/usr/bin/env python
import string
from random import choice
from Crypto.Cipher import AES

EOD = '`%EofD%`' # This should be something that will not occur in strings

def genstring(length=16, chars=string.printable):
    return ''.join([choice(chars) for i in range(length)])

def encrypt(key, s):
    obj = AES.new(key)
    datalength = len(s) + len(EOD)
    if datalength < 16:
        saltlength = 16 - datalength
    else:
        saltlength = 16 - datalength % 16
    ss = ''.join([s, EOD, genstring(saltlength)])
    return obj.encrypt(ss)

def decrypt(key, s):
    obj = AES.new(key)
    ss = obj.decrypt(s)
    return ss.split(EOD)[0]

if __name__ == '__main__':
    for i in xrange(8, 20):
        s = genstring(i)
        key = genstring(32)
        print 'The key is', key
        print 'The string is', s, i
        cipher  = encrypt(key, s)
        print 'The encrypted string is', cipher
        print 'This decrypted string is', decrypt(key, cipher)
        
        
    #!/usr/bin/env python
    import binascii
    
    key = "32 character key can be anything"
    
    s = "Sensitive Data"
    print "Unencrypted data:", s
    
    es = encrypt(key, s)
    print "Encrypted binary:", es
    
    esb64 = binascii.b2a_base64(es)
    print "Encrypted base64:", esb64
    
    esbin = binascii.a2b_base64(esb64)
    print "Back to binary:", esbin
    
    ds = decrypt(key, esbin)
    print "Decrypted data", ds
    