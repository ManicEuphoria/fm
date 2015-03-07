$(document).ready(function(){
    TweenLite.ticker.useRAF(false);
    TweenLite.lagSmoothing(0);
    loading_bar = $('.waiting-loading');
    bar_tween = new TweenLite.to(loading_bar, 360, {width:'100%', ease:Linear.easeNone});


    setInterval(init, 15000);
    function init(){
        $.get('/status', function(data, status){
            console.log(data['status']);
            if (data['status'] == "ok"){
                window.location.href='http://fm.chom.me';
            }
    });
}
});

