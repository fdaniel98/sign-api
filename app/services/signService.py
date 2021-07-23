from flask import request, url_for

from app.models.Sign import Sign
from app.utils.response import response, gen_links
from config import SignsDatabase


def get_all():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))

    count = SignsDatabase.count_documents({})

    cursor = SignsDatabase.find().skip(per_page * (page - 1)).limit(per_page);
    signs = [Sign(**doc).to_json() for doc in cursor]

    links = gen_links(page, count, per_page, 'main_route')

    return response(signs, links)
