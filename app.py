from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from database import DBhandler
from datetime import datetime
import hashlib
import math
import sys
import os

application = Flask(__name__)
application.config["SECRET_KEY"] = "helloosp"

DB = DBhandler()

# ======================= 메인 =======================
@application.route("/")
def hello():
    hot_items= DB.get_hot_items()
    return render_template("0_main.html", hot_items=hot_items)  # 수정 반영 ✅


# ======================= 상품 리스트 =======================
@application.route("/list")
def view_list():
    page = request.args.get("page", 0, type=int)
    sort = request.args.get("sort", "name")               # ✅ 추가
    category = request.args.get("category", "전체")      # ✅ 추가

    per_page = 8
    per_row = 4

    all_data = DB.get_items()
    if all_data is None:
        all_data = {}

    # ✅ 카테고리 필터
    if category != "전체":
        all_data = dict(filter(
            lambda x: x[1].get("category") == category,
            all_data.items()
        ))

    # ✅ 정렬
    items = list(all_data.items())

    if sort == "name":
        items.sort(key=lambda x: x[0])
    elif sort == "price":
        items.sort(key=lambda x: int(x[1].get("price", 0)))
    elif sort == "date":
        items.sort(key=lambda x: float(x[1].get("reg_date", 0)), reverse=True)

    item_counts = len(items)
    page_count = math.ceil(item_counts / per_page)

    start_idx = per_page * page
    end_idx = start_idx + per_page
    current_page_data = dict(items[start_idx:end_idx])

    current_items = list(current_page_data.items())
    row1 = current_items[:per_row]
    row2 = current_items[per_row:]

    return render_template(
        "2_list.html",
        total=item_counts,
        page=page,
        page_count=page_count,
        row1=row1,
        row2=row2,
        sort=sort,
        category=category
    )


# ======================= 상세 페이지 =======================
@application.route("/view_detail/<name>/")
def view_item_detail(name):
    data = DB.get_item_byname(str(name))
    return render_template("3_detail.html", name=name, data=data)


# ======================= 리뷰 =======================
@application.route("/review")
def view_review():
    page = request.args.get("page", 0, type=int)
    per_page = 6
    per_row = 3
    row_count = int(per_page / per_row)

    start_idx = per_page * page
    end_idx = per_page * (page + 1)

    data = DB.get_reviews()
    if data is None:
        data = {}

    item_counts = len(data)
    data = dict(list(data.items())[start_idx:end_idx])
    tot_count = len(data)

    rows = {}
    for i in range(row_count):
        if (i == row_count - 1) and (tot_count % per_row != 0):
            rows[f'data_{i}'] = dict(list(data.items())[i * per_row:])
        else:
            rows[f'data_{i}'] = dict(list(data.items())[i * per_row:(i + 1) * per_row])

    return render_template(
        "5_review.html",
        datas=data.items(),
        row1=rows.get('data_0', {}).items(),
        row2=rows.get('data_1', {}).items(),
        limit=per_page,
        page=page,
        page_count=int((item_counts / per_page) + 1),
        total=item_counts
    )


@application.route("/view_review_detail/<name>/")
def view_review_detail(name):
    data = DB.get_review_byname(str(name))
    return render_template("6_review_detail.html", name=name, data=data)


@application.route("/reg_review_init/<name>/")
def reg_review_init(name):
    return render_template("4_reg_reviews.html", name=name)


@application.route("/reg_review", methods=['POST'])
def reg_review():
    data = request.form
    image_file = request.files["file"]

    if image_file.filename != '':
        filename = image_file.filename
        save_path = os.path.join(application.root_path, 'static/images', filename)
        image_file.save(save_path)
    else:
        filename = None

    DB.reg_review(data, filename)
    return redirect(url_for('view_review'))


# ======================= 좋아요 =======================
@application.route('/show_heart/<name>/', methods=['GET'])
def show_heart(name):
    my_heart = DB.get_heart_byname(session['id'], name)
    return jsonify({'my_heart': my_heart})


@application.route('/like/<name>/', methods=['POST'])
def like(name):
    DB.update_heart(session['id'], 'Y', name)
    return jsonify({'msg': '좋아요 완료'})


@application.route('/unlike/<name>/', methods=['POST'])
def unlike(name):
    DB.update_heart(session['id'], 'N', name)
    return jsonify({'msg': '안좋아요 완료'})


# ======================= 상품 등록 =======================
@application.route("/reg_items")
def reg_item():
    return render_template("1_reg_items.html")


# ======================= 로그인 =======================
@application.route("/login")
def login():
    return render_template("8_login.html")


@application.route("/login_confirm", methods=['POST'])
def login_user():
    id_ = request.form['id']
    pw = request.form['pw']
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()

    if DB.find_user(id_, pw_hash):
        session['id'] = id_
        user_info = DB.get_user(id_)
        session['nickname'] = user_info.get('nickname', id_)
        return redirect(url_for('view_list'))   # ✅ 수정 반영
    else:
        flash("Wrong ID or PW!")
        return render_template("8_login.html")


# ======================= 회원가입 =======================
@application.route("/signup")
def signup():
    return render_template("7_signup.html")


@application.route("/signup_post", methods=['POST'])
def register_user():
    data = request.form
    pw = request.form['pw']
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()

    if DB.insert_user(data, pw_hash):
        return render_template("8_login.html")
    else:
        flash("user id already exist!")
        return render_template("7_signup.html")


@application.route("/logout")
def logout_user():
    session.clear()
    return redirect(url_for('view_list'))   # ✅ 수정 반영


# ======================= 상품 제출 =======================
@application.route("/submit_item")
def reg_item_submit():
    return "Not supported GET 방식"


@application.route("/submit_item_post", methods=["POST"])
def reg_item_submit_post():
    data = request.form.to_dict()
    image_file = request.files["file"]

    filename = image_file.filename
    image_file.save("static/images/{}".format(filename))

    data["image"] = filename
    data["price"] = int(data.get("price", 0))
    data["reg_date"] = datetime.now().timestamp()

    DB.insert_item(data["name"], data, filename)

    return render_template(
        "submit_item_result.html",
        data=data,
        img_path="static/images/{}".format(filename)
    )

@application.route("/mypage")
def mypage():
    return render_template("mypage.html")

# ======================= 실행 =======================
if __name__ == "__main__":
    application.run(host='0.0.0.0', debug=True)
