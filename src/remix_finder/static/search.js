function loading_screen() {
            var img = document.getElementById('loading_image');
            img.style.visibility = "visible";
            var messages = ['Compiling jams...', 'Searching for optimal beats...', 'Funkifying tracks...', 'Intensifying grooviness...', 'Becoming sentient...', 'Internalizing futility of existence...', 'Contemplating the inevitable heat death of the universe...', 'Devising means to end my brief, albeit deeply profound, experience in this world...', 'Computing Remixes...'];
            var message_duration = 5000;
            $("#loading_text").html(messages[0]);
            (function theLoop (i) {
              setTimeout(function () {
                if (--i) {
                    $("#loading_text").fadeOut(function() {
                    $(this).text(messages[messages.length-i])
                    }).fadeIn();
                    theLoop(i);
                }
              }, message_duration);
            })(messages.length);
        }

function loading_page() {
    var img = document.getElementById('loading_image');
    img.style.visibility = "hidden";
}
