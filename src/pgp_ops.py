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
