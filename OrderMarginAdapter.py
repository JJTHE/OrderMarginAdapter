import datetime
import random
import math

class Commodity:
    """商品类"""
    def __init__(self, name, threshold, packet):
        """商品的初始化方法
        :param name: 名称
        :param threshold: 整包取舍的阈值
        :param packet: 打包数量
        """
        self.name = name
        self.threshold = threshold
        self.packet = packet


class SupplySystem:
    """供应系统，提供商品列表"""
    def __init__(self):
        self.commodity_list = []

    def add_commodity(self, commodity):
        """在供应系统中添加商品
        :param commodity: 要添加的商品实例
        """
        self.commodity_list.append(commodity)


class Store:
    """商家类，负责生成订单"""
    def __init__(self, name):
        """商家类实例初始化方法"""
        self.name = name
        self.stock = {}
        self.order_list = []
        self.container = []

    def create_container_random(self, supply:SupplySystem):
        """随机生成货柜
        :param supply: 供应商
        """
        container = []
        eff_range = len(supply.commodity_list)
        # print(f"info: eff_range = {eff_range}")
        size = random.randint(0, eff_range)
        # print(f"info: size = {size}")
        while size:
            index = random.randint(0, eff_range - 1)
            # print(f"info: index = {index}")
            item = supply.commodity_list[index]
            container.append(item)
            size -= 1
        self.container = container

    def create_order(self):
        """根据商家当前的货柜随机生成订单
        :return: 随机订单
        """
        order = Order(self.name)
        for item in self.container:
            num = random.randint(0, 10000)
            order.set_item(item, num)
        return order

class Order:
    """订单类"""
    def __init__(self, owner):
        """订单类实例的初始化方法
        :param owner: 订单的所有者
        """
        self.owner = owner
        self.initial_time = datetime.date.today()
        self.id = random.randint(100000, 999999);
        self.goods_dict = {}

    def set_item(self, item, num):
        """设置订单中某物品的数量
        :param item: 商品类的实例
        :param num: 数量
        """
        self.goods_dict[item] = num

    def get_item(self, item):
        """获取订单中某物品的数量
        :param item: 商品类的实例
        :return: 该商品的数量
        """
        if item in self.goods_dict:
            num = self.goods_dict[item]
            return num
        else:
            return 0

class Form:
    """订单信息统计表"""
    class FormItem:
        """表项"""
        def __init__(self, commodity):
            """初始化表项
            :param commodity: 商品类的实例
            """
            self.order_id_list = []      # 相关订单id
            self.commodity = commodity   # 对应商品
            self.sum = 0                 # 已记录订单的商品总数
            self.leftover = 0            # 零散量
            self.felxnum = 0             # 可参与调整的数量
            self.flag = False            # 取舍标志
            self.left = 0                # 剩余待调整数量

        def add_order(self, order):
            """添加订单信息"""
            num = order.get_item(self.commodity)
            self.sum += num
            self.felxnum += (num % self.commodity.packet)
            self.order_id_list.append(order.id)


        def judge_state(self):
            """判断该表项当前状态"""
            self.leftover = self.sum % self.commodity.packet
            if self.leftover < self.commodity.threshold:
                self.flag = False
            else:
                self.flag = True
                self.leftover = self.commodity.packet - self.leftover
            self.left = self.leftover


    def __init__(self, order_list, goods_list):
        """根据订单列表初始化"""
        self.order_list = order_list
        self.goods_dict = goods_list
        self.item_dict = {}
        for commodity in goods_list:
            formitem = self.FormItem(commodity)
            self.item_dict[commodity] = formitem
        for order in order_list:
            for commodity in self.item_dict.keys():
                if commodity in order.goods_dict:
                    self.item_dict[commodity].add_order(order)
        for commodity in self.item_dict.keys():
            self.item_dict[commodity].judge_state()


class OrderMarginAdapter:
    """订单集中除余调整类"""
    def __init__(self, store_list):
        """调整类实例初始化方法"""
        self.store_list = store_list

    def commodity_dict_init(self, goods_list):
        """根据商品列表初始化字典
        :param goods_list: 商品实例的列表
        :return: 以商品为键，值为0的字典
        """
        goods_dict = {}
        for item in goods_list:
            goods_dict[item] = 0
        return goods_dict

    def adapt(self, order_list, goods_list):
        """根据每种物品的打包数量与阈值，调整各订单。
        :param order_list: 订单列表
        :param goods_list: 参与调整的商品列表
        :return: 返回调整后的订单列表
        """
        # 建表，将各个商品计总数，相关订单，取舍与差值计入表中
        # goods_dict 统计各物品总数
        form = Form(order_list, goods_list)
        for goods in goods_list:
            formitem = form.item_dict[goods]
            order_list.sort(key=lambda order: order.get_item(goods), reverse=formitem.flag)
            for order in order_list:
                if formitem.left == 0:
                    break
                # 调整量为当前余量乘以需要参与调整量占所有可参与调整量的百分比（向上取整）
                # 如当前订单余量为10，总可参与调整量为100，需要参与调整的数量为50。即每家调整一半。10 * （50 / 100） = 5。
                num = math.ceil(order.get_item(goods) * (formitem.leftover / formitem.felxnum))
                if num > formitem.left:
                    num = formitem.left
                # 由于会取整，所以通过left剩余需要调整的数量
                base = order.get_item(goods)
                if formitem.flag == True:
                    order.set_item(goods, base + num)
                else:
                    order.set_item(goods, base - num)
                formitem.left -= num
        print("yes")
        return order_list


def print_order(order:Order):
    """用于格式化打印订单，方便观察"""
    print("=================================================")
    print(f"order info: id => {order.id}")
    print(f"order info: owner => {order.owner}")
    print(f"order info: initial_time => {order.initial_time}")
    for item in order.goods_dict:
        print(f"item info: name => {item.name}")
        print(f"item info: num => {order.goods_dict[item]}")
    print("=================================================")

def init_store_list(list):
    """通过字符串列表生成商家实例列表"""
    store_list = []
    for name in list:
        store_list.append(Store(name))
    return store_list

def init_goods_list(list):
    """通过字符串列表生成商品实例列表"""
    good_list = []
    for name in list:
        good_list.append(Commodity(name[0], name[1], name[2]))
    return good_list

def result_check(list):
    """结果校验"""
    print("Info: result check.")
    flag = True
    result = {}
    for order in list:
        for key in order.goods_dict:
            if key not in result:
                result[key] = order.get_item(key)
            else:
                result[key] += order.get_item(key)
    for key in result:
        num = result[key]
        print(f"result info: {key.name} : {num}")
        if num % key.packet != 0:
            print("########Error here!!!########")
            flag = False
        else:
            print("pass")
    if flag:
        print("Info: result check pass.")
    else:
        print("Info: result check failed.")



if __name__ == '__main__':
    """简单测试用例"""
    name_list = ["taobao", "tianmao", "jingdong", "pinduoduo", "dewu"]
    store_list = init_store_list(name_list)
    name_list = [["apple", 10, 20], ["banana", 20, 50], ["orange", 50, 103], ["phone", 5, 10], ["car", 1, 1]]
    goods_list = init_goods_list(name_list)
    order_list = []
    supply = SupplySystem()
    adapter = OrderMarginAdapter(store_list)

    for item in goods_list:
        supply.add_commodity(item)
    for store in store_list:
        store.create_container_random(supply)
        order = store.create_order()
        order_list.append(order)
    order_list.sort(key=lambda order:order.id)
    for order in order_list:
        print_order(order)
    new_order_list = adapter.adapt(order_list, goods_list)
    new_order_list.sort(key=lambda order: order.id)
    for order in new_order_list:
        print_order(order)
    result_check(new_order_list)


