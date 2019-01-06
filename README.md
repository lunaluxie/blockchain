# blockchain

> A simple blockchain made in python.

This repository is a barebones implementation of a blockchain. It uses the proof of work protocol (sha256 with 4 leading zeros by default), and uses the 'longest is autorative' consensus algorithm.

## Installation
```
git clone https://github.com/kasperfred/blockchain.git
cd blockchain
```

### Dependencies
The blockchain relies on `requests` and `Flask`.

## Usage
This implementation offers a simple webapi for handling nodes.

To start a node, run the following command.

```
python3 app.py
```

This exposes a webapi you can use to communicate with the node. 

### Node Identifier
```
GET: http://0.0.0.0:5000/

3f99f012-3620-494b-934b-261b6958c511
```

### Register Nodes
This will will add other nodes to the network.

```
POST: http://0.0.0.0:5000/nodes/register
BODY (JSON): {"nodes":["192.168.1.124:5000", "192.168.1.125:5000"]}
```
The body should be a JSON object with a `nodes` key containing a list of reachable addresses belonging to other nodes on the network.

### Resolve Conflicts
Runs consensus algorithm (longest chain is autorative)

```
GET: http://0.0.0.0:5000/nodes/resolve
```

### Chain
Get the chain of the node. 
```
GET: http://0.0.0.0:5000/chain
```

### Add Transaction
This will add a transaction to a future block. 
```
POST: http://0.0.0.0:5000/transactions/new
BODY (JSON): {"whatever":"your transaction looks like"}

Transaction will be added to Block {block_index}
```

### Mine
This will mine a block using the proof of work protocol. 
```
GET: http://0.0.0.0:5000/mine
```
