process_turn = function(check_quiver_url, take_turn_url, move) {
    check_quiver(check_quiver_url, move)
        .then(function(data) {
            console.log("arrows: " + data);
            take_turn(take_turn_url, move);
        })
        .catch(function(data) {
            console.log("arrows: " + arrows)
        })
};

var check_quiver = function(check_quiver_url, move) {
    let errorMessages = $("#error_messages");
    let errorBadge = $(".badge-danger");
    errorBadge.hide();
    errorMessages.empty();
    return new Promise(function(resolve, reject) {
        $.ajax({
            url: check_quiver_url,
            type: 'GET',
            success: function (response) {
                let arrows = response['arrows'];
                if (arrows === 1 && move === 'shoot') {
                    let answer = confirm("This is your last arrow.  Are you sure you want to shoot it?");
                    if (!answer) {
                        reject("save last one");
                    }
                    else {
                        resolve("shoot last one");
                    }
                }
                else {
                    resolve("no issue");
                }
            },
            error: function(request) {
                reject("error");
            }
        });
    });
};

var take_turn = function(take_turn_url, move) {

    let choices = $("#choices");
    let shootButton = $("#shoot");
    let caveSelector = $("#cave_id");
    let errorMessages = $("#error_messages");
    let statusMessages = $("#status_messages");
    let errorBadge = $(".badge-danger");
    let notebook = $("#notebook");

    let cave_id = caveSelector.val();

    $.ajax({
        url: take_turn_url,
        data: JSON.stringify({"move": move, "cave_id": cave_id}),
        dataType: "json",
        contentType: "application/json",
        type: 'POST',
        success: function(response) {
            //console.log(response);
            let messages = response['messages'];
            let cave_ids = response['cave_ids'];
            let arrows = response['arrows'];
            let game_over = response['game_over'];
            let notes = response['notes'];
            let optionList = "<option value=''>Choose...</option>";
            cave_ids.forEach(function(item) {
                optionList += "<option value='" + item + "'>" + item + "</option>";
            });
            caveSelector.html(optionList);

            let messageList = "";
            messages.forEach(function(message) {
                let color_class = 'text-default';
                if(message.type === 'WARNING') {
                    color_class = 'text-warning'
                }
                if(message.type === 'TERMINAL') {
                    color_class = 'text-danger'
                }
                messageList += "<li class='list-group-item " + color_class + "'>" + message.content + "</li>";
            });
            statusMessages.html(messageList);

            if(game_over) {
                let game_button = "<div class='text-center'><a class='btn btn-primary' href='/'>New Game?</a></div>";
                choices.html(game_button)
            }
            if(arrows === 0) {
                shootButton.hide()
            }
            if(notes) {
                notebook.html(notes);
            }
        },
        error: function (request) {
            let errors = $.parseJSON(request.responseText).errors;
            if(errors) {
                errorBadge.show();
            }
            let errorList = "";
            errors.forEach(function(item) {
                errorList += "<li>" + item + "</li>";
            });
            errorMessages.html(errorList);
        }
    });
};