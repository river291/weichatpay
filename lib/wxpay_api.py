from .wxpay_config import WxPayConfig
from .wxpay_exception import WxPayException
from .wxpay_data import WxPayResults, WxPayReport

import requests, datetime


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

    # 下载对账单，WxPayDownloadBill中bill_date为必填参数
    # appid、mchid、spbill_create_ip、nonce_str不需要填入
    # @ param WxPayDownloadBill $inputObj
    # @ param int $timeOut
    # @ throws WxPayException
    # @ return 成功时返回，其他抛异常
    @staticmethod
    def downloadBill(inputObj, timeOut=6):
        url = "https://api.mch.weixin.qq.com/pay/downloadbill"
        if not inputObj.IsBill_dateSet():
            WxPayException("对账单接口中，缺少必填参数bill_date！")
        inputObj.SetAppid(WxPayConfig.__APPID__)  # 公众账号ID
        inputObj.SetMch_id(WxPayConfig.__MCHID__)  # 商户号
        inputObj.SetNonce_str(WxPayApi.getNonceStr())  # 随机字符串

        inputObj.SetSign()  # 签名
        xml = inputObj.ToXml()

        response = WxPayApi.postXmlCurl(xml, url, False, timeOut)
        if response[0:5] == "<xml>":
            return ""
        return response

    # 提交被扫支付API
    # 收银员使用扫码设备读取微信用户刷卡授权码以后，二维码或条码信息传送至商户收银台，
    # 由商户收银台或者商户后台调用该接口发起支付。
    # WxPayWxPayMicroPay中body、out_trade_no、total_fee、auth_code参数必填
    # appid、mchid、spbill_create_ip、nonce_str不需要填入
    # @ param WxPayWxPayMicroPay $inputObj
    # @ param int $timeOut
    @staticmethod
    def micropay(inputObj, timeOut=10):
        url = "https://api.mch.weixin.qq.com/pay/micropay"
        # 检测必填参数
        if not inputObj.IsBodySet():
            WxPayException("提交被扫支付API接口中，缺少必填参数body！")
        elif inputObj.IsOut_trade_noSet():
            WxPayException("提交被扫支付API接口中，缺少必填参数out_trade_no！")
        elif inputObj.IsTotal_feeSet():
            WxPayException("提交被扫支付API接口中，缺少必填参数total_fee！")
        elif inputObj.IsAuth_codeSet():
            WxPayException("提交被扫支付API接口中，缺少必填参数auth_code！")

        inputObj.SetSpbill_create_ip("1.1.1.1")  # 终端ip
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

    # 撤销订单API接口，WxPayReverse中参数out_trade_no和transaction_id必须填写一个
    # appid、mchid、spbill_create_ip、nonce_str不需要填入
    # @ param WxPayReverse $inputObj
    # @ param int $timeOut
    # @ throws WxPayException
    @staticmethod
    def reverse(inputObj, timeOut=6):
        url = "https://api.mch.weixin.qq.com/secapi/pay/reverse"
        if not inputObj.IsOut_trade_noSet() and not inputObj.IsTransaction_idSet():
            WxPayException("撤销订单API接口中，参数out_trade_no和transaction_id必须填写一个！")
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

    # 测速上报，该方法内部封装在report中，使用时请注意异常流程
    # WxPayReport中interface_url、return_code、result_code、user_ip、execute_time_必填
    # appid、mchid、spbill_create_ip、nonce_str不需要填入
    # @ param WxPayReport $inputObj
    # @ param int $timeOut
    # @ throws WxPayException
    # @ return 成功时返回，其他抛异常
    @staticmethod
    def report(inputObj, timeOut=1):
        url = "https://api.mch.weixin.qq.com/payitil/report"
        # 检测必填参数
        if not inputObj.IsInterface_urlSet():
            WxPayException("接口URL，缺少必填参数interface_url！")
        if not inputObj.IsReturn_codeSet():
            WxPayException("返回状态码，缺少必填参数return_code！")
        if not inputObj.IsResult_codeSet():
            WxPayException("业务结果，缺少必填参数result_code！")
        if not inputObj.IsUser_ipSet():
            WxPayException("访问接口IP，缺少必填参数user_ip！")
        if not inputObj.IsExecute_time_Set():
            WxPayException("接口耗时，缺少必填参数execute_time_！")
        inputObj.SetAppid(WxPayConfig.__APPID__)  # 公众账号ID
        inputObj.SetMch_id(WxPayConfig.__MCHID__)  # 商户号
        inputObj.SetUser_ip("1.1.1.1")  # 终端IP
        inputObj.SetTime("1991-1-1 00:00:00")  # 商户上报时间
        inputObj.SetNonce_str(WxPayApi.getNonceStr())

        inputObj.SetSign()  # 签名
        xml = inputObj.ToXml()

        startTimeStamp = WxPayApi.getMillisecond()  # 请求开始时间
        response = WxPayApi.postXmlCurl(xml, url, False, timeOut)
        return response

    # 生成二维码规则, 模式一生成支付二维码
    # appid、mchid、spbill_create_ip、nonce_str不需要填入
    # @ param WxPayBizPayUrl $inputObj
    # @ param int $timeOut
    # @ throws WxPayException
    # @ return 成功时返回，其他抛异常
    @staticmethod
    def bizpayurl(inputObj, timeOut=6):
        if not inputObj.IsProduct_idSet():
            WxPayException("生成二维码，缺少必填参数product_id！")

        inputObj.SetAppid(WxPayConfig.__APPID__)  # 公众账号ID
        inputObj.SetMch_id(WxPayConfig.__MCHID__)  # 商户号
        inputObj.SetTime_stamp("1991-1-1 00:00:00")  # 时间戳
        inputObj.SetNonce_str(WxPayApi.getNonceStr())  # 随机字符串

        inputObj.SetSign()  # 签名

        return inputObj.GetValues()

    # 转换短链接
    # 该接口主要用于扫码原生支付模式一中的二维码链接转成短链接(weixin: // wxpay / s / XXXXXX)，
    # 减小二维码数据量，提升扫描速度和精确度。
    # appid、mchid、spbill_create_ip、nonce_str不需要填入
    # @ param WxPayShortUrl $inputObj
    # @ param int $timeOut
    # @ throws WxPayException
    # @ return 成功时返回，其他抛异常
    @staticmethod
    def shorturl(inputObj, timeOut=6):
        url = "https://api.mch.weixin.qq.com/tools/shorturl"
        # 检测必填参数
        if not inputObj.IsLong_urlSet():
            WxPayException("需要转换的URL，签名用原串，传输需URL encode！")
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

    # 支付结果通用通知
    # @ param function $callback
    # 直接回调函数使用方法: notify(you_function);
    # 回调类成员函数方法: notify(array($this, you_function));
    # $callback 原型为：function function_name($data){}
    @staticmethod
    def notify(callback, msg):
        # 获取通知的数据
        xml = ''

        # 如果返回成功则验证签名
        try:
            result = WxPayResults.Init(xml)
        except WxPayException as e:
            msg = e.errorMessage()
            return False
        return callback(result)

    # 产生随机字符串，不长于32位
    # @ param int $length
    # @ return 产生的随机字符串
    @staticmethod
    def getNonceStr(length=32):
        chars = "abcdefghijklmnopqrstuvwxyz0123456789"
        wx_str = ""

        import random
        for i in range(length):
            rand_num = random.randint(0, len(chars) - 1)
            wx_str += chars[rand_num]
        return wx_str

    # 直接输出xml
    @staticmethod
    def replyNotify(xml):
        return xml

    # 上报数据， 上报的时候将屏蔽所有异常流程
    # @ param string $usrl
    # @ param int $startTimeStamp
    # @ param array $data
    @staticmethod
    def reportCostTime(url, startTimeStamp, data):
        # 如果不需要上报数据
        if WxPayConfig.REPORT_LEVENL == 0:
            return
        # 如果仅上失败上报
        if WxPayConfig.REPORT_LEVENL == 1 and \
                        "return_code" in data.keys() and \
                        data["return_code"] == "SUCCESS" and \
                        "result_code" in data.keys() and \
                        data["result_code"] == "SUCCESS":
            return

        # 上报逻辑
        endTimeStamp = WxPayApi.getMillisecond()
        objInput = WxPayReport()
        objInput.SetInterface_url(url)
        objInput.SetExecute_time_(endTimeStamp - startTimeStamp)
        # 返回状态码
        if "return_code" in data.keys():
            objInput.SetReturn_code(data["return_code"])
        # 返回信息
        if "return_msg" in data.keys():
            objInput.SetReturn_msg(data["return_msg"])
        # 业务结果
        if "result_code" in data.keys():
            objInput.SetResult_code(data["result_code"])
        # 错误代码
        if "err_code" in data.keys():
            objInput.SetErr_code(data["err_code"])
        # 错误代码描述
        if "err_code_des" in data.keys():
            objInput.SetErr_code_des(data["err_code_des"])
        # 商户订单号
        if "out_trade_no" in data.keys():
            objInput.SetOut_trade_no(data["out_trade_no"])
        # 设备号
        if "device_info" in data.keys():
            objInput.SetDevice_info(data["device_info"])

        try:
            WxPayApi.report(objInput)
        except WxPayException as e:
            # 不做任何处理
            pass

    # 以post方式提交xml到对应的接口url
    #
    # @ param string $xml  需要post的xml数据
    # @ param string $url url
    # @ param bool $useCert 是否需要证书，默认不需要
    # @ param int $second url执行超时时间，默认30s
    # @ throws WxPayException
    @staticmethod
    def postXmlCurl(xml, url, useCert=False, second=30):
        url = url
        # 是否严格校验
        verify = True
        # 设置超时
        timeout = second
        # 如果有配置代理这里就设置代理
        proxies = {}
        if WxPayConfig.CURL_PROXY_HOST != "0.0.0.0" and \
                        WxPayConfig.CURL_PROXY_PORT != 0:
            proxies = {
                "http": "http://" + WxPayConfig.CURL_PROXY_HOST + ":" + WxPayConfig.CURL_PROXY_PORT,
                "https": "https://" + WxPayConfig.CURL_PROXY_HOST + ":" + WxPayConfig.CURL_PROXY_PORT
            }
        if useCert:
            # 设置证书
            # 使用证书：cert与key分别属于两个.pem文件
            pass
        # post提交方式
        response = requests.post(url, data=xml)

        # 返回结果
        if response.status_code == "200":
            return response.text
        else:
            error = response.status_code
            WxPayException("curl出错，错误码:" + error)

    # 获取毫秒级别的时间戳
    @staticmethod
    def getMillisecond():
        # 获取毫秒的时间戳
        import time
        now_timestmap = time.time()
        time_tuple = str(now_timestmap).split('.')
        new_time = time_tuple[0] + time_tuple[1][0:3]
        return new_time
