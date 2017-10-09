# TODO doesn't work...encoding issue?
from OpenSSL.crypto import load_publickey, FILETYPE_PEM, verify, X509

with open('./downloads/opq.box.updates.tar.gz', 'rb') as f:
    file_data = f.read()

with open('./downloads/opq.box.updates.tar.gz.sig', 'rb') as f:
    signature = f.read()

with open('./downloads/opq-signing-public.pem') as f:
    public_key_data = f.read()

# load in the publickey file, in my case, I had a .pem file.
# If the file starts with
#     "-----BEGIN PUBLIC KEY-----"
# then it is of the PEM type. The only other FILETYPE is
# "FILETYPE_ASN1".
pkey = load_publickey(FILETYPE_PEM, public_key_data)

# the verify() function expects that the public key is
# wrapped in an X.509 certificate
x509 = X509()
x509.set_pubkey(pkey)

# perform the actual verification. We need the X509 object,
# the signature to verify, the file to verify, and the
# algorithm used when signing.
verify(x509, signature, file_data, "sha256")
