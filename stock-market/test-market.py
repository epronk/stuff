import unittest

class Order :
    def __init__(self, code, price, quantity):
        self.price = price
        self.quantity = quantity
        pass

class Trade :
    def __init__(self):
        pass

class OrderQueue :
    def __init__(self):
        self.levels = {}
        self.subscribers = []

    def add(self, order):
        if self.levels.has_key(order.price):
            level = self.queue[order.price]
        else:
            level = Level()
            self.levels[order.price] = level

            for subscriber in self.subscribers:
                subscriber.on_price_level_added(order.price)

        level.orders.append(order)
        #self.sell_queue.add(order)

    def remove(self, price, id):
        level = self.levels[price]
        for order in level.orders:
            if order.id == id:
                level.orders.remove(order)

        if len(level.orders) == 0:
            for subscriber in self.subscribers:
                subscriber.on_price_level_removed(order.price)

class BuyOrderQueue(OrderQueue) :
    def best_price(self):
        return self.levels.keys()[-1]
    def best_price_level(self):
        return self.levels[self.best_price()]

class SellOrderQueue(OrderQueue) :
    def best_price(self):
        return self.levels.keys()[0]
    def best_price_level(self):
        return self.levels[self.best_price()]

class Level :
    def __init__(self):
        self.orders = []

class Market :
    def __init__(self):
        self.order_id = 1;
        self.sell_queue = SellOrderQueue();
        self.buy_queue = BuyOrderQueue();
        self.trade_subscribers = []
        self.order_subscribers = []

    def new_sell_order(self, order):
        order.side = 'Sell'
        order.id = self.order_id
        self.order_id += 1
        for subscriber in self.order_subscribers:
            subscriber.on_order_added(order)
        self.sell_queue.add(order)
        self.match()

    def new_buy_order(self, order):
        order.side = 'Buy'
        order.id = self.order_id
        self.order_id += 1
        for subscriber in self.order_subscribers:
            subscriber.on_order_added(order)
        self.buy_queue.add(order)
        self.match()

    def reduce(self, order, quantity):
        order.quantity -= quantity
        if order.quantity == 0:
            for subscriber in self.order_subscribers:
                subscriber.on_order_removed(order)
        else:
            for subscriber in self.order_subscribers:
                subscriber.on_order_changed(order)

    def match(self):
        if self.buy_queue.levels and self.sell_queue.levels:
            trade = Trade()
            buy_order = self.buy_queue.best_price_level().orders[0]
            sell_order = self.sell_queue.best_price_level().orders[0]
            quantity=  min(sell_order.quantity, buy_order.quantity)
            if buy_order.price >= sell_order.price:
                self.reduce(buy_order, quantity)
                self.reduce(sell_order, quantity)
                for subscriber in self.trade_subscribers:
                    subscriber.on_trade(trade)

class Exchange :
    def __init__(self):
        self.market = Market()

    def login(self):
        return self

    def new_sell_order(self, order):
        return self.market.new_sell_order(order)

    def new_buy_order(self, order):
        return self.market.new_buy_order(order)


class Trades:
    def __init__(self):
        self.trades = []

    def on_trade(self, trade):
        self.trades.append(trade)

class Orders:
    def __init__(self):
        self.orders = []

    def on_order_added(self, order):
        print 'order added', order.__dict__

    def on_order_changed(self, order):
        print 'order changed', order.__dict__

    def on_order_removed(self, order):
        print 'order removed', order.__dict__

class Prices:
    def __init__(self):
        pass

    def on_price_level_added(self, price):
        print 'price level added : %s' % price

class TestOrderQueue(unittest.TestCase):
    def setUp(self):
        self.queue = BuyOrderQueue()
        self.queue.subscribers.append(self)

    def on_price_level_added(self, price) : pass
    def on_price_level_removed(self, price) : pass

    def testBest(self):
        order = Order(code='BHP', price=49, quantity=10)
        order.id = 5
        self.queue.add(order)
        self.queue.remove(order.price, 5)

class TestBidOrderQueue(unittest.TestCase):
    def setUp(self):
        self.queue = BuyOrderQueue()
        #self.queue.subscribers.append(self)

    def on_price_level_added(self, price):
        print price

    def testBest(self):
        order_id1 = self.queue.add(Order(code='BHP', price=49, quantity=10))
        order_id1 = self.queue.add(Order(code='BHP', price=48, quantity=10))
        self.assertEqual(self.queue.best_price(), 49)

class TestOfferOrderQueue(unittest.TestCase):
    def setUp(self):
        self.queue = SellOrderQueue()
        #self.queue.subscribers.append(self)

    def on_price_level_added(self, price):
        print price

    def testBest(self):
        order_id1 = self.queue.add(Order(code='BHP', price=52, quantity=10))
        order_id1 = self.queue.add(Order(code='BHP', price=51, quantity=10))
        self.assertEqual(self.queue.best_price(), 51)

class TestMarket(unittest.TestCase):
    
    #    self.assert_(element in self.seq)
    #    self.assertEqual(self.seq, range(10))

    def setUp(self):
        self.asx = Exchange()
        self.connection = self.asx.login()
        self.trades = Trades()
        self.orders = Orders()

        self.prices = Prices()
        #self.asx.market.price_subscribers.append(self.prices)
        #self.asx.market.order_subscribers.append(self.orders)
        self.asx.market.trade_subscribers.append(self.trades)

    def testNoMatch(self):
        order_id1 = self.connection.new_sell_order(Order(code='BHP', price=50, quantity=10))
        order_id2 = self.connection.new_buy_order(Order(code='BHP', price=49, quantity=5))
        self.assertEqual(len(self.trades.trades), 0)

    def testMatch(self):
        order_id1 = self.connection.new_sell_order(Order(code='BHP', price=50, quantity=10))
        order_id2 = self.connection.new_buy_order(Order(code='BHP', price=50, quantity=5))
        self.assertEqual(len(self.trades.trades), 1)

if __name__ == '__main__':
    unittest.main()
