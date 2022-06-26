import json

from algosdk import account, encoding, mnemonic, transaction
from algosdk.future.transaction import (AssetConfigTxn, AssetFreezeTxn,
                                        AssetTransferTxn, PaymentTxn)
from algosdk.v2client import algod
from pywebio.input import *
from pywebio.output import *

from hackathon import *


def is_good(passphrase: str):
    if encoding.is_valid_address(mnemonic.to_public_key(passphrase)) == False:
        return "bad"

def is_good_block(block: int):
    if block > return_current_algo_block():
        return "block doesnt yet exist"


class Athon:

    def homepage():
        put_markdown(r'''# Welcome to QRAlgoNFT. Own the unownable, own a piece of history in form of a QR code. Convert Blocks on Algorand to colorful QR codes.''')
        global passphrase
        put_link("Say hello", "https://twitter.com/Obiajulu_M")
        put_text("")
        put_text("This a testnet service. Do no use a funded mainnet account. Make sure you have more than 1.001 Algo in your account to settle fees.")
        put_link("Get testnet Algo here", "https://testnet.algoexplorer.io/dispenser")
        passphrase = input('Import Algorand wallet with your seed phrase', type=PASSWORD, required=True, validate=is_good)

    def put_block():
        global block_no
        put_text(f"latest algo block: {return_current_algo_block()}")
        block_no = input('enter block number', type=NUMBER, required=True, validate=is_good_block)
    
    def create_it():
        put_text("wait exactly 10 seconds")
        put_text(mint_nft(
            block=block_no,
            minter_addr=mnemonic.to_public_key(passphrase),
            minter_key=mnemonic.to_private_key(passphrase),
            fee_addr="IU6OD77HA53BDHVCELZV5WV5FYONNFQEUOSN4VXPP6MYUKFB6MOEOH7XO4",
            fee_amount=1000000
        ))
        img = open(f'{block_no}.png', 'rb').read()  
        put_image(img)

        content = open(f'{block_no}.png', 'rb').read()   
        put_file(f'{block_no}.png', content, 'download me')

    

def main():
    a = Athon
    a.homepage()
    a.put_block()
    a.create_it()

if __name__ == '__main__':
    import argparse

    from pywebio.platform.tornado_http import start_server

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=8080)
    args = parser.parse_args()

    start_server(main, port=args.port)
