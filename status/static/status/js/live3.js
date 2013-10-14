$(function(){

    $.ajax({
        url: '/status/devicehr_data/',
        dataType: 'json',
        success: function (data) {
            var palette = new Rickshaw.Color.Palette({scheme: 'classic9'});
            data = $.map(data, function(i){
                i['color'] = palette.color();
                return i;
            });

            if (data.length === 0) {
                $('#devicehr-chart').html('<div class="row"><div class="span8 offset2"><h3>No data available</h3></div></div>');
                return;
            }

            graph = new Rickshaw.Graph( {
                element: document.getElementById("devicehr-chart"),
                height: 300,
                renderer: 'area',
                stroke: true,
                preserve: true,
                series: data
            });
            graph.render();

            $(window).resize(function(){
                graph.width = $("#chart-container").width();
                graph.render();
            });

            var hoverDetail = new Rickshaw.Graph.HoverDetail( {
                graph: graph
            });

            var annotator = new Rickshaw.Graph.Annotate( {
                graph: graph,
                element: document.getElementById('timeline')
            });

            var legend = new Rickshaw.Graph.Legend( {
                graph: graph,
                element: document.getElementById('legend')
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
                    success: function (newData) {
                        var palette = new Rickshaw.Color.Palette({scheme: 'classic9'});

                        $.each(graph.series, function(index, item){
                            var time = new Date().getTime() / 1000;

                            // search this item in new data
                            var newItem = _.find(newData, function(i){return i.name === item.name;});

                            if (newItem !== undefined){
                                graph.series[index].data = _.union(graph.series[index].data, newItem.data);
                            } else {
                                graph.series[index].data = _.union(graph.series[index].data, {
                                    x: time,
                                    y: 0
                                });
                            }
                        });

                        graph.render();
                    }
                });
            }, 5000 );
        }
    });
});
