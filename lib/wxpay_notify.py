#
# 回调基础类
#
from .wxpay_api import WxPayApi
from .wxpay_data import WxPayNotifyReply


class WxPayNotify(WxPayNotifyReply):
    def Handle(self, needSign=True):
        msg = "OK"
        result = WxPayApi.notify()
