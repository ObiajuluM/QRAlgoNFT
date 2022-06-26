import hashlib
import random
import time
from datetime import datetime
from os import urandom

import qrcode
from algosdk.future import transaction
from algosdk.future.transaction import (AssetConfigTxn, AssetTransferTxn,
                                        PaymentTxn)
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import RadialGradiantColorMask

algod_address = "https://testnet-algorand.api.purestake.io/ps2" 
indexer_address = "https://testnet-algorand.api.purestake.io/idx2"
algod_token = "HcMuKoVwiiaghFBOIdTFOcK1280ECCA2x4oMLN5h"
headers = {
    "X-API-Key": algod_token, # api key
}
algod_client = AlgodClient(algod_token, algod_address, headers)
indexer_client = IndexerClient("", indexer_address, headers)

params = algod_client.suggested_params()
params.flat_fee = True
params.fee = 1000

def write_to_block(sender_addr: str, sender_key: str, msg: str, fee_addr: str):
    assert len(msg) < 1000
    txn = PaymentTxn(sender_addr, params, fee_addr, 10000, note=msg)
    stxn = txn.sign(sender_key)
    txid = algod_client.send_transaction(stxn)
    return txid

def return_current_algo_block() -> int:
    status = algod_client.status()
    current_round = int(status['last-round'])
    return current_round

def return_current_algo_block_inf() -> int:
    while 1 > 0:
        status = algod_client.status()
        current_round = int(status['last-round'])
        return current_round

def return_block_time(block: int) -> str:
    """returns time a block was verified"""
    time_stamp = algod_client.block_info(block)["block"]["ts"]
    dt_obj = datetime.fromtimestamp(time_stamp)
    date_time = dt_obj.strftime("%A %d %B %Y, %H:%M:%S")
    return date_time

def hash_block(block: int) -> bytes:
    """hash info about the nft to verify intergrity"""
    s = hashlib.sha256()
    block_binary = f'{block}'.encode('utf-8')
    s.update(block_binary)
    return s.digest()

# print(json.dumps(indexer_client.block_info(21895901), indent=2))

def txns_count(block: int) -> int:
    if "txns" in algod_client.block_info(block)["block"]:
        return len(algod_client.block_info(block)["block"]["txns"])
    else :
        return 0

def bytes_generator() -> bytes:
    """generates a random byte"""
    return urandom(random.randint(10, 20))

def block_dict(block: int, minter: str) -> dict:
    return{
        "Block": block,
        "Date_Created": return_block_time(block),
        "Transaction_Count": txns_count(block),
        "Minter": minter,
        "Date_Minted": f'{datetime.now().strftime("%A %d %B %Y, %H:%M:%S")}',
        "Unique_Id": bytes_generator()
    }

# print(block_dict(17017319, "BENCIYB3PBD77K4VQ2NA3DGBSH6OORMYX4TEOHC6635GUKPP7QLQ"))

def mint_nft(block: int, minter_addr: str, minter_key: str, fee_addr: str, fee_amount):
    assert return_current_algo_block() >= block

    bd = block_dict(block, minter_addr)

    txn1 = AssetConfigTxn(strict_empty_address_check=False,
    sender=minter_addr,
    sp=params,
    total=1, # max 18 quintillion
    default_frozen=False, # bool
    unit_name="QRAlgo", # max 8
    asset_name=F"{block}", # max 32
    manager="",
    reserve="",
    freeze="",
    clawback="",
    url="",
    decimals=0, # max 19
    metadata_hash=hash_block(block))

    txn2 = PaymentTxn(minter_addr, params, fee_addr, fee_amount)

    gid = transaction.calculate_group_id([txn1, txn2])
    txn1.group = gid
    txn2.group = gid
    stxn1 = txn1.sign(minter_key)    
    stxn2 = txn2.sign(minter_key)
    signed_group =  [stxn1, stxn2]
    txid = algod_client.send_transactions(signed_group)
    
    time.sleep(9)

    if 'confirmed-round' in indexer_client.transaction(txid)['transaction']:
        # add wait to verify txn
        color_code = [i for i in range(256)]
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=5, border=2,)

        qr.add_data(bd)
        qr.make(fit=True)
        img = qr.make_image(image_factory=StyledPilImage, embeded_image_path="algo.png",color_mask=RadialGradiantColorMask(
            back_color=(255, 255, 255),
            center_color=(random.choice(color_code), random.choice(color_code), random.choice(color_code)),
            edge_color=(random.choice(color_code), random.choice(color_code), random.choice(color_code)),
        ))
        img.save(f"{block}.png")
        return "Successfull!, you now own a piece of history"
    else: 
        return "something went wrong"

# print(mint_nft(
#     17017309,
#     "VQIMXAPONHJV3W2HIQACCZWNUC5JIVWIFHRAV35ZH524M6NIZJXXHTLPJE",
#     "W3I9M28ZU3BNy8mZKlS4q2F4prsqHH5JDKoRiRe0y2CsEMuB7mnTXdtHRAAhZs2gupRWyCniCu+5P3XGeajKbw==",
#     "SNKNM4AICGBH5CGN6E6EEWJ64UXAX55A7IDPYYUKGXHFTG3XVZ2G7SCZBA", 
#     100000
# ))
