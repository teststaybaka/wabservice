window.onload = function() {
    var now_url = location.href.split('/');
    var bar;
    if (now_url[now_url.length-1] == 'discussions') {
        bar = document.getElementById('discussions-bar');
    } else if (now_url[now_url.length-1] == 'completions') {
        bar = document.getElementById('completions-bar');
    } else {
        bar = document.getElementById('intro-bar');
    }
    bar.setAttribute('class', 'active bar');
};