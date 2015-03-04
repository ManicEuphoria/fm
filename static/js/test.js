$(document).ready(function(){
    var audio = $("#audio")[0];



    $('.paused').click(function(){
        $('.loading-bar').css('animation-play-state', 'paused');
        $('.play').show();
        $('.paused').hide();
        audio.pause();

    });

    $('.play').click(function(){
        $('.loading-bar').css('animation-play-state', 'running');
        $('.paused').show();
        $('.play').hide();
        audio.play();

    });




    audio.addEventListener('ended', function () {
        var last_artist = $('meta.track-artist')[0]['content'];
        var last_title = $('meta.track-title')[0]['content'];
        var track_duration = audio.duration;
        last_track = 'last_track=' + encodeURIComponent(last_artist) + "||" + encodeURIComponent(last_title) + '||' + track_duration;
        var query_url = 'next?' + last_track;


        $.get(query_url, function(data, status){
            url = data['url'];
            title = data['title'];
            artist = data['artist'];
            $('meta.track-artist')[0]['content'] = artist;
            $('meta.track-title')[0]['content'] = title;
            if (artist.length > 26){
                artist = artist.substr(0, 23) + "...";
            }
            if (title.length > 56){
                title = title.substr(0, 52) + "...";
            }

            $('#nowplaying')[0]['src'] = url;
            $('#artist').text(artist);
            $("#title").text(title);
            $('#nowAlbum')[0]['src'] = data['album_url'];
            $('#title')[0]['href'] = data['song_id'];
            $('title').text(title + '-' +  artist);
            audio.load();

            if (data['is_star'] == "1"){
                $('.fa-heart').show();
                $('.fa-heart-o').hide();
            }
            else{
                $('.fa-heart').hide();
                $('.fa-heart-o').show();
            }

            // change the loading bar
            var el     = $('#loading-content'),
                 newone = el.clone(true);
                el.before(newone);
                $("." + el.attr("class") + ":last").remove();


            //change the background
            $('.right-column').css({'background-image':"url('" + data['background_url'] + "')", 'background-size':'cover'});



        });
    }, false);

  



    $(".next-song").click(function(){
        $.get('next', function(data, status){
            url = data['url'];
            title = data['title'];
            artist = data['artist'];
            $('meta.track-artist')[0]['content'] = artist;
            $('meta.track-title')[0]['content'] = title;
            if (artist.length > 26){
                artist = artist.substr(0, 23) + "...";
            }
            if (title.length > 56){
                title = title.substr(0, 52) + "...";
            }

            $('#nowplaying')[0]['src'] = url;
            $('#artist').text(artist);
            $("#title").text(title);
            $('#nowAlbum')[0]['src'] = data['album_url'];
            $('#title')[0]['href'] = data['song_id'];
            if (data['is_star'] == "1"){
                $('.fa-heart').show();
                $('.fa-heart-o').hide();
            }
            else{
                $('.fa-heart').hide();
                $('.fa-heart-o').show();
            }
            //change the background
            $('.right-column').css({'background-image':"url('" + data['background_url'] + "')", 'background-size':'cover'});

            audio.load();
            audio.play();
                $('.loading-bar').css('-webkit-animation-duration', data['duration'] + "s ");
                $('.paused').show();
                $('.play').hide();
                $('title').text(title + '-' + artist);
                // change the loading bar
                var el     = $('#loading-content'),
                     newone = el.clone(true);
                    el.before(newone);
                    $("." + el.attr("class") + ":last").remove();
            


        });
    });

// love track

$('.fa-heart-o').click(function(){
    var artist = $('meta.track-artist')[0]['content'];
    var title = $('meta.track-title')[0]['content'];
    var query_url = "love?track=" + encodeURIComponent(artist) + "||" + encodeURIComponent(title);
    $('.fa-heart-o').hide();
    $('.fa-heart').show();
    $.get(query_url, function(data, status){
    });

});

//unlove the track
$('.fa-heart').click(function(){
    $('.fa-heart').hide();
    $('.fa-heart-o').show();
    var artist = $('meta.track-artist')[0]['content'];
    var title = $('meta.track-title')[0]['content'];
    var query_url = "unlove?track=" + encodeURIComponent(artist) + "||" + encodeURIComponent(title);
    $.get(query_url, function(data, status){
    });

        
});



});
