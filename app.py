"""Flask app for Cupcakes"""
from flask import Flask, render_template, jsonify, request
from models import connect_db, db, Cupcake

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/cupcakes'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "oh-so-secret"

with app.app_context():
    connect_db(app)
    db.create_all()


@app.route('/')
def home_page():
    return render_template('index.html')


@app.route('/api/cupcakes')
def get_all_cupcakes():
    cupcakes = Cupcake.query.all()
    cupcakes = [cupcake.serialize() for cupcake in cupcakes]
    return jsonify({"cupcakes": cupcakes}), 200


@app.route('/api/cupcakes/<int:cupcake_id>')
def get_cupcake(cupcake_id):
    cupcake = Cupcake.query.get_or_404(cupcake_id)
    return jsonify({"cupcake": cupcake.serialize()}), 200


@app.route('/api/cupcakes', methods=['POST'])
def create_cupcake():
    data = request.json
    try:
        new_cupcake = Cupcake(flavor=data['flavor'], size=data['size'], rating=data['rating'], image=data.get('image'))
    except KeyError:
        return jsonify({
            "error": "Bad request",
            "message": "Missing required field(s)"
        }), 400

    db.session.add(new_cupcake)
    db.session.commit()

    return jsonify({"cupcake": new_cupcake.serialize()}), 201


@app.route('/api/cupcakes/<int:cupcake_id>', methods=['PATCH'])
def update_cupcake(cupcake_id):
    cupcake = Cupcake.query.get_or_404(cupcake_id)
    data = request.json

    if not data:
        return jsonify({
            "error": "Bad request",
            "message": "Missing required field(s)"
        }), 400

    flavor = data.get('flavor')
    size = data.get('size')
    rating = data.get('rating')
    image = data.get('image')

    if not flavor and not size and not rating and not image:
        return jsonify({
            "error": "Bad request",
            "message": "At least one field must be provided to update"
        }), 400

    if flavor:
        cupcake.flavor = flavor
    if size:
        cupcake.size = size
    if rating:
        cupcake.rating = rating
    if image:
        cupcake.image = image

    db.session.commit()
    return jsonify({"cupcake": cupcake.serialize()}), 200


@app.route("/api/cupcakes/<int:cupcake_id>", methods=["DELETE"])
def remove_cupcake(cupcake_id):
    cupcake = Cupcake.query.get_or_404(cupcake_id)

    db.session.delete(cupcake)
    db.session.commit()

    return jsonify({
        "acknowledged": True,
        "message": "Deleted"
    }), 200
