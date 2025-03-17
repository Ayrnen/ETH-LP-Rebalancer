from classes.config_reader import ConfigReader
from classes.etherscan_client import EtherscanClient

import asyncio
import json
import requests
from web3 import Web3
from websockets import connect


class ETHLAddressClient:
    def __init__(self, address):
        self.config = ConfigReader()
        self.etherscan = EtherscanClient('Mainnet')

        self.ws_url = 'wss://mainnet.infura.io/ws/v3/990dd01e4e974b4ea477b0dbeeacb288'
        self.http_url = 'https://mainnet.infura.io/v3/990dd01e4e974b4ea477b0dbeeacb288'
        self.web3 = Web3(Web3.HTTPProvider(self.http_url))
        self.address = address
    

    def get_balance_eth(self):
        balance = self.web3.eth.get_balance(self.address)
        return self.web3.from_wei(balance, 'ether')

    def get_balance_token(self, token_code):
        token_address = self.config.get_specific_value('mainnet-token-addresses', token_code)
        token_abi = self.etherscan.get_token_abi(token_address)
        token_contract = self.web3.eth.contract(address=token_address, abi=token_abi)
        balance = token_contract.functions.balanceOf(self.address).call()
        return balance

    def get_transaction_count(self):
        transactions = self.web3.eth.get_transaction_count(self.address)
        return transactions
    
    async def get_pending_txns(self):
        async with connect(self.ws_url) as ws:
            await ws.send(json.dumps({
                'jsonrpc': '2.0',
                'id': 1,
                'method': 'eth_subscribe',
                'params': ['newPendingTransactions']
            }))
            # subscription_response = await ws.recv()

            while True:
                try:
                    message = await asyncio.wait_for(ws.recv(), timeout=15)
                    response = json.loads(message)
                    txHash = response['params']['result']
                    print(txHash)

                    tx = self.web3.eth.get_transaction(txHash)
                    if self.address == None:
                        message = await asyncio.wait_for(ws.recv(), timeout=15)
                        response = json.loads(message)
                        txHash = response['params']['result']
                        print(txHash)

                    elif tx.to == self.address:
                        print('Pending transaction found with the following details:')
                        print({
                            'hash': txHash,
                            'from': tx['from'],
                            'value': self.web3.fromWei(tx['value'], 'ether')
                        })

                except Exception as e:
                    print(f'An error occurred: {e}')
                    pass