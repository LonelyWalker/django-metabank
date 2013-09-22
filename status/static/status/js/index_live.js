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

                $.each(['ghs_av', 'get_failures', 'hardware_errors', 'utility', 'rejected'], function(index, item){
                    $('#' + item).text(data.offline ? '-' : data.summary[item].value);
                });

                $.each(['cpu_percent', 'cpu_temp', 'mem_percent',
                        'mem_used', 'mem_total',
                        'disk_percent', 'disk_used', 'disk_total',
                        'eth0_recv', 'eth0_sent'], function(index, item){
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
