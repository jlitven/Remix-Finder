$(window).scroll(function() {
  sessionStorage.scrollTop = $(this).scrollTop();
});

$(document).ready(function() {
  if (sessionStorage.scrollTop != "undefined") {
    $(window).scrollTop(sessionStorage.scrollTop);
  }
});

$('.form').submit(function() {
    var span = $(this).find('.btn').children("span");
    span.text('Creating Playlist...');
    $(this).find('.btn').prop('disabled', true);
});

function pause(id) {
    var play_icon = document.getElementById('play_' + id)
    var pause_icon = document.getElementById('pause_' + id)
    pause_icon.style.display = "none";
    play_icon.style.display = "initial";
}

function pause_all(){
    var players = document.getElementsByClassName("control");
    for (var i = 0; i < players.length; i++) {
        pause(players[i].id);
    }
}

function play(id) {
    pause_all();
    var play_icon = document.getElementById('play_' + id);
    var pause_icon = document.getElementById('pause_' + id);
    play_icon.style.display = "none";
    pause_icon.style.display = "initial";

}

function play_pause(src, id) {
    var myAudio = document.getElementById('audio_player');
    var source = document.getElementById('source');
    if (source.src != src){
       source.src = src;
       myAudio.load();
       myAudio.play();
       play(id);
    }else
    {
        if (myAudio.paused){
            myAudio.play(id);
            play(id);
        }else{
            myAudio.pause(id);
            pause(id);
        }
    }
}
$("#audio_player").bind("ended", function(){
    pause_all();
});
