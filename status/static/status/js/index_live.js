$(function(){
    lock = false;
    function update(){
        if (lock) {
            return;
        }
        lock = true;
        $.ajax({
            url: '/',
            dataType: 'json',
            success: function (data) {
                lock = false;
                if (data.offline) {
                    $('.offline').show();
                    $('.online').hide();
                } else {
                    $('.offline').hide();
                    $('.online').show();
                }

                $.each(['get_failures', 'hardware_errors', 'rejected'], function(index, item){
                    var value = data.offline ? '-' : '' + Number(data.summary[item].value).toFixed();
                    $('#' + item).text(value);
                });

                $.each(['ghs_av', 'utility'], function(index, item){
                    var value = data.offline ? '-' : '' + Number(data.summary[item].value).toFixed(3);
                    $('#' + item).text(value);
                });

                $.each(['server_uptime', 'cpu_percent', 'cpu_temp',
                        'mem_percent', 'mem_used', 'mem_total',
                        'disk_percent', 'disk_used', 'disk_total',
                        'eth0_recv', 'eth0_sent', 'wlan0_recv', 'wlan0_sent'], function(index, item){
                    var value = data.system[item];
                    $('#' + item).text(value);
                });

                $('#cpu_bar').width(data.system.cpu_percent + '%');
                $('#mem_bar').width(data.system.mem_percent + '%');
                $('#disk_bar').width(data.system.disk_percent + '%');

                $.each(data.summary, function(key, value) {
                    $('#sum_' + key).text(value.value);
                });
            },
            error: function () {
                lock = false;
            }
        });
    }

    setInterval(update, 2000);
});
