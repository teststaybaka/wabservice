//do not use this script!!!!

var xmlHttpRequest;

function createXmlHttpRequest(){  
  if(window.ActiveXObject){ //如果是IE浏览器  
      return new ActiveXObject("Microsoft.XMLHTTP");  
  }
  else if(window.XMLHttpRequest){ //非IE浏览器  
      return new XMLHttpRequest();  
  }
}

function handleIpResponse() {
    if(xmlHttpRequest.readyState == 4 && xmlHttpRequest.status == 200){  
        var result = xmlHttpRequest.responseText;
        console.log(result);
    } 
}

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