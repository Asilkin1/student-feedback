from Crypto.Cipher import AES
from base64 import b64encode
import Padding
import binascii
import hashlib
random_key = b"J3FTV1PL1jDFeMh01I9r+A=="
random_key = b64encode(random_key).decode('utf-8')
# Encryption


def mysql_aes_encrypt(val, key):
    '''Perform encryption'''
    val = Padding.appendPadding(
        val, blocksize=Padding.AES_blocksize, mode='Random')

    def mysql_aes_key(key):
        return hashlib.sha256(key.encode()).digest()

    def mysql_aes_val(val, key):
        encrypted = AES.new(key, AES.MODE_ECB)
        return encrypted.encrypt(val)

    k = mysql_aes_key(key)
    v = mysql_aes_val(val.encode(), k)
    v = binascii.hexlify(bytearray(v))

    return v

# Decryption


def mysql_aes_decrypt(val, key):
    '''Perform decryption'''
    val = binascii.unhexlify(bytearray(val))

    def mysql_aes_key(key):
        return hashlib.sha256(key.encode()).digest()

    def mysql_aes_val(val, key):
        decrypted = AES.new(key, AES.MODE_ECB)
        return decrypted.decrypt(val)

    k = mysql_aes_key(key)
    v = mysql_aes_val(val, k)

    v = Padding.removePadding(v.decode(), mode='Random')

    return v

# ----------------------------------------------------------------
# Decrypt frame


def decrypt_frame(frame):
    # Go through the columns and data in each column in the Frame
    for (column, column_data) in frame.iteritems():
        # if the column is emoji
        if column == "emoji":
            # Go through the data in emoji column
            for values in column_data.values:
                # If it is decrypted, continue
                if isinstance(values, int):
                    continue
                else:
                    # If it isn't decrypted, decrypt it
                    decrypt_value = mysql_aes_decrypt(values, random_key)
                    # Replace it everywhere in the column
                    frame[column] = frame[column].replace(
                        values, int(decrypt_value))
        # if the column is elaborateText
        if column == "elaborateText":
            # Go through the data in emoji column
            for values in column_data.values:
                # If it is decrypted, continue
                if isinstance(values, str):
                    continue
                else:
                    # If it isn't decrypted, decrypt it
                    decrypt_value = mysql_aes_decrypt(values, random_key)
                    # Replace it everywhere in the column
                    frame[column] = frame[column].replace(
                        values, decrypt_value)
        # if the column is elaborateNumber
        if column == "elaborateNumber":
            # Go through the data in emoji column
            for values in column_data.values:
                # If it is decrypted, continue
                if isinstance(values, str):
                    continue
                else:
                    # If it isn't decrypted, decrypt it
                    decrypt_value = mysql_aes_decrypt(values, random_key)
                    # Replace it everywhere in the column
                    frame[column] = frame[column].replace(
                        values, decrypt_value)
    return frame
