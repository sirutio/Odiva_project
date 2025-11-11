import os
import hashlib
from flask import Flask, render_template, request, redirect, url_for, flash
from database import DBhandler
import sys

app = Flask(__name__)
app.config["SECRET_KEY"]="hellosp"

DB = DBhandler()

@app.route("/")
def hello():
  return render_template("index.html")
 

@app.route("/pg1_product_register")
def view_pg1_product_register():
  return render_template("pg1_product_register.html")

@app.route("/submit_product", methods=["POST"])
def submit_product():
    data = {
        'iname': request.form.get("iname"),
        'price': request.form.get("price"),
        'description': request.form.get("description"),
        'category': request.form.get("category"),
        'status': request.form.get("status"),
        'creditcard': request.form.get("creditcard"),
        'sID': request.form.get("sID"),
        'email': request.form.get("email"),
        'addr': request.form.get("addr"),
        'phone': request.form.get("phone")
    }
    image_file = request.files.get("file")
    img_path = None

    if image_file and image_file.filename != "":
        save_path = "static/images/"

        if not os.path.exists(save_path):
            os.makedirs(save_path)

        filename = image_file.filename
        image_file.save(os.path.join(save_path, filename))

        # 템플릿에서 사용할 이미지 경로
        data["image"]=filename
    else:
       data["image"]=None

    DB.insert_item(data['iname'], data, data['image'])

    return render_template("submit_item_result.html", data=data, img_path=data.get("image"))

@app.route("/pg2_상품전체조회화면")
def view_pg2_상품전체조회화면():
  return render_template("pg2_상품전체조회화면.html")

@app.route("/pg3_AboutProducts")
def view_pg3_AboutProducts():
  return render_template("pg3_AboutProducts.html")

@app.route("/pg4_register_review")
def view_pg4_register_review():
  return render_template("pg4_register_review.html")

@app.route("/pg5_상품리뷰전체조회화면")
def view_pg5_상품리뷰전체조회화면r():
  return render_template("pg5_상품리뷰전체조회화면.html")

@app.route("/pg6_AboutReviews")
def view_pg6_AboutReviews():
  return render_template("pg6_AboutReviews.html")

@app.route("/pg7_signin")
def view_pg7_signin():
  return render_template("pg7_signin.html")

@app.route("/pg8_login")
def view_pg8_login():
  return render_template("pg8_login.html")

@app.route("/login", methods=["POST"])
def login():
    userid = request.form.get("userid")
    pw = request.form.get("pw")
    return redirect(url_for("hello"))

@app.route("/signup", methods=["POST"])
def signup():
    name = request.form.get("name")
    userid = request.form.get("userid")
    pw = request.form.get("pw")
    email = request.form.get("email")
    phone = request.form.get("phone")

    print("회원가입 요청")
    print(name, userid, pw, email, phone)

    if DB.find_userID(userid):
        flash("이미 존재하는 아이디입니다. 다른 아이디를 사용해주세요.")
        return redirect(url_for("view_pg7_signin"))  

    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()

    user_data = {
        'name': name,
        'userid': userid,
        'pw_hash': pw_hash,
        'email': email,
        'phone': phone
    }

    DB.insert_user(user_data)

    flash("회원가입이 완료되었습니다. 로그인 해주세요.")
    return redirect(url_for("view_pg8_login"))


if __name__ == "__main__":
 app.run(host='0.0.0.0', debug=True)