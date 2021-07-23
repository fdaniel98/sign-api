from flask import url_for


def response(data, incoming_links, code=200):
    return {
        'data': data,
        'links': incoming_links,
        'code': code
    }


def gen_links(page, count, per_page, route):
    value = {
        "self": {"href": url_for(f".{route}", page=page, _external=True)},
        "last": {
            "href": url_for(
                f".{route}", page=(count // per_page) + 1, _external=True
            )
        },
    }
    # Add a 'prev' link if it's not on the first page:
    if page > 1:
        value["prev"] = {
            "href": url_for(f".{route}", page=page - 1, _external=True)
        }
    # Add a 'next' link if it's not on the last page:
    if page - 1 < count // per_page:
        value["next"] = {
            "href": url_for(f".{route}", page=page + 1, _external=True)
        }

    return value
