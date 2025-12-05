function purchaseItem(name, price) {
    // 1. 확인 창 띄우기
    if (confirm("'" + name + "' 상품을 결제하시겠습니까?")) {
        // 2. '예'를 누르면 서버로 구매 요청
        $.ajax({
            type: "POST",
            url: "/buy_item",
            data: { 
                name: name, 
                price: price 
            },
            success: function(response) {
                // 3. 성공 메시지 띄우기
                alert(response.msg);
                // 필요하다면 결제 내역 페이지로 이동
                // window.location.href = "/payment_history"; 
            },
            error: function() {
                alert("로그인이 필요하거나 오류가 발생했습니다.");
                window.location.href = "/login";
            }
        });
    } else {
        // '아니오'를 누르면 아무 일도 일어나지 않음
    }
}