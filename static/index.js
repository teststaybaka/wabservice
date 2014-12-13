/**
 * Insert a parameter into the URL and update the page. If the parameter
 * already exists, update it with the provided value.
 *
 * @param {string} key The name of the parameter to be inserted or updated.
 * @param {string} value The new value for the parameter..
 */
function insertParam(key, value){
    key = encodeURI(key);
    value = encodeURI(value);

    var kvp = document.location.search.substr(1).split('&');
    var i = kvp.length;
    var x;
    while(i--) {
        x = kvp[i].split('=');
        if (x[0] == key) {
            x[1] = value;
            kvp[i] = x.join('=');
            break;
        }
    }

    if(i < 0){
        kvp[kvp.length] = [key,value].join('=');
    }
    document.location.search = kvp.join('&');
}

$(document).ready(function(){
        $("#search-button").click(function(){
            keyword = $("#search-field").val();
            insertParam('keyword', keyword);
        });

        $(".per-category").click(function(){
            category = $(this).text();
            insertParam('now_category', category);
        });
    }
);