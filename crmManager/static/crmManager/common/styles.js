//api


function get_notification(csrf_token) {
    var token = csrf_token;
    console.log("TOKEN ", token)
    $.ajax({
        type: 'POST',
        headers: { "X-CSRFToken": token },
        url: '/crm/get-notification',
        success: function (data) {
            console.log(data)
        },
        error: function (xhr, textStatus, errorThrown) {

        },
        contentType: "application/json",
        dataType: 'json'
    });
}