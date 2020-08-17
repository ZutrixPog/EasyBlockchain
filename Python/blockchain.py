from time import time
import hashlib
import requests
import json
from urllib.parse import urlparse

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.new_block(100, 1)
        self.nodes = set()

    def new_block(self, proof, prev_hash):
        #Creates a new block and add it on top of the chain
        new_block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': prev_hash
        }
        #reset the list of current transactions
        self.current_transactions = []

        self.chain.append(new_block)
        return new_block

    def new_transaction(self, sender, recipient, amount):
        #Adds a new transaction to the current block
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })

        return self.latest_block['index'] + 1

    def PoW(self, last_PoW):
        #mines the Proof Of Work
        proof = 0
        while self.validate_PoW(last_PoW, proof) is False:
            proof += 1

        return proof

    def register_node(self, address):
        #register new node on the disturbuted network
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def validate_chain(self, chain):
        #validates the chain of blocks
        last_block = chain[0]
        i = 1

        for i in range(len(chain)):
            block = chain[i]
            #check hash of the block
            if block['previous_hash'] != self.hash(last_block):
                return False

            #check proof of work
            if not self.validate_PoW(last_block['proof'], block['proof']):
                return False
            
            last_block = block
        return True

    def detect_main_chain(self):
        #The Consensus algorithm

        neighbors = self.nodes
        new_chain = None
        max_length = len(self.chain)

        #verify all the chains
        for node in neighbors:
            res = requests.get(f'http://{node}/chain')
            
            if res.status_code == 200:
                length = res.json()['length']
                chain  = res.json()['chain']

                if length > max_length and self.validate_chain(chain):
                    max_length = length
                    new_chain  = chain

        if new_chain:
            self.chain = new_chain
            return True

        return False

    @staticmethod
    def validate_PoW(last_PoW, proof):
        #determines wether pow is valid or not(considering our rule)
        guess = f'{last_PoW}{proof}'.encode()
        hashed = hashlib.sha256(guess).hexdigest()
        return hashed[:5] == '00000'

    @staticmethod
    def hash(block):
        #Use sha256 to hash the block Created
        #convert block dict to json string
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def latest_block(self):
        #returns latest block
            return self.chain[-1]
