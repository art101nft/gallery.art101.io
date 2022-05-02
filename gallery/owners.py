from ens.auto import ns
from web3.auto import w3


class Owner(object):
    def __init__(self, address):
        try:
            if address.endswith('.eth'):
                self.ens = address
                # self.address = w3.toChecksumAddress(ns.name(address))
            else:
                self.address = w3.toChecksumAddress(address)
                self.ens = ns.name(self.address)
        except Exception as e:
            print(e)
            raise('Invalid address')

        return
