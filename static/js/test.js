$(document).ready(function(){
    function nextrack(radio_type, do_background){
        function audioFadeout(){
            if (audio.volume > 0.1){
                var originalVolume = audio.volume;
                audio.volume = originalVolume - 0.1;
            }
            else{
                clearInterval(fdId);
            }
        }

        var fdId = setInterval(audioFadeout, 120);

        $.get('next?radio_type=' + radio_type, function(data, status){
            url = data['mp3_url'];
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
            if (do_background == "True"){
                $('.right-column').css({'background-image':"url('" + data['background_url'] + "')", 'background-size':'cover'});
            }
            audio.load();
            audio.play();



                $('.paused').show();
                $('.play').hide();
                $('title').text(title + '-' + artist);

            // change the loading bar
                bar_tween.restart();
                bar_tween.pause();
                bar_tween.kill();
                bar_tween = new TweenLite.to(bar, data['duration'], {width:'100%',  ease:Linear.easeNone});
                bar_tween.pause();




            


        });

    }
    function play_emotion(){
        nextrack("emotion", "False");
        // $('#mizar').show();
        $('.en-emotion').fadeOut("normal");
        $('meta.radio-type')[0]['content'] = "emotion";
    }


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

    audio.onplaying = function(){
        audio.volume = 0.8;
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
        var radio_type = $('meta.radio-type')[0]['content'];
        last_track = 'last_track=' + encodeURIComponent(last_artist) + "||" + encodeURIComponent(last_title) + '||' + track_duration;
        var query_url = 'next?' + last_track + '&radio_type=' + radio_type;


        $.get(query_url, function(data, status){
            url = data['mp3_url'];
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
            bar_tween.pause();
            bar_tween.kill();
            bar_tween = new TweenLite.to(bar, data['duration'], {width:'100%',  ease:Linear.easeNone});
            bar_tween.pause();


            //change the background
            $('.right-column').css({'background-image':"url('" + data['background_url'] + "')", 'background-size':'cover'});




        });
    }, false);


  



    $(".next-song").click(function(){
        var radio_type = $('meta.radio-type')[0]['content'];
        nextrack(radio_type, "True");
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
//choose emotion radio
$('.random#emotion-choose-icon').click(function(){
    $('#mizar').hide();
    $('.right-column').css({'opacity':'1', 'background':"rgba(67, 157, 168, 0.39)", "background-image":"url('http://nipponcolors.com/images/texture.png')"});
    $('.more-radio').fadeIn(1000);
    $('.chosen-word').hide();
    $('.emotion-choice').fadeIn(2000);
    $('.choose-word').fadeIn(2000);
});

//back to the normal radio
$('.random#back-icon').click(function(){
    nextrack("normal", "False");
    $('.more-radio').hide();
    $('#mizar').fadeIn(2000);
    $('.chosen-word').hide();
    $('.display-emotion-chi').hide();
    $('meta.radio-type')[0]['content'] = "normal";
    $('#emotion-choose-icon').show();
    $('#back-icon').hide();
});

$('.low-emotion').mouseover(function(){
    $('.down-color').css({'opacity': "0.1"});
    $('.up-color').css({'opacity': "0.1"});
    $('.high-color').css({'opacity': "0.1"});
    $('.down-word').css({'opacity': "0.2"});
    $('.up-word').css({'opacity': "0.2"});
    $('.high-word').css({'opacity': "0.2"});
});

$('.low-emotion').mouseout(function(){
    $('.down-color').css({'opacity': "0.75"});
    $('.up-color').css({'opacity': "0.75"});
    $('.high-color').css({'opacity': "0.75"});
    $('.down-word').css({'opacity': "1"});
    $('.up-word').css({'opacity': "1"});
    $('.high-word').css({'opacity': "1"});
});

$('.up-emotion').mouseover(function(){
    $('.down-color').css({'opacity': "0.1"});
    $('.low-color').css({'opacity': "0.1"});
    $('.high-color').css({'opacity': "0.1"});
    $('.down-word').css({'opacity': "0.2"});
    $('.low-word').css({'opacity': "0.2"});
    $('.high-word').css({'opacity': "0.2"});
});

$('.up-emotion').mouseout(function(){
    $('.down-color').css({'opacity': "0.75"});
    $('.low-color').css({'opacity': "0.75"});
    $('.high-color').css({'opacity': "0.75"});
    $('.down-word').css({'opacity': "1"});
    $('.low-word').css({'opacity': "1"});
    $('.high-word').css({'opacity': "1"});
});


$('.high-emotion').mouseover(function(){
    $('.down-color').css({'opacity': "0.1"});
    $('.up-color').css({'opacity': "0.1"});
    $('.low-color').css({'opacity': "0.1"});
    $('.down-word').css({'opacity': "0.2"});
    $('.up-word').css({'opacity': "0.2"});
    $('.low-word').css({'opacity': "0.2"});
});

$('.high-emotion').mouseout(function(){
    $('.down-color').css({'opacity': "0.75"});
    $('.up-color').css({'opacity': "0.75"});
    $('.low-color').css({'opacity': "0.75"});
    $('.down-word').css({'opacity': "1"});
    $('.up-word').css({'opacity': "1"});
    $('.low-word').css({'opacity': "1"});
});

$('.down-emotion').mouseover(function(){
    $('.low-color').css({'opacity': "0.1"});
    $('.up-color').css({'opacity': "0.1"});
    $('.high-color').css({'opacity': "0.1"});
    $('.low-word').css({'opacity': "0.2"});
    $('.up-word').css({'opacity': "0.2"});
    $('.high-word').css({'opacity': "0.2"});
});

$('.down-emotion').mouseout(function(){
    $('.low-color').css({'opacity': "0.75"});
    $('.up-color').css({'opacity': "0.75"});
    $('.high-color').css({'opacity': "0.75"});
    $('.low-word').css({'opacity': "1"});
    $('.up-word').css({'opacity': "1"});
    $('.high-word').css({'opacity': "1"});
});



$('.low-emotion').click(function(){
    $('.choose-word').fadeOut();
    $('.emotion-choice').fadeOut();
    $('.emotion-word-display').fadeOut();
    $('.right-column').css({'transition':'background-color 2s ease-in','background': '#81C7D4', "background-image":"url('http://nipponcolors.com/images/texture.png')"});
    $('.chosen-word').fadeIn(1500);
    $('.chosen-low').fadeIn(2500);
    $('#jing').fadeIn(3000);
    $('#en-jing').fadeIn(4500);
    query_url = 'emotion?request=choose&emotion_type=low';
    $('#emotion-choose-icon').hide();
    $('#back-icon').show();

    function bk_fade(){
        $('.right-column').attr('style', "background:white");
        function bb_fade(){
            $('.right-column').attr('style', "background-image:url('https://ununsplash.imgix.net/46/yzS7SdLJRRWKRPmVD0La_creditcard.jpg?fit=crop&fm=jpg&h=600&q=75&w=1050')");
        }
        setTimeout(bb_fade, 500);

    }

    setTimeout(bk_fade, 4000);


    $.get(query_url, function(data, status){
    });
    setTimeout(play_emotion, 5000);

});

$('.up-emotion').click(function(){
    $('.choose-word').fadeOut();
    $('.emotion-choice').fadeOut();
    $('.emotion-word-display').fadeOut();
    $('.right-column').css({'transition':'background-color 2s ease-in','background': '#BEC23F', "background-image":"url('http://nipponcolors.com/images/texture.png')"});
    $('.chosen-word').fadeIn(1500);
    $('.chosen-low').fadeIn(2500);
    $('#dong').fadeIn(3000);
    $('#en-dong').fadeIn(4500);
    $('#emotion-choose-icon').hide();
    $('#back-icon').show();
    function bk_fade(){
        $('.right-column').attr('style', "background:white");
        $('.right-column').attr('style', "background-image:url('https://ununsplash.imgix.net/46/yzS7SdLJRRWKRPmVD0La_creditcard.jpg?fit=crop&fm=jpg&h=600&q=75&w=1050')");

    }

    setTimeout(bk_fade, 4000);


    query_url = 'emotion?request=choose&emotion_type=up';
    $.get(query_url, function(data, status){
    });
    setTimeout(play_emotion, 5000);
});

$('.down-emotion').click(function(){
    $('.choose-word').fadeOut();
    $('.emotion-choice').fadeOut();
    $('.emotion-word-display').fadeOut();
    $('.right-column').css({'transition':'background-color 2s ease-in','background': '#1B813E', "background-image":"url('http://nipponcolors.com/images/texture.png')"});
    $('.chosen-word').fadeIn(1500);
    $('.chosen-low').fadeIn(2500);
    $('#emotion-choose-icon').hide();
    $('#back-icon').show();

    function bk_fade(){
        $('.right-column').attr('style', "background:white");
        $('.right-column').attr('style', "background-image:url('https://ununsplash.imgix.net/46/yzS7SdLJRRWKRPmVD0La_creditcard.jpg?fit=crop&fm=jpg&h=600&q=75&w=1050')");
    }

    setTimeout(bk_fade, 4000);
    $('#yi').fadeIn(3000);
    $('#en-yi').fadeIn(4500);
    query_url = 'emotion?request=choose&emotion_type=down';
    $.get(query_url, function(data, status){
    });
    setTimeout(play_emotion, 5000);
});
$('.high-emotion').click(function(){
    $('.choose-word').fadeOut();
    $('.emotion-choice').fadeOut();
    $('.emotion-word-display').fadeOut();
    $('.right-column').css({'transition':'background-color 2s ease-in','background': '#D0104C', "background-image":"url('http://nipponcolors.com/images/texture.png')"});
    $('.chosen-word').fadeIn(1500);
    $('.chosen-low').fadeIn(2500);
    $('#nao').fadeIn(3000);
    $('#en-nao').fadeIn(4500);
    $('#emotion-choose-icon').hide();
    $('#back-icon').show();

    function bk_fade(){
        $('.right-column').attr('style', "background:white");
        $('.right-column').attr('style', "background-image:url('https://ununsplash.imgix.net/46/yzS7SdLJRRWKRPmVD0La_creditcard.jpg?fit=crop&fm=jpg&h=600&q=75&w=1050')");

    }

    setTimeout(bk_fade, 4000);



    query_url = 'emotion?request=choose&emotion_type=high';
    $.get(query_url, function(data, status){
    });
    setTimeout(play_emotion, 5000);
});






});

