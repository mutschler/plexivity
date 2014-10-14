function currentActivity() {
	$('#activity').load('/load/activity');
}


(function(document,navigator,standalone) {
            // prevents links from apps from oppening in mobile safari
            // this javascript must be the first script in your <head>
            if ((standalone in navigator) && navigator[standalone]) {
                var curnode, location=document.location, stop=/^(a|html)$/i;
                document.addEventListener('click', function(e) {
                    curnode=e.target;
                    while (!(stop).test(curnode.nodeName)) {
                        curnode=curnode.parentNode;
                    }
                    // Condidions to do this only on links to your own app
                    // if you want all links, use if('href' in curnode) instead.
                    if('href' in curnode && ( curnode.href.indexOf('http') || ~curnode.href.indexOf(location.host) ) ) {
                        e.preventDefault();
                        location.href = curnode.href;
                    }
                },false);
            }
        })(document,window.navigator,'standalone');


function renderCharts(){

    var tt = document.createElement('div'),
      leftOffset = -(~~$('html').css('padding-left').replace('px', '') + ~~$('body').css('margin-left').replace('px', '')),
      topOffset = -35;
    tt.className = 'ex-tooltip';
    document.body.appendChild(tt);

    var hdata = {
      "xScale": "ordinal",
      "yScale": "linear",

      "main": [
        {
          "className": ".playChartHourly",
          "data": hourlyPlayFinal
        }
      ]
    };
    var hopts = {
      "dataFormatX": function (x) { return d3.time.format('%Y-%m-%d %H').parse(x); },
      "tickFormatX": function (x) { return d3.time.format('%-I:00 %p')(x); },
      "paddingLeft": ('35'),
      "paddingRight": ('35'),
      "paddingTop": ('10'),
      "tickHintY": ('5'),
      "mouseover": function (d, i) {
        var pos = $(this).offset();
        $(tt).text(d3.time.format('%-I:00 %p')(d.x) + ': ' + d.y + ' play(s)')
          .css({top: topOffset + pos.top, left: pos.left + leftOffset})
          .show();
      },
      "mouseout": function (x) {
        $(tt).hide();
      }
    };
    var myChart = new xChart('line-dotted', hdata, '#playChartHourly', hopts);


    var mhdata = {
      "xScale": "ordinal",
      "yScale": "linear",

      "main": [
        {
          "className": ".maxplayChartHourly",
          "data": maxhourlyPlayFinal
        }
      ]
    };
    var mhopts = {
      "dataFormatX": function (x) { return d3.time.format('%Y-%m-%d %H').parse(x); },
      "tickFormatX": function (x) { return d3.time.format('%-I:00 %p')(x); },
      "paddingLeft": ('35'),
      "paddingRight": ('35'),
      "paddingTop": ('10'),
      "tickHintY": ('5'),
      "mouseover": function (d, i) {
        var pos = $(this).offset();
        $(tt).text(d3.time.format('%-I:00 %p')(d.x) + ': ' + d.y + ' play(s)')
          .css({top: topOffset + pos.top, left: pos.left + leftOffset})
          .show();
      },
      "mouseout": function (x) {
        $(tt).hide();
      }
    };
    var myChart = new xChart('bar', mhdata, '#playChartMaxHourly', mhopts);


    var ddata = {
      "xScale": "ordinal",
      "yScale": "linear",
      "main": [
        {
          "className": ".playcount",
          "data": dailyPlayFinal
        }
      ]
    };
    var dopts = {
      "dataFormatX": function (x) { return d3.time.format('%Y-%m-%d').parse(x); },
      "tickFormatX": function (x) { return d3.time.format('%b %e')(x); },
      "paddingLeft": ('35'),
      "paddingRight": ('35'),
      "paddingTop": ('10'),
      "tickHintY": ('5'),
      "mouseover": function (d, i) {
        var pos = $(this).offset();
        $(tt).text(d3.time.format('%b %e')(d.x) + ': ' + d.y + ' play(s)')
          .css({top: topOffset + pos.top, left: pos.left + leftOffset})
          .show();
      },
      "mouseout": function (x) {
        $(tt).hide();
      }
    };
    var myChart = new xChart('bar', ddata, '#playChartDaily', dopts);

     var mdata = {
      "xScale": "ordinal",
      "yScale": "linear",
      "main": [
        {
          "className": ".playcount",
          "data": monthlyPlayFinal
        }
      ]
    };
    var mopts = {
      "dataFormatX": function (x) { return d3.time.format('%Y-%m').parse(x); },
      "tickFormatX": function (x) { return d3.time.format('%b')(x); },
      "paddingLeft": ('35'),
      "paddingRight": ('35'),
      "paddingTop": ('10'),
      "tickHintY": ('5'),
      "mouseover": function (d, i) {
        var pos = $(this).offset();
        $(tt).text(d3.time.format('%b')(d.x) + ': ' + d.y + ' play(s)')
          .css({top: topOffset + pos.top, left: pos.left + leftOffset})
          .show();
      },
      "mouseout": function (x) {
        $(tt).hide();
      }
    };
    var myChart = new xChart('line-dotted', mdata, '#playChartMonthly', mopts);
}


$(document).ready(function() {

	//only set the interval if we are on a page that contains activity feed
	if($('#activity').length){
		setInterval('currentActivity()', 15000);
	}

            if($('#globalHistory').length){
                $('#globalHistory').dataTable( {
            	"paging": true,
            	"responsive": true,
            	"sPaginationType": "bootstrap",
            	"iDisplayLength": 25,
            	"bAutoWidth": true,
            	"aaSorting": [[ 0, "desc" ]],
            	"language": tableLanguage
	   } );
            }

        if($('#history-charts-wrapper').length){
        renderCharts()
        }
} );