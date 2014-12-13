$(document).ready(function(){
        $("#search-button").click(function(){
            keyword = $("#search-field").val();
            url = "?keyword=" + keyword;
            window.location = url;
        });

        $(".per-category").click(function(){
            url = "?now_category=" + $(this).text();
            window.location = url;
        });
    }
);