from binascii import unhexlify

from lux.utils import test

from lux.utils.crypt.pbkdf2 import (_0xffffffffL, algorithms,
                                    isbytes, isinteger, callable, binxor,
                                    b64encode, verify, b2a_hex, PBKDF2,
                                    crypt, _makesalt, encrypt,
                                    sha1, sha256, sha512)


class TestPBKDF2(test.TestCase):
    config_params = dict(CRYPT_ALGORITHM='lux.utils.crypt.pbkdf2',
                         EXTENSIONS=['lux.extensions.rest'])

    def u(self, value):
        return value.encode('utf-8')

    def test__0xffffffffL(self):
        self.assertEqual(_0xffffffffL, 0xffffffff)

    def test_algorithms(self):
        self.assertEqual(len(algorithms), 3)
        self.assertEqual(set(algorithms), set(('sha1', 'sha256', 'sha512')))

    def test_isbytes(self):
        self.assertTrue(isbytes(bytes(self.u('test'))), True)

    def test_isinteger(self):
        self.assertTrue(isinteger(1), True)

    def test_callable(self):
        self.assertTrue(callable(print), True)

    def test_binxor(self):
        self.assertEqual(binxor([1], [2]), self.u('\x03'))

    def test_b64encode(self):
        self.assertEqual(b64encode(self.u('test')), 'dGVzdA==')
        self.assertEqual(b64encode(self.u('test'), './'), 'dGVzdA==')
        self.assertEqual(b64encode(bytes(1)), 'AA==')

    def test_b2a_hex(self):
        self.assertEqual(b2a_hex(self.u('test')), '74657374')

    def test_pbkdf2(self):
        """Module self-test"""
        from binascii import a2b_hex as _a2b_hex

        def a2b_hex(s):
            return _a2b_hex(s.encode('latin-1'))

        #
        # Test vectors from RFC 3962
        #

        # Test 1
        result = PBKDF2("password", "ATHENA.MIT.EDUraeburn", 1, sha1).read(16)
        expected = a2b_hex("cdedb5281bb2f801565a1122b2563515")
        self.assertEqual(expected, result)

        # Test 2
        result = PBKDF2("password", "ATHENA.MIT.EDUraeburn",
                        1200, sha1).hexread(32)
        expected = ("5c08eb61fdf71e4e4ec3cf6ba1f5512b"
                    "a7e52ddbc5e5142f708a31e2e62b1e13")
        self.assertEqual(expected, result)

        # Test 3
        result = PBKDF2("X"*64, "pass phrase equals block size",
                        1200, sha1).hexread(32)
        expected = ("139c30c0966bc32ba55fdbf212530ac9"
                    "c5ec59f1a452f5cc9ad940fea0598ed1")
        self.assertEqual(expected, result)

        # Test 4
        result = PBKDF2("X"*65, "pass phrase exceeds block size",
                        1200, sha1).hexread(32)
        expected = ("9ccad6d468770cd51b10e6a68721be61"
                    "1a8b4d282601db3b36be9246915ec82a")
        self.assertEqual(expected, result)

        #
        # Test vectors for PBKDF2 HMAC-SHA1, from RFC 6070
        #

        result = PBKDF2('password', 'salt', 1, sha1).hexread(20)
        expected = '0c60c80f961f0e71f3a9b524af6012062fe037a6'
        self.assertEqual(expected, result)

        #
        # Test vectors for PBKDF2 HMAC-SHA256
        #

        result = PBKDF2('password', 'salt', 1, sha256).hexread(32)
        e = '120fb6cffcf8b32c43e7225256c4f837a86548c92ccc35480805987cb70be17b'
        self.assertEqual(e, result)

        result = PBKDF2('password', 'salt', 2, sha256).hexread(32)
        e = 'ae4d0c95af6b46d32d0adff928f06dd02a303f8ef3c251dfd6e2d85a95474c43'
        self.assertEqual(e, result)

        result = PBKDF2('password', 'salt', 4096, sha256).hexread(32)
        e = 'c5e478d59288c841aa530db6845c4c8d962893a001ce4e11a4963873aa98134a'
        self.assertEqual(e, result)

        result = PBKDF2('passwordPASSWORDpassword',
                        'saltSALTsaltSALTsaltSALTsaltSALTsalt',
                        4096, sha256).hexread(40)
        e = '348c89dbcbd32b2f32d814b8116e84cf2b17347ebc1800181c4e2a1fb8dd5' + \
            '3e1c635518c7dac47e9'
        self.assertEqual(e, result)

        result = PBKDF2('pass\0word', 'sa\0lt', 4096, sha256).hexread(16)
        expected = '89b69d0516f829893c696226650a8687'
        self.assertEqual(expected, result)

        salt = unhexlify(
            '9290F727ED06C38BA4549EF7DE25CF5642659211B7FC076F2D28FEFD71'
            '784BB8D8F6FB244A8CC5C06240631B97008565A120764C0EE9C2CB0073'
            '994D79080136')
        result = PBKDF2('hello', salt, 10000, sha512).hexread(64)
        expected = (
            '887CFF169EA8335235D8004242AA7D6187A41E3187DF0CE14E256D85ED'
            '97A97357AAA8FF0A3871AB9EEFF458392F462F495487387F685B7472FC'
            '6C29E293F0A0').lower()
        self.assertEqual(expected, result)

        #
        # Other test vectors
        #

        # Chunked read
        f = PBKDF2("kickstart", "workbench", 256, sha1)
        result = f.read(17)
        result += f.read(17)
        result += f.read(1)
        result += f.read(2)
        result += f.read(3)
        expected = PBKDF2("kickstart", "workbench", 256, sha1).read(40)
        self.assertEqual(expected, result)

    def test_crypt(self):
        result = crypt("secret", iterations=4096, digestmodule=sha512)
        self.assertEqual(result[:6], "$p5k2$")

        result = crypt("secret", "XXXXXXXX", 4096, sha512)
        expected = '$p5k2$sha512$1000$XXXXXXXX$'
        self.assertEqual(expected, result[:27])

        # 400 iterations
        result = crypt("secret", "XXXXXXXX", 400, sha512)
        expected = '$p5k2$sha512$190$XXXXXXXX$'
        self.assertEqual(expected, result[:26])

        # 400 iterations (keyword argument)
        result = crypt("spam", "FRsH3HJB", iterations=400, digestmodule=sha512)
        expected = '$p5k2$sha512$190$FRsH3HJB$'
        self.assertEqual(expected, result[:26])

        # 1000 iterations
        result = crypt("spam", "H0NX9mT/", iterations=1000,
                       digestmodule=sha512)
        expected = '$p5k2$sha512$3e8$H0NX9mT/$'
        self.assertEqual(expected, result[:26])

        # 1000 iterations (iterations count taken from salt parameter)
        expected = '$p5k2$sha1$3e8$H0NX9mT/$ih6FhDyRXAaEN4UXk50pNsZP/nU='
        result = crypt("spam", expected, digestmodule=sha1)
        self.assertEqual(expected, result)

        # Feed the result back in; both hashes should match, as the algo and
        # iteration count are taken from the expected hash
        expected = crypt("spam")
        result = crypt("spam", expected)
        self.assertEqual(expected, result)

        # ...and this one shouldn't match
        expected = crypt("password")
        result = crypt("passwd", expected)
        self.assertNotEqual(expected, result)

        #
        # SHA256
        #
        result = crypt("spam", "XXXXXXXX", iterations=1000,
                       digestmodule=sha256)
        expected = '$p5k2$sha256$3e8$XXXXXXXX$'
        self.assertEqual(expected, result[:26])

        # Feed the result back in; both hashes should match, as the algo and
        # iteration count are taken from the expected hash
        expected = crypt("spam", digestmodule=sha256)
        result = crypt("spam", expected)
        self.assertEqual(expected, result)

        # ...and this one shouldn't match
        expected = crypt("password", digestmodule=sha256)
        result = crypt("passwd", expected)
        self.assertNotEqual(expected, result)

        #
        # SHA512
        #
        result = crypt("spam", "XXXXXXXX", iterations=1000,
                       digestmodule=sha512)
        expected = '$p5k2$sha512$3e8$XXXXXXXX$'
        self.assertEqual(expected, result[:26])

        # Feed the result back in; both hashes should match, as the algo and
        # iteration count are taken from the expected hash
        expected = crypt("spam", digestmodule=sha512)
        result = crypt("spam", expected)
        self.assertEqual(expected, result)

        # ...and this one shouldn't match
        expected = crypt("password", digestmodule=sha512)
        result = crypt("passwd", expected)
        self.assertNotEqual(expected, result)

        #
        # crypt() test vectors
        #

        # crypt 1
        result = crypt("cloadm", "exec", iterations=400, digestmodule=sha1)
        expected = '$p5k2$sha1$190$exec$jkxkBaZJp.nvBg4WV7BW96972fE='
        self.assertEqual(expected, result)

        # crypt 2
        result = crypt("gnu", '$p5k2$sha1$c$u9HvcT4d$.....')
        expected = '$p5k2$sha1$c$u9HvcT4d$iDgHukD37rW7UgWCS24lnNRjO3c='
        self.assertEqual(expected, result)

        # crypt 3
        result = crypt("dcl", "tUsch7fU", iterations=13, digestmodule=sha1)
        expected = "$p5k2$sha1$d$tUsch7fU$.8H47sUSBmz0PDHbKfXHkjDDboo="
        self.assertEqual(expected, result)

        # crypt 3, SHA256
        result = crypt("dcl", "tUsch7fU", iterations=13, digestmodule=sha256)
        expected = "$p5k2$sha256$d$tUsch7fU$A1I2wQdnQb28U7UD4aaxwuFL5IFj" + \
                   ".AWLngbwVLHOkVo="
        self.assertEqual(expected, result)

        # crypt3, SHA512
        result = crypt("dcl", "tUsch7fU", iterations=13, digestmodule=sha512)
        e = "$p5k2$sha512$d$tUsch7fU$GM78GODhPDWxODRnH4/L9lGnTqMgms" + \
            "YJEROltbxUVquPm1P9qmbRkQM1KuFOf6QEBXX20eMGwYRmDrFLHDyn6Q=="
        self.assertEqual(e, result)

        # crypt 4 (unicode)
        t_msg = b'\xce\x99\xcf\x89\xce\xb1\xce\xbd\xce\xbd\xce\xb7\xcf\x82'
        result = crypt(
            t_msg.decode('utf-8'),
            '$p5k2$sha1$3e8$KosHgqNo$jJ.gcxXLu6COVzAlz5SRvAqZTd8='
        )
        expected = '$p5k2$sha1$3e8$KosHgqNo$jJ.gcxXLu6COVzAlz5SRvAqZTd8='
        self.assertEqual(expected, result)

        # crypt 5 (UTF-8 bytes)
        result = crypt(
            b'\xce\x99\xcf\x89\xce\xb1\xce\xbd\xce\xbd\xce\xb7\xcf\x82',
            '$p5k2$sha1$3e8$KosHgqNo$jJ.gcxXLu6COVzAlz5SRvAqZTd8='
        )
        expected = '$p5k2$sha1$3e8$KosHgqNo$jJ.gcxXLu6COVzAlz5SRvAqZTd8='
        self.assertEqual(expected, result)

    def test_secret_key(self):
        result = crypt('test', secret_key='123')
        # algo and iteration count and salt are taken from the result hash
        # but without providing a secret key, the hash should be different
        # from what we expecting!
        self.assertNotEqual(result, crypt('test', result))
        # providing wrong secret key also should lead to wrong hash
        self.assertNotEqual(result, crypt('test', result, secret_key='111'))
        # hash match
        self.assertEqual(result, crypt('test', result, secret_key='123'))

    def test_crypt_staticmethod(self):
        self.assertTrue(hasattr(PBKDF2, 'crypt'))

    def test__makesalt(self):
        salt = _makesalt()
        self.assertEqual(len(self.u(salt)), 8)
        # ensure that this size is not changing
        for x in range(1000):
            salt = _makesalt()
            self.assertEqual(len(self.u(salt)), 8)

    def test_encrypt(self):
        result = encrypt('test')
        self.assertEqual(result, self.u(crypt('test', result)))
        self.assertNotEqual(result, self.u(crypt('test', result,
                                                 secret_key='123')))
        # salt_length is consumed but not used!
        result = encrypt('test', salt_length=100)
        self.assertEqual(result, self.u(crypt('test', result)))
        # any other params are consumed to avoid errors
        self.assertTrue(encrypt('test', iterations=100))

    def test_verify(self):
        result0 = crypt('test')
        result1 = crypt('test', secret_key='123')
        self.assertFalse(verify(result0, 'test', '123'))
        self.assertTrue(verify(result1, 'test', '123'))

    def test_pbkdf2_pseudorandom(self):
        pb = PBKDF2('test', 'salt')
        self.assertTrue(pb._pseudorandom(self.u('salt'), self.u('test')))
        pb = PBKDF2('test', 'salt', secret_key='123')
        self.assertTrue(pb._pseudorandom(self.u('salt'), self.u('test')))

    def test_pbkdf2_read(self):
        pb = PBKDF2('test', 'salt')
        pb.closed = True
        with self.assertRaises(ValueError) as e:
            pb.read(8)
        self.assertEqual(str(e.exception), "file-like object is closed")
        pb.closed = False
        self.assertTrue(pb.read(8))

    def test_pbkdf2_close(self):
        pb = PBKDF2('test', 'salt')
        pb.close()
        self.assertTrue(pb.closed)

    def test_pbkdf2_hexread(self):
        pb = PBKDF2('test', 'salt')
        self.assertEqual(pb.hexread(8), 'a7c6a595ae3e3907')

    def test_pbkdf2___f(self):
        pb = PBKDF2('test', 'salt')
        self.assertTrue(pb._PBKDF2__f(2))
        self.assertRaises(AssertionError, lambda: pb._PBKDF2__f(0))

    def test_pbkdf2__setup(self):
        pb = PBKDF2('test', 'salt')
        with self.assertRaises(TypeError) as e:
            pb._setup(123, 'salt', 1, pb._pseudorandom(self.u('salt'),
                                                       self.u('test')))
        self.assertEqual(str(e.exception), "passphrase must be str or unicode")

        with self.assertRaises(TypeError) as e:
            pb._setup('test', 123, 1, pb._pseudorandom(self.u('salt'),
                                                       self.u('test')))
        self.assertEqual(str(e.exception), "salt must be str or unicode")

        with self.assertRaises(TypeError) as e:
            pb._setup('test', 'salt', '1', pb._pseudorandom(self.u('salt'),
                                                            self.u('test')))
        self.assertEqual(str(e.exception), "iterations must be an integer")

        with self.assertRaises(ValueError) as e:
            pb._setup('test', 'salt', 0, pb._pseudorandom(self.u('salt'),
                                                          self.u('test')))
        self.assertEqual(str(e.exception), "iterations must be at least 1")

        with self.assertRaises(TypeError) as e:
            pb._setup('test', 'salt', 1, 'prf')
        self.assertEqual(str(e.exception), "prf must be callable")

    def test_crypt_errors(self):
        with self.assertRaises(TypeError) as e:
            crypt('test', 1)
        self.assertEqual(str(e.exception), "salt must be a string")

        with self.assertRaises(TypeError) as e:
            crypt(123, 'salt')
        self.assertEqual(str(e.exception), "word must be a string or unicode")

        salt = '$p5k2$sha1$0$H0NX9mT/$ih6FhDyRXAaEN4UXk50pNsZP/nU='
        with self.assertRaises(ValueError) as e:
            crypt('test', salt)
        self.assertEqual(str(e.exception), "Invalid salt")

        salt = '$p5k2$md5$3e8$H0NX9mT/$ih6FhDyRXAaEN4UXk50pNsZP/nU='
        with self.assertRaises(ValueError) as e:
            crypt('test', salt)
        self.assertEqual(
            str(e.exception),
            "Digest algorithm=md5 not supported!"
        )

        with self.assertRaises(ValueError) as e:
            crypt('test', '$$$')
        self.assertEqual(str(e.exception), "Illegal character '$' in salt")

    def test_password_mixin(self):
        from lux.extensions.rest import PasswordMixin
        app = self.application(PASSWORD_SECRET_KEY='ekwjfbnerxfo8475f0cnk')
        raw = 'test-password-123'
        mixin = PasswordMixin()
        mixin.on_config(app)
        psw = mixin.encrypt(raw)
        self.assertNotEqual(raw, psw)
        self.assertTrue(mixin.crypt_verify(psw, raw))
