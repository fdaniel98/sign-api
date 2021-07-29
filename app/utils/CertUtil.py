import datetime
import uuid

from OpenSSL import crypto
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import NameOID
from dotenv import dotenv_values

from app.models.Cert import Cert
from app.utils.AWService import upload_to_s3
from app.utils.JWToken import get_user

config = dotenv_values(".env")


class CertUtil(object):
    def __init__(self):
        self.pem_path = config['PEM_KEY']
        self.p12_path = config['P12_PATH']
        self.aws_p12_path = None
        self.aws_key = None
        self.aws_crt = None
        self.aws_pub = None
        self.password_encode = 'utf-8'
        self.user = get_user();
        self.ca_cert = None
        self.ca_pk = None
        self.filename = None

    @staticmethod
    def key_create():
        return rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

    def key_save(self, filename, key, password):
        path = self.pem_path.format(self.user['id'], filename)
        # get our key to a var for later safe
        if not password:
            data = key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        else:
            data = key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.BestAvailableEncryption(password.encode('utf-8')),
            )
        return upload_to_s3(data, path)

    def key_load(self,filename, password):
        with open(filename, "rb") as f:
            private_key = serialization.load_pem_private_key(
                f.read(),
                password.encode(self.password_encode),
                default_backend())
            return private_key

    @staticmethod
    def cert_load(filename):
        with open(filename, "rb") as f:
            return x509.load_pem_x509_certificate(f.read(), default_backend())

    def pem_save(self, filename, data):
        path = self.pem_path.format(self.user['id'], filename)
        public_data = data.public_bytes(serialization.Encoding.PEM)
        return upload_to_s3(public_data, path)

    @staticmethod
    def csr_load(filename):
        with open(filename, 'rb') as f:
            return x509.load_pem_x509_csr(data=f.read(), backend=default_backend())

    @staticmethod
    def csr_create(csr_info, key):
        return x509.CertificateSigningRequestBuilder().subject_name(
            x509.Name([
                x509.NameAttribute(NameOID.COMMON_NAME, csr_info['name']),
                x509.NameAttribute(NameOID.COUNTRY_NAME, csr_info['country']),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, csr_info['state']),
                x509.NameAttribute(NameOID.LOCALITY_NAME, csr_info['city']),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, csr_info['company']),
            ])
        ).sign(
            # Sign the CSR with our private key.
            key, hashes.SHA256(), default_backend()
        )

    def csr_sign(self, csr):
        return x509.CertificateBuilder().subject_name(
            csr.subject
        ).issuer_name(
            self.ca_cert.subject
        ).public_key(
            csr.public_key()
        ).serial_number(
            uuid.uuid4().int  # pylint: disable=no-member
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        ).add_extension(
            extval=x509.KeyUsage(
                digital_signature=True, key_encipherment=True, content_commitment=True,
                data_encipherment=False, key_agreement=False, encipher_only=False, decipher_only=False,
                key_cert_sign=False, crl_sign=False
            ),
            critical=True
        ).add_extension(
            extval=x509.BasicConstraints(ca=False, path_length=None),
            critical=True
        ).add_extension(
            extval=x509.AuthorityKeyIdentifier.from_issuer_public_key(self.ca_pk.public_key()),
            critical=False
        ).sign(
            private_key=self.ca_pk,
            algorithm=hashes.SHA256(),
            backend=default_backend()
        )

    def pk12_create(self, name, cert, key):
        pk12 = crypto.PKCS12()
        pk12.set_certificate(crypto.X509.from_cryptography(cert))
        pk12.set_privatekey(crypto.PKey.from_cryptography_key(key))
        pk12.set_ca_certificates((crypto.X509.from_cryptography(self.ca_cert),))
        pk12.set_friendlyname(name)
        return pk12

    def pk12_save(self, filename, p12, password):
        path = self.p12_path.format(self.user['id'], filename)
        return upload_to_s3(p12.export(password.encode(self.password_encode)), path)

    def pk12_load(self, filename, password):
        with open(filename, 'rb') as fp:
            return pkcs12.load_key_and_certificates(fp.read(), password.encode(self.password_encode), default_backend())

    @staticmethod
    def ca_create(key, csr_info):
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, csr_info['name']),
            x509.NameAttribute(NameOID.COUNTRY_NAME, csr_info['country']),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, csr_info['state']),
            x509.NameAttribute(NameOID.LOCALITY_NAME, csr_info['city']),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, csr_info['company']),
        ])
        return x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            # Our certificate will be valid for given years
            datetime.datetime.utcnow() + datetime.timedelta(days=csr_info['year'] * 365)
        ).add_extension(
            extval=x509.BasicConstraints(ca=True, path_length=None),
            critical=True
        ).sign(
            # Sign our certificate with our private key
            key, hashes.SHA256(), default_backend()
        )

    def load_certificate_authority(self, password, ca_key, ca):
        print('CA certificate found, using it')
        # .key.pem file
        ca_pk = self.key_load(ca_key, password)
        # .crt.pem file
        ca_cert = self.cert_load(ca)
        self.ca_cert = ca_cert
        self.ca_pk = ca_pk

    def create_certificate_authority(self, csr_info):
        print('CA... generating it')
        filename = int(datetime.datetime.utcnow().timestamp())
        ca_pk = self.key_create()
        ca_cert = self.ca_create(ca_pk, csr_info)
        key_res = self.key_save("{}.key.pem".format(filename), ca_pk, csr_info['password'])
        pub_res = self.key_save("{}.pub.pem".format(filename), ca_pk, None)
        crt_res = self.pem_save("{}.crt.pem".format(filename), ca_cert)

        self.aws_crt = {
            'bucket': crt_res.bucket_name,
            'path': crt_res.key
        }
        self.aws_key = {
            'bucket': key_res.bucket_name,
            'path': key_res.key
        }
        self.aws_pub = {
            'bucket': pub_res.bucket_name,
            'path': pub_res.key
        }

        self.ca_cert = ca_cert
        self.ca_pk = ca_pk
        self.filename = filename

    def create_pk12(self, csr_info):
        client_pk = self.ca_pk
        client_csr = self.csr_create(csr_info, client_pk)
        client_cert = self.csr_sign(client_csr)
        client_p12 = self.pk12_create(csr_info['name'].encode(), client_cert, client_pk)
        p12_res = self.pk12_save("{}.p12".format(self.filename), client_p12, csr_info['password'])

        cert = {
            'extension': '.p12',
            'filename': self.filename,
            'path': p12_res.key,
            'pub': self.aws_pub,
            'key': self.aws_key,
            'crt': self.aws_crt,
            'provider': config['PROVIDER'],
            'bucket': config['AWS_BUCKET'],
            'created_at': datetime.datetime.utcnow().timestamp()
        }

        return cert

# print('Generating certificates')
# cls = CertUtil()
# cls.CA()
# cls.USERs()
