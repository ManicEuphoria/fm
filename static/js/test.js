$(document).ready(function(){
    var audio = $("#audio")[0];

    audio.addEventListener('ended', function () {
        var last_artist = $("#artist").text();
        var last_title = $("#title").text();
        var track_duration = audio.duration;
        last_track = 'last_track=' + last_artist + "||" + last_title + '||' + track_duration;
        var query_url = 'next?' + last_track;

        var now_url = $('#nextUrl').text();
        var now_artist = $('#nextArtist').text();
        var now_title = $("#nextTitle").text();
        var this_track = '&this_track=' + now_artist + "||" + now_title;
        query_url = query_url + this_track;
        $('#nowplaying')[0]['src'] = now_url
        $('#artist').text(now_artist);
        $("#title").text(now_title);

        audio.load();
        $.get(query_url, function(data, status){
            url = data['url'];
            title = data['title'];
            artist = data['artist'];
            $('#nextArtist').text(artist);
            $('#nextTitle').text(title);
            $("#nextplay")[0]['src'] = url;
            $('#nextUrl').text(url);
        });
    }, false);

    $("#nextTrack").click(function(){
        var now_url = $('#nextUrl').text();
        var now_artist = $('#nextArtist').text();
        var now_title = $("#nextTitle").text();
        var query_url = 'next?this_track=' + now_artist + "||" + now_title;

        $('#nowplaying')[0]['src'] = now_url
        $('#artist').text(now_artist);
        $("#title").text(now_title);
        audio.load();
        $.get(query_url, function(data, status){
            url = data['url'];
            title = data['title'];
            artist = data['artist'];
            $('#nextArtist').text(artist);
            $('#nextTitle').text(title);
            $("#nextplay")[0]['src'] = url;
            $('#nextUrl').text(url);
        });
    })

});
