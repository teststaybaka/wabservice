var xmlHttpRequest;

function createXmlHttpRequest(){  
  if(window.ActiveXObject){ //如果是IE浏览器  
      return new ActiveXObject("Microsoft.XMLHTTP");  
  }
  else if(window.XMLHttpRequest){ //非IE浏览器  
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
          console.log('Successful login for: ' + response.name);
          // document.getElementById('navigation-bar').appendChild() = '<a href="/account" id="username-link" class="user-info">'+response.name+'</a> \
          // <a href="/inbox" id="inbox-link" class="user-info">inbox</a><a href="/history" id="history-link" class="user-info">history</a>';
          // var img = document.createElement('img');
          // FB.api('/me/picture', {"redirect": false, "height": "10", "type": "normal", "width": "10"}, function(response) {
          // if (response && !response.error) {
          //     var profileImage = response.data.url;
          //     console.log('imgdata: ' + profileImage);
          //     img.setAttribute('src', profileImage);
          //   }
          // });

          var uname = document.createElement("a");
          uname.setAttribute('href', '/account');
          uname.setAttribute('id', 'username-link');
          uname.setAttribute('class', 'user-info');
          var text = document.createTextNode(response.name);
          // uname.appendChild(img);
          uname.appendChild(text);

          var inbox = document.createElement("a");
          inbox.setAttribute('href', '/inbox');
          inbox.setAttribute('id', 'inbox-link');
          inbox.setAttribute('class', 'user-info');
          var text = document.createTextNode('inbox');
          inbox.appendChild(text);

          var hist = document.createElement("a");
          hist.setAttribute('href', '/history');
          hist.setAttribute('id', 'history-link');
          hist.setAttribute('class', 'user-info');
          var text = document.createTextNode('history');
          hist.appendChild(text);
          var bar = document.getElementById("navigation-bar");
          bar.appendChild(hist);
          bar.appendChild(inbox);
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