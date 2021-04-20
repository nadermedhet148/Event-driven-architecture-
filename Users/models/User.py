from config.db import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=False, nullable=False)
    ordersCount = db.Column(db.Integer , default=0)
    cashBackBalance = db.Column(db.Integer,default=0)


    def toDict(self):
        return {
            "userId": self.id,
            "name" : self.name,
            "ordersCount" : self.ordersCount,
            "cashBackBalance" : self.cashBackBalance,
            }