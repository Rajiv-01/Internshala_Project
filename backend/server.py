
from flask import Flask, jsonify, request, url_for, redirect, session
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import json


app = Flask(__name__)
app.secret_key = "super secret key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(32), index=True)
    last_name = db.Column(db.String(32), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    phone_number = db.Column(db.Integer, index=True)
    profession = db.Column(db.String(128), index=True)
    experience = db.Column(db.Integer, index=True)
    password_hash = db.Column(db.String(128))

    # def __init__(self, first_name, last_name, email, phone_number, profession, experience):
    #     self.first_name = first_name
    #     self.last_name = last_name
    #     self.email = email
    #     self.phone_number = phone_number
    #     self.profession = profession
    #     self.experience = experience

    def set_password(self, password):
        new_password = password[::-1]
        self.password_hash = new_password

    def check_password(self, password):
        if(len(self.password_hash) != len(password)):
            return False
        for i in range(len(self.password_hash)):
            if (chr(ord(password[i])+10) != self.password_hash[i]):
                return False
        return True


@app.route('/')
def home():
    return 'Done', 201


@app.route('/sign-up', methods=["POST", "GET"])
def signUp():
    if request.method == "POST":
        user_data = request.get_json()
        found_usr = User.query.filter_by(email=user_data['mail']).first()
        if found_usr:
            return redirect(url_for("signIn"))
        session['email'] = user_data['mail']

        user = User(first_name=user_data['fname'], last_name=user_data['lname'], phone_number=user_data['phone'],
                    email=user_data['mail'], profession=user_data['prof'], experience=user_data['experience'])
        user.set_password(user_data['pass'])
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("profile"))
    else:
        if "email" in session:
            return redirect(url_for("profile"))
        return 'Error', 404


@app.route('/sign-in', methods=['POST', 'GET'])
def signIn():
    if request.method == "POST":
        user_data = request.get_json()
        mail = user_data['mail']
        password = user_data['pass']
        session['email'] = mail
        found_user = User.query.filter_by(email=mail).first()
        if found_user:
            if(found_user.check_password(password)):
                return redirect(url_for("profile"))
            else:
                return 'Password Incorrect', 404
        return 'No User Found', 404
    else:
        if "email" in session:
            return redirect(url_for("profile"))
        return redirect(url_for("signUp"))


@app.route('/logout')
def logout():
    session.pop("email", None)

    return redirect(url_for("signIn"))


@app.route('/profile')
def profile():
    mail = session['email']
    if mail:
        user = User.query.filter_by(email=mail).first()
        data = []
        for query in user.query.all():
            data.append({"firstName": query.first_name, "lastName": query.last_name,
                        "phoneNumber": query.phone_number,  "profession": query.profession, "experience": query.experience, })
        return jsonify({"user": data})
    return redirect(url_for('signIn'))


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
