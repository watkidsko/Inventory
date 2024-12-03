from app import db
from datetime import datetime

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ebay_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(200), nullable=False)
    sku = db.Column(db.String(50), unique=True)
    quantity = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Product {self.name}>' 