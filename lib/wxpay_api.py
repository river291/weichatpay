from .wxpay_config import WxPayConfig
from .wxpay_exception import WxPayException
from .wxpay_data import WxPayResults

import requests


# 接口访问类，包含所有微信支付API列表的封装，类中方法为static方法，
# 每个接口有默认超时时间（除提交被扫支付为10s，上报超时时间为1s外，其他均为6s）
# @author widyhu

class WxPayApi:
    """
    #
    #统一下单，WxPayUnifiedOrder中out_trade_no、body、total_fee、trade_type必填
    #appid、mchid、spbill_create_ip、nonce_str不需要填入
    # @ param WxPayUnifiedOrder $inputObj
    # @ param int $timeOut
    # @ throws WxPayException
    # @ return 成功时返回，其他抛异常
    #
    """

    @staticmethod
    def unifiedOrder(inputObj, timeOut=6):
        url = 'https://api.mch.weixin.qq.com/pay/unifiedorder'
        # 检测必要参数
        if not inputObj.IsOut_trade_noSet():
            WxPayException("缺少统一支付接口必填参数out_trade_no！")
        elif not inputObj.IsBodySet():
            WxPayException("缺少统一支付接口必填参数body！")
        elif not inputObj.IsTotal_feeSet():
            WxPayException("缺少统一支付接口必填参数total_fee！")
        elif not inputObj.IsTrade_typeSet():
            WxPayException("缺少统一支付接口必填参数trade_type！")

        # 关联参数
        if inputObj.GetTrade_type() == "JSAPI" and not inputObj.IsOpenidSet():
            WxPayException("统一支付接口中，缺少必填参数openid！trade_type为JSAPI时，openid为必填参数！")
        if inputObj.GetTrade_type() == "NATIVE" and not inputObj.IsProduct_idSet():
            WxPayException("统一支付接口中，缺少必填参数product_id！trade_type为JSAPI时，product_id为必填参数！")

        # 异步通知url未设置，则使用配置文件中的url
        if not inputObj.IsNotify_urlSet():
            inputObj.SetNotify_url(WxPayConfig.__NOTIFY_URL__)

        inputObj.SetAppid(WxPayConfig.__APPID__)  # 公众账号ID
        inputObj.SetMch_id(WxPayConfig.__MCHID__)  # 商户号
        inputObj.SetSpbill_create_ip('0.0.0.0')  # 终端IP
        inputObj.SetSpbill_create_ip("1.1.1.1")
        inputObj.SetNonce_str(WxPayApi.getNonceStr())

        # 签名
        inputObj.SetSign()
        xml = inputObj.ToXml()

        startTimeStamp = WxPayApi.getMillisecond()  # 请求开始时间
        response = WxPayApi.postXmlCurl(xml, url, False, timeOut)
        result = WxPayResults.Init(response)
        WxPayApi.reportCostTime(url, startTimeStamp, result)

        return result

    # 查询订单，WxPayOrderQuery中out_trade_no、transaction_id至少填一个
    # appid、mchid、spbill_create_ip、nonce_str不需要填入
    # @ param WxPayOrderQuery $inputObj
    # @ param int $timeOut
    # @ throws WxPayException
    # @ return 成功时返回，其他抛异常
    @staticmethod
    def orderQuery(inputObj, timeOut=6):
        url = "https://api.mch.weixin.qq.com/pay/orderquery"
        # 检测必填参数
        if not inputObj.IsOut_trade_noSet() and not inputObj.IsTransaction_idSet():
            WxPayException("订单查询接口中，out_trade_no、transaction_id至少填一个！")
        inputObj.SetAppid(WxPayConfig.__APPID__)  # 公众账号ID
        inputObj.SetMch_id(WxPayConfig.__MCHID__)  # 商户号
        inputObj.SetNonce_str(WxPayApi.getNonceStr())  # 随机字符串

        inputObj.SetSign()  # 签名
        xml = inputObj.ToXml()

        startTimeStamp = WxPayApi.getMillisecond()  # 请求开始时间
        response = WxPayApi.postXmlCurl(xml, url, False, timeOut)
        result = WxPayResults.Init(response)
        WxPayApi.reportCostTime(url, startTimeStamp, result)  # 上报请求花费时间

        return result

    # 关闭订单，WxPayCloseOrder中out_trade_no必填
    # appid、mchid、spbill_create_ip、nonce_str不需要填入
    # @ param WxPayCloseOrder $inputObj
    # @ param int $timeOut
    # @ throws WxPayException
    # @ return 成功时返回，其他抛异常
    @staticmethod
    def closeOrder(inputObj, timeOut=6):
        url = "https://api.mch.weixin.qq.com/pay/closeorder"
        # 检测必填参数
        if not inputObj.IsOut_trade_noSet():
            WxPayException("订单查询接口中，out_trade_no必填！")
        inputObj.SetAppid(WxPayConfig.__APPID__)  # 公众账号ID
        inputObj.SetMch_id(WxPayConfig.__MCHID__)  # 商户号
        inputObj.SetNonce_str(WxPayApi.getNonceStr())  # 随机字符串

        inputObj.SetSign()  # 签名
        xml = inputObj.ToXml()

        startTimeStamp = WxPayApi.getMillisecond()  # 请求开始时间
        response = WxPayApi.postXmlCurl(xml, url, False, timeOut)
        result = WxPayResults.Init(response)
        WxPayApi.reportCostTime(url, startTimeStamp, result)  # 上报请求花费时间

        return result

    # 申请退款，WxPayRefund中out_trade_no、transaction_id至少填一个且
    # out_refund_no、total_fee、refund_fee、op_user_id为必填参数
    # appid、mchid、spbill_create_ip、nonce_str不需要填入
    # @ param WxPayRefund $inputObj
    # @ param int $timeOut
    # @ throws WxPayException
    # @ return 成功时返回，其他抛异常
    @staticmethod
    def refund(inputObj, timeOut=6):
        url = "https://api.mch.weixin.qq.com/secapi/pay/refund"
        # 检测必要参数
        if not inputObj.IsOut_trade_noSet() and not inputObj.IsTransaction_idSet():
            WxPayException("退款申请接口中，out_trade_no、transaction_id至少填一个！")
        elif not inputObj.IsOut_refund_noSet():
            WxPayException("退款申请接口中，缺少必填参数out_refund_no！")
        elif not inputObj.IsTotal_feeSet():
            WxPayException("退款申请接口中，缺少必填参数total_fee！")
        elif not inputObj.IsRefund_feeSet():
            WxPayException("退款申请接口中，缺少必填参数refund_fee！")
        elif not inputObj.IsOp_user_idSet():
            WxPayException("退款申请接口中，缺少必填参数op_user_id！")
        inputObj.SetAppid(WxPayConfig.__APPID__)  # 公众账号ID
        inputObj.SetMch_id(WxPayConfig.__MCHID__)  # 商户号
        inputObj.SetNonce_str(WxPayApi.getNonceStr())  # 随机字符串

        inputObj.SetSign()  # 签名
        xml = inputObj.ToXml()
        startTimeStamp = WxPayApi.getMillisecond()  # 请求开始时间
        response = WxPayApi.postXmlCurl(xml, url, False, timeOut)
        result = WxPayResults.Init(response)
        WxPayApi.reportCostTime(url, startTimeStamp, result)  # 上报请求花费时间

        return result

    # 查询退款
    # 提交退款申请后，通过调用该接口查询退款状态。退款有一定延时，
    # 用零钱支付的退款20分钟内到账，银行卡支付的退款3个工作日后重新查询退款状态。
    # WxPayRefundQuery中out_refund_no、out_trade_no、transaction_id、refund_id四个参数必填一个
    # appid、mchid、spbill_create_ip、nonce_str不需要填入
    # @ param WxPayRefundQuery $inputObj
    # @ param int $timeOut
    # @ throws WxPayException
    # @ return 成功时返回，其他抛异常

    @staticmethod
    def refundQuery(inputObj, timeOut=6):
        url = "https://api.mch.weixin.qq.com/pay/refundquery"
        # 检测必要参数
        if not inputObj.IsOut_refund_noSet() and \
                not inputObj.IsOut_trade_noSet() and \
                not inputObj.IsTransaction_idSet() and \
                not inputObj.IsRefund_idSet():
            WxPayException("退款查询接口中，out_refund_no、out_trade_no、transaction_id、refund_id四个参数必填一个！")
        inputObj.SetAppid(WxPayConfig.__APPID__)  # 公众账号ID
        inputObj.SetMch_id(WxPayConfig.__MCHID__)  # 商户号
        inputObj.SetNonce_str(WxPayApi.getNonceStr())  # 随机字符串

        inputObj.SetSign()  # 签名
        xml = inputObj.ToXml()
        startTimeStamp = WxPayApi.getMillisecond()  # 请求开始时间
        response = WxPayApi.postXmlCurl(xml, url, False, timeOut)
        result = WxPayResults.Init(response)
        WxPayApi.reportCostTime(url, startTimeStamp, result)  # 上报请求花费时间

        return result

    @staticmethod
    def notify(callback, msg):
        xml = ''

        try:
            result = WxPayResults.Init(xml)
        except WxPayException as e:
            msg = e.errorMessage()
            return False
        return callback(result)

    @staticmethod
    def getNonceStr(length=32):
        chars = "abcdefghijklmnopqrstuvwxyz0123456789"
        wx_str = ""
        for i in range(length):
            wx_str += ''
        return wx_str

    # 直接输出xml
    @staticmethod
    def replyNotify(xml):
        return xml

    @staticmethod
    def reportCostTime(url, startTimeStamp, data):
        pass

    @staticmethod
    def postXmlCurl(xml, url, useCert=False, second=30):
        return xml

    @staticmethod
    def getMillisecond():
        pass
