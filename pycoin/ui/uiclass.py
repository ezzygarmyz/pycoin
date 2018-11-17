import hashlib

from pycoin.contrib import segwit_addr
from pycoin.encoding.b58 import b2a_hashed_base58
from pycoin.encoding.hash import hash160
from pycoin.encoding.hexbytes import b2h
from pycoin.intbytes import iterbytes


# PARTS:
# - turn network elements (key, address) into text and back (Parser objects)


class UI(object):
    def __init__(self, puzzle_scripts, generator, bip32_prv_prefix=None, bip32_pub_prefix=None,
                 wif_prefix=None, sec_prefix=None, address_prefix=None, pay_to_script_prefix=None, bech32_hrp=None):
        self._script_info = puzzle_scripts
        self._bip32_prv_prefix = bip32_prv_prefix
        self._bip32_pub_prefix = bip32_pub_prefix
        self._wif_prefix = wif_prefix
        self._sec_prefix = sec_prefix
        self._address_prefix = address_prefix
        self._pay_to_script_prefix = pay_to_script_prefix
        self._bech32_hrp = bech32_hrp

    def bip32_as_string(self, blob, as_private):
        prefix = self._bip32_prv_prefix if as_private else self._bip32_pub_prefix
        return b2a_hashed_base58(prefix + blob)

    def wif_for_blob(self, blob):
        return b2a_hashed_base58(self._wif_prefix + blob)

    def sec_text_for_blob(self, blob):
        return self._sec_prefix + b2h(blob)

    # address_for_script and script_for_address stuff

    def address_for_script(self, script):
        script_info = self._script_info.info_for_script(script)
        return self.address_for_script_info(script_info)

    def address_for_script_info(self, script_info):
        type = script_info.get("type")

        if type == "p2pkh":
            return self.address_for_p2pkh(script_info["hash160"])

        if type == "p2pkh_wit":
            return self.address_for_p2pkh_wit(script_info["hash160"])

        if type == "p2sh_wit":
            return self.address_for_p2sh_wit(script_info["hash256"])

        if type == "p2pk":
            h160 = hash160(script_info["sec"])
            # BRAIN DAMAGE: this isn't really a p2pkh
            return self.address_for_p2pkh(h160)

        if type == "p2sh":
            return self.address_for_p2sh(script_info["hash160"])

        if type == "nulldata":
            return "(nulldata %s)" % b2h(script_info["data"])

        return "???"

    def address_for_p2pkh(self, h160):
        if self._address_prefix:
            return b2a_hashed_base58(self._address_prefix + h160)
        return "???"

    def address_for_p2sh(self, h160):
        if self._pay_to_script_prefix:
            return b2a_hashed_base58(self._pay_to_script_prefix + h160)
        return "???"

    def address_for_p2pkh_wit(self, h160):
        if self._bech32_hrp and len(h160) == 20:
            return segwit_addr.encode(self._bech32_hrp, 0, iterbytes(h160))
        return "???"

    def address_for_p2sh_wit(self, hash256):
        if self._bech32_hrp and len(hash256) == 32:
            return segwit_addr.encode(self._bech32_hrp, 0, iterbytes(hash256))
        return "???"

    def script_for_address(self, address):
        return self.parse(address, types=["address"])

    # p2s and p2s_wit helpers

    def address_for_p2s(self, script):
        return self.address_for_p2sh(hash160(script))

    def address_for_p2s_wit(self, script):
        return self.address_for_p2sh_wit(hashlib.sha256(script).digest())
