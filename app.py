from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    Response,
    jsonify,
    make_response,
)
#import pymysql
#from flask_restful import Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields
from marshmallow_sqlalchemy import ModelSchema

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost:3306/contact"
db = SQLAlchemy(app)


class Contact(db.Model):
    _tablename_ = "contact"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    email = db.Column(db.String(100))
    phno = db.Column(db.String(10))

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def _init_(self, name, email, phno):
        self.name = name
        self.email = email
        self.phno = phno


db.create_all()


class ContactSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Contact
        sqla_session = db.session

    id = fields.Number(dump_only=True)
    name = fields.String(required=True)
    email = fields.String(required=True)
    phno = fields.String(required=True)


@app.route("/api/contact", methods=["GET"])
def index():
    of = request.args.get("offset")
    li = request.args.get("limit")
    get_contact = Contact.query.offset(of).limit(li).all()
    contact_schema = ContactSchema(many=True)
    contacts = contact_schema.dump(get_contact)
    print(contacts[0]["id"])
    return make_response(jsonify({"contact": contacts}))


@app.route("/api/contact", methods=["POST"])
def create_contact():
    data = request.get_json()
    contact_schema = ContactSchema()
    contact = contact_schema.load(data)
    result = contact_schema.dump(contact.create())
    return make_response(jsonify({"Contact": result}), 200)


@app.route("/api/contact/search/<id>", methods=["GET"])
def get_contact_by_name(id):
    get_contact = Contact.query.get(id)
    contact_schema = ContactSchema()
    contact = contact_schema.dump(get_contact)
    return make_response(jsonify({"contact": contact}))


@app.route("/api/contact/<id>", methods=["PUT"])
def update_contact_by_id(id):
    data = request.get_json()
    get_Contact = Contact.query.get(id)
    if data.get("name"):
        get_Contact.name = data["name"]
    if data.get("email"):
        get_Contact.email = data["email"]
    if data.get("phno"):
        get_Contact.phno = data["phno"]
    db.session.add(get_Contact)
    db.session.commit()
    contact_schema = ContactSchema(only=["id", "name", "email", "phno"])
    contacts = contact_schema.dump(get_Contact)
    return make_response(jsonify({"contact": contacts}))


@app.route("/api/contact/<id>", methods=["DELETE"])
def delete_contact_by_id(id):
    get_contact = Contact.query.get(id)
    db.session.delete(get_contact)
    db.session.commit()
    return make_response("", 204)


if __name__ == "__main__":
    app.run(debug=True)