#
# 2015-06-29 修复签名问题
#

from .wxpay_config import WxPayConfig
from .wxpay_exception import WxPayException

import hashlib


# 数据对象基础类，该类中定义数据类最基本的行为，包括：
# 计算/设置/获取签名、输出xml格式的参数、从xml读取数据对象等
# @author widyhu

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
        if type(self.values) is not dict or len(self.values) <= 0:
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
        # libxml_disable_entity_loader(true)
        self.values = json_decode(json_encode(simplexml_load_string(xml, 'SimpleXMLElement', LIBXML_NOCDATA)), True)
        return self.values

    # 格式化参数格式化成url参数
    def ToUrlParams(self):
        buff = ""
        tmp = []
        for key, value in self.values.items():
            if key != "sign" and value != "" and type(value) is not dict:
                tmp.append(key + "=" + str(value))
        buff = "&".join(tmp)
        return buff

    # 生成签名
    def MakeSign(self):
        # 签名步骤一： 按字典序排序参数
        self.values = sorted(self.values.items, key=lambda self: self.values[0])
        wx_string = self.ToUrlParams()
        wx_string = wx_string + "&key=" + WxPayConfig.__KEY__
        wx_string = hashlib.md5(wx_string.encode('utf-8')).hexdigest()
        result = wx_string.upper()
        return result

    # 获取设置的值
    def GetValues(self):
        return self.values;


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
        obj = self
        obj.FromArray(**array)
        if noCheckSign == False
            obj.CheckSign()
        return obj

    # 设置参数
    def SetData(self, key, value):
        self.values[key] = value

    # 将xml转成array
    def Init(self, xml):
        obj = self
        obj.FromXml(xml)
        # fix bug 2015-06-29
        if obj.values['return_code'] != 'SUCCESS':
            return obj.GetValues()
        obj.CheckSign()
        return obj.GetValues()


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
        return hasattr(self.values, 'appid')

    # 设置微信支付分配的商户号
    def SetMch_id(self, value):
        self.values['mch_id'] = value

    # 获取微信支付分配的商户号的值
    def GetMch_id(self):
        return self.values['mch_id']

    # 判断微信支付分配的商户号是否存在
    def IsMch_idSet(self):
        return hasattr(self.values, 'mch_id')

    # 设置微信支付分配的终端设备号，商户自定义
    def SetDevice_info(self, value):
        self.values['device_info'] = value

    # 获取微信支付分配的终端设备号，商户自定义的值
    def GetDevice_info(self):
        return self.values['device_info']

    # 判断微信支付分配的终端设备号，商户自定义是否存在
    def IsDevice_infoSet(self):
        return hasattr(self.values, 'device_info')

    # 设置随机字符串， 不长于32位， 推荐随机数生成算法
    def SetNonce_str(self, value):
        self.values['nonce_str'] = value

    # 获取随机字符串， 不长于32位， 推荐随机数生成算法
    def GetNonce_str(self):
        return self.values['nonce_str']

    # 判断随机字符串， 不长于32位， 推荐随机数生成算法是否存在
    def IsNonce_strSet(self):
        return hasattr(self.values, 'nonce_str')

    # 设置商品或支付单简要描述
    def SetBody(self, value):
        self.values['body'] = value

    # 获取商品或支付单简要描述
    def GetBody(self):
        return self.values['body']

    # 判断商品或支付单简要描述是否存在
    def IsBodySet(self):
        return hasattr(self.values, 'body')

    # 设置商品名称明细列表
    def SetDetail(self, value):
        self.values['detail'] = value

    # 获取商品名称明细列表的值
    def GetDetail(self):
        return self.values['detail']

    # 判断商品名称明细列表是否存在
    def IsDetailSet(self):
        return hasattr(self.values, 'detail')

    # 设置附加数据，在查询API和支付通知中原样返回，该字段主要用于商户携带订单的自定义数据
    def SetAttach(self, value):
        self.values['attach'] = value

    # 获取附加数据，在查询API和支付通知中原样返回，该字段主要用于商户携带订单的自定义数据的值
    def GetAttach(self):
        return self.values['attach']

    # 判断附加数据，在查询API和支付通知中原样返回，该字段主要用于商户携带订单的自定义数据是否存在
    def IsAttachSet(self):
        return hasattr(self.values, 'attach')

    # 设置商户系统内部的订单号，32个字符内、可包含字母，其他说明见商户订单号
    def SetOut_trade_no(self, value):
        self.values['out_trade_no'] = value

    # 获取商户系统内部的订单号，32个字符内、可包含字母，其他说明见商户订单号的值
    def GetOut_trade_no(self):
        return self.values['out_trade_no']

    # 判断商户系统内部的订单号，32个字符内、可包含字母，其他说明见商户订单号是否存在
    def IsOut_trade_noSet(self):
        return hasattr(self.values, 'out_trade_no')
