//do not use this script!!!!

(function retrieve_content () {
    var now_url = location.href.split('/');
    console.log(now_url);
    console.log(now_url[now_url.length-1]);
    if (now_url[now_url.length-1] == 'history') {
        var i;
        var url = '';
        // for (i = 0; i < now_url.length-1; i++) {
        //     url += now_url[i]
        // }
        url += '/history_innerHTML';
        console.log(url);

        xmlHttpRequest = createXmlHttpRequest();
        xmlHttpRequest.onreadystatechange = handleIpResponse;
        xmlHttpRequest.open("GET", url, true);
        xmlHttpRequest.send(null);
    }
})();