from flask import request

from app.models.Cert import Cert
from app.utils import CertUtil
from app.utils.CertUtil import CertUtil
from app.utils.response import response, gen_links
from config import config, CertsDatabase


def get_all():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", config['PER_PAGE']))

    count = CertsDatabase.count_documents({})

    cursor = CertsDatabase.find().skip(per_page * (page - 1)).limit(per_page)
    certs = [Cert(**doc).to_json() for doc in cursor]

    links = gen_links(page, count, per_page, 'main_route')

    return response(certs, links)


def create_cert():
    params = request.get_json()
    cls = CertUtil()
    cls.create_certificate_authority(params)
    unsaved_cert = cls.create_pk12(params)
    valid_cert = Cert(**unsaved_cert).to_json()
    cert_saved = CertsDatabase.insert_one(valid_cert)
    return response({
        'id': str(cert_saved.inserted_id),
        'success': True
    }, None)
