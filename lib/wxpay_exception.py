#
#
# 微信支付API异常类
# @author widyhu
#
#

class WxPayException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def errorMessage(self):
        raise self.msg
