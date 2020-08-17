from flask import Flask, jsonify, request
from blockchain import Blockchain
from uuid import uuid4

app = Flask(__name__)
node_id = str(uuid4()).replace('-', '')

blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.latest_block
    last_proof = last_block['proof']
    proof = blockchain.PoW(last_proof)

    blockchain.new_transaction(
        sender= '0',
        recipient= node_id,
        amount= 1,
    )

    prev_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, prev_hash)

    res = {
        'message': 'block added',
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(res), 200

@app.route('/transactions/new', methods=['POST'])
def new_transactions():
    prams = request.get_json()

    if not all(a in prams for a in ['sender', 'recipient', 'amount']):
        return 'Something is WRONG', 400
    
    index = blockchain.new_transaction(prams['sender'], prams['recipient'], prams['amount'])
    res = f'Your transaction was successfuly added to the block number {index}'
    return jsonify(res), 201

@app.route('/chain', methods=['GET'])
def get_chain():
    res = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(res), 200

@app.route('/nodes/register', methods=['POST'])
def register():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return 'Error: Missing Nodes list', 400

    for node in nodes:
        blockchain.register_node(node)

    res = {
        'message': 'Nodes have been registered!',
        'nodes': list(blockchain.nodes),
    }
    return jsonify(res), 201

@app.route('/nodes/detect_chain', methods=['GET'])
def detect_chain():
    replacement = blockchain.detect_main_chain()
    
    if replacement:
        res = {
            'message': 'Our chain was replaced!',
            'new_chain': blockchain.chain
        }
    else: 
        res = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(res), 201


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=4000)