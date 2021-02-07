from Crypto.Cipher import AES
from base64 import b64encode
import Padding
import binascii
import hashlib

random_key = b"J3FTV1PL1jDFeMh01I9r+A=="
random_key = b64encode(random_key).decode('utf-8')

# Encryption
def mysql_aes_encrypt(val, key):
    val = Padding.appendPadding(
        val, blocksize=Padding.AES_blocksize, mode='Random')

    def mysql_aes_key(key):
        return hashlib.sha256(key.encode()).digest()

    def mysql_aes_val(val, key):
        encrypted = AES.new(key, AES.MODE_ECB)
        print(encrypted)
        return(encrypted.encrypt(val))

    k = mysql_aes_key(key)
    v = mysql_aes_val(val.encode(), k)
    v = binascii.hexlify(bytearray(v))

    return v

# Decryption


def mysql_aes_decrypt(val, key):
    val = binascii.unhexlify(bytearray(val))

    def mysql_aes_key(key):
        return hashlib.sha256(key.encode()).digest()

    def mysql_aes_val(val, key):
        decrypted = AES.new(key, AES.MODE_ECB)
        return(decrypted.decrypt(val))

    k = mysql_aes_key(key)
    v = mysql_aes_val(val, k)

    v = Padding.removePadding(v.decode(), mode='Random')

    return v

def decryption(classCode, Category):
    Frame = pd.read_sql_query("SELECT * from feedback", databaseConnection)

    for row in range(0, len(Frame.index)):
        Frame.at[row, 'emoji'] = mysql_aes_decrypt(
            Frame.at[row, 'emoji'], random_key)
        Frame.at[row, 'elaborateNumber'] = mysql_aes_decrypt(
            Frame.at[row, 'elaborateNumber'], random_key)
        Frame.at[row, 'elaborateText'] = mysql_aes_decrypt(
            Frame.at[row, 'elaborateText'], random_key)

    return Frame

