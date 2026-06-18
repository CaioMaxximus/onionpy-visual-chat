import aiobcrypt

async def verify_hash(hashed_pass, raw_data):

    raw_data_b = raw_data.encode('utf-8')
    hashed_pass_b = hashed_pass.encode('utf-8')
    res = await aiobcrypt.checkpw(raw_data_b,hashed_pass_b)
    if res:
        return
    else:
        raise RuntimeError("Invalid pass!")
    
