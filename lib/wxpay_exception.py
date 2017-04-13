#
#
# 微信支付API异常类
# @author widyhu
#
#
import traceback


class WxPayException(Exception):
    def errorMessage(self):
        return traceback.print_last()
