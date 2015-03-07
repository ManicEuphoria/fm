$(document).ready(function(){
    var audio = $("#audio")[0];

    TweenLite.ticker.useRAF(false);
    TweenLite.lagSmoothing(0);
    var duration = $('meta.track-duration')[0]['content'];
    bar = $('.loading-bar');
    bar_tween = new TweenLite.to(bar, duration, {width:'100%', ease:Linear.easeNone});
    bar_tween.pause();
    audio.onpause = function(){
        bar_tween.pause();
    };

    audio.onplay = function(){
        bar_tween.play();
    };

    $('.paused').click(function(){
        $('.play').show();
        $('.paused').hide();
        audio.pause();
    });

    $('.play').click(function(){
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
            bar_tween.restart();
            bar_tween = new TweenLite.to(bar, data['duration'], {width:'100%',  ease:Linear.easeNone});


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
                $('.paused').show();
                $('.play').hide();
                $('title').text(title + '-' + artist);
            // change the loading bar
            bar_tween.restart();
            bar_tween = new TweenLite.to(bar, data['duration'], {width:'100%',  ease:Linear.easeNone});


            setTimeout(refresh, 10000);

            


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
//config
$('.fa-cog').mouseover(function(){
    $('.fa-cog').addClass('fa-spin');
});

$('.fa-cog').mouseout(function(){
    $('.fa-cog').removeClass('fa-spin');
});

$('.fa-cog').click(function(){
    $('.right-column').css({'background-color':'black', "background-image":'none'});
    $('#mizar').animate({marginTop:'1%'}, 2000);
    function show_introduction(){
        $('#introduction').show();
    }
    setTimeout(show_introduction, 2000);
});

//back to normal
$('.fa-mail-reply').click(function(){
    $('#introduction').hide();
    $('#mizar').animate({marginTop:'125px'}, 1000);
  $('.right-column').removeAttr('style');
});

});


