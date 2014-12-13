function getAction() {
    var file = document.getElementById("file-input").files[0];
    if (file) {
        var url = window.location.href + "/getUploadURL"
        xmlHttpRequest = createXmlHttpRequest();

        xmlHttpRequest.onreadystatechange = uploadingFile;  
        xmlHttpRequest.open("GET", url, false);  

        xmlHttpRequest.send(null);
    } else {
        var dialog = document.getElementById('bottom-dialog');
        dialog.lastChild.nodeValue = 'Please select a file to upload!';
    }
}

function uploadProgress(evt) {
    var progress_bar = document.getElementById('progress-bar');
    var p_bar = document.getElementById('p-bar');
    if (p_bar == null) {
        p_bar = document.createElement('p');
        p_bar.setAttribute('id', 'p-bar');
        progress_bar.appendChild(p_bar);
    }
    if (evt.lengthComputable) {
        var percentComplete = Math.round(evt.loaded * 100 / evt.total);
        p_bar.style.backgroundPosition = - p_bar.offsetWidth + p_bar.offsetWidth*percentComplete/100 + "px";
        if (p_bar.lastChild) {
            p_bar.lastChild.nodeValue = percentComplete.toString() + '%';
        } else {
            var text = document.createTextNode(percentComplete.toString() + '%');
            p_bar.appendChild(text);
        }
    } else {
        p_bar.style.backgroundPosition = - p_bar.offsetWidth + "px";
        if (p_bar.lastChild) {
            p_bar.lastChild.nodeValue = 'unable to compute';
        } else {
            var text = document.createTextNode('unable to compute');
            p_bar.appendChild(text);
        }
    }
}

function uploadComplete(evt) {
    var progress_bar = document.getElementById('progress-bar');
    var p_bar = progress_bar.lastChild;
    var p_text = p_bar.lastChild;
    p_text.nodeValue = 'Completed!'
    p_bar.style.backgroundPosition = "0% 0%";
}


function uploadingFile() {
    if(xmlHttpRequest.readyState == 4 && xmlHttpRequest.status == 200){  
        var result = xmlHttpRequest.responseText;
        console.log(result);
        var myForm = document.getElementById('upload-form');
        // myForm.setAttribute('action', result);
        // myForm.submit();

        var xhr = createXmlHttpRequest();
        var fd = new FormData(myForm);

        xhr.upload.addEventListener("progress", uploadProgress, false);
        xhr.addEventListener("load", uploadComplete, false);

        xhr.open("POST", result, true);
        xhr.send(fd);
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
