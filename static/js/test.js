$(document).ready(function(){
    var audio = $("#audio")[0];
    console.log(audio);

    audio.addEventListener('ended', function () {
        $.get('next', function(data, status){
            url = data['url'];
            title = data['title'];
            artist = data['artist'];
            $('#artist').text(artist);
            $('#title').text(title);
            $("#audio")[0]['src'] = url;
        });
    }, false);
});
