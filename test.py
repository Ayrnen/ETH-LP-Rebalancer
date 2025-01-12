from classes.aws_api import AWSAPIHandler
from classes.etherscan_api import EtherscanAPIHandler
from classes.runtime_tracker import RuntimeTracker
from web3 import Web3
import datetime as dt



class Sepolia:
    def __init__(self):
        self.aws_api = AWSAPIHandler()
        self.etherscan = EtherscanAPIHandler()
        self.credentials = self.aws_api.get_sepolia_credentials()
        self.provider_url = self.credentials['sepolia-endpoint']
        self.wallet_key = self.credentials['private-key']
        self.web3 = Web3(Web3.HTTPProvider(self.provider_url))

        if self.web3.is_connected():
            print("Connected to Sepolia Testnet!")
        else:
            print("Failed to connect")

    def get_wallet_address(self):
        return self.web3.eth.account.from_key(self.wallet_key).address

    def get_wallet_balance(self):
        wallet_address = self.get_wallet_address()
        balance = self.web3.eth.get_balance(wallet_address)
        return self.web3.from_wei(balance, 'ether')


    def interact_with_pool(self):
        v3_factory_address = '0x0227628f3F023bb0B980b67D528571c95c6DaC1c'
        v3_factory_abi = self.etherscan.get_contract_abi(v3_factory_address)
        print('ABI Fetched!')

        contract = self.web3.eth.contract(address=Web3.to_checksum_address(v3_factory_address), abi=v3_factory_abi)
        print('Contract Created!')

        eth_sep = '0x7b79995e5f793A07Bc00c21412e50Ecae098E7f9'
        usdc_sep = '0x94a9D9AC8a22534E3FaCa9F4e7F2E2cf85d5E4C8'
        fee = 3000

        pool_address = contract.functions.getPool(eth_sep, usdc_sep, fee).call()
        print(f"Pool Address: {pool_address}")

        pool_abi = self.etherscan.get_contract_abi(pool_address)
        pool_contract = self.web3.eth.contract(address=Web3.to_checksum_address(pool_address), abi=pool_abi)

        slot0 = pool_contract.functions.slot0().call()
        unformatted_price = slot0[0]
        price = (unformatted_price / (2 ** 96)) ** 2
        curr_tick = slot0[1]  
        obs_idx = slot0[2] 
        obs_cardinality = slot0[3]
        obs_cardinality_next = slot0[4]
        fee_protocol = slot0[5]
        lock_status = slot0[6] 

        print(price)




if __name__ == '__main__':
    RuntimeTracker.start()
    sepolia = Sepolia()

    print(f'Wallet Address: {sepolia.get_wallet_address()}')
    print(f'Wallet Balance: {sepolia.get_wallet_balance()} ETH')

    sepolia.interact_with_pool()

    RuntimeTracker.stop()