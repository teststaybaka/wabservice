var xmlHttpRequest;

function createXmlHttpRequest(){  
  if(window.ActiveXObject){ // IE browser
      return new ActiveXObject("Microsoft.XMLHTTP");  
  }
  else if(window.XMLHttpRequest){ // non-IE browser
      return new XMLHttpRequest();  
  }
}

function getCookie(cname) {
  var name = cname + "=";
  var ca = document.cookie.split(';');
  for (var i = 0; i < ca.length; i++) {
    var c = ca[i];
    while(c.charAt(0) == ' ') c = c.substring(1);
    if (c.indexOf(name) == 0) return c.substring(name.length, c.length);
  }
  return ""
}

function statusChangeCallback(response) {
  var last_status = getCookie('status');
  if (last_status === "") {
    status_change();
    return;
  }
  console.log(last_status);
  console.log('statusChangeCallback');
  console.log(response);
  if (response.status === 'connected') {
    if (last_status === 'logout') {
      status_change();
    } else {
      FB.api('/me', function(response) {
        if (response && !response.error) {
          var uname = document.createElement("a");
          uname.setAttribute('href', '/account');
          uname.setAttribute('id', 'username-link');
          uname.setAttribute('class', 'user-info');
          var text = document.createTextNode(response.name);
          // uname.appendChild(img);
          uname.appendChild(text);

          var hist = document.createElement("a");
          hist.setAttribute('href', '/history');
          hist.setAttribute('id', 'history-link');
          hist.setAttribute('class', 'user-info');
          var text = document.createTextNode('history');
          hist.appendChild(text);
          var bar = document.getElementById("navigation-bar");
          bar.appendChild(hist);
          bar.appendChild(uname);
        }
      });
    }
  } else {
    console.log('logout!');
    if (last_status === 'login') {
      status_change();
    }
  }
}

function status_change() {
  var hostname = window.location.hostname;
  var href = window.location.href;
  var parts = href.split('/');
  var index = -1;
  for (var i = 0; i < parts.length; i++) {
    if (parts[i].indexOf(hostname) != -1) {
      index = i;
      break;
    }
  }
  console.log(parts);
  var para = "/";
  for (var i = index + 1; i < parts.length; i++) {
    if (parts[i] == "") continue;
    para += parts[i] + "/"
  }
  console.log(para);
  window.location.href = '/loginstatuschange' + para;
}

// function checkLoginState() {
//   FB.getLoginStatus(function(response) {
//     statusChangeCallback(response);
//   });
// }

window.fbAsyncInit = function() {
  FB.init({
    appId      : '797761393603664',
    cookie     : true,
    xfbml      : true,
    version    : 'v2.1'
  });

  FB.getLoginStatus(function(response) {
    statusChangeCallback(response);
  });
};

(function(d, s, id){
   var js, fjs = d.getElementsByTagName(s)[0];
   if (d.getElementById(id)) {return;}
   js = d.createElement(s); js.id = id;
   js.src = "//connect.facebook.net/en_US/sdk.js";
   fjs.parentNode.insertBefore(js, fjs);
 }(document, 'script', 'facebook-jssdk'));