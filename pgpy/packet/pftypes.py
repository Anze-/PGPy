""" types.py
"""
from enum import IntEnum

from cryptography.hazmat.backends import openssl
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import algorithms, modes

from ..errors import PGPOpenSSLCipherNotSupported
from ..util import int_to_bytes


class PFIntEnum(IntEnum):
    def __bytes__(self):
        return int_to_bytes(self.value)


class PubKeyAlgo(PFIntEnum):
    Invalid = 0x00
    RSAEncryptOrSign = 0x01
    RSAEncrypt = 0x02
    RSASign = 0x03
    ElGamal = 0x10
    DSA = 0x11

    def __str__(self):
        if self == PubKeyAlgo.RSAEncryptOrSign:
            return "RSA Encrypt or Sign"

        if self == PubKeyAlgo.ElGamal:
            return "ElGamal Encrypt-Only"

        if self == PubKeyAlgo.DSA:
            return "DSA Digital Signature Algorithm"

        ##TODO: do the rest of these
        raise NotImplementedError(self.name)  # pragma: no cover


class SymmetricKeyAlgo(PFIntEnum):
    Plaintext = 0x00
    IDEA = 0x01
    TripleDES = 0x02
    CAST5 = 0x03
    Blowfish = 0x04
    AES128 = 0x07
    AES192 = 0x08
    AES256 = 0x09
    Twofish256 = 0x0A
    Camellia128 = 0x0B
    Camellia192 = 0x0C
    Camellia256 = 0x0D

    @property
    def block_size(self):
        if self == SymmetricKeyAlgo.Plaintext:
            return 0

        if self in [SymmetricKeyAlgo.IDEA,
                    SymmetricKeyAlgo.CAST5,
                    SymmetricKeyAlgo.TripleDES,
                    SymmetricKeyAlgo.Blowfish]:
            return 64

        if self in [SymmetricKeyAlgo.AES128,
                    SymmetricKeyAlgo.AES192,
                    SymmetricKeyAlgo.AES256,
                    SymmetricKeyAlgo.Camellia128,
                    SymmetricKeyAlgo.Camellia192,
                    SymmetricKeyAlgo.Camellia256,
                    SymmetricKeyAlgo.Twofish256]:
            return 128

        raise NotImplementedError(self.name)  # pragma: no cover

    @property
    def keylen(self):
        if self in [SymmetricKeyAlgo.IDEA,
                    SymmetricKeyAlgo.CAST5,
                    SymmetricKeyAlgo.AES128,
                    SymmetricKeyAlgo.Camellia128,
                    SymmetricKeyAlgo.Blowfish]:
            return 128

        if self in [SymmetricKeyAlgo.AES192,
                    SymmetricKeyAlgo.Camellia192,
                    SymmetricKeyAlgo.TripleDES]:
            return 192

        if self in [SymmetricKeyAlgo.AES256,
                    SymmetricKeyAlgo.Camellia256,
                    SymmetricKeyAlgo.Twofish256]:
            return 256

        raise NotImplementedError(self.name)  # pragma: no cover

    @property
    def backend_alg_name(self):
        return self.name if self.name[-3:] not in ['128', '192', '256'] else self.name[:-3]

    @property
    def decalg(self):
        if hasattr(algorithms, self.backend_alg_name):
            return getattr(algorithms, self.backend_alg_name)

        else:
            raise PGPOpenSSLCipherNotSupported("Algorithm " +
                                               self.backend_alg_name +
                                               " not supported by OpenSSL")

    @property
    def encalg(self):
        # encryption cipher
        pass

    def __str__(self):
        if self in [SymmetricKeyAlgo.CAST5,
                    SymmetricKeyAlgo.Blowfish,
                    SymmetricKeyAlgo.IDEA]:
            return self.name

        if self == SymmetricKeyAlgo.TripleDES:
            return "Triple-DES"

        if self in [SymmetricKeyAlgo.AES128,
                    SymmetricKeyAlgo.AES192,
                    SymmetricKeyAlgo.AES256,
                    SymmetricKeyAlgo.Camellia128,
                    SymmetricKeyAlgo.Camellia192,
                    SymmetricKeyAlgo.Camellia256,
                    SymmetricKeyAlgo.Twofish256]:
            return "{alg} with {keysize}-bit key".format(alg=self.name[:-3], keysize=self.name[-3:])

        raise NotImplementedError(self.name)  # pragma: no cover


class CompressionAlgo(PFIntEnum):
    Uncompressed = 0x00
    ZIP = 0x01
    ZLIB = 0x02
    BZ2 = 0x03

    def __str__(self):
        if self == CompressionAlgo.Uncompressed:
            return "Uncompressed"

        if self == CompressionAlgo.ZIP:
            return "ZIP <RFC1951>"

        if self == CompressionAlgo.ZLIB:
            return "ZLIB <RFC1950>"

        if self == CompressionAlgo.BZ2:
            return "BZip2"

        raise NotImplementedError(self.name)  # pragma: no cover


class HashAlgo(PFIntEnum):
    Invalid = 0x00
    MD5 = 0x01
    SHA1 = 0x02
    RIPEMD160 = 0x03
    SHA256 = 0x08
    SHA384 = 0x09
    SHA512 = 0x0A
    SHA224 = 0x0B

    @property
    def digestlen(self):
        if self == HashAlgo.MD5:
            return 128

        if self in [HashAlgo.SHA1,
                    HashAlgo.RIPEMD160]:
            return 160

        if self in [HashAlgo.SHA256,
                    HashAlgo.SHA384,
                    HashAlgo.SHA512,
                    HashAlgo.SHA224]:
            return int(self.name[-3:])

        raise NotImplementedError(self.name)  # pragma: no cover

    @property
    def hasher(self):
        if hasattr(hashes, self.name):
            return getattr(hashes, self.name)()

        raise NotImplementedError(self.name)  # pragma: no cover

    def __str__(self):
        return self.name


class PacketField(object):
    def __init__(self, packet=None):
        if packet is not None:
            self.parse(packet)

    def parse(self, packet):
        """
        :param packet: raw packet bytes
        """
        raise NotImplementedError()  # pragma: no cover

    def __bytes__(self):
        raise NotImplementedError()  # pragma: no cover
