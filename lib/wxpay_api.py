from .wxpay_exception import WxPayException
from .wxpay_data import WxPayResults

class WxPayApi:
    @staticmethod
    def notify(callback, msg):
        xml = ''

        try:
            result = WxPayResults.Init(xml)
        except WxPayException as e:
            msg = e.errorMessage()
            return False
        return call_user_func(callback, result)
