import aiobcrypt


async def encrypt_data(raw_data):
    
    byte_data = raw_data.encode('utf-8')
    salt = await aiobcrypt.gensalt()
    hashed_data = await aiobcrypt.hashpw(byte_data, salt)

    return hashed_data.decode('utf-8')