var MAX_LENGTH = 50;

function fill_notification_list_with_link(data) {
    var menu = document.getElementById("notification-menu");
    if (menu) {
        menu.innerHTML = "";
        for (var i=0; i < data.unread_list.length; i++) {
            var item = data.unread_list[i];
            var message = item.verb;
            if (message.length > MAX_LENGTH) {
            	message = message.substring(0, MAX_LENGTH) + "...";
            }
            var item_data = JSON.parse(item.data);
            var url_name = item_data['url_name']
            url = Urls[url_name]()
            menu.innerHTML = menu.innerHTML + "<li><a href='" + url +  "'>"+ message + "</a></li>";
        }
        menu.innerHTML = menu.innerHTML + "<li class=\"divider\"></li>";
        url = Urls['notifications:all']()
        menu.innerHTML = menu.innerHTML + "<li><a href='" + url +  "'>Notification center</a></li>";
    }
}