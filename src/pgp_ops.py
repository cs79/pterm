import pgpy
from pgpy.constants import PubKeyAlgorithm, EllipticCurveOID, KeyFlags, HashAlgorithm, SymmetricKeyAlgorithm, CompressionAlgorithm

# Generate a new PGP key pair
def gen_keypair():
    """
    Generate a new key pair.
    Returns ECDSA keys with the curve SECP256K1 (for Bitcoin compatibility out-of-the-box).
    """
    return pgpy.PGPKey.new(PubKeyAlgorithm.ECDSA, EllipticCurveOID.NIST_P256)

# TODO: functionality to add user info to key, basic operations for signing / verifying, encrypting / decrypting, etc.
# limit this for now to what is useful for the pterm project; not all pgpy functionality is needed

def add_user_info(keypair, username, email=None):
    """
    Add user information to a key pair.
    Hardcodes some options here for now; we can make these configurable later.
    """
    uid = pgpy.PGPUID.new(username, comment='pterm PGP key', email=email)
    keypair.add_uid(uid,
                    usage={KeyFlags.Sign, KeyFlags.EncryptCommunications, KeyFlags.EncryptStorage},
                    hashes=[HashAlgorithm.SHA256],
                    ciphers=[SymmetricKeyAlgorithm.AES256],
                    compression=[CompressionAlgorithm.ZLIB, CompressionAlgorithm.BZ2, CompressionAlgorithm.ZIP, CompressionAlgorithm.Uncompressed])
    return keypair
