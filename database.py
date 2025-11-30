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
            "nickname": data.get('nickname', None),
            "email": data.get('email', None),  # [추가됨] 이메일 저장
            "phone": data.get('phone', None)   # [추가됨] 전화번호 저장
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
        users = self.db.child("user").get()
        
        # 데이터가 아예 없으면 None 반환
        if users.val() is None:
            return None

        for res in users.each():
            value = res.val()
            
            # [수정된 부분] 
            # value['id'] 대신 value.get('id')를 사용합니다.
            # 데이터에 'id'가 없으면 에러 대신 None을 반환하여 안전하게 넘어갑니다.
            if value.get('id') == id_:
                return value
                
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
    
    def get_hot_items(self, limit=3):

        items = self.get_items()  
        if not items:
            return []


        hearts = self.db.child("heart").get().val() or {}


        like_counts = {name: 0 for name in items.keys()}

        for user_id, user_hearts in hearts.items():
            if not user_hearts:
                continue
            for item_name, heart_info in user_hearts.items():
                if heart_info.get('interested') == 'Y' and item_name in like_counts:
                    like_counts[item_name] += 1


        hot_list = []
        for name, info in items.items():
            data = info.copy()
            data['name'] = name   
            data['like_count'] = like_counts.get(name, 0)
            hot_list.append(data)


        hot_list.sort(key=lambda x: x['like_count'], reverse=True)
        return hot_list[:limit]