#!/usr/bin/env python3

from web3.auto import w3
from hexbytes import HexBytes

from gallery.constants import mint_topic, opensea_sale_topic, looksrare_sale_topic
from gallery.collections import all_collections, Collection
from gallery.models import Events


if __name__ == '__main__':
    last_block = Events.select().order_by(Events.date.desc()).first()
    if last_block:
        start_block = last_block.block_number
    else:
        start_block = 13105421 # hardcoded, first contract launch

    # collections = [Collection(k) for k in all_collections]
    contracts = [v['contract_address'].lower() for k,v in all_collections.items()]
    print(contracts)
    current_block = w3.eth.get_block_number()
    chunk_size = 1
    print(f'[+] Start block {start_block} to {start_block + chunk_size}')
    # for collection in collections:
        # eventsFilter = collection.contract.events.Transfer().createFilter(fromBlock=start_block, toBlock=start_block+1)
        # logs = w3.eth.get_filter_logs(eventsFilter.filter_id)
        # print(logs)
        # print(f'[+] Getting events from contract {collection.contract_address} starting in block {start_block}')
        # for log in logs:
        #     print(log)
    filter = w3.eth.filter({
        'fromBlock': start_block,
        'toBlock': start_block + chunk_size,
        'topics': [[
            mint_topic,
            opensea_sale_topic,
            looksrare_sale_topic
        ]]
    })
    logs = w3.eth.get_filter_logs(filter.filter_id)
    # print(logs)
    for log in logs:
        # print(log['address'].lower())
        # print(contracts)
        if log['address'].lower():
            if HexBytes(mint_topic) in log['topics']:
                print(f'Found mint in {log["transactionHash"].hex()} block {log["blockNumber"]} contract {log["address"]}')
                # print(log)
            elif HexBytes(opensea_sale_topic) in log['topics']:
                print(f'Found Opensea sale in {log["transactionHash"].hex()} block {log["blockNumber"]} contract {log["address"]}')
                # print(log)
            elif HexBytes(looksrare_sale_topic) in log['topics']:
                print(f'Found LooksRare sale in {log["transactionHash"].hex()} block {log["blockNumber"]} contract {log["address"]}')
                # print(log)

    # print(f'Saving ')
    # for i in range(start_block, start_block + 1):
    #     print(w3.eth.get_block(i))

    # NFS
    # filter = w3.eth.filter({'fromBlock': 13105807, 'toBlock': 13105807, 'address': w3.toChecksumAddress('0xdc8bed466ee117ebff8ee84896d6acd42170d4bb')})
    # w3.eth.get_filter_logs(filter.filter_id)
    # 0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef - minted
    # for l in logs:
    #   if l['topics'][0].hex() == '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef':
    #     print(f'minted token in tx hash {l["transactionHash"].hex()}')
    # filter2 = w3.eth.filter({'fromBlock': 13241601, 'toBlock': 13241601, 'address': w3.toChecksumAddress('0xdc8bed466ee117ebff8ee84896d6acd42170d4bb')})
    # logs2 = w3.eth.get_filter_logs(filter2.filter_id)
    # nfs_sale_topic = '0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925'

    # MND
