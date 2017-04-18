#
# 2015-06-29 修复签名问题
#

from .wxpay_config import WxPayConfig
from .wxpay_exception import WxPayException

import hashlib


# 数据对象基础类，该类中定义数据类最基本的行为，包括：
# 计算/设置/获取签名、输出xml格式的参数、从xml读取数据对象等
# @author widyhu
# edit by River

class WxPayDataBase:
    values = dict()

    # 设置签名， 详见签名生成算法
    def SetSign(self):
        sign = self.MakeSign()
        self.values['sign'] = sign
        return sign

    # 获取签名， 详见签名生成算法的值
    def GetSign(self):
        return self.values['sign']

    # 判断签名，详见签名生成算法是否存在
    def IsSignSet(self):
        return hasattr(self.values, 'sign')

    # 输出xml字符
    def ToXml(self):
        if not isinstance(self.values, dict) or len(self.values) <= 0:
            raise WxPayException("数组数据异常！")
        xml = "<xml>"
        for key, value in self.values.items():
            if value.isnumeric():
                xml += "<{0}>{1}</{0}".format(key, value)
            else:
                xml += "<{0}><![CDATA[{1}]]></{0}>".format(key, value)
        xml += "</xml>"
        return xml

    # 将xml转为array
    def FromXml(self, xml):
        if not xml:
            raise WxPayException("xml数据异常！")

        # 引入ElementTree
        try:
            import xml.etree.cElementTree as ET
        except ImportError:
            import xml.etree.ElementTree as ET
        # 处理xml
        xml2dict = {}

        xml_tree = ET.fromstring(xml)
        for child_node in xml_tree:
            xml2dict[child_node.tag] = child_node.text

        self.values = xml2dict
        return self.values

    # 格式化参数格式化成url参数
    def ToUrlParams(self):
        buff = ""
        tmp = []
        for key, value in self.values.items():
            if key != "sign" and value != "" and not isinstance(value, dict):
                tmp.append(key + "=" + str(value))
        buff = "&".join(tmp)
        return buff

    # 生成签名
    def MakeSign(self):
        # 签名步骤一： 按字典序排序参数
        self.values = sorted(self.values.items, key=lambda self: self.values[0])
        wx_string = self.ToUrlParams()
        # 签名步骤二：在string后加入KEY
        wx_string = wx_string + "&key=" + WxPayConfig.__KEY__
        # 签名步骤三：MD5加密
        wx_string = hashlib.md5(wx_string.encode('utf-8')).hexdigest()
        # 签名步骤四：所有字符转为大写
        result = wx_string.upper()
        return result

    # 获取设置的值
    def GetValues(self):
        return self.values


# 接口调用结果类
class WxPayResults(WxPayDataBase):
    # 检测签名
    def CheckSign(self):
        if self.IsSignSet():
            raise WxPayException("签名错误！")
        sign = self.MakeSign()
        if self.GetSign() == sign:
            return True
        raise WxPayException("签名错误！")

    # 使用字典初始化
    def FromArray(self, **array):
        self.values = array

    # 使用数组初始化对象
    def InitFromArray(self, noCheckSign=False, **array):
        self.FromArray(**array)
        if noCheckSign == False:
            self.CheckSign()
        return self

    # 设置参数
    def SetData(self, key, value):
        self.values[key] = value

    # 将xml转成array
    def Init(self, xml):
        self.FromXml(xml)
        # fix bug 2015-06-29
        if self.values['return_code'] != 'SUCCESS':
            return self.GetValues()
        self.CheckSign()
        return self.GetValues()


# 回调基础类
class WxPayNotifyReply(WxPayDataBase):
    # 设置错误码 FAIL 或者 SUCCESS
    def SetReturn_code(self, return_code):
        self.values['return_code'] = return_code

    # 获取错误码 FAIL 或者 SUCCESS
    def GetReturn_code(self):
        return self.values['return_code']

    # 设置错误信息
    def SetReturn_msg(self, return_msg):
        self.values['return_msg'] = return_msg

    # 获取错误信息
    def GetReturn_msg(self):
        return self.values['return_msg']

    # 设置返回参数
    def SetData(self, key, value):
        self.values[key] = value


# 统一下单输入对象
class WxPayUnifiedOrder(WxPayDataBase):
    # 设置微信分配的公众账号ID
    def SetAppid(self, value):
        self.values['appid'] = value

    # 获取微信分配的公众账号ID的值
    def GetAppid(self):
        return self.values['appid']

    # 判断微信分配的公众账号ID是否存在
    def IsAppidSet(self):
        return 'appid' in self.values.keys()

    # 设置微信支付分配的商户号
    def SetMch_id(self, value):
        self.values['mch_id'] = value

    # 获取微信支付分配的商户号的值
    def GetMch_id(self):
        return self.values['mch_id']

    # 判断微信支付分配的商户号是否存在
    def IsMch_idSet(self):
        return 'mch_id' in self.values.keys()

    # 设置微信支付分配的终端设备号，商户自定义
    def SetDevice_info(self, value):
        self.values['device_info'] = value

    # 获取微信支付分配的终端设备号，商户自定义的值
    def GetDevice_info(self):
        return self.values['device_info']

    # 判断微信支付分配的终端设备号，商户自定义是否存在
    def IsDevice_infoSet(self):
        return 'device_info' in self.values.keys()

    # 设置随机字符串， 不长于32位， 推荐随机数生成算法
    def SetNonce_str(self, value):
        self.values['nonce_str'] = value

    # 获取随机字符串， 不长于32位， 推荐随机数生成算法
    def GetNonce_str(self):
        return self.values['nonce_str']

    # 判断随机字符串， 不长于32位， 推荐随机数生成算法是否存在
    def IsNonce_strSet(self):
        return 'nonce_str' in self.values.keys()

    # 设置商品或支付单简要描述
    def SetBody(self, value):
        self.values['body'] = value

    # 获取商品或支付单简要描述
    def GetBody(self):
        return self.values['body']

    # 判断商品或支付单简要描述是否存在
    def IsBodySet(self):
        return 'body' in self.values.keys()

    # 设置商品名称明细列表
    def SetDetail(self, value):
        self.values['detail'] = value

    # 获取商品名称明细列表的值
    def GetDetail(self):
        return self.values['detail']

    # 判断商品名称明细列表是否存在
    def IsDetailSet(self):
        return 'detail' in self.values.keys()

    # 设置附加数据，在查询API和支付通知中原样返回，该字段主要用于商户携带订单的自定义数据
    def SetAttach(self, value):
        self.values['attach'] = value

    # 获取附加数据，在查询API和支付通知中原样返回，该字段主要用于商户携带订单的自定义数据的值
    def GetAttach(self):
        return self.values['attach']

    # 判断附加数据，在查询API和支付通知中原样返回，该字段主要用于商户携带订单的自定义数据是否存在
    def IsAttachSet(self):
        return 'attach' in self.values.keys()

    # 设置商户系统内部的订单号，32个字符内、可包含字母，其他说明见商户订单号
    def SetOut_trade_no(self, value):
        self.values['out_trade_no'] = value

    # 获取商户系统内部的订单号，32个字符内、可包含字母，其他说明见商户订单号的值
    def GetOut_trade_no(self):
        return self.values['out_trade_no']

    # 判断商户系统内部的订单号，32个字符内、可包含字母，其他说明见商户订单号是否存在
    def IsOut_trade_noSet(self):
        return 'out_trade_no' in self.values.keys()

    # 设置符合ISO 4217标准的三位字母代码，默认人民币：CNY，其他值列表详见货币类型
    def SetFee_type(self, value):
        self.values['fee_type'] = value

    # 获取符合ISO 4217标准的三位字母代码，默认人民币：CNY，其他值列表详见货币类型的值
    def GetFee_type(self):
        return self.values['fee_type']

    # 判断符合ISO 4217标准的三位字母代码，默认人民币：CNY，其他值列表详见货币类型是否存在
    def IsFee_typeSet(self):
        return 'fee_type' in self.values.keys()

    # 设置订单总金额，只能为整数，详见支付金额
    def SetTotal_fee(self, value):
        self.values['total_fee'] = value

    # 获取订单总金额，只能为整数，详见支付金额的值
    def GetTotal_fee(self):
        return self.values['total_fee']

    # 判断订单总金额，只能为整数，详见支付金额是否存在
    def IsTotal_feeSet(self):
        return 'total_fee' in self.values.keys()

    # 设置APP和网页支付提交用用户端IP，Native支付填调用微信支付API的机器IP。
    def SetSpbill_create_ip(self, value):
        self.values['spbill_create_ip'] = value

    # 获取APP和网页支付提交用户端IP， Navtive支付填调用微信支付API的机器IP的值
    def GetSpbill_create_ip(self):
        return self.values['spbill_create_ip']

    # 判断APP和网页支付提交用户端IP， Native支付填调用微信支付API的机器IP是否存在
    def IsSpbill_create_ipSet(self):
        return 'spbill_create_ip' in self.values.keys()

    # 设置订单生成时间，格式yyyyMMddHHmmss，如2009年12月25日9点10分10秒表示为20091225091910
    def SetTime_start(self, value):
        self.values['time_start'] = value

    # 获取订单生成时间，格式yyyyMMddHHmmss，如2009年12月25日9点10分10秒表示为20091225091910的值
    def GetTime_start(self):
        return self.values['time_start']

    # 判断订单生成时间，格式为yyyMMddHHmmss,如2009年12月25日9点10分10秒表示为20091225091910的值是否存在
    def IsTime_startSet(self):
        return 'time_start' in self.values.keys()

    # 设置订单失效时间，格式为yyyyMMddHHmmss，如2009年12月27日9点10分10秒表示为20091227091010。其他详见时间规则
    def SetTime_expire(self, value):
        self.values['time_expire'] = value

    # 获取订单失效时间，格式为yyyyMMddHHmmss，如2009年12月27日9点10分10秒表示为20091227091010。其他详见时间规则的值
    def GetTime_expire(self):
        return self.values['time_expire']

    # 判断订单失效时间，格式为yyyyMMddHHmmss，如2009年12月27日9点10分10秒表示为20091227091010。其他详见时间规则是否存在
    def IsTime_expireSet(self):
        return 'time_expire' in self.values.keys()

    # 设置商品标记，代金券或立减优惠功能的参数，说明详见代金券或立减优惠
    def SetGoods_tag(self, value):
        self.values['goods_tag'] = value

    # 获取商品标记，代金券或立减优惠功能的参数，说明详见代金券或立减优惠的值
    def GetGoods_tag(self):
        return self.values['goods_tag']

    # 判断商品标记，代金券或立减优惠功能的参数，说明详见代金券或立减优惠是否存在
    def IsGoods_tagSet(self):
        return 'goods_tag' in self.values.keys()

    # 设置接收微信支付异步通知回调地址
    def SetNotify_url(self, value):
        self.values['notify_url'] = value

    # 获取接收微信支付异步通知回调地址的值
    def GetNotify_url(self):
        return self.values['notify_url']

    # 判断接收微信支付异步通知回调地址是否存在
    def IsNotify_urlSet(self):
        return 'notify_url' in self.values.keys()

    # 设置取值如下：JSAPI，NATIVE，APP，详细说明见参数规定
    def SetTrade_type(self, value):
        self.values['trade_type'] = value

    # 获取取值如下：JSAPI，NATIVE，APP，详细说明见参数规定的值
    def GetTrade_type(self):
        return self.values['trade_type']

    # 判断取值如下：JSAPI，NATIVE，APP，详细说明见参数规定是否存在
    def IsTrade_typeSet(self):
        return 'trade_type' in self.values.keys()

    # 设置trade_type=NATIVE，此参数必传。此id为二维码中包含的商品ID，商户自行定义。
    def SetProduct_id(self, value):
        self.values['product_id'] = value

    # 获取trade_type=NATIVE，此参数必传。此id为二维码中包含的商品ID，商户自行定义。的值
    def GetProduct_id(self):
        return self.values['product_id']

    # 判断trade_type=NATIVE，此参数必传。此id为二维码中包含的商品ID，商户自行定义。是否存在
    def IsProduct_idSet(self):
        return 'product_id' in self.values.keys()

    # 设置trade_type=JSAPI，此参数必传，用户在商户appid下的唯一标识。下单前需要调用【网页授权获取用户信息】接口获取到用户的Openid。
    def SetOpenid(self, value):
        self.values['openid'] = value

    # 获取trade_type=JSAPI，此参数必传，用户在商户appid下的唯一标识。下单前需要调用【网页授权获取用户信息】接口获取到用户的Openid。 的值
    def GetOpenid(self):
        return self.values['openid']

    # 判断trade_type=JSAPI，此参数必传，用户在商户appid下的唯一标识。下单前需要调用【网页授权获取用户信息】接口获取到用户的Openid。 是否存在
    def IsOpenidSet(self):
        return 'openid' in self.values.keys()


#
# 订单查询输入对象
#
class WxPayOrderQuery(WxPayDataBase):
    # 设置微信分配的公众账号ID
    def SetAppid(self, value):
        self.values['appid'] = value

    # 获取微信分配的公众账号ID的值
    def GetAppid(self):
        return self.values['appid']

    # 判断微信分配的公众账号ID是否存在
    def IsAppidSet(self):
        return 'appid' in self.values.keys()

    # 设置微信支付分配的商户号
    def SetMch_id(self, value):
        self.values['mch_id'] = value

    # 获取微信支付分配的商户号的值
    def GetMch_id(self):
        return self.values['mch_id']

    # 判断微信支付分配的商户号是否存在
    def IsMch_idSet(self):
        return 'mch_id' in self.values.keys()

    # 设置微信的订单号，优先使用
    def SetTransaction_id(self, value):
        self.values['transaction_id'] = value

    # 获取微信的订单号，优先使用的值
    def GetTransaction_id(self):
        return self.values['transaction_id']

    # 判断微信的订单号，优先使用是否存在
    def IsTransaction_idSet(self):
        return 'transaction_id' in self.values.keys()

    # 设置商户系统内部的订单号，当没提供transaction_id时需要传这个。
    def SetOut_trade_no(self, value):
        self.values['out_trade_no'] = value

    # 获取商户系统内部的订单号，当没提供transaction_id时需要传这个。的值
    def GetOut_trade_no(self):
        return self.values['out_trade_no']

    # 判断商户系统内部的订单号，当没提供transaction_id时需要传这个。是否存在
    def IsOut_trade_noSet(self):
        return 'out_trade_no' in self.values.keys()

    # 设置随机字符串，不长于32位。推荐随机数生成算法
    def SetNonce_str(self, value):
        self.values['nonce_str'] = value

    # 获取随机字符串，不长于32位。推荐随机数生成算法的值
    def GetNonce_str(self):
        return self.values['nonce_str']

    # 判断随机字符串，不长于32位。推荐随机数生成算法是否存在
    def IsNonce_strSet(self):
        return 'nonce_str' in self.values.keys()


#
# 关闭订单输入对象
#
class WxPayCloseOrder(WxPayDataBase):
    # 设置微信分配的公众账号ID
    def SetAppid(self, value):
        self.values['appid'] = value

    # 获取微信分配的公众账号ID的值
    def GetAppid(self):
        return self.values['appid']

    # 判断微信分配的公众账号ID是否存在
    def IsAppidSet(self):
        return 'appid' in self.values.keys()

    # 设置微信支付分配的商户号
    def SetMch_id(self, value):
        self.values['mch_id'] = value

    # 获取微信支付分配的商户号的值
    def GetMch_id(self):
        return self.values['mch_id']

    # 判断微信支付分配的商户号是否存在
    def IsMch_idSet(self):
        return 'mch_id' in self.values.keys()

    # 设置商户系统内部的订单号
    def SetOut_trade_no(self, value):
        self.values['out_trade_no'] = value

    # 获取商户系统内部的订单号的值
    def GetOut_trade_no(self):
        return self.values['out_trade_no']

    # 判断商户系统内部的订单号是否存在
    def IsOut_trade_noSet(self):
        return 'out_trade_no' in self.values.keys()

    # 设置商户系统内部的订单号,32个字符内、可包含字母, 其他说明见商户订单号
    def SetNonce_str(self, value):
        self.values['nonce_str'] = value

    # 获取商户系统内部的订单号,32个字符内、可包含字母, 其他说明见商户订单号的值
    def GetNonce_str(self):
        return self.values['nonce_str']

    # 判断商户系统内部的订单号,32个字符内、可包含字母, 其他说明见商户订单号是否存在
    def IsNonce_strSet(self):
        return 'nonce_str' in self.values.keys()


#
# 提交退款输入对象
#
class WxPayRefund(WxPayDataBase):
    # 设置微信分配的公众账号ID
    def SetAppid(self, value):
        self.values['appid'] = value

    # 获取微信分配的公众账号ID的值
    def GetAppid(self):
        return self.values['appid']

    # 判断微信分配的公众账号ID是否存在
    def IsAppidSet(self):
        return 'appid' in self.values.keys()

    # 设置微信支付分配的商户号
    def SetMch_id(self, value):
        self.values['mch_id'] = value

    # 获取微信支付分配的商户号的值
    def GetMch_id(self):
        return self.values['mch_id']

    # 判断微信支付分配的商户号是否存在
    def IsMch_idSet(self):
        return 'mch_id' in self.values.keys()

    # 设置微信支付分配的终端设备号，与下单一致
    def SetDevice_info(self, value):
        self.values['device_info'] = value

    # 获取微信支付分配的终端设备号，与下单一致的值
    def GetDevice_info(self):
        return self.values['device_info']

    # 判断微信支付分配的终端设备号，与下单一致是否存在
    def IsDevice_infoSet(self):
        return 'device_info' in self.values.keys()

    # 设置随机字符串，不长于32位。推荐随机数生成算法
    def SetNonce_str(self, value):
        self.values['nonce_str'] = value

    # 获取随机字符串，不长于32位。推荐随机数生成算法的值
    def GetNonce_str(self):
        return self.values['nonce_str']

    # 判断随机字符串，不长于32位。推荐随机数生成算法是否存在
    def IsNonce_strSet(self):
        return 'nonce_str' in self.values.keys()

    # 设置微信订单号
    def SetTransaction_id(self, value):
        self.values['transaction_id'] = value

    # 获取微信订单号的值
    def GetTransaction_id(self):
        return self.values['transaction_id']

    # 判断微信订单号是否存在
    def IsTransaction_idSet(self):
        return 'transaction_id' in self.values.keys()

    # 设置商户系统内部的订单号,transaction_id、out_trade_no二选一，如果同时存在优先级：transaction_id> out_trade_no
    def SetOut_trade_no(self, value):
        self.values['out_trade_no'] = value

    # 获取商户系统内部的订单号,transaction_id、out_trade_no二选一，如果同时存在优先级：transaction_id> out_trade_no的值
    def GetOut_trade_no(self):
        return self.values['out_trade_no']

    # 判断商户系统内部的订单号,transaction_id、out_trade_no二选一，如果同时存在优先级：transaction_id> out_trade_no是否存在
    def IsOut_trade_noSet(self):
        return 'out_trade_no' in self.values.keys()

    # 设置商户系统内部的退款单号，商户系统内部唯一，同一退款单号多次请求只退一笔
    def SetOut_refund_no(self, value):
        self.values['out_refund_no'] = value

    # 获取商户系统内部的退款单号，商户系统内部唯一，同一退款单号多次请求只退一笔的值
    def GetOut_refund_no(self):
        return self.values['out_refund_no']

    # 判断商户系统内部的退款单号，商户系统内部唯一，同一退款单号多次请求只退一笔是否存在
    def IsOut_refund_noSet(self):
        return 'out_refund_no' in self.values.keys()

    # 设置订单总金额，单位为分，只能为整数，详见支付金额
    def SetTotal_fee(self, value):
        self.values['total_fee'] = value

    # 获取订单总金额，单位为分，只能为整数，详见支付金额的值
    def GetTotal_fee(self):
        return self.values['total_fee']

    # 判断订单总金额，单位为分，只能为整数，详见支付金额是否存在
    def IsTotal_feeSet(self):
        return 'total_fee' in self.values.keys()

    # 设置退款总金额，订单总金额，单位为分，只能为整数，详见支付金额
    def SetRefund_fee(self, value):
        self.values['refund_fee'] = value

    # 获取退款总金额，订单总金额，单位为分，只能为整数，详见支付金额的值
    def GetRefund_fee(self):
        return self.values['refund_fee']

    # 判断退款总金额，订单总金额，单位为分，只能为整数，详见支付金额是否存在
    def IsRefund_feeSet(self):
        return 'refund_fee' in self.values.keys()

    # 设置货币类型，符合ISO 4217标准的三位字母代码，默认人民币：CNY，其他值列表详见货币类型
    def SetRefund_fee_type(self, value):
        self.values['refund_fee_type'] = value

    # 获取货币类型，符合ISO 4217标准的三位字母代码，默认人民币：CNY，其他值列表详见货币类型的值
    def GetRefund_fee_type(self):
        return self.values['refund_fee_type']

    # 判断货币类型，符合ISO 4217标准的三位字母代码，默认人民币：CNY，其他值列表详见货币类型是否存在
    def IsRefund_fee_typeSet(self):
        return 'refund_fee_type' in self.values.keys()

    # 设置操作员帐号, 默认为商户号
    def SetOp_user_id(self, value):
        self.values['op_user_id'] = value

    # 获取操作员帐号, 默认为商户号的值
    def GetOp_user_id(self):
        return self.values['op_user_id']

    # 判断操作员帐号, 默认为商户号是否存在
    def IsOp_user_idSet(self):
        return 'op_user_id' in self.values.keys()


#
# 退款查询输入对象
#
class WxPayRefundQuery(WxPayDataBase):
    # 设置微信分配的公众账号ID
    def SetAppid(self, value):
        self.values['appid'] = value

    # 获取微信分配的公众账号ID的值
    def GetAppid(self):
        return self.values['appid']

    # 判断微信分配的公众账号ID是否存在
    def IsAppidSet(self):
        return 'appid' in self.values.keys()

    # 设置微信支付分配的商户号
    def SetMch_id(self, value):
        self.values['mch_id'] = value

    # 获取微信支付分配的商户号的值
    def GetMch_id(self):
        return self.values['mch_id']

    # 判断微信支付分配的商户号是否存在
    def IsMch_idSet(self):
        return 'mch_id' in self.values.keys()

    # 设置微信支付分配的终端设备号
    def SetDevice_info(self, value):
        self.values['device_info'] = value

    # 获取微信支付分配的终端设备号的值
    def GetDevice_info(self):
        return self.values['device_info']

    # 判断微信支付分配的终端设备号是否存在
    def IsDevice_infoSet(self):
        return 'device_info' in self.values.keys()

    # 设置随机字符串，不长于32位。推荐随机数生成算法
    def SetNonce_str(self, value):
        self.values['nonce_str'] = value

    # 获取随机字符串，不长于32位。推荐随机数生成算法的值
    def GetNonce_str(self):
        return self.values['nonce_str']

    # 判断随机字符串，不长于32位。推荐随机数生成算法是否存在
    def IsNonce_strSet(self):
        return 'nonce_str' in self.values.keys()

    # 设置微信订单号
    def SetTransaction_id(self, value):
        self.values['transaction_id'] = value

    # 获取微信订单号的值
    def GetTransaction_id(self):
        return self.values['transaction_id']

    # 判断微信订单号是否存在
    def IsTransaction_idSet(self):
        return 'transaction_id' in self.values.keys()

    # 设置商户系统内部的订单号
    def SetOut_trade_no(self, value):
        self.values['out_trade_no'] = value

    # 获取商户系统内部的订单号的值
    def GetOut_trade_no(self):
        return self.values['out_trade_no']

    # 判断商户系统内部的订单号是否存在
    def IsOut_trade_noSet(self):
        return 'out_trade_no' in self.values.keys()

    # 设置商户退款单号
    def SetOut_refund_no(self, value):
        self.values['out_refund_no'] = value

    # 获取商户退款单号的值
    def GetOut_refund_no(self):
        return self.values['out_refund_no']

    # 判断商户退款单号是否存在
    def IsOut_refund_noSet(self):
        return 'out_refund_no' in self.values.keys()

    # 设置微信退款单号refund_id、out_refund_no、out_trade_no、transaction_id四个参数必填一个，如果同时存在优先级为：refund_id>out_refund_no>transaction_id>out_trade_no
    def SetRefund_id(self, value):
        self.values['refund_id'] = value

    # 获取微信退款单号refund_id、out_refund_no、out_trade_no、transaction_id四个参数必填一个，如果同时存在优先级为：refund_id
    def GetRefund_id(self):
        return self.values['refund_id']

    # 判断微信退款单号refund_id、out_refund_no、out_trade_no、transaction_id四个参数必填一个，如果同时存在优先级为：refund_id
    def IsRefund_idSet(self):
        return 'refund_id' in self.values['refund_id']


#
# 下载对账单输入对象
#
class WxPayDownloadBill(WxPayDataBase):
    # 设置微信分配的公众账号ID
    def SetAppid(self, value):
        self.values['appid'] = value

    # 获取微信分配的公众账号ID的值
    def GetAppid(self):
        return self.values['appid']

    # 判断微信分配的公众账号ID是否存在
    def IsAppidSet(self):
        return 'appid' in self.values.keys()

    # 设置微信支付分配的商户号
    def SetMch_id(self, value):
        self.values['mch_id'] = value

    # 获取微信支付分配的商户号的值
    def GetMch_id(self):
        return self.values['mch_id']

    # 判断微信支付分配的商户号是否存在
    def IsMch_idSet(self):
        return 'mch_id' in self.values.keys()

    # 设置微信支付分配的终端设备号，填写此字段，只下载该设备号的对账单
    def SetDevice_info(self, value):
        self.values['device_info'] = value

    # 获取微信支付分配的终端设备号，填写此字段，只下载该设备号的对账单的值
    def GetDevice_info(self):
        return self.values['device_info']

    # 判断微信支付分配的终端设备号，填写此字段，只下载该设备号的对账单是否存在
    def IsDevice_infoSet(self):
        return 'device_info' in self.values.keys()

    # 设置随机字符串，不长于32位。推荐随机数生成算法
    def SetNonce_str(self, value):
        self.values['nonce_str'] = value

    # 获取随机字符串，不长于32位。推荐随机数生成算法的值
    def GetNonce_str(self):
        return self.values['nonce_str']

    # 判断随机字符串，不长于32位。推荐随机数生成算法是否存在
    def IsNonce_strSet(self):
        return 'nonce_str' in self.values.keys()

    # 设置下载对账单的日期，格式：20140603
    def SetBill_date(self, value):
        self.values['bill_date'] = value

    # 获取下载对账单的日期，格式：20140603的值
    def GetBill_date(self):
        return self.values['bill_date']

    # 判断下载对账单的日期，格式：20140603是否存在
    def IsBill_dateSet(self):
        return 'bill_date' in self.values.keys()

    # 设置ALL，返回当日所有订单信息，默认值SUCCESS，返回当日成功支付的订单REFUND，返回当日退款订单REVOKED，已撤销的订单
    def SetBill_type(self, value):
        self.values['bill_type'] = value

    # 获取ALL，返回当日所有订单信息，默认值SUCCESS，返回当日成功支付的订单REFUND，返回当日退款订单REVOKED，已撤销的订单的值
    def GetBill_type(self):
        return self.values['bill_type']

    # 判断ALL，返回当日所有订单信息，默认值SUCCESS，返回当日成功支付的订单REFUND，返回当日退款订单REVOKED，已撤销的订单是否存在
    def IsBill_typeSet(self):
        return 'bill_type' in self.values.keys()


#
# 测速上报输入对象
#
class WxPayReport(WxPayDataBase):
    # 设置微信分配的公众账号ID
    def SetAppid(self, value):
        self.values['appid'] = value

    # 获取微信分配的公众账号ID的值
    def GetAppid(self):
        return self.values['appid']

    # 判断微信分配的公众账号ID是否存在
    def IsAppidSet(self):
        return 'appid' in self.values.keys()

    # 设置微信支付分配的商户号
    def SetMch_id(self, value):
        self.values['mch_id'] = value

    # 获取微信支付分配的商户号的值
    def GetMch_id(self):
        return self.values['mch_id']

    # 判断微信支付分配的商户号是否存在
    def IsMch_idSet(self):
        return 'mch_id' in self.values.keys()

    # 设置微信支付分配的终端设备号，商户自定义
    def SetDevice_info(self, value):
        self.values['device_info'] = value

    # 获取微信支付分配的终端设备号，商户自定义的值
    def GetDevice_info(self):
        return self.values['device_info']

    # 判断微信支付分配的终端设备号，商户自定义是否存在
    def IsDevice_infoSet(self):
        return 'device_info' in self.values.keys()

    # 设置随机字符串，不长于32位。推荐随机数生成算法
    def SetNonce_str(self, value):
        self.values['nonce_str'] = value

    # 获取随机字符串，不长于32位。推荐随机数生成算法的值
    def GetNonce_str(self):
        return self.values['nonce_str']

    # 判断随机字符串，不长于32位。推荐随机数生成算法是否存在
    def IsNonceStrSet(self):
        return 'nonce_str' in self.values.keys()

    # 设置上报对应的接口的完整URL，类似：https://api.mch.weixin.qq.com/pay/unifiedorder对于被扫支付，为更好的和商户共同分析一次业务行为的整体耗时情况，对于两种接入模式，请都在门店侧对一次被扫行为进行一次单独的整体上报，上报URL指定为：https://api.mch.weixin.qq.com/pay/micropay/total关于两种接入模式具体可参考本文档章节：被扫支付商户接入模式其它接口调用仍然按照调用一次，上报一次来进行。
    def SetInterface_url(self, value):
        self.values['interface_url'] = value

    # 获取上报对应的接口的完整URL，类似：https://api.mch.weixin.qq.com/pay/unifiedorder对于被扫支付，为更好的和商户共同分析一次业务行为的整体耗时情况，对于两种接入模式，请都在门店侧对一次被扫行为进行一次单独的整体上报，上报URL指定为：https://api.mch.weixin.qq.com/pay/micropay/total关于两种接入模式具体可参考本文档章节：被扫支付商户接入模式其它接口调用仍然按照调用一次，上报一次来进行。的值
    def GetInterface_url(self):
        return self.values['interface_url']

    # 判断上报对应的接口的完整URL，类似：https://api.mch.weixin.qq.com/pay/unifiedorder对于被扫支付，为更好的和商户共同分析一次业务行为的整体耗时情况，对于两种接入模式，请都在门店侧对一次被扫行为进行一次单独的整体上报，上报URL指定为：https://api.mch.weixin.qq.com/pay/micropay/total关于两种接入模式具体可参考本文档章节：被扫支付商户接入模式其它接口调用仍然按照调用一次，上报一次来进行。是否存在
    def IsInterface_urlSet(self):
        return 'interface_url' in self.values.keys()

    # 设置接口耗时情况，单位为毫秒
    def SetExecute_time_(self, value):
        self.values['execute_time_'] = value

    # 获取接口耗时情况，单位为毫秒的值
    def GetExecute_time_(self):
        return self.values['execute_time_']

    # 判断接口耗时情况，单位为毫秒是否存在
    def IsExecute_time_Set(self):
        return 'execute_time_' in self.values.keys()

    # 设置SUCCESS/FAIL此字段是通信标识，非交易标识，交易是否成功需要查看trade_state来判断
    def SetReturn_code(self, value):
        self.values['return_code'] = value

    # 获取SUCCESS/FAIL此字段是通信标识，非交易标识，交易是否成功需要查看trade_state来判断的值
    def GetReturn_code(self):
        return self.values['return_code']

    # 判断SUCCESS/FAIL此字段是通信标识，非交易标识，交易是否成功需要查看trade_state来判断是否存在
    def IsReturn_codeSet(self):
        return 'return_code' in self.values.keys()

    # 设置返回信息，如非空，为错误原因签名失败参数格式校验错误
    def SetReturn_msg(self, value):
        self.values['return_msg'] = value

    # 获取返回信息，如非空，为错误原因签名失败参数格式校验错误的值
    def GetReturn_msg(self):
        return self.values['return_msg']

    # 判断返回信息，如非空，为错误原因签名失败参数格式校验错误是否存在
    def IsReturn_msgSet(self):
        return 'return_msg' in self.values.keys()

    # 设置SUCCESS/FAIL
    def SetResult_code(self, value):
        self.values['result_code'] = value

    # 获取SUCCESS/FAIL的值
    def GetResult_code(self):
        return self.values['result_code']

    # 判断SUCCESS/FAIL是否存在
    def IsResult_codeSet(self):
        return 'result_code' in self.values.keys()

    # 设置ORDERNOTEXIST—订单不存在SYSTEMERROR—系统错误
    def SetErr_code(self, value):
        self.values['err_code'] = value

    # 获取ORDERNOTEXIST—订单不存在SYSTEMERROR—系统错误的值
    def GetErr_code(self):
        return self.values['err_code']

    # 判断ORDERNOTEXIST—订单不存在SYSTEMERROR—系统错误是否存在
    def IsErr_codeSet(self):
        return 'err_code' in self.values.keys()

    # 设置结果信息描述
    def SetErr_code_des(self, value):
        self.values['err_code_des'] = value

    # 获取结果信息描述的值
    def GetErr_code_des(self):
        return self.values['err_code_des']

    # 判断结果信息描述是否存在
    def IsErr_code_desSet(self):
        return 'err_code_des' in self.values.keys()

    # 设置商户系统内部的订单号,商户可以在上报时提供相关商户订单号方便微信支付更好的提高服务质量。
    def SetOut_trade_no(self, value):
        self.values['out_trade_no'] = value

    # 获取商户系统内部的订单号,商户可以在上报时提供相关商户订单号方便微信支付更好的提高服务质量。 的值
    def GetOut_trade_no(self):
        return self.values['out_trade_no']

    # 判断商户系统内部的订单号,商户可以在上报时提供相关商户订单号方便微信支付更好的提高服务质量。 是否存在
    def IsOut_trade_noSet(self):
        return 'out_trade_no' in self.values.keys()

    # 设置发起接口调用时的机器IP
    def SetUser_ip(self, value):
        self.values['user_ip'] = value

    # 获取发起接口调用时的机器IP 的值
    def GetUser_ip(self):
        return self.values['user_ip']

    # 判断发起接口调用时的机器IP 是否存在
    def IsUser_ipSet(self):
        return 'user_ip' in self.values.keys()

    # 设置系统时间，格式为yyyyMMddHHmmss，如2009年12月27日9点10分10秒表示为20091227091010。其他详见时间规则
    def SetTime(self, value):
        self.values['time'] = value

    # 获取系统时间，格式为yyyyMMddHHmmss，如2009年12月27日9点10分10秒表示为20091227091010。其他详见时间规则的值
    def GetTime(self):
        return self.values['time']

    # 判断系统时间，格式为yyyyMMddHHmmss，如2009年12月27日9点10分10秒表示为20091227091010。其他详见时间规则是否存在
    def IsTimeSet(self):
        return 'time' in self.values.keys()


#
# 短链转换输入对象
#
class WxPayShortUrl(WxPayDataBase):
    # 设置微信分配的公众账号ID
    def SetAppid(self, value):
        self.values['appid'] = value

    # 获取微信分配的公众账号ID的值
    def GetAppid(self):
        return self.values['appid']

    # 判断微信分配的公众账号ID是否存在
    def IsAppidSet(self):
        return 'appid' in self.values.keys()

    # 设置微信支付分配的商户号
    def SetMch_id(self, value):
        self.values['mch_id'] = value

    # 获取微信支付分配的商户号的值
    def GetMch_id(self):
        return self.values['mch_id']

    # 判断微信支付分配的商户号是否存在
    def IsMch_idSet(self):
        return 'mch_id' in self.values.keys()

    # 设置需要转换的URL，签名用原串，传输需URL encode
    def SetLong_url(self, value):
        self.values['long_url'] = value

    # 获取需要转换的URL，签名用原串，传输需URL encode的值
    def GetLong_url(self):
        return self.values['long_url']

    # 判断需要转换的URL，签名用原串，传输需URL encode是否存在
    def IsLong_urlSet(self):
        return 'long_url' in self.values.keys()

    # 设置随机字符串，不长于32位。推荐随机数生成算法
    def SetNonce_str(self, value):
        self.values['nonce_str'] = value

    # 获取随机字符串，不长于32位。推荐随机数生成算法的值
    def GetNonce_str(self):
        return self.values['nonce_str']

    # 判断随机字符串，不长于32位。推荐随机数生成算法是否存在
    def IsNonce_strSet(self):
        return 'nonce_str' in self.values.keys()


#
# 提交被扫输入对象
#
class WxPayMicroPay(WxPayDataBase):
    # 设置微信分配的公众账号ID
    def SetAppid(self, value):
        self.values['appid'] = value

    # 获取微信分配的公众账号ID的值
    def GetAppid(self):
        return self.values['appid']

    # 判断微信分配的公众账号ID是否存在
    def IsAppidSet(self):
        return 'appid' in self.values.keys()

    # 设置微信支付分配的商户号
    def SetMch_id(self, value):
        self.values['mch_id'] = value

    # 获取微信支付分配的商户号的值
    def GetMch_id(self):
        return self.values['mch_id']

    # 判断微信支付分配的商户号是否存在
    def IsMch_idSet(self):
        return 'mch_id' in self.values.keys()

    # 设置终端设备号(商户自定义，如门店编号)
    def SetDevice_info(self, value):
        self.values['device_info'] = value

    # 获取终端设备号(商户自定义，如门店编号)的值
    def GetDevice_info(self):
        return self.values['device_info']

    # 判断终端设备号(商户自定义，如门店编号)是否存在
    def IsDevice_infoSet(self):
        return 'device_info' in self.values.keys()

    # 设置随机字符串，不长于32位。推荐随机数生成算法
    def SetNonce_str(self, value):
        self.values['nonce_str'] = value

    # 获取随机字符串，不长于32位。推荐随机数生成算法的值
    def GetNonce_str(self):
        return self.values['nonce_str']

    # 判断随机字符串，不长于32位。推荐随机数生成算法是否存在
    def IsNonce_strSet(self):
        return 'nonce_str' in self.values.keys()

    # 设置商品或支付单简要描述
    def SetBody(self, value):
        self.values['body'] = value

    # 获取商品或支付单简要描述的值
    def GetBody(self):
        return self.values['body']

    # 判断商品或支付单简要描述是否存在
    def IsBodySet(self):
        return 'body' in self.values.keys()

    # 设置商品名称明细列表
    def SetDetail(self, value):
        self.values['detail'] = value

    # 获取商品名称明细列表的值
    def GetDetail(self):
        return self.values['detail']

    # 判断商品名称明细列表是否存在
    def IsDetailSet(self):
        return 'detail' in self.values.keys()

    # 设置附加数据，在查询API和支付通知中原样返回，该字段主要用于商户携带订单的自定义数据
    def SetAttach(self, value):
        self.values['attach'] = value

    # 获取附加数据，在查询API和支付通知中原样返回，该字段主要用于商户携带订单的自定义数据的值
    def GetAttach(self):
        return self.values['attach']

    # 判断附加数据，在查询API和支付通知中原样返回，该字段主要用于商户携带订单的自定义数据是否存在
    def IsAttachSet(self):
        return 'attach' in self.values.keys()

    # 设置商户系统内部的订单号,32个字符内、可包含字母, 其他说明见商户订单号
    def SetOut_trade_no(self, value):
        self.values['out_trade_no'] = value

    # 获取商户系统内部的订单号,32个字符内、可包含字母, 其他说明见商户订单号的值
    def GetOut_trade_no(self):
        return self.values['out_trade_no']

    # 判断商户系统内部的订单号,32个字符内、可包含字母, 其他说明见商户订单号是否存在
    def IsOut_trade_noSet(self):
        return 'out_trade_no' in self.values.keys()

    # 设置订单总金额，单位为分，只能为整数，详见支付金额
    def SetTotal_fee(self, value):
        self.values['total_fee'] = value

    # 获取订单总金额，单位为分，只能为整数，详见支付金额的值
    def GetTotal_fee(self):
        return self.values['total_fee']

    # 判断订单总金额，单位为分，只能为整数，详见支付金额是否存在
    def IsTotal_feeSet(self):
        return 'total_fee' in self.values.keys()

    # 设置符合ISO 4217标准的三位字母代码，默认人民币：CNY，其他值列表详见货币类型
    def SetFee_type(self, value):
        self.values['fee_type'] = value

    # 获取符合ISO 4217标准的三位字母代码，默认人民币：CNY，其他值列表详见货币类型的值
    def GetFee_type(self):
        return self.values['fee_type']

    # 判断符合ISO 4217标准的三位字母代码，默认人民币：CNY，其他值列表详见货币类型是否存在
    def IsFee_typeSet(self):
        return 'fee_type' in self.values.keys()

    # 设置调用微信支付API的机器IP
    def SetSpbill_create_ip(self, value):
        self.values['spbill_create_ip'] = value

    # 获取调用微信支付API的机器IP 的值
    def GetSpbill_create_ip(self):
        return self.values['spbill_create_ip']

    # 判断调用微信支付API的机器IP 是否存在
    def IsSpbill_create_ipSet(self):
        return 'spbill_create_ip' in self.values.keys()

    # 设置订单生成时间，格式为yyyyMMddHHmmss，如2009年12月25日9点10分10秒表示为20091225091010。详见时间规则
    def SetTime_start(self, value):
        self.values['time_start'] = value

    # 获取订单生成时间，格式为yyyyMMddHHmmss，如2009年12月25日9点10分10秒表示为20091225091010。详见时间规则的值
    def GetTime_start(self):
        return self.values['time_start']

    # 判断订单生成时间，格式为yyyyMMddHHmmss，如2009年12月25日9点10分10秒表示为20091225091010。详见时间规则是否存在
    def IsTime_startSet(self):
        return 'time_start' in self.values.keys()

    # 设置订单失效时间，格式为yyyyMMddHHmmss，如2009年12月27日9点10分10秒表示为20091227091010。详见时间规则
    def SetTime_expire(self, value):
        self.values['time_expire'] = value

    # 获取订单失效时间，格式为yyyyMMddHHmmss，如2009年12月27日9点10分10秒表示为20091227091010。详见时间规则的值
    def GetTime_expire(self):
        return self.values['time_expire']

    # 判断订单失效时间，格式为yyyyMMddHHmmss，如2009年12月27日9点10分10秒表示为20091227091010。详见时间规则是否存在
    def IsTime_expireSet(self):
        return 'time_expire' in self.values.keys()

    # 设置商品标记，代金券或立减优惠功能的参数，说明详见代金券或立减优惠
    def SetGoods_tag(self, value):
        self.values['goods_tag'] = value

    # 获取商品标记，代金券或立减优惠功能的参数，说明详见代金券或立减优惠的值
    def GetGoods_tag(self):
        return self.values['goods_tag']

    # 判断商品标记，代金券或立减优惠功能的参数，说明详见代金券或立减优惠是否存在
    def IsGoods_tagSet(self):
        return 'goods_tag' in self.values.keys()

    # 设置扫码支付授权码，设备读取用户微信中的条码或者二维码信息
    def SetAuth_code(self, value):
        self.values['auth_code'] = value

    # 获取扫码支付授权码，设备读取用户微信中的条码或者二维码信息的值
    def GetAuth_code(self):
        return self.values['auth_code']

    # 判断扫码支付授权码，设备读取用户微信中的条码或者二维码信息是否存在
    def IsAuth_codeSet(self):
        return 'auth_code' in self.values.keys()


#
# 撤销输入对象
#
class WxPayReverse(WxPayDataBase):
    # 设置微信分配的公众账号ID
    def SetAppid(self, value):
        self.values['appid'] = value

    # 获取微信分配的公众账号ID的值
    def GetAppid(self):
        return self.values['appid']

    # 判断微信分配的公众账号ID是否存在
    def IsAppidSet(self):
        return 'appid' in self.values.keys()

    # 设置微信支付分配的商户号
    def SetMch_id(self, value):
        self.values['mch_id'] = value

    # 获取微信支付分配的商户号的值
    def GetMch_id(self):
        return self.values['mch_id']

    # 判断微信支付分配的商户号是否存在
    def IsMch_idSet(self):
        return 'mch_id' in self.values.keys()

    # 设置微信的订单号，优先使用
    def SetTransaction_id(self, value):
        self.values['transaction_id'] = value

    # 获取微信的订单号，优先使用的值
    def GetTransaction_id(self):
        return self.values['transaction_id']

    # 判断微信的订单号，优先使用是否存在
    def IsTransaction_idSet(self):
        return 'transaction_id' in self.values.keys()

    # 设置商户系统内部的订单号,transaction_id、out_trade_no二选一，如果同时存在优先级：transaction_id> out_trade_no
    def SetOut_trade_no(self, value):
        self.values['out_trade_no'] = value

    # 获取商户系统内部的订单号,transaction_id、out_trade_no二选一，如果同时存在优先级：transaction_id> out_trade_no的值
    def GetOut_trade_no(self):
        return self.values['out_trade_no']

    # 判断商户系统内部的订单号,transaction_id、out_trade_no二选一，如果同时存在优先级：transaction_id> out_trade_no是否存在
    def IsOut_trade_noSet(self):
        return 'out_trade_no' in self.values.keys()

    # 设置随机字符串，不长于32位。推荐随机数生成算法
    def SetNonce_str(self, value):
        self.values['nonce_str'] = value

    # 获取随机字符串，不长于32位。推荐随机数生成算法的值
    def GetNonce_str(self):
        return self.values['nonce_str']

    # 判断随机字符串，不长于32位。推荐随机数生成算法是否存在
    def IsNonce_strSet(self):
        return 'nonce_str' in self.values.keys()


#
# 提交JSAPI输入对象
#
class WxPayJsApiPay(WxPayDataBase):
    # 设置微信分配的公众账号ID
    def SetAppid(self, value):
        self.values['appid'] = value

    # 获取微信分配的公众账号ID的值
    def GetAppid(self):
        return self.values['appid']

    # 判断微信分配的公众账号ID是否存在
    def IsAppidSet(self):
        return 'appid' in self.values.keys()

    # 设置支付时间戳
    def SetTimeStamp(self, value):
        self.values['timestamp'] = value

    # 获取支付时间戳的值
    def GetTimeStamp(self):
        return self.values['timestamp']

    # 判断支付时间戳是否存在
    def IsTimeStampSet(self):
        return 'timestamp' in self.values.keys()

    # 随机字符串
    def SetNonceStr(self, value):
        self.values['nonceStr'] = value

    # 获取notify随机字符串值
    def GetReturn_code(self):
        return self.values['nonceStr']

    # 判断随机字符串是否存在
    def IsReturn_codeSet(self):
        return 'nonceStr' in self.values.keys()

    # 设置订单详情扩展字符串
    def SetPackage(self, value):
        self.values['package'] = value

    # 获取订单详情扩展字符串的值
    def GetPackage(self):
        return self.values['package']

    # 判断订单详情扩展字符串是否存在
    def IsPackageSet(self):
        return 'package' in self.values.keys()

    # 设置签名方式
    def SetSignType(self, value):
        self.values['signType'] = value

    # 获取签名方式
    def GetSignType(self):
        return self.values['signType']

    # 判断签名方式是否存在
    def IsSignTypeSet(self):
        return 'signType' in self.values.keys()

    # 设置签名方式
    def SetPaySign(self, value):
        self.values['paySign'] = value

    # 获取签名方式
    def GetPaySign(self):
        return self.values['paySign']

    # 判断签名方式是否存在
    def IsPaySignSet(self):
        return 'paySign' in self.values.keys()


#
# 扫码支付模式一生成二维码参数
#

class WxPayBizPayUrl(WxPayDataBase):
    # 设置微信分配的公众账号ID
    def SetAppid(self, value):
        self.values['appid'] = value

    # 获取微信分配的公众账号ID的值
    def GetAppid(self):
        return self.values['appid']

    # 判断微信分配的公众账号ID是否存在
    def IsAppidSet(self):
        return 'appid' in self.values.keys()

    # 设置微信支付分配的商户号
    def SetMch_id(self, value):
        self.values['mch_id'] = value

    # 获取微信支付分配的商户号的值
    def GetMch_id(self):
        return self.values['mch_id']

    # 判断微信支付分配的商户号是否存在
    def IsMch_idSet(self):
        return 'mch_id' in self.values.keys()

    # 设置支付时间戳
    def SetTime_stamp(self, value):
        self.values['time_stamp'] = value

    # 获取支付时间戳的值
    def GetTime_stamp(self):
        return self.values['time_stamp']

    # 判断支付时间戳是否存在
    def IsTime_stampSet(self):
        return 'time_stamp' in self.values.keys()

    # 设置随机字符串
    def SetNonce_str(self, value):
        self.values['nonce_str'] = value

    # 获取随机字符串的值
    def GetNonce_str(self):
        return self.values['nonce_str']

    # 判断随机字符串是否存在
    def IsNonce_strSet(self):
        return 'nonce_str' in self.values.keys()

    # 设置商品ID
    def SetProduct_id(self, value):
        self.values['product_id'] = value

    # 获取商品ID的值
    def GetProduct_id(self):
        return self.values['product_id']

    # 判断商品ID是否存在
    def IsProduct_idSet(self):
        return 'product_id' in self.values.keys()
