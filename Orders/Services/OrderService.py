from Models.Order import Order
from Models.Event import Event
from Config.db import db
from Messages.publish import publish
from Commands.CheckProductQuantity import CheckProductQuantity
from Commands.CheckUserBalance import CheckUserBalance
from Commands.RollBackOrderFromProduct import RollBackOrderFromProduct
import json


OrderStatus = {
    "AWAIT_PRODUCT_QUANTITY_CHECK" : "AWAIT_PRODUCT_QUANTITY_CHECK", 
    "AWAIT_USER_BALANCE_CHECK" : "AWAIT_USER_BALANCE_CHECK", 
    "REJECTED_PRODUCT_CANNOT_ACCEPT" : "REJECTED_PRODUCT_CANNOT_ACCEPT", 
    "REJECTED_USER_CANNOT_ACCEPT" : "REJECTED_USER_CANNOT_ACCEPT", 
    "ACCEPTED" : "ACCEPTED"    
}
    


class OrderService:
    def createOrder(self , productId , userId , quantity ):
        order = Order(
            userId= userId,
            productId= productId,
            totalQuantity= quantity ,
            status= OrderStatus['AWAIT_PRODUCT_QUANTITY_CHECK']
        )
        db.session.add(order)
        db.session.commit()
        command = CheckProductQuantity(order.id,order.productId,order.totalQuantity)
        publish('product/order_created' ,command.to_string())
        payload = {
            "userId": userId,
            "productId": productId,
            "totalQuantity": quantity ,
            "orderId": order.id,
        }
        self.saveEvent(payload, 'createOrder')
        return order

    def handleProductRejectOrder(self , payload):
        order = Order.query.get(payload['orderId'])
        order.status = OrderStatus['REJECTED_PRODUCT_CANNOT_ACCEPT']
        db.session.add(order)
        db.session.commit()
        self.saveEvent(payload , 'handleProductRejectOrder')


    def handleProductAccpetOrder(self, payload):
        order = Order.query.get(payload['orderId'])
        order.status = OrderStatus['AWAIT_USER_BALANCE_CHECK']
        order.totalPrice = payload['price']
        db.session.add(order)
        db.session.commit()        
        command = CheckUserBalance(order.id,order.userId,order.totalPrice)
        publish('user/order_created' ,command.to_string())
        self.saveEvent(payload , 'handleProductAccpetOrder')


    def handleUserRejectOrder(self , payload):
        print(payload, 'handleUserRejectOrder')
        order = Order.query.get(payload['orderId'])
        order.status = OrderStatus['REJECTED_USER_CANNOT_ACCEPT']
        db.session.add(order)
        db.session.commit()
        command = RollBackOrderFromProduct(order.id,order.productId,order.totalQuantity)
        publish('product/roll_back_order' ,command.to_string())
        self.saveEvent(payload , 'handleUserRejectOrder')


    def handleUserAccpetOrder(self, payload):
        print(payload , 'handleUserAccpetOrder')
        order = Order.query.get(payload['orderId'])
        order.status = OrderStatus['ACCEPTED']
        db.session.add(order)
        db.session.commit()
        self.saveEvent(payload , 'handleUserAccpetOrder')


    def saveEvent(self, payload , type):
        event = Event(
        type = type,
        orderId = payload['orderId'],
        payload = json.dumps(payload)
        )
        db.session.add(event)
        db.session.commit() 


