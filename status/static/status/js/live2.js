$(function(){

    $.ajax({
        url: '/status/devicehr_data/',
        dataType: 'json',
        success: function (data) {
            var palette = new Rickshaw.Color.Palette({scheme: 'classic9'});
            var data = $.map(data, function(i){
                i['color'] = palette.color();
                return i;
            });

            var graph = new Rickshaw.Graph( {
                element: document.getElementById("devicehr-chart2"),
                height: 300,
                renderer: 'area',
                stroke: true,
                preserve: true,
                series: data
            });
            graph.render();

            $(window).resize(function(){
                graph.width = $("#chart-container2").width();
                graph.render();
            });

            var hoverDetail = new Rickshaw.Graph.HoverDetail( {
                graph: graph
            });

            var annotator = new Rickshaw.Graph.Annotate( {
                graph: graph,
                element: document.getElementById('timeline2')
            });

            var legend = new Rickshaw.Graph.Legend( {
                graph: graph,
                element: document.getElementById('legend2')

            });

            var shelving = new Rickshaw.Graph.Behavior.Series.Toggle( {
                graph: graph,
                legend: legend
            });

            var order = new Rickshaw.Graph.Behavior.Series.Order( {
                graph: graph,
                legend: legend
            });

            var highlighter = new Rickshaw.Graph.Behavior.Series.Highlight( {
                graph: graph,
                legend: legend
            });

            var ticksTreatment = 'glow';

            var xAxis = new Rickshaw.Graph.Axis.Time( {
                graph: graph,
                ticksTreatment: ticksTreatment,
                timeUnit: {
                    name: '20min',
                    seconds: 60 * 20,
                    formatter: function(d) {
                        return moment(d).format('HH:mm');
                    }
                }
            });

            xAxis.render();

            var yAxis = new Rickshaw.Graph.Axis.Y( {
                graph: graph,
                tickFormat: Rickshaw.Fixtures.Number.formatKMBT,
                ticksTreatment: ticksTreatment
            });

            yAxis.render();

            setInterval( function() {
                $.ajax({
                    url: '/status/devicehr_data/',
                    dataType: 'json',
                    success: function (data) {
                        var palette = new Rickshaw.Color.Palette({scheme: 'classic9'});
                        var data = $.map(data, function(i){
                            i['color'] = palette.color();
                            return i;
                        });
                        $.each(data, function(index, item){
                            graph.series[index].data = item.data;
                        })

                        graph.render();
                    }
                });
            }, 5000 );


        }
    })



});
