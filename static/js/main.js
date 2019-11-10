/**
 * Calls the promise identifying whether the hunter is ready to proceed with the turn.  Depending upon the outcome of
 * that promise, the hunter either continues to take or abandon his/her turn.  Because both involve asynchronous calls
 * to the server, a promise is required.
 * @param check_quiver_url - url of the ajax call to check the quiver contents
 * @param take_turn_url - url of the ajax call to carry out the hunter's turn request.
 * @param move - whether the hunter wants to enter or shoot into a cave on this upcoming turn.
 */
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

/**
 * Wraps in a promise object, an ajax call to determine the number of arrows the hunter has remaining in the quiver.
 * If the quiver contains just 1 arrow, the hunter is cautioned against using it unwisely.  The hunter may decide
 * to shoot it anyway.  The hunter's actual turn is deferred until the hunter decides whether to shoot his/her last
 * arrow.  If the hunter refrains, the turn is aborted.
 * @param check_quiver_url - url of the ajax call to check the quiver contents
 * @param move - whether the hunter wants to enter or shoot into a cave on this upcoming turn.
 * @returns {Promise<any>}
 */
var check_quiver = function(check_quiver_url, move) {

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

/**
 * Ajax call to implement the hunter's turn request (whether the enter or shoot and the cave involved) and report the
 * consequences of that action.  An error may occur if the use neglects to select a cave.
 * @param take_turn_url - url of the ajax call to carry out the hunter's turn request.
 * @param move - whether the hunter wants to enter or shoot into a cave on this turn.
 */
var take_turn = function(take_turn_url, move) {

    let choices = $("#choices");
    let shootButton = $("#shoot");
    let caveSelector = $("#cave_id");
    let errorMessages = $("#error_messages");
    let statusMessages = $("#status_messages");
    let errorSection = $(".error-section");
    let notebook = $("#notebook");

    let cave_id = caveSelector.val();
    errorSection.addClass("d-none");

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

            // Update the cave options to take into account the hunter's (possibly new) surroundings.
            let optionList = "<option value=''>Choose...</option>";
            cave_ids.forEach(function(item) {
                optionList += "<option value='" + item + "'>" + item + "</option>";
            });
            caveSelector.html(optionList);

            // Populate the status board with the status messages returned by the call and color them appropriately.
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

            // If the game is over (either hunter or Wumpus killed), replace the player's move elements with a
            // button inviting the player to a new game.
            if(game_over) {
                let game_button = "<div class='text-center'><a class='btn btn-primary' href='/'>New Game?</a></div>";
                choices.html(game_button)
            }

            // If the hunter has no arrows remaining in the quiver, remove the Shoot button.
            if(arrows === 0) {
                shootButton.hide()
            }

            // Upldate the field notes with the latest cavern map.
            if(notes) {
                notebook.html(notes);
            }
        },
        error: function (request) {
            let errors = $.parseJSON(request.responseText).errors;
            if(errors) {
                errorSection.removeClass("d-none");
            }
            let errorList = "";
            errors.forEach(function(item) {
                errorList += "<li>" + item + "</li>";
            });
            errorMessages.html(errorList);
        }
    });
};