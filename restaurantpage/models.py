from datetime import datetime
from restaurantpage import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id): #for the extention login_manager to know how to search a user
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(15), unique = True, nullable=False)
    password = db.Column(db.String(60), nullable = False)
    email = db.Column(db.String(120), unique = True, nullable=False)
    image_file = db.Column(db.String(22), nullable = True, default = 'user.png')
    
    restaurants = db.relationship('Restaurant', backref = 'owner', lazy = True)

    def __repr__(self):
        return f'(Username: {self.username}, Email: {self.email}, Image: {self.image_file})'

    @property
    def serialize(self):
        return{
            'id': self.id,
            'email': self.email
        }

class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(17), nullable = False,unique = True)
    image_file = db.Column(db.String(20), nullable = True, default = 'restaurant.png')
    type = db.Column(db.String(17), nullable = False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    menuitems = db.relationship('MenuItem', backref = 'restaurant', lazy = True)

    def __repr__(self):
        return f"(Name: {self.name}, Image = {self.image_file})"
    
    @property
    def serialize(self):
        return{
            'id': self.id,
            'name': self.name,
            'type': self.type
        }

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20), nullable = False)
    course = db.Column(db.String(120), nullable = False)
    description = db.Column(db.Text, nullable = False)
    price = db.Column(db.String(8), nullable = True, default = '0.00')
    image_file = db.Column(db.String(30), nullable = True, default = 'food.png')
    date_posted = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)

    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable = False)

    def __repr__(self):
        return f"(name: {self.name}, course:{self.course}, price: {self.price})"
    
    @property
    def serialize(self):
        return{
            'id': self.id,
            'name': self.name,
            'course': self.course, 
            'description': self.description,
            'price': self.price,
            'date_posted': self.date_posted,
            'restaurant_id': self.restaurant_id
        }
