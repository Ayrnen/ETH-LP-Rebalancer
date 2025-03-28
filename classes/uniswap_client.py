from classes.aws_client import AWSClient
from classes.etherscan_client import EtherscanClient
from classes.runtime_tracker import RuntimeTracker
from classes.config_reader import ConfigReader
from classes.rpc_client import RPCClient

from web3 import Web3



class UniswapClient:
    def __init__(self):
        self.aws_client = AWSClient()
        self.etherscan_client = EtherscanClient()
        self.web3_client = RPCClient()
        self.credentials = self.aws_client.get_sepolia_credentials()
        self.provider_url = self.credentials['sepolia-endpoint']
        self.wallet_key = self.credentials['private-key']
        
    # UniSwap API calls
    def get_factory_contract(self, factory_address):
        factory_abi = self.etherscan_client.get_contract_abi(factory_address)
        factory_contract = self.web3_client.web3.eth.contract(address=Web3.to_checksum_address(factory_address), abi=factory_abi)
        return factory_contract

    def get_pool_address(self, factory_contract, token0, token1, fee_tier):
        pool_address = factory_contract.functions.getPool(
            Web3.to_checksum_address(token0),
            Web3.to_checksum_address(token1),
            fee_tier
        ).call()
        return pool_address

    def get_pool_contract(self, pool_address):
        pool_abi = self.etherscan_client.get_contract_abi(pool_address)
        pool_contract = self.web3_client.web3.eth.contract(address=Web3.to_checksum_address(pool_address), abi=pool_abi)
        return pool_contract
    
    def get_pool_tokens(self, pool_address):
        pool_abi = self.etherscan_client.get_contract_abi(pool_address)
        pool_contract = self.web3_client.web3.eth.contract(address=Web3.to_checksum_address(pool_address), abi=pool_abi)
        token0 = pool_contract.functions.token0().call()
        token1 = pool_contract.functions.token1().call()
        return {'token0': token0, 'token1': token1}

    def create_pool(self, factory_contract, token0, token1, fee, tick_lower, tick_upper):
        token0_address = self.web3_client.token_addresses[token0]
        token1_address = self.web3_client.token_addresses[token1]
        pool_address = factory_contract.functions.createPool(token0_address, token1_address, fee, tick_lower, tick_upper).call()
        return pool_address

    def get_pool_slot0(self, pool_contract):
        slot0 = pool_contract.functions.slot0().call()

        sqrt_price_x96 = slot0[0]
        current_tick = slot0[1]
        observation_index = slot0[2]
        observation_cardinality = slot0[3]
        observation_cardinality_next = slot0[4]
        fee_protocol = slot0[5]
        unlocked = slot0[6]
        price = (sqrt_price_x96 / (2 ** 96)) ** 2

        return {
            'price': price,
            'current_tick': current_tick,
            'observation_index': observation_index,
            'observation_cardinality': observation_cardinality,
            'observation_cardinality_next': observation_cardinality_next,
            'fee_protocol': fee_protocol,
            'unlocked': unlocked,
        }
    
    def get_pool_ticks(self, pool_contract):
        # Fetch slot0 data to get the current tick
        slot0_data = pool_contract.functions.slot0().call()
        current_tick = slot0_data[1]  # Index 1 corresponds to the current tick

        # Fetch tick spacing from the pool contract
        tick_spacing = pool_contract.functions.tickSpacing().call()

        # Calculate tick range boundaries based on tick spacing
        lower_tick = (current_tick // tick_spacing) * tick_spacing
        upper_tick = lower_tick + tick_spacing

        return {
            'current_tick': current_tick,
            'tick_spacing': tick_spacing,
            'lower_tick': lower_tick,
            'upper_tick': upper_tick,
        }
    
    def get_pool_liquidity(self, pool_contract):
        liquidity = pool_contract.functions.liquidity().call()
        return liquidity

    