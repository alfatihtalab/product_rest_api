import os
from flask import Flask, jsonify, request, json
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# DATABASE_URL = 'postgres://gjdepasfdadwsx:021d923f60469ee2b08de7ad2ecdc0815065678941248c553a6aad1ba247efda@ec2-3-221-243-122.compute-1.amazonaws.com:5432/dduopruoikpg4a'
# engine = create_engine("sqlite+pysqlite:///:memory:", echo=True, future=True)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('postgres://avnadmin:UXnAnZSuFIBO3G3n@pg-products-alfatihtalab7-5e0e.aivencloud.com:26020/defaultdb?sslmode=require')
#postgresql://postgres:1993239@localhost:5432/markt_db

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


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
                {"message": 'user with an id '\
                            '{0} has already found'.format(user_data['id'])
                 })
        else:
            try:
                user = User(id=user_data['id'])
                db.session.add(user)
                db.session.commit()

            except:
                return jsonify({'message': 'user not inserted'})
            return jsonify(user_data['id'])


# TODO get user by id
@app.route('/user/<string:id>')
def get_user(id):
    users = User.query.all()
    for user in users:
        if user.id == id:
            # it must be serilized
            return jsonify({'user': str(user.id)})
    return jsonify({'message': 'user not found'})


# TODO add new product
@app.route('/product', methods=['post'])
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

        except:
            return jsonify({'message': 'user not inserted'})
        return jsonify(product_data)


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
    products = Product.query.all()
    product_list = []
    for p in products:
        product = {}
        product['id'] = p.id
        product['name'] = str(p.name)
        product['price'] = str(p.price)
        product['url'] = str(p.url)

        product_list.append(product)

    return jsonify({'products': product_list})


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
    orders = Order.query.filter_by(user_id = id)
    order_list = []
    for o in orders:
        order = {}
        order['id'] = o.id
        order['product_id'] = str(o.product_id)
        order['product_count'] = str(o.product_count)

        order_list.append(order)
    return jsonify({'orders': order_list})



# TODO get all order



