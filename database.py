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