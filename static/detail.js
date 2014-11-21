function getAction() {
    var url = window.location.href + "/getUploadURL"
    //1.创建XMLHttpRequest组建  
    xmlHttpRequest = createXmlHttpRequest();  
    //2.设置回调函数  
    xmlHttpRequest.onreadystatechange = uploadingFile;  
    //3.初始化XMLHttpRequest组建  
    xmlHttpRequest.open("GET", url, false);  
    //4.发送请求  
    xmlHttpRequest.send(null);
}


function uploadingFile() {
    if(xmlHttpRequest.readyState == 4 && xmlHttpRequest.status == 200){  
        var result = xmlHttpRequest.responseText;
        console.log(result);
        var myForm = document.getElementById('upload-form');
        myForm.setAttribute('action', result);
        myForm.submit()
    }
}

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

    var button = document.getElementById('submit-button')
    button.addEventListener('click', getAction);
};
