import datetime

from cryptography.hazmat import backends
from cryptography.hazmat.primitives.serialization import pkcs12
from endesive.pdf import pdf
from werkzeug.datastructures import FileStorage
from bson.objectid import ObjectId


from app.models.Cert import Cert
from app.models.Sign import Sign
from app.utils.AWService import read_file_from_s3
from app.utils.response import response, gen_links
from config import SignsDatabase, CertsDatabase


def get_all(page: int, per_page: int) -> dict:
    count = SignsDatabase.count_documents({})

    cursor = SignsDatabase.find().skip(per_page * (page - 1)).limit(per_page)
    signs = [Sign(**doc).to_json() for doc in cursor]

    links = gen_links(page, count, per_page, 'main_route')

    return response(signs, links)


def make_sign(data: dict, file: FileStorage) -> dict:
    if not file:
        return response(None, None, 400)

    date = datetime.datetime.utcnow() - datetime.timedelta(hours=12)
    date = date.strftime('%Y%m%d%H%M%S+00\'00\'')
    dct = {
        'sigflags': 3,
        'contact': data['contact'],
        'location': data['location'],
        'signingdate': date,
        'reason': data['reason'],
    }

    cursor = CertsDatabase.find_one({'_id': ObjectId(data['cert'])})
    cert = Cert(**cursor).to_json()
    key_bytes = read_file_from_s3(cert['bucket'], cert['path'])

    p12 = pkcs12.load_key_and_certificates(key_bytes, b'123', backends.default_backend())
    doc = pdf.FPDF()
    doc.pkcs11_setup(dct,
                     p12[0], p12[1], p12[2],
                     'sha256'
                     )
    for i in range(2):
        doc.add_page()
        doc.set_font('helvetica', '', 13.0)
        doc.cell(w=75.0, h=22.0, align='C', txt='Hello, world page=%d.' % i, border=0, ln=0)

    return response(doc.output('pdf-signed-fpdf.pdf', "F"))
