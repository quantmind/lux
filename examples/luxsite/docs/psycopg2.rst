Symlink the ``libssl.dylib`` and ``libcrypto.dylib`` from the
``/usr/local/Cellar/openssl/x.x.x/lib`` to ``/usr/local/lib`` directory:

    ln -s /usr/local/Cellar/openssl/x.x.x/lib/libssl.dylib /usr/local/lib/libssl.dylib
    ln -s /usr/local/Cellar/openssl/x.x.x/lib/libcrypto.dylib /usr/local/lib/libcrypto.dylib

Install psycopyg2:

    pip install psycopg2