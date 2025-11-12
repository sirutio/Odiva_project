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
            "seller": data.get('sID'),
            "addr": data.get('addr'),
            "email": data.get('email'),
            "category": data.get('category'),
            "card": data.get('creditcard'),
            "status": data.get('status'),
            "phone": data.get('phone'),
            "price": data.get('price'),
            "description": data.get('description'),
            "img_path": img_path,
            "iname": data.get('iname')
        }

        self.db.child("item").child(name).set(item_info)

        print("Firebase 저장 완료:", item_info)
        return True

    def insert_user(self, userid_or_data, pw=None):
        
        if isinstance(userid_or_data, dict):
            user_data = userid_or_data
            userid = str(user_data.get('userid') or user_data.get('id'))
            pw_val = user_data.get('pw_hash') or user_data.get('pw') or pw
            payload = {
                "userid": userid,
                "pw_hash": pw_val,
                "name": user_data.get('name'),
                "email": user_data.get('email'),
                "phone": user_data.get('phone')
            }
          
            self.db.child("user").push(payload)
            return True

        userid = str(userid_or_data)
        payload = {"userid": userid, "pw": pw}
        self.db.child("user").push(payload)
        return True

    def user_duplicate_check(self, id_string):
        users = self.db.child("user").get()
        if users.val() is None:
            return True
        if users.each() is None:
            return True
        for res in users.each():
            value = res.val()
            if isinstance(value, dict):
                if value.get('id') == id_string or value.get('userid') == id_string:
                    return False
        return True

    def find_userID(self, userid):
        users = self.db.child("user").get()
        if users.val() is None:
            return False
        if users.each() is None:
            return False
        for res in users.each():
            value = res.val()
            if isinstance(value, dict):
                if value.get('id') == userid or value.get('userid') == userid:
                    return True
        return False
    
    def find_user(self,id_,pw_):
        users = self.db.child("user").get()
        if not users.each():
            return False

        for res in users.each():
            value=res.val()

            userid = value.get('userid') or value.get('id')
            pwh = value.get('pw_hash') or value.get('pw')
            if userid == id_ and pwh == pw_:
                return True
            
        return False
                
