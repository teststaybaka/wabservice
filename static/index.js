window.onload = function(){
    var btn = document.getElementById("search-button");
    btn.addEventListener("click", function(){
        var keyword = document.getElementById("search-field").value;
        url = "?keyword=" + keyword;
        window.location = url;
    });
};