import datetime
import os
import uuid
from urllib import request

from OpenSSL import crypto
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import NameOID
from flask import request

(
    ca, ca_key,
    cert1, cert1_key, cert1_pub, cert1_p12,
    cert2, cert2_key, cert2_pub, cert2_p12
) = (
    'demo2_ca.crt.pem', 'demo2_ca.key.pem',
    'demo2_user1.crt.pem', 'demo2_user1.key.pem', 'demo2_user1.pub.pem', 'demo2_user1.p12',
    'demo2_user2.crt.pem', 'demo2_user2.key.pem', 'demo2_user2.pub.pem', 'demo2_user2.p12'
)


class CertUtil(object):
    def key_create(self):
        return rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

    def key_save(self, fname, key, password):
        # Write our key to disk for safe keeping
        with open(fname, "wb") as f:
            if not password:
                f.write(key.public_key().public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ))
            else:
                f.write(key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.BestAvailableEncryption(password.encode('utf-8')),
                ))

    def key_load(self, fname, password):
        with open(fname, "rb") as f:
            private_key = serialization.load_pem_private_key(f.read(), password.encode('utf-8'), default_backend())
            return private_key

    def cert_load(self, fname):
        with open(fname, "rb") as f:
            return x509.load_pem_x509_certificate(f.read(), default_backend())

    def pem_save(self, fname, data):
        with open(fname, "wb") as f:
            f.write(data.public_bytes(serialization.Encoding.PEM))

    def csr_load(self, fname):
        with open(fname, 'rb') as f:
            return x509.load_pem_x509_csr(data=f.read(), backend=default_backend())

    def csr_create(self, csr_info, key):
        return x509.CertificateSigningRequestBuilder().subject_name(
            x509.Name([
                x509.NameAttribute(NameOID.COMMON_NAME, csr_info['name']),
                x509.NameAttribute(NameOID.COUNTRY_NAME, csr_info['country']),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, csr_info['state']),
                x509.NameAttribute(NameOID.LOCALITY_NAME, csr_info['city']),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME,csr_info['company']),
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
        pkcs12 = crypto.PKCS12()
        pkcs12.set_certificate(crypto.X509.from_cryptography(cert))
        pkcs12.set_privatekey(crypto.PKey.from_cryptography_key(key))
        pkcs12.set_ca_certificates((crypto.X509.from_cryptography(self.ca_cert),))
        pkcs12.set_friendlyname(name)
        return pkcs12

    def pk12_save(self, fname, p12, password):
        with open(fname, 'wb') as f:
            f.write(p12.export(password.encode('utf-8')))

    def pk12_load(self, fname, password):
        with open(fname, 'rb') as fp:
            return pkcs12.load_key_and_certificates(fp.read(), password.encode('utf-8'), default_backend())

    def ca_create(self, key, csr_info):
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
            # Our certificate will be valid for 10 years
            datetime.datetime.utcnow() + datetime.timedelta(days=10 * 365)
        ).add_extension(
            extval=x509.BasicConstraints(ca=True, path_length=None),
            critical=True
        ).sign(
            # Sign our certificate with our private key
            key, hashes.SHA256(), default_backend()
        )

    def load_certificate_authority(self):
        print('CA certificate found, using it')
        ca_pk = self.key_load(ca_key, '1234')
        ca_cert = self.cert_load(ca)
        self.ca_cert = ca_cert
        self.ca_pk = ca_pk

    def create_certificate_authority(self, csr_info):
        print('CA... generating it')
        filename = int(datetime.datetime.utcnow().timestamp())
        ca_pk = self.key_create()
        ca_cert = self.ca_create(ca_pk, csr_info)
        self.key_save("{}.key.pem".format(filename), ca_pk, csr_info['password'])
        self.key_save("{}.pub.pem".format(filename), ca_pk, None)
        self.pem_save("{}.crt.pem".format(filename), ca_cert)
        self.ca_cert = ca_cert
        self.ca_pk = ca_pk
        self.filename = filename

    def create_pk12(self, csr_info):
        client_pk = self.ca_pk
        client_csr = self.csr_create(csr_info, client_pk)
        client_cert = self.csr_sign(client_csr)
        client_p12 = self.pk12_create(csr_info['name'].encode(), client_cert, client_pk)
        self.pk12_save("{}.p12".format(self.filename), client_p12, csr_info['password'])



    def USERs(self):
        self.USER(1, cert1, cert1_key, cert1_pub, cert1_p12)
        self.USER(2, cert2, cert2_key, cert2_pub, cert2_p12)


#print('Generating certificates')
#cls = CertUtil()
#cls.CA()
#cls.USERs()