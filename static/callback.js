var params = {},
    queryString = location.hash.substring(1),
    regex = /([^&=]+)=([^&]*)/g, m;
while (m = regex.exec(queryString)) {
  params[decodeURIComponent(m[1])] = decodeURIComponent(m[2]);
}

(function csrf() {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
})();

const request = {
    method: 'POST',
    url: '/rest-auth/google/',
    data: params,
};
$.ajax(request)
    .then(
        r => {
            const expires_at = new Date();
            expires_at.setSeconds(expires_at.getSeconds() + parseInt(params.expires_in));
            const data = {
                token: r.key,
                expires_at,
            };
            window.opener.postMessage(data, cb_params.FRONTEND_CLIENT);
            setTimeout(() => window.close(), 1000);
        },
        () => {
            window.opener.postMessage('failure', cb_params.FRONTEND_CLIENT);
            setTimeout(() => window.close(), 1000);
        }
    );
