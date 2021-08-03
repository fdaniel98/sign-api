import datetime
import os

from bson.objectid import ObjectId
from cryptography.hazmat import backends
from cryptography.hazmat.primitives.serialization import pkcs12
from endesive.pdf import cms
from werkzeug.datastructures import FileStorage

from app.models.Cert import Cert
from app.models.Sign import Sign
from app.utils.AWService import read_file_from_s3
from app.utils.response import response, gen_links
from config import SignsDatabase, CertsDatabase, config


def get_all(page: int, per_page: int) -> dict:
    count = SignsDatabase.count_documents({})

    cursor = SignsDatabase.find().skip(per_page * (page - 1)).limit(per_page)
    signs = [Sign(**doc).to_json() for doc in cursor]

    links = gen_links(page, count, per_page, 'main_route')

    return response(signs, links)


def make_sign(data: dict, file: FileStorage) -> str:
    if not file:
        return response(None, None, 400)

    date = datetime.datetime.utcnow() - datetime.timedelta(hours=12)
    date = date.strftime("D:%Y%m%d%H%M%S+00'00'")
    dct = {
        "aligned": 0,
        "sigflags": 3,
        "sigflagsft": 132,
        "sigpage": 0,
        "sigbutton": True,
        "sigfield": "Signature1",
        "auto_sigfield": True,
        "sigandcertify": True,
        "signaturebox": (470, 840, 570, 640),
        "signature": "TEST - SIGN",
        #        "signature_img": "signature_test.png",
        'contact': data['contact'],
        'location': data['location'],
        "signingdate": date,
        'reason': data['reason'],
        "password": "1234",
    }

    cursor = CertsDatabase.find_one({'_id': ObjectId(data['cert'])})
    cert = Cert(**cursor).to_json()
    key_bytes = read_file_from_s3(cert['bucket'], cert['path'])

    p12 = pkcs12.load_key_and_certificates(key_bytes, b'123', backends.default_backend())
    read_data = file.stream.read()
    sign_data = cms.sign(read_data, dct, p12[0], p12[1], p12[2], "sha256")

    path = '{}\\signed-{}'.format(config['SIGNED_TMP_PATH'], file.filename)

    with open(path, "wb") as fp:
        fp.write(read_data)
        fp.write(sign_data)

    return path
