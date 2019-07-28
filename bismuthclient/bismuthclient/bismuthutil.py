"""
Generic helpers  Bismuth
"""

import re
import hashlib
import base64
from decimal import Decimal

__version__ = '0.0.4'


def checksum(string):
    """ Base 64 checksum of MD5. Used by bisurl"""
    m = hashlib.md5()
    m.update(string.encode("utf-8"))
    return base64.b85encode(m.digest()).decode("utf-8")


RE_RSA_ADDRESS = re.compile(r"^[abcdef0123456789]{56}$")
# TODO: improve that ECDSA one
RE_ECDSA_ADDRESS = re.compile(r"^Bis")


class BismuthUtil():
    """Static helper utils"""

    @staticmethod
    def valid_address(address: str):
        """Says if that address looks ok"""
        # Dup from polysign - https://github.com/bismuthfoundation/Bismuth/blob/postfork/polysign/signerfactory.py
        # TODO: polysign as module for future versions.
        if RE_RSA_ADDRESS.match(address):
            # RSA, 56 hex
            return True
        elif RE_ECDSA_ADDRESS.match(address):
            if 50 < len(address) < 60:
                # ED25519, around 54
                return True
            if 30 < len(address) < 50:
                # ecdsa, around 37
                return True
        return False

    @staticmethod
    def fee_for_tx(openfield: str = '', operation: str = '', block: int = 0) -> Decimal:
        # block var will be removed after HF
        fee = Decimal("0.01") + (Decimal(len(openfield)) / Decimal("100000"))  # 0.01 dust
        if operation == "token:issue":
            fee = Decimal(fee) + Decimal("10")
        if openfield.startswith("alias="):
            fee = Decimal(fee) + Decimal("1")
        # if operation == "alias:register": #add in the future, careful about forking
        #    fee = Decimal(fee) + Decimal("1")
        return fee.quantize(Decimal('0.00000000'))

    @staticmethod
    def height_to_supply(height):
        """Gives total supply at a given block height"""
        R0 = 11680000.4
        delta = 2e-6
        pos = 0.8
        pow = 12.6
        N = height - 8e5
        dev_rew = 1.1
        R = dev_rew * R0 + N * (pos + dev_rew * (pow - N / 2 * delta))
        return R

    @staticmethod
    def create_bis_url(recipient, amount, operation, openfield):
        """
        Constructs a bis url from tx elements
        """

        # Only command supported so far.
        command = "pay"
        openfield_b85_encode = base64.b85encode(openfield.encode("utf-8")).decode("utf-8")
        operation_b85_encode = base64.b85encode(operation.encode("utf-8")).decode("utf-8")
        url_partial = "bis://{}/{}/{}/{}/{}/".format(command,recipient,amount,operation_b85_encode,openfield_b85_encode)
        url_constructed = url_partial + checksum(url_partial)
        return url_constructed

    @staticmethod
    def read_url(url):
        """
        Takes a bis url, checks its checksum and gives the components
        """
        url_split = url.split("/")
        reconstruct = "bis://{}/{}/{}/{}/{}/".format(url_split[2],url_split[3],url_split[4],url_split[5],url_split[6],url_split[7])
        operation_b85_decode = base64.b85decode(url_split[5]).decode("utf-8")
        openfield_b85_decode = base64.b85decode(url_split[6]).decode("utf-8")

        if checksum(reconstruct) == url_split[7]:
            url_deconstructed = {"recipient": url_split[3], "amount": url_split[4], "operation": operation_b85_decode,
                                 "openfield": openfield_b85_decode}
            return url_deconstructed
        else:
            return {'Error': 'Checksum failed'}
