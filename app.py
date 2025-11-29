from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from database import DBhandler
import hashlib
import math
import sys
import os

application = Flask(__name__)
application.config["SECRET_KEY"] = "helloosp"

DB = DBhandler()

@application.route("/")
def hello():
    hot_items = DB.get_hot_items(limit=3)
    return render_template("0_main.html", hot_items=hot_items)

# list 화면 구현
@application.route("/list")
def view_list():
    # 1. 페이지 정보 가져오기 (기본값 0)
    page = request.args.get("page", 0, type=int)
    per_page = 8  # 한 페이지당 8개
    per_row = 4   # 한 줄당 4개

    # 2. 전체 데이터 가져오기
    all_data = DB.get_items() 
    item_counts = len(all_data)
    
    # 3. 전체 페이지 수 계산 (math.ceil 사용하여 올림 처리)
    # 예: 9개 아이템이면 2페이지가 되어야 함 (9/8 = 1.125 -> 2)
    page_count = math.ceil(item_counts / per_page)

    # 4. 현재 페이지에 보여줄 데이터만 자르기 (Slicing)
    start_idx = per_page * page
    end_idx = per_page * (page + 1)
    
    # 딕셔너리를 리스트로 변환 후 슬라이싱하고 다시 딕셔너리로 변환
    # (데이터가 없으면 빈 딕셔너리가 됩니다)
    current_page_data = dict(list(all_data.items())[start_idx:end_idx])

    # 5. row1(첫째 줄), row2(둘째 줄) 데이터 나누기
    # current_page_data에서 앞 4개는 row1, 뒤 4개는 row2
    current_items = list(current_page_data.items())
    
    row1 = current_items[:per_row]        # 0번부터 3번까지
    row2 = current_items[per_row:]        # 4번부터 끝까지

    # 6. 템플릿 렌더링
    return render_template(
        "2_list.html",
        total=item_counts,
        page=page,
        page_count=page_count,
        row1=row1,
        row2=row2
    )

@application.route("/view_detail/<name>/")
def view_item_detail(name):
  print("###name:",name)
  data = DB.get_item_byname(str(name))
  print("####data:",data)
  return render_template("3_detail.html", name=name, data=data)

# review
@application.route("/review")
def view_review():
  page = request.args.get("page", 0, type=int)
  per_page = 6  # 한 페이지에 6개 (3개 x 2줄)
  per_row = 3   # 한 줄에 3개
  row_count=int(per_page/per_row)
  start_idx=per_page*page
  end_idx=per_page*(page+1)
  
  data = DB.get_reviews() #read the table
  if data is None:
        data = {}

  item_counts = len(data)
  data = dict(list(data.items())[start_idx:end_idx])
  tot_count = len(data)

  rows = {}

  for i in range(row_count): #last row
    if (i == row_count-1) and (tot_count%per_row != 0):
      rows[f'data_{i}'] = dict(list(data.items())[i*per_row:])
    else:
      rows[f'data_{i}'] = dict(list(data.items())[i*per_row:(i+1)*per_row])
  return render_template("5_review.html",
  datas=data.items(),
  row1=rows.get('data_0', {}).items(),
  row2=rows.get('data_1', {}).items(),
  limit=per_page,
  page=page,
  page_count=int((item_counts/per_page)+1),
  total=item_counts)

@application.route("/view_review_detail/<name>/")
def view_review_detail(name):
  print("###review_name:", name)
  data = DB.get_review_byname(str(name)) 
  print("####review_data:", data)
  return render_template("6_review_detail.html", name=name, data=data)

@application.route("/reg_review_init/<name>/")
def reg_review_init(name):
  return render_template("4_reg_reviews.html", name=name)

@application.route("/reg_review", methods=['POST'])
def reg_review():
  data=request.form
  image_file=request.files["file"]
  if image_file.filename != '':
    filename = image_file.filename
    save_path = os.path.join(application.root_path, 'static/images', filename)
    image_file.save(save_path)
  else:
    filename = None
  DB.reg_review(data, filename)
  return redirect(url_for('view_review'))


# 좋아요 기능
@application.route('/show_heart/<name>/', methods=['GET'])
def show_heart(name):
  my_heart = DB.get_heart_byname(session['id'], name)
  return jsonify({'my_heart': my_heart})

@application.route('/like/<name>/', methods=['POST'])
def like(name):
  my_heart = DB.update_heart(session['id'], 'Y', name)
  return jsonify({'msg' : '좋아요 완료'})

@application.route('/unlike/<name>/', methods=['POST'])
def unlike(name):
  my_heart = DB.update_heart(session['id'], 'N', name)
  return jsonify({'msg' : '안좋아요 완료'})


# reg_items
@application.route("/reg_items")
def reg_item():
  return render_template("1_reg_items.html")




# login
@application.route("/login")
def login():
  return render_template("8_login.html")

@application.route("/login_confirm", methods=['POST'])
def login_user():
  id_=request.form['id']
  pw=request.form['pw']
  pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
  if DB.find_user(id_,pw_hash):
    session['id']=id_
    user_info = DB.get_user(id_) 
    if user_info and 'nickname' in user_info:
      session['nickname'] = user_info['nickname']
    else:
      session['nickname'] = id_
    return redirect(url_for('hello'))
  else:
    flash("Wrong ID or PW!")
    return render_template("8_login.html")


# signup
@application.route("/signup")
def signup():
  return render_template("7_signup.html")

@application.route("/signup_post", methods=['POST'])
def register_user():
  data=request.form
  pw=request.form['pw']
  pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
  if DB.insert_user(data,pw_hash):
    return render_template("8_login.html")
  else:
    flash("user id already exist!")
    return render_template("7_signup.html")
  
@application.route("/logout")
def logout_user():
  session.clear()
  return redirect(url_for('hello'))

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
  DB.insert_item(data['name'],data,image_file.filename)

  return render_template("submit_item_result.html", data=data, img_path="static/images/{}".format(image_file.filename))

if __name__ == "__main__":
  application.run(host='0.0.0.0', debug=True)