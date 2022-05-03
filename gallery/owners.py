from ens.auto import ns
from web3.auto import w3

from gallery.library.cache import cache


class Owner(object):
    def __init__(self, address):
        try:
            key_name = f'wallet-{address}'
            _d = cache.get_data(key_name)
            if address.endswith('.eth'):
                self.ens = address
                if _d:
                    self.address = _d.decode()
                else:
                    _d = w3.toChecksumAddress(ns.address(self.ens))
                    cache.store_data(key_name, 604800, _d)
                    self.address = _d
            else:
                self.address = w3.toChecksumAddress(address)
                if _d:
                    self.ens = _d.decode()
                else:
                    _d = ns.name(self.address)
                    cache.store_data(key_name, 604800, _d)
                    self.ens = _d
        except Exception as e:
            print(e)
            raise('Invalid address')

        return
