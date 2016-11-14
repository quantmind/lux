# Adapted from
###########################################################################
# pbkdf2 - PKCS#5 v2.0 Password-Based Key Derivation                      #
#                                                                         #
# Copyright (C) 2007-2011 Dwayne C. Litzenberger <dlitz@dlitz.net>        #
#                                                                         #
# Permission is hereby granted, free of charge, to any person obtaining   #
# a copy of this software and associated documentation files (the         #
# "Software"), to deal in the Software without restriction, including     #
# without limitation the rights to use, copy, modify, merge, publish,     #
# distribute, sublicense, and/or sell copies of the Software, and to      #
# permit persons to whom the Software is furnished to do so, subject to   #
# the following conditions:                                               #
#                                                                         #
# The above copyright notice and this permission notice shall be          #
# included in all copies or substantial portions of the Software.         #
#                                                                         #
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,         #
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF      #
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND                   #
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE  #
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION  #
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION   #
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.         #
#                                                                         #
# Country of origin: Canada                                               #
#                                                                         #
###########################################################################

import hmac
from struct import pack
from random import randint
from hashlib import sha1
from hashlib import sha256
from hashlib import sha512
from base64 import b64encode as _b64encode
from binascii import b2a_hex as _b2a_hex


__all__ = ['PBKDF2', 'crypt', 'encrypt', 'verify']


_0xffffffffL = 0xffffffff

# A dict of supported hash functions, to get from a string
# (as stored as part of `crypt`'s output) to a digestmodule
algorithms = {
    'sha1': sha1,
    'sha256': sha256,
    'sha512': sha512,
}


def isunicode(s):
    return isinstance(s, str)


def isbytes(s):
    return isinstance(s, bytes)


def isinteger(n):
    return isinstance(n, int)


def callable(obj):
    return hasattr(obj, '__call__')


def binxor(a, b):
    return bytes([x ^ y for (x, y) in zip(a, b)])


def b64encode(data, chars="+/"):
    if isunicode(chars):
        return _b64encode(data, chars.encode('utf-8')).decode('utf-8')
    else:
        return _b64encode(data, chars)  # pragma nocover


def b2a_hex(s):
    return _b2a_hex(s).decode('us-ascii')


class PBKDF2:

    """PBKDF2.py : PKCS#5 v2.0 Password-Based Key Derivation

    This implementation takes a passphrase and a salt (and optionally an
    iteration count, a digest module, and a MAC module and a secret_kay
    for additional salting) and provides a file-like object from which
    an arbitrarily-sized key can be read.

    If the passphrase and/or salt are unicode objects, they are encoded as
    UTF-8 before they are processed.

    The idea behind PBKDF2 is to derive a cryptographic key from a
    passphrase and a salt.

    PBKDF2 may also be used as a strong salted password hash.  The
    'crypt' function is provided for that purpose.

    Remember: Keys generated using PBKDF2 are only as strong as the
    passphrases they are derived from.
    """

    def __init__(self, passphrase, salt, iterations=24000,
                 digestmodule=sha256, macmodule=hmac, secret_key=None):
        self.__macmodule = macmodule
        self.__digestmodule = digestmodule
        if isinstance(secret_key, str):
            secret_key = secret_key.encode('latin-1')
        self.__secret_key = secret_key
        self._setup(passphrase, salt, iterations, self._pseudorandom)

    def _pseudorandom(self, key, msg):
        """Pseudorandom function.  e.g. HMAC-SHA256"""
        # We need to generate a derived key from our base key. We can do this
        # by passing the secret key and our base key through a pseudo-random
        # function and SHA1 works nicely.
        if self.__secret_key:
            key = sha1(self.__secret_key + key).digest()
        return self.__macmodule.new(key=key, msg=msg,
                                    digestmod=self.__digestmodule).digest()

    def read(self, bytes):
        """Read the specified number of key bytes."""
        if self.closed:
            raise ValueError("file-like object is closed")

        size = len(self.__buf)
        blocks = [self.__buf]
        i = self.__blockNum
        while size < bytes:
            i += 1
            if i > _0xffffffffL or i < 1:
                # We could return "" here, but
                raise OverflowError("derived key too long")  # pragma nocover
            block = self.__f(i)
            blocks.append(block)
            size += len(block)
        buf = b"".join(blocks)
        retval = buf[:bytes]
        self.__buf = buf[bytes:]
        self.__blockNum = i
        return retval

    def __f(self, i):
        # i must fit within 32 bits
        assert 1 <= i <= _0xffffffffL
        U = self.__prf(self.__passphrase, self.__salt + pack("!L", i))
        result = U
        for j in range(2, 1+self.__iterations):
            U = self.__prf(self.__passphrase, U)
            result = binxor(result, U)
        return result

    def hexread(self, octets):
        """Read the specified number of octets. Return them as hexadecimal.

        Note that len(obj.hexread(n)) == 2*n.
        """
        return b2a_hex(self.read(octets))

    def _setup(self, passphrase, salt, iterations, prf):
        # Sanity checks:

        # passphrase and salt must be str or unicode (in the latter
        # case, we convert to UTF-8)
        if isunicode(passphrase):
            passphrase = passphrase.encode("UTF-8")
        elif not isbytes(passphrase):
            raise TypeError("passphrase must be str or unicode")
        if isunicode(salt):
            salt = salt.encode("UTF-8")
        elif not isbytes(salt):
            raise TypeError("salt must be str or unicode")

        # iterations must be an integer >= 1
        if not isinteger(iterations):
            raise TypeError("iterations must be an integer")
        if iterations < 1:
            raise ValueError("iterations must be at least 1")

        # prf must be callable
        if not callable(prf):
            raise TypeError("prf must be callable")

        self.__passphrase = passphrase
        self.__salt = salt
        self.__iterations = iterations
        self.__prf = prf
        self.__blockNum = 0
        self.__buf = b""
        self.closed = False

    def close(self):
        """Close the stream."""
        if not self.closed:
            del self.__passphrase
            del self.__salt
            del self.__iterations
            del self.__prf
            del self.__blockNum
            del self.__buf
            self.closed = True


def crypt(word, salt=None, iterations=24000, digestmodule=sha256,
          secret_key=None):
    """PBKDF2-based unix crypt(3) replacement.

    The number of iterations specified in the salt overrides the 'iterations'
    parameter.

    The effective hash length is dependant on the used `digestmodule`.
    """

    # Generate a (pseudo-)random salt if the user hasn't provided one.
    if salt is None:
        salt = _makesalt()

    # salt must be a string or the us-ascii subset of unicode
    if isunicode(salt):
        salt = salt.encode('us-ascii').decode('us-ascii')
    elif isbytes(salt):
        salt = salt.decode('us-ascii')
    else:
        raise TypeError("salt must be a string")

    # word must be a string or unicode
    # (in the latter case, we convert to UTF-8)
    if isunicode(word):
        word = word.encode("UTF-8")
    elif not isbytes(word):
        raise TypeError("word must be a string or unicode")

    # Try to extract the real salt and iteration count from the salt
    if salt.startswith("$p5k2$"):
        (digest_name, iterations, salt) = salt.split("$")[2:5]

        converted = int(iterations, 16)
        if iterations != "%x" % converted:  # lowercase hex, minimum digits
            raise ValueError("Invalid salt")  # pragma nocover
        iterations = converted
        if not (iterations >= 1):
            raise ValueError("Invalid salt")

        if digest_name in algorithms:
            digestmodule = algorithms[digest_name]
        else:
            raise ValueError("Digest algorithm=%s not supported!"
                             % digest_name)

    # Instantiate a `digestmodule`, so we can inspect
    # it's `name` and `digest_size`
    digest = digestmodule()

    # Make sure the salt matches the allowed character set
    allow = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789./"
    for ch in salt:
        if ch not in allow:
            raise ValueError("Illegal character %r in salt" % (ch,))

    salt = "$p5k2$%s$%x$%s" % (digest.name.lower(),  iterations, salt)

    rawhash = PBKDF2(word, salt, iterations, digestmodule,
                     secret_key=secret_key).read(digest.digest_size)
    return salt + "$" + b64encode(rawhash, "./")


# Add crypt as a static method of the PBKDF2 class
# This makes it easier to do "from PBKDF2 import PBKDF2" and still use
# crypt.
PBKDF2.crypt = staticmethod(crypt)


def _makesalt(altchars="./"):
    """Return a 64-bit pseudorandom salt for crypt().

    This function is not suitable for generating cryptographic secrets.
    """
    binarysalt = b"".join([pack("@H", randint(0, 0xffff)) for i in range(3)])
    return b64encode(binarysalt, altchars)


def encrypt(word, secret_key=None, salt_length=None, *args, **kwargs):
    """This function exist for compatibility with lux auth mechanism.
    Use `crypt` directly for PBKDF2 cryptic algorithm.
    """
    return crypt(word, secret_key=secret_key, *args, **kwargs).encode('utf-8')


def verify(hashpass, raw, key, salt_length=None, *args, **kwargs):
    """Check if provided password match hash stored in db.
    """
    if isinstance(hashpass, bytes):
        hashpass = hashpass.decode('utf-8')
    if isinstance(raw, bytes):
        raw = raw.decode('utf-8')
    return hashpass == crypt(raw, hashpass, secret_key=key)
