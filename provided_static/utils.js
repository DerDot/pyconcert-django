function desiredHeight() {
    var windowHeight = window.innerHeight || document.documentElement.clientHeight|| document.body.clientHeight;
    return windowHeight + 50;
}

function currentHeight() {
    var body = document.body;
    var html = document.documentElement;
    var height = Math.max(body.scrollHeight, body.offsetHeight,
                          html.clientHeight, html.scrollHeight,
                          html.offsetHeight);
    return height;
}

function addWhitespace() {
    var desired = desiredHeight();
    var current = currentHeight();
    if (desired > current) {
        var content_div = document.getElementById('content_div')
        content_div.setAttribute("style","height:" + desired + "px");
        content_div.style.height = desired + "px";
    }
}

function unique(arr) {
  return arr.filter(function(x, i) {
    return arr.indexOf(x) === i && x !== undefined
  })
}