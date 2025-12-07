import pyrebase
import json
from datetime import datetime

class DBhandler:
    def __init__(self):
        with open('./authentication/firebase_auth.json', 'r', encoding='utf-8') as f:
            config = json.load(f)

        firebase = pyrebase.initialize_app(config)
        self.db = firebase.database()

    # ✅ 상품 등록 (price, reg_date 추가 반영)
    def insert_item(self, name, data, img_path):
        item_info = {
            "seller": data.get('seller'),
            "addr": data.get('addr'),
            "email": data.get('email'),
            "category": data.get('category'),
            "card": data.get('card'),
            "status": data.get('status'),
            "phone": data.get('phone'),
            "img_path": img_path,
            "price": data.get("price"),
            "reg_date": datetime.now().timestamp()   # ✅ 등록시간 추가
        }

        self.db.child("item").child(name).set(item_info)
        print(data, img_path)
        return True

    # ✅ 회원가입 (email, phone 포함)
    def insert_user(self, data, pw):
        user_info = {
            "id": data.get('id'),
            "pw": pw,
            "nickname": data.get('nickname'),
            "email": data.get('email'),
            "phone": data.get('phone')
        }

        if self.user_duplicate_check(str(data['id'])):
            self.db.child("user").push(user_info)
            print(data)
            return True
        else:
            return False

    # ✅ 중복확인 버그 수정 (기존엔 마지막 유저만 검사했던 문제)
    def user_duplicate_check(self, id_string):
        users = self.db.child("user").get()

        if users.val() is None:  # 첫 가입자
            return True

        for res in users.each():
            value = res.val()
            if value.get('id') == id_string:
                return False

        return True

    # ✅ 로그인 검증
    def find_user(self, id_, pw_):
        users = self.db.child("user").get()

        if users.val() is None:
            return False

        for res in users.each():
            value = res.val()
            if value.get('id') == id_ and value.get('pw') == pw_:
                return True
        
        return False

    # ✅ 특정 사용자 정보 가져오기
    def get_user(self, id_):
        users = self.db.child("user").get()

        if users.val() is None:
            return None

        for res in users.each():
            value = res.val()
            if value.get('id') == id_:
                return value

        return None

    # ✅ 전체 상품 조회
    def get_items(self):
        items = self.db.child("item").get().val()
        return items if items else {}

    # ✅ 상품 하나 조회
    def get_item_byname(self, name):
        items = self.db.child("item").get()
        target_value = ""

        for res in items.each():
            if res.key() == name:
                target_value = res.val()
        return target_value

    # ✅ 리뷰 등록
    def reg_review(self, data, img_path):
        category = self.get_item_category(data['name'])

        review_info = {
            "item_name": data['name'],
            "title": data['title'],
            "rate": data['reviewStar'],
            "review": data['reviewContents'],
            "img_path": img_path,
            "category": category
        }
        self.db.child("review").push(review_info)
        return True
    #리뷰 등록 시 상품 category를 DB에서 꺼내오기

    def get_item_category(self, item_name):
        item=self.db.child("item").child(item_name).get()
        if item.val():
            return item.val().get("category")
        return None

    # ✅ 리뷰 전체 조회
    def get_reviews(self):
        return self.db.child("review").get().val()

    # ✅ 특정 리뷰 조회
    def get_review_byname(self, name):
        return self.db.child("review").child(name).get().val()

    # ✅ 찜 조회
    def get_heart_byname(self, uid, name):
        hearts = self.db.child("heart").child(uid).get()
        target_value = ""

        if hearts.val() is None:
            return target_value

        for res in hearts.each():
            if res.key() == name:
                target_value = res.val()

        return target_value

    # ✅ 찜 업데이트
    def update_heart(self, user_id, isHeart, item):
        heart_info = {"interested": isHeart}
        self.db.child("heart").child(user_id).child(item).set(heart_info)
        return True

    # ✅ 인기 상품 조회 (좋아요 순)
    def get_hot_items(self, limit=3):
        items = self.get_items()
        if not items:
            return []

        hearts = self.db.child("heart").get().val() or {}

        like_counts = {name: 0 for name in items.keys()}

        for user_hearts in hearts.values():
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

    # ======================= [추가] 좋아요한 상품 목록 조회 =======================
    def get_liked_items(self, user_id):
        hearts = self.db.child("heart").child(user_id).get().val()
        if not hearts:
            return {}

        liked_items = {}
        items = self.get_items()  # 전체 상품 로드

        for item_name, info in hearts.items():
            if info.get("interested") == "Y" and item_name in items:
                liked_items[item_name] = items[item_name]

        return liked_items
    
    def get_items_by_seller(self, seller_id):
        items = self.db.child("item").get()
        target_value = {}
        
        if items.val():
            for res in items.each():
                value = res.val()

                if value.get('seller') == seller_id:
                    target_value[res.key()] = value
                    
        return target_value
    
    # ... (기존 코드들) ...

    # ======================= [추가] 구매(Order) 관련 메서드 =======================

    # 1. 구매 내역 저장 (user_id 하위에 저장)
    def insert_order(self, user_id, name, price):
        order_info = {
            "name": name,
            "price": price,
            "date": datetime.now().timestamp()
        }
        # users -> user_id -> orders -> (random_key) -> order_info 구조로 저장
        self.db.child("orders").child(user_id).push(order_info)
        return True

    # 2. 특정 사용자의 구매 내역 조회
    def get_orders(self, user_id):
        orders = self.db.child("orders").child(user_id).get().val()
        # Firebase는 {key: {data}, ...} 형태로 반환하므로 값만 리스트로 변환하면 편함
        if orders:
            # 딕셔너리의 값들만 뽑아서 리스트로 반환 (날짜 역순 정렬 추천)
            order_list = list(orders.values())
            order_list.sort(key=lambda x: x['date'], reverse=True) # 최신순 정렬
            return order_list
        return []

    # 3. 구매 취소 (삭제)
    def cancel_order(self, user_id, item_name):
        orders = self.db.child("orders").child(user_id).get()
        
        if orders.val():
            for res in orders.each():
                # 이름이 같은 상품을 찾아서 삭제 (가장 먼저 발견된 것 하나만)
                if res.val().get('name') == item_name:
                    # 해당 키(key)를 찾아 제거
                    self.db.child("orders").child(user_id).child(res.key()).remove()
                    return True
        return False
