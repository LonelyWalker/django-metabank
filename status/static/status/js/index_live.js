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
                    if (value > 1000000) {
                        $('#' + item).text((value / 1000000).toFixed(2) + ' M');
                    } else if (value > 100000) {
                        $('#' + item).text((value / 1000).toFixed() + ' k');
                    } else {
                        $('#' + item).text(value);
                    }
                });

                $.each(['ghs_av', 'utility'], function(index, item){
                    var value = data.offline ? '-' : '' + Number(data.summary[item].value).toFixed(3);
                    $('#' + item).text(value);
                });

                $.each(['server_uptime', 'cpu_percent', 'cpu_temp',
                        'mem_percent', 'mem_used', 'mem_total',
                        'disk_percent', 'disk_used', 'disk_total',
                        'disktmp_percent', 'disktmp_used', 'disktmp_total',
                        'diskvarlog_percent', 'diskvarlog_used', 'diskvarlog_total',
                        'eth0_recv', 'eth0_sent', 'wlan0_recv', 'wlan0_sent'], function(index, item){
                    var value = data.system[item];
                    $('#' + item).text(value);
                });

                $('#cpu_bar').width(data.system.cpu_percent + '%');
                $('#mem_bar').width(data.system.mem_percent + '%');
                $('#disk_bar').width(data.system.disk_percent + '%');
                $('#disktmp_bar').width(data.system.disktmp_percent + '%');
                $('#diskvarlog_bar').width(data.system.diskvarlog_percent + '%');

                $.each(['disk', 'disktmp', 'diskvarlog'], function(index, item){
                    var value = data.system[item + '_percent'];
                    bar = $('#' + item + '_bar').parent();
                    if (value > 90) {
                        bar.removeClass("progress-success");
                        bar.removeClass("progress-warning");
                        bar.addClass("progress-danger");
                    } else if (value > 66) {
                        bar.removeClass("progress-success");
                        bar.addClass("progress-warning");
                        bar.removeClass("progress-danger");
                    } else {
                        bar.addClass("progress-success");
                        bar.removeClass("progress-warning");
                        bar.removeClass("progress-danger");
                    }
                });

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
