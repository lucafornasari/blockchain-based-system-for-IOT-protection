"""
Client class for IoT devices
It connects to other nodes using a TCP/IP connection
It connects to the Ethereum Blockchain in order to send and read transactions
It also uses a specific smart-contract for probing transactions and another smart-contract for sending requested datas of a particular given service
"""
import json
import random
from web3 import Web3
from NodeServer import NodeServer
import socket
import threading
import sys
from random import seed
from random import random

class Client(threading.Thread):

    # Everything needed to connect to the blockchain and to define the contract
    endpoint = "http://127.0.0.1:7545"
    web3 = Web3(Web3.HTTPProvider(endpoint))
    contract_address = web3.toChecksumAddress("0x622abCc594a578ced6924ACA6397170B58AaA025")
    contract_abi = json.loads('[{"inputs":[{"internalType":"uint256","name":"tdata","type":"uint256"},{"internalType":"uint256[]","name":"datas","type":"uint256[]"},{"internalType":"string","name":"_trustee","type":"string"}],"name":"calculateTrust","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"position","type":"uint256"},{"internalType":"string","name":"service","type":"string"},{"internalType":"string","name":"ip","type":"string"}],"name":"changeInformations","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"position","type":"uint256"},{"internalType":"string","name":"service","type":"string"},{"internalType":"string","name":"ip","type":"string"}],"name":"connect","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"getNodes","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string","name":"ip","type":"string"}],"name":"getPosition","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string","name":"te","type":"string"}],"name":"getRep","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string","name":"ip","type":"string"}],"name":"getService","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"_id","type":"uint256"}],"name":"getTrust","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]')
    contract = web3.eth.contract(abi=contract_abi, address=contract_address)

    # String array that contains the nodes' IPs that belong to this node's community
    community_nodes = ["1001", "1002", "1003", "1004", "1005", "1006"]

    # Node informations
    position = 15
    service = "Temperature"
    ip = "1002"

    prun_condition = 30
    pact = 0.7

    # ---------------------------------------- FUNCTIONS ----------------------------------------

    """
    Constructor method, called when Client object is created, it connects the node to the contract
    """
    def __init__(self, eth, port, temp):
        super().__init__()
        self.web3.eth.defaultAccount = self.web3.eth.accounts[eth]
        self.ip = port
        self.contract.functions.connect(self.position, self.service, self.ip).transact()
        self.server = NodeServer(int(port), str(temp))

        self.community_nodes.remove(port)

    """
    Method that generates a random number, and if it matched with the probability, it starts a probingTransaction
    """
    def probingTransaction(self, trustee):
        if random() <= self.pact:
            myData = self.askInformation(int(trustee))
            pruned_nodes = self.pruning(trustee)
            datas = self.askInformations(pruned_nodes)
            self.contract.functions.calculateTrust(myData, datas, trustee).transact()
            return True
        #else:
            #return False

    """
    Method that iterates through the mapped informations in the smart contract and returns the pruned nodes' IPs
    """
    def pruning(self, _trustee):
        prun_result = []
        for i in self.community_nodes:
            if(i != _trustee):
                if (abs(int(self.contract.functions.getPosition(i).call()) - int(self.contract.functions.getPosition(_trustee).call())) < self.prun_condition) and (self.contract.functions.getService(i).call() == self.contract.functions.getService(_trustee).call()):
                    prun_result.append(i)

        return prun_result

    """
    Method that start the communications with the pruned nodes, returns an array that contains the acquired informations
    """
    def askInformations(self, _pruned_nodes):
        datas = []
        for p in _pruned_nodes:
            datas.append( self.askInformation(int(p)))

        return datas

    """
    Method that start the communications with a particular node
    """
    def askInformation(self, node):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('localhost', node))

        msg = s.recv(1024)
        msgint = int(msg.decode("utf-8"))

        return msgint


    def run(self):

        self.server.start()
        input()
        if self.ip == "1001" :
            self.probingTransaction("1002")
        elif self.ip == "1002" :
            self.probingTransaction("1006")
        elif self.ip == "1004" :
            self.probingTransaction("1005")
        elif self.ip == "1003" :
            self.probingTransaction("1005")

        input()

        if self.ip == "1001" :
            self.probingTransaction("1003")

        input()

        #print(threading.active_count())


args = sys.argv
c = Client(int(args[1]), args[2], args[3])
c.run()