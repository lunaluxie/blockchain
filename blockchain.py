import hashlib
import json
import requests
from urllib.parse import urlparse
from time import time

import random


class Blockchain():
    def __init__(self):
        """Initializes the blockchain"""

        self.current_transactions = []
        self.chain = []

        self.nodes = set()

        # genesis block
        self.new_block(previous_hash=1, proof=100)

    def register_node(self, address: str):
        """Makes the blockchain aware of the registered node

        Args:
            address (str): Reachable address of the node eg. 'http://192.168.1.100:5000'
        """

        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
    
    @property
    def get_nodes(self):
        return self.nodes

    def valid_chain(self, chain: list) -> bool:
        """Check if chain is valid

        Args:
            chain (list): The chain

        Returns:
            bool: True if valid
        """

        last_block = chain[0]
        for block in chain[1:]:
            # Check that the chain is indeed a chain
            if block['previous_hash'] != self.hash(last_block):
                return False

            # Check that proof of work is correct
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block

        return True

    def resolve_conflicts(self) -> bool:
        """Consensus algorithm that replaces the chain to the longest in the network

        Returns:
            bool: True if chain has been replaced, False if not.
        """

        new_chain = None

        # Only look for chains longer than current chain
        current_length = len(self.chain)

        for node in self.nodes:
            response = requests.get('http://{}/chain'.format(node))
            content = response.json()

            if response.status_code == 200:
                length = content['length']
                chain = content['chain']

                # ensure chain is valid, and check if it's longer than current
                if length > current_length and self.valid_chain(chain):
                    current_length = length
                    new_chain = chain

            # Replace chain if new chain
            if new_chain:
                self.chain = new_chain
                return True

        return False

    def new_block(self, proof: int, previous_hash: str=None) -> dict:
        """Adds a block to the blockchain

        Args:
            proof (int): The proof given by the proof of work algorithm
            previous_hash (str, optional): Defaults to None. Hash of previous Block

        Returns:
            dict: The new block
        """

        block = {
            'index': len(self.chain),
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reset the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, payload: dict) -> int:
        """Creates a new transaction to go into the blockchain

        Args:
            payload (dict): The data of the transaction

        Returns:
            int: The index of the Block that will hold the transaction
        """
        self.current_transactions.append(payload)

        return self.last_block['index'] + 1

    @property
    def last_block(self)->dict:
        """Gets the last block

        Returns:
            dict: The last block
        """
        return self.chain[-1]

    @staticmethod
    def hash(block: dict) -> str:
        """Returns the hash of a block

        Args:
            block (dict): Block

        Returns:
            str: Hash
        """

        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof: int) -> int:
        """Simple proof of work Algorithm:

        Find p* such that hash(pp*) has correct number of leading zeros
        where p is the previous proof, and p* is the new proof

        Args:
            last_proof (int): previous proof (p)

        Returns:
            int: new proof (p*)
        """

        # use random guessing to facilitate concurrent operation
        proof = random.randint(1, 2*32)
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    def valid_proof(self, last_proof: int, proof: int, leading_zeros: int=4) -> bool:
        """Validates a proof (p)

        Args:
            last_proof (int): Previous proof
            proof (int): Proposed proof to be validated
            leading_zeros (int, optional): Defaults to 4. Number of leading zeros required for validation

        Returns:
            bool: Whether proof is valid or not
        """

        guess = '{}{}'.format(last_proof, proof).encode()
        guess_hash = hashlib.sha256(guess).hexdigest()

        return guess_hash[:leading_zeros] == "0"*leading_zeros
