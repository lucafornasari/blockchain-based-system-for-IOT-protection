"""
Client class for IoT devices
It connects to other nodes using a TCP/IP connection
It connects to the Ethereum Blockchain in order to send and read transactions
It also uses a specific smart-contract for probing transactions and another smart-contract for sending requested datas of a particular given service
"""
import json
import random
from web3 import Web3
class Client:

    # Everything needed to connect to the blockchain and to define the contract
    endpoint = "http://127.0.0.1:7545"
    web3 = Web3(Web3.HTTPProvider(endpoint))
    contract_address = web3.toChecksumAddress("0xdFC2A51aC5a60d357ca9417D0C3ba4C66BfB6443")
    contract_abi = json.loads('[{"inputs":[{"internalType":"uint256","name":"tdata","type":"uint256"},{"internalType":"uint256[]","name":"datas","type":"uint256[]"},{"internalType":"string","name":"_trustee","type":"string"}],"name":"calculateTrust","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"position","type":"uint256"},{"internalType":"string","name":"service","type":"string"},{"internalType":"string","name":"ip","type":"string"}],"name":"changeInformations","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"position","type":"uint256"},{"internalType":"string","name":"service","type":"string"},{"internalType":"string","name":"ip","type":"string"}],"name":"connect","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"string","name":"ip","type":"string"}],"name":"getPosition","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string","name":"ip","type":"string"}],"name":"getService","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"_id","type":"uint256"}],"name":"getTrust","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]')
    contract = web3.eth.contract(abi=contract_abi, address=contract_address)

    # String array that contains the nodes' IPs that belong to this node's community
    community_nodes = ["166.198.0.1", "166.198.0.2", "166.198.0.3"]
    # Dictionary that links a node IP's to a Probing Transaction probability to be started
    probabilities = {
        "166.198.0.1" : 15,
        "166.198.0.2" : 50,
        "166.198.0.3" : 43
    }

    # Node informations
    position = 15
    service = "Temperature"
    ip = "166.198.0.0"

    prun_condition = 30

    # ---------------------------------------- FUNCTIONS ----------------------------------------

    """
    Constructor method, called when Client object is created, it connects the node to the contract
    """
    def __init__(self):
        self.web3.eth.defaultAccount = self.web3.eth.accounts[0]
        self.contract.functions.connect(self.position, self.service, self.ip).transact()

    """
    Method that generates a random number, and if it matched with the probability, it starts a probingTransaction
    """
    def probingTransaction(self, trustee):
        if random.randint(0, 100) <= self.probabilities[trustee]:
            myData = self.askInformations(trustee)
            pruned_nodes = self.pruning(trustee)
            datas = self.askInformations(pruned_nodes)
            self.contract.functions.calculateTrust(myData, datas, trustee).transact()
            return True
        else:
            return False

    """
    Method that iterates through the mapped informations in the smart contract and returns the pruned nodes' IPs
    """
    def pruning(self, _trustee):
        prun_result = []
        for i in self.community_nodes:
            if (abs(int(self.contract.functions.getPosition(i).call()) - int(self.contract.functions.getPosition(_trustee).call())) < self.prun_condition) and (self.contract.functions.getService(i).call() == self.contract.functions.getService(_trustee).call()):
                prun_result.append(i)

        return prun_result

    """
    Method that start the communications with the pruned nodes, returns an array that contains the acquired informations
    """
    def askInformations(self, _pruned_nodes):
        # asks informations to the nodes in the list
        return [10, 20, 15]

    """
    Method that start the communications with a particular node
    """
    def askInformation(self, node):
        # asks information to a node
        return 30