

class SignUtil(object):
    def __init__(self, form):
        self.dimensions = (470, 840, 570, 640)
        self.form = form

    def get_sign_data(self):
        local = {
            'dimension_box': self.dimensions,
            'text_sign': self.form['text_sign'] if 'text_sign' in self.form else None,
            'signature_img': self.form['signature_img'] if 'signature_img' in self.form else '', #  should use this https://pillow.readthedocs.io/en/stable/reference/Image.html
            'signature_page': self.form['signature_page'] if 'signature_page' in self.form else 0,
            'signature_name': 'user-signature',  # should be from company's user
        }
        return {**self.form, **local}
