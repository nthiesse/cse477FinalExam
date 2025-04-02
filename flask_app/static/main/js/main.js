// feedback button 
const feedbackbutton = document.getElementById("feedbackbutton");
const form = document.getElementById("feedbackform");
// when the feedback button is pressed, have the form appear 
feedbackbutton.addEventListener("click", () => {
    form.style.display = form.style.display === 'none' || form.style.display === '' ? 'block' : 'none';
});


// code for login feature 
let count = 0
    function checkCredentials() {
        // package data in a JSON object
        // var data_d = {'email': 'owner@email.com', 'password': 'password'}
        // console.log('data_d', data_d)

        // get the email and password from the form
        let email = document.getElementById("email").value;
        let password = document.getElementById("password").value;
        var data_d = { 'email': email, 'password': password }
        console.log('data_d', data_d)

        // SEND DATA TO SERVER VIA jQuery.ajax({})
        jQuery.ajax({
            url: "/processlogin",
            data: data_d,
            type: "POST",
            success: function (retruned_data) {
                retruned_data = JSON.parse(retruned_data);
                //   console.log("TEST", retruned_data)
                //   window.location.href = "/home";
                if (retruned_data.status === 1) {
                    window.location.href = "/home"; // Redirect to home on success
                    count = 0;
                } else {
                    count++;
                    let errorMessage = document.getElementById("error-message");
                    errorMessage.style.visibility = "visible";
                    errorMessage.innerHTML = `Email or password are incorrect. Attempt: ${count}`;
                }
            }
        });
    }

    // code for the chat feature
    $(document).ready(function () {

        // socket = io.connect('https://' + document.domain + ':' + location.port + '/chat');
        socket = io.connect('http://' + document.domain + ':' + location.port + '/chat');
        socket.on('connect', function () {
            socket.emit('joined', {});
        });

        socket.on('status', function (data) {
            let tag = document.createElement("p");
            let text = document.createTextNode(data.msg);
            let element = document.getElementById("chat");
            tag.appendChild(text);
            tag.style.cssText = data.style;
            element.appendChild(tag);
            $('#chat').scrollTop($('#chat')[0].scrollHeight);

        });

        socket.on('message', function (data) {
                let tag = document.createElement("p");
                let text = document.createTextNode(data.msg);
                let element = document.getElementById("chat");
                tag.appendChild(text);
                tag.style.cssText = data.style;
                element.appendChild(tag);
                $('#chat').scrollTop($('#chat')[0].scrollHeight);
        });

        // start the process of putting the message on the screen when the user presses enter 
        $('input').unbind('keypress').keypress(function(event) {
            if (event.which === 13) {
                let message = $(this).val();
                socket.emit('message', { 'msg': message });
                $(this).val('');
            }
        });

        // leave the chat button
        $('#leave').click(function() {
            socket.emit('leaveChat', {});
            window.location.href = '/';
            socket.disconnect();
        });
    });