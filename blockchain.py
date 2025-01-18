import time
import hashlib

# Block class for creating a new block
class Block:
    def __init__(self, index, transactions, timestamp, previous_hash):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.hash = None
        self.nonce = 0

    def compute_hash(self):
        block_string = f"{self.index}{self.transactions}{self.timestamp}{self.previous_hash}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()


# Blockchain class for managing the entire blockchain
class Blockchain:
    difficulty = 4  # Proof of Work difficulty
    blockchain_name = "OLAS Network"  # OLAS Network blockchain name

    def __init__(self):
        self.unconfirmed_transactions = []
        self.chain = []
        self.balances = {}  # User balances
        self.smart_contracts = {}  # Store deployed smart contracts
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(0, [], time.time(), "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, block):
        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash

    def add_block(self, block, proof):
        previous_hash = self.last_block().hash
        if previous_hash != block.previous_hash:
            return False

        if not self.is_valid_proof(block, proof):
            return False

        block.hash = proof
        self.chain.append(block)
        return True

    def is_valid_proof(self, block, block_hash):
        return (block_hash.startswith('0' * Blockchain.difficulty) and
                block_hash == block.compute_hash())

    def add_new_transaction(self, sender, receiver, amount):
        if sender not in self.balances or self.balances[sender] < amount:
            return "Insufficient balance."
        # Update balances
        self.balances[sender] -= amount
        self.balances[receiver] = self.balances.get(receiver, 0) + amount
        self.unconfirmed_transactions.append({"from": sender, "to": receiver, "amount": amount})
        return "Transaction added!"

    def mine(self, miner_address):
        if not self.unconfirmed_transactions:
            return False

        last_block = self.last_block()
        new_block = Block(index=last_block.index + 1,
                          transactions=self.unconfirmed_transactions,
                          timestamp=time.time(),
                          previous_hash=last_block.hash)

        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)

        # Reward the miner
        reward_transaction = {"from": "Network", "to": miner_address, "amount": 50}
        self.balances[miner_address] = self.balances.get(miner_address, 0) + 50
        self.unconfirmed_transactions = []
        return new_block.index

    # Staking system
    def stake_tokens(self, user, amount, staking_system):
        if user not in self.balances or self.balances[user] < amount:
            return f"Insufficient balance for {user} to stake {amount} tokens."
        
        # Deduct tokens from the user's balance and stake them
        self.balances[user] -= amount
        staking_system.stake(user, amount)
        return f"{user} staked {amount} tokens."

    # Smart contracts
    def deploy_contract(self, contract_name, creator, contract_code):
        contract = SmartContract(creator, contract_code)
        self.smart_contracts[contract_name] = contract
        return f"Contract '{contract_name}' deployed by {creator}"

    def execute_contract(self, contract_name, *args):
        if contract_name in self.smart_contracts:
            contract = self.smart_contracts[contract_name]
            return contract.execute(*args)
        else:
            return f"Contract '{contract_name}' not found."


class StakingSystem:
    def __init__(self):
        self.stakes = {}  # User's staked tokens
        self.rewards = {}  # User rewards
        self.annual_reward_rate = 10  # Reward rate in percentage

    def stake(self, user, amount):
        self.stakes[user] = self.stakes.get(user, 0) + amount

    def calculate_rewards(self, user):
        if user not in self.stakes or self.stakes[user] == 0:
            return f"{user} has no staked tokens."

        # Calculate rewards based on annual percentage rate
        staked_amount = self.stakes[user]
        annual_reward = (staked_amount * self.annual_reward_rate) / 100
        daily_reward = annual_reward / 365
        self.rewards[user] = self.rewards.get(user, 0) + daily_reward
        return f"Daily reward for {user}: {daily_reward:.2f} tokens."

    def withdraw_stake(self, user, blockchain):
        if user not in self.stakes or self.stakes[user] == 0:
            return f"{user} has no staked tokens to withdraw."

        # Return staked tokens and clear rewards
        blockchain.balances[user] += self.stakes[user]
        self.stakes[user] = 0
        self.rewards[user] = 0
        return f"{user} withdrew all staked tokens."


class SmartContract:
    def __init__(self, creator, contract_code):
        self.creator = creator
        self.contract_code = contract_code  # The code is passed as a string
        self.execution_count = 0

    def execute(self, *args):
        try:
            exec_globals = {}
            exec_locals = {"args": args}
            exec(self.contract_code, exec_globals, exec_locals)
            self.execution_count += 1
            return exec_locals.get("result", "No result returned.")
        except Exception as e:
            return f"Contract execution failed: {e}"


# Testing code execution
if __name__ == "__main__":
    # Initialize blockchain and staking system
    blockchain = Blockchain()
    staking_system = StakingSystem()

    # Check Genesis Block
    print(f"Genesis Block of {Blockchain.blockchain_name}:", blockchain.chain[0].__dict__)

    # Add transactions
    blockchain.balances['user1'] = 500
    blockchain.balances['user2'] = 100
    print(blockchain.add_new_transaction('user1', 'user2', 50))
    
    # Mine the block
    print(f"Mining block in {Blockchain.blockchain_name}...")
    block_index = blockchain.mine('miner_address')
    if block_index:
        print(f"Block {block_index} mined successfully!")
    
    # Check user balances after transaction
    print(f"Balance of user1 in {Blockchain.blockchain_name}:", blockchain.balances['user1'])
    print(f"Balance of user2 in {Blockchain.blockchain_name}:", blockchain.balances['user2'])

    # Stake tokens
    print(blockchain.stake_tokens('user1', 100, staking_system))
    print(staking_system.calculate_rewards('user1'))

    # Deploy smart contract
    contract_code = """
result = args[0] + args[1]
"""
    print(blockchain.deploy_contract("AddContract", "user1", contract_code))
    print(blockchain.execute_contract("AddContract", 10, 20))
