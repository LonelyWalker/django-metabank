function paramName(key) {
  if (key.indexOf('ghash') !== -1)            return 'ghash';
  if (key.indexOf('match_work_count') !== -1) return 'match_work_count';
  if (key.indexOf('hw_errors') !== -1)        return 'hw_errors';
  if (key.indexOf('clock_bits') !== -1)       return 'clock_bits';
  if (key === 'avg_gh_per_chip')              return 'avg_gh_per_chip';
}

function getExtent(key) {
  var p = paramName(key);
  if (p === 'ghash') return [0, 4];
  if (p === 'avg_gh_per_chip') return [0, 4];
  if (p === 'clock_bits') return [0, 60];
}

function getColor(key) {
  var p = paramName(key);
  if (p === 'match_work_count') return ['#000', '#000', '#000', '#000', '#BDC9E1', '#74A9CF', '#2B8CBE', '#045A8D'];  // blue
  if (p === 'hw_errors') return ['#000', '#000', '#000', '#000', '#bdd7e7', '#6baed6', '#3182bd', '#08519c'];  // blue
  if (p === 'clock_bits') return ['#000', '#000', '#000', '#000', '#FED98E', '#FE9929', '#D95F0E', '#993404'];

  return ['#000', '#000', '#000', '#000', '#bae4b3', '#74c476', '#31a354', '#006d2c'];  // green
}

$(function(){
  var last_data = {},
      initialized = false;

  setInterval( function() {
      $.ajax({
          url: '/status/realtime_data/',
          dataType: 'json',
          success: function (data) {
              var idata = {};

              _.each(data.stats[0], function(item, key) {
                var slot;
                if (key.indexOf('ghash') !== -1) {
                  slot = key.split('ghash_')[1] + '_ghash';
                  idata[slot] = item;
                }
                if (key.indexOf('match_work_count') !== -1) {
                  slot = key.split('match_work_count_')[1] + '_match_work_count';
                  idata[slot] = item;
                }
                if (key.indexOf('hw_errors_') !== -1) {
                  slot = key.split('hw_errors_')[1] + '_hw_errors';
                  idata[slot] = item;
                }
                if (key.indexOf('clock_bits_') !== -1) {
                  slot = key.split('clock_bits_')[1] + '_clock_bits';
                  idata[slot] = item;
                }
                if (key === 'total_gh') {
                  idata['total_gh'] = item;
                }
                if (key === 'avg_gh_per_chip') {
                  idata['avg_gh_per_chip'] = item;
                }
                if (key === 'total_hw') {
                  idata['total_hw'] = item;
                }
              });

              last_data.idata = idata;

              if (! initialized) {
                var sorted = _.sortBy(_.map(idata, function(v,k){return k;}), function(i) {return i;});
                sorted.unshift(sorted.pop());
                sorted.unshift(sorted.pop());
                sorted.unshift(sorted.pop());

                d3.select("#placeholder").selectAll(".horizon")
                    .data(sorted.map(getData))
                  .enter().insert("div", ".bottom")
                    .attr("class", function(i) {return 'horizon ' + paramName(i.toString());})
                    .call(
                      context.horizon()
                      .extent(function(i){return getExtent(i.toString());})
                      .colors(function(i){return getColor(i.toString());})
                      .format(d3.format('.4s'))
                    );

                initialized = true;
              }
          }
      });
  }, 1000 );

  var context = realtime.context()
      .step(1e3)
      .size($('#placeholder').width());

  // create axis
  d3.select("#placeholder").selectAll(".axis")
      .data(["top", "bottom"])
    .enter().append("div")
      .attr("class", function(d) { return d + " axis"; })
      .each(function(d) { d3.select(this).call(context.axis().ticks(12).orient(d)); });

  // create rule
  d3.select("#placeholder").append("div")
      .attr("class", "rule")
      .call(context.rule());

  context.on("focus", function(i) {
    d3.selectAll(".value").style("right", i === null ? null : context.size() - i + "px");
  });

  // Replace this with context.graphite and graphite.metric!
  function getData(x) {
    var value = 0,
        values = [],
        i = 0,
        last;
    return context.metric(function(start, stop, step, callback) {
      start = +start, stop = +stop;
      if (isNaN(last)) last = start;
      while (last < stop) {
        last += step;
        //if (last < (new Date(new Date().getTime() - 10000).getTime())) {
        if (last < stop - step*3) {
          value = 0;
        } else {
          value = last_data.idata[x];
        }
        values.push(value);
      }
      callback(null, values = values.slice((start - stop) / step));
    }, x);
  }

  $('.gswitch').change(function(){
      var name = this.name;
      $('#placeholder .' + name).toggle(200);
  });
});
