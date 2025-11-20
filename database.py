import pyrebase
import json

class DBhandler:
    def __init__(self):
        with open('./authentication/firebase_auth.json', 'r', encoding='utf-8') as f:
            config = json.load(f)

        firebase = pyrebase.initialize_app(config)
        self.db = firebase.database()

    def insert_item(self, name, data, img_path):
        item_info = {
            "seller": data.get('seller'),
            "addr": data.get('addr'),
            "email": data.get('email'),
            "category": data.get('category'),
            "card": data.get('card'),
            "status": data.get('status'),
            "phone": data.get('phone'),
            "img_path": img_path
        }

        self.db.child("item").child(name).set(item_info)
        print(data,img_path)
        return True
    
    def insert_user(self, data, pw):
        user_info ={
            "id": data.get('id', None),
            "pw": pw,
            "nickname": data.get('nickname', None)
        }
        if self.user_duplicate_check(str(data['id'])):
            self.db.child("user").push(user_info)   
            print(data)
            return True
        else:
            return False

    def user_duplicate_check(self, id_string):
        users = self.db.child("user").get()

        print("users###",users.val())
        if str(users.val()) == "None": # first registration
            return True
        else:
            for res in users.each():
                value = res.val()

            if value.get('id') == id_string:
                return False
        return True
    
    def find_user(self, id_, pw_):
        users = self.db.child("user").get()
        target_value=[]
        for res in users.each():
            value = res.val()

        if value['id'] == id_ and value['pw'] == pw_:
            return True
        
        return False
    
    # database.py의 DBhandler 클래스 안에 추가해주세요!
    
    def get_user(self, id_):
        # 'user' 테이블의 모든 데이터를 가져옴
        users = self.db.child("user").get()
        
        # 데이터베이스에 사용자가 아무도 없을 경우 처리
        if users.val() is None:
            return None

        # 반복문을 돌면서 아이디가 일치하는 사용자 정보를 찾음
        for user in users.each():
            if user.key() == id_:
                return user.val()
                
        return None
    
    def get_items(self):
        items = self.db.child("item").get().val()
        return items if items else {} # 오류 방지 위해 items가 None이면 {} 반환하도록 함.

    def get_item_byname(self, name):
        items = self.db.child("item").get()
        target_value=""
        print("###########",name)
        for res in items.each():
            key_value = res.key()
            if key_value == name:
                target_value=res.val()
        return target_value
    
    def reg_review(self, data, img_path):
        review_info ={
        "item_name": data['name'],
        "title": data['title'],
        "rate": data['reviewStar'],
        "review": data['reviewContents'],
        "img_path": img_path
        }
        self.db.child("review").push(review_info)
        return True
    
    def get_reviews(self):
        reviews = self.db.child("review").get().val()
        return reviews
    
    def get_review_byname(self, name):
        data = self.db.child("review").child(name).get().val()
        return data
    
    def get_heart_byname(self, uid, name):
        hearts = self.db.child("heart").child(uid).get()
        target_value = ""
        if hearts.val() == None:
            return target_value
        
        for res in hearts.each():
            key_value = res.key()
            
            if key_value == name:
                target_value = res.val()
        return target_value
    
    def update_heart(self, user_id, isHeart, item):
        heart_info = {"interested" : isHeart}
        self.db.child("heart").child(user_id).child(item).set(heart_info)
        return True
    