function csrf_token() {
    var name = "csrftoken=";
    var ca = document.cookie.split(';');
    for(var i=0; i<ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1);
        if (c.indexOf(name) != -1) return c.substring(name.length,c.length);
    }
    return "";
}

function shake_cart() {
    $("#shopping_cart_icon").attr("class", "am-icon-shopping-cart am-animation-shake");
    setTimeout(function () {
        $("#shopping_cart_icon").attr("class", "am-icon-shopping-cart");
    }, 300);
}


$.AMUI.FastClick.attach(document.body);