from flask import Flask, render_template, request
import sys

application = Flask(__name__)

@application.route("/")
def hello():
  return  render_template("index.html")
@application.route("/list")
def view_list():
  return render_template("list.html")
@application.route("/review")
def view_review():
  return render_template("review.html")
@application.route("/reg_items")
def reg_item():
  return render_template("reg_items.html")
@application.route("/reg_reviews")
def reg_review():
  return render_template("reg_reviews.html")

# GET 방식: 터미널과 주소에 모든 특징이 표현되나 이러한 이유로 파라미터 길이에 제한 O
@application.route("/submit_item")
def reg_item_submit():
  name=request.args.get("name")
  seller=request.args.get("seller")
  addr=request.args.get("addr")
  email=request.args.get("email")
  category=request.args.get("category")
  card=request.args.get("card")
  status=request.args.get("status")
  phone=request.args.get("phone")

  print(name,seller,addr,email,category,card,status,phone)
  #return render_template("reg_item.html")

# POST 방식
@application.route("/submit_item_post", methods=['POST'])
def reg_item_submit_post():
  image_file=request.files["file"]
  image_file.save("static/images/{}".format(image_file.filename))
  data=request.form
  return render_template("submit_item_result.html", data=data, img_path="static/images/{}".format(image_file.filename))

if __name__ == "__main__":
  application.run(host='0.0.0.0', debug=True)