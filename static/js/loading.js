$(document).ready(function(){
    setInterval(init, 2000);
    function init(){
        $.get('/status', function(data, status){
            console.log(data['status']);
            if (data['status'] == "ok"){
                window.location.href='http://fm.chom.me';
            }
    });
}
});
