$(function(){
    $.ajax({
        url: '/status/av_data/',
        dataType: 'json',
        success: function (data) {
            var max = _.max(data[0].values, function(i){return i.y;}).y;
            max = max + max/5;

            var lineResize,
                lineChart;
            function lineChartOperaHack(){
                //lineChart is somehow not rendered correctly after updates. Need to reupdate
                if ($.browser.opera){
                    clearTimeout(lineResize);
                    lineResize = setTimeout(lineChart.update, 300);
                }
            }

            nv.addGraph(function() {
                var chart = nv.models.lineWithFocusChart()
                    .margin({top: 0, bottom: 25, left: 25, right: 0})
                    .showLegend(false)
                    .color([
                        $orange, '#cf6d51'
                    ]);

                chart.legend.margin({top: 3});

                chart.yAxis
                    .showMaxMin(false)
                    .tickFormat(d3.format(',.f'));

                chart.forceY([0, max]);


                chart.xAxis
                    .showMaxMin(false)
                    .tickFormat(function(d) { return d3.time.format('%d %b %H:%M')(new Date(d*1000));});
                chart.x2Axis
                    .showMaxMin(false)
                    .tickFormat(function(d) { return d3.time.format('%d %b')(new Date(d*1000));});


                d3.select('#visits-chart').append("svg")
                    .datum(data)
                    .transition().duration(500)
                    .call(chart);

                nv.utils.windowResize(chart.update);

                chart.legend.dispatch.on('legendClick.updateExamples', function() {
                    lineChartOperaHack();
                });

                lineChart = chart;

                lineChartOperaHack();

                return chart;
            });
        }
    });
});
