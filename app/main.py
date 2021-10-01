import os
from flask import Flask, jsonify, request, json
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import psycopg2

app = Flask(__name__)

uri = os.getenv("DATABASE_URL")  # or other relevant config var
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
# rest of connection code using the connection string `uri`

# conn = psycopg2.connect(DATABASE_URL, sslmode='require')
db = SQLAlchemy(app)

migrate = Migrate(app, db)


class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    price = db.Column(db.Float, db.CheckConstraint('price>0'))
    url = db.Column(db.String(), nullable=False)

    # order = db.relationship('Order', backref='user', lazy=True)

    def __repr__(self):
        return '<Product %r>' % self.name


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.String, primary_key=True)

    def __repr__(self):
        return '<User %r>' % self.id


class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product_count = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Order %r>' % self.name


db.create_all()


@app.route('/')
def index():
    return 'Hello'


# TODO add new user
@app.route('/user', methods=['POST'])
def add_user():
    if request.method == 'POST':
        user_data = request.get_json()
        check_user = User.query.get(user_data['id'])
        if check_user:
            return jsonify(
                {"message": 'user with an id ' \
                            '{0} has already found'.format(user_data['id'])
                 })
        else:
            try:
                user = User(id=user_data['id'])
                db.session.add(user)
                db.session.commit()

            except:
                return jsonify({'message': 'user not inserted'})

            db.session.close()
            return jsonify(user_data['id'])


# TODO get user by id
@app.route('/user/<string:id>')
def get_user(id):
    try:
        users = User.query.all()
        if users:
            for user in users:
                if user.id == id:
                    return jsonify({'user': str(user.id)})
                else:
                    return jsonify({'message': 'user with an id {0} not found'.format(id)})

    except:
        jsonify({'message': 'user not found'})


# GET all users
@app.route('/users')
def get_users():
    user_list = []
    try:
        users = User.query.all()
        if users:
            for u in users:
                user = {}
                user['id'] = u.id
                user_list.append(user)
            return jsonify({'users': user_list})
        else:
            return jsonify({'message': 'no users'})
    except:
        return jsonify({'message': 'error in fetching data'})


# DELETE user by ID
@app.route('/user/<string:id>', methods=['DELETE'])
def delete_user(id):
    try:
        user = User.query.filter_by(id=id)
        if user:
            db.session.delete(user)
            db.session.commit()

            return jsonify({'message': 'user with an id {0} has been deleted'.format(id)})
        else:
            return jsonify(
                {'message': 'user with an id {0} is not found'.format(id)})
    except:
        return jsonify({'message': 'error please try again'})


# TODO add new product
@app.route('/product', methods=['POST'])
def add_product():
    if request.method == 'POST':
        product_data = request.get_json()
        try:
            product = Product(
                name=product_data['name'],
                price=product_data['price'],
                url=product_data['url'])
            db.session.add(product)
            db.session.commit()
            db.session.close()
            return jsonify(product_data)
        except:
            return jsonify({'message': 'product not inserted'})


# TODO get product by id
@app.route('/product/<int:id>')
def get_product(id):
    try:
        products = Product.query.all()
        for p in products:
            if p.id == id:
                # it must be serilized
                return jsonify({'product': str(p.name)})
    except:
        return jsonify({'message': 'please try again'})

    return jsonify({'message': 'product with an id {0} not found'.format(id)})


# TODO get all product
@app.route('/products')
def get_all_products():
    product_list = []
    try:
        products = Product.query.all()
        if products:
            for p in products:
                product = {}
                product['id'] = p.id
                product['name'] = str(p.name)
                product['price'] = str(p.price)
                product['url'] = str(p.url)
                product_list.append(product)

            return jsonify({'products': product_list})
        else:
            return jsonify({'message': 'no products'})
    except:
        return jsonify({'message': 'error in fetching data'})


# TODO add new order
@app.route('/order', methods=['POST'])
def add_order():
    if request.method == 'POST':
        order_data = request.get_json()
        try:
            order = Order(
                user_id=order_data['user_id'],
                product_id=order_data['product_id'],
                product_count=order_data['product_count'])
            db.session.add(order)
            db.session.commit()

        except:
            return jsonify({'message': 'user not inserted'})

        return jsonify(order_data)


# TODO get all orders belong to user
@app.route('/orders/<string:id>')
def get_orders_user(id):
    orders = db.session.query(Order, Product.id, User.id).filter(Order.user_id == id) \
        .join(Product).all()
    order_list = []
    for o in orders:
        order = {}
        order['id'] = o.id
        order['user_id'] = o.user_id
        order['product_price'] = o.price
        order['product_id'] = str(o.product_id)
        order['product_count'] = str(o.product_count)

        order_list.append(order)
    return jsonify({'orders': order_list})


# TODO get all order
@app.route('/orders')
def get_orders():
    order_list = []
    try:
        orders = Order.query.all()
        if orders:
            for o in orders:
                order = {}
                order['id'] = o.id
                order['product_id'] = str(o.product_id)
                order['product_count'] = str(o.product_count)
                order_list.append(order)
            return jsonify({'orders': order_list})
        else:
            return jsonify({'message': 'no orders'})

    except:
        return jsonify({'message': 'error in fetching data try again'})
