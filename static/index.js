const google_endpoint = 'https://accounts.google.com/o/oauth2/v2/auth';
const data = {
    response_type: 'token',
    client_id: '907377379670-suvgso3siks409qfqgmqvfk2c18g4buh.apps.googleusercontent.com',
    redirect_uri: 'http://localhost:8000/auth/callback',
    scope: 'email',
};

const refresh = () => location.reload();

function serialize(obj) {
  var str = [];
  for(var p in obj)
    if (obj.hasOwnProperty(p)) {
      str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
    }
  return str.join("&");
}

function popupwindow() {
    const url = `${google_endpoint}?${serialize(data)}`;
    const title='Let me in with Google';
    const w = 500;
    const h = 600;
    var left = (screen.width/2)-(w/2);
    var top = (screen.height/2)-(h/2);
    return window.open(url, title, 'toolbar=no, location=no, directories=no, status=no, menubar=no, scrollbars=no, resizable=no, copyhistory=no, width='+w+', height='+h+', top='+top+', left='+left);
}

function authenticated(response) {
    refresh();
}

function letmeout() {
    $.ajax({
        method: 'GET',
        url: '/rest-auth/logout/',
    })
    .then(refresh, console.error.bind(console));
}