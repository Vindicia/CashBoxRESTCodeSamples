import hashlib
import base64
import hmac

class Authoriser:

    hmac_key = ''
    signature = ''
    debug = False

    def __init__(self, request_signature, hmac_key, debug=False):
        self.signature = bytes(request_signature, encoding='utf8')
        self.hmac_key = bytes(hmac_key, encoding='utf8')
        self.debug = False

    def validate(self, body):
        body = bytes(str(body), encoding='utf8')
        body_hash = base64.b64encode(hmac.new(self.hmac_key, body, hashlib.sha256).digest())
        if self.debug == True:
            print(body_hash)
            print(self.signature)

        if body_hash == self.signature:
            return True

        return False