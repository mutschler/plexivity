function currentActivity() {
	$('#activity').load(load_activity);
}

function recentlyAdded(){
  $('#recentlyAdded').load(load_recentlyAdded);
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
      "dataFormatX": function (x) { return d3.time.format('%H').parse(x); },
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


    //plays per user
     var udata = {
      "xScale": "ordinal",
      "yScale": "linear",
      "main": [
        {
          "className": ".playcount",
          "data": usersPlayFinal
        }
      ]
    };
    var uopts = {
      //"dataFormatX": function (x) { return d3.time.format('%Y-%m-%d').parse(x); },
      //"tickFormatX": function (x) { return x; },
      "paddingLeft": ('35'),
      "paddingRight": ('35'),
      "paddingTop": ('10'),
      "tickHintY": ('5'),
      "mouseover": function (d, i) {
        var pos = $(this).offset();
        $(tt).text(d.x + ': ' + d.y + ' play(s)')
          .css({top: topOffset + pos.top, left: pos.left + leftOffset})
          .show();
      },
      "mouseout": function (x) {
        $(tt).hide();
      }
    };
    var myChart = new xChart('bar', udata, '#playChartUser', uopts);


    //plays per user alltime
     var udataa = {
      "xScale": "ordinal",
      "yScale": "linear",
      "main": [
        {
          "className": ".playcount",
          "data": usersPlayAlltimeFinal
        }
      ]
    };
    var uoptsa = {
      //"dataFormatX": function (x) { return d3.time.format('%Y-%m-%d').parse(x); },
      //"tickFormatX": function (x) { return x; },
      "paddingLeft": ('35'),
      "paddingRight": ('35'),
      "paddingTop": ('10'),
      "tickHintY": ('5'),
      "mouseover": function (d, i) {
        var pos = $(this).offset();
        $(tt).text(d.x + ': ' + d.y + ' play(s)')
          .css({top: topOffset + pos.top, left: pos.left + leftOffset})
          .show();
      },
      "mouseout": function (x) {
        $(tt).hide();
      }
    };
    var myChart = new xChart('bar', udataa, '#playChartAlltimeUser', uoptsa);
    

}


$(document).ready(function() {

	//only set the interval if we are on a page that contains activity feed
	if($('#activity').length){
		setInterval('currentActivity()', 15000);
	}
    if($('#recentlyAdded').length){
        setInterval('recentlyAdded()', 300000);
    }

            if($('#globalHistory').length){
                $('#globalHistory').dataTable( {
            	"paging": true,
            	"responsive": true,
            	"sPaginationType": "bootstrap",
            	"iDisplayLength": 25,
              "start": 0,
            	"bAutoWidth": true,
            	"aaSorting": [[ 0, "desc" ]],
              "serverSide": true,
              "processing": true,
              "ajax": load_history,
            	"language": tableLanguage,
              columns: [
                { data: "date" },
                { data: "user" },
                { data: "platform" },
                { data: "title" },
                { data: "type", sortable: false },
                { data: "streaminfo", sortable: false },
                { data: "time" },
                { data: "paused_counter" },
                { data: "stopped" },
                { data: "duration" },
                { data: "completed", sortable: false },
              ]
	     });
            }

            if($('#History').length){
                $('#History').dataTable( {
              "paging": true,
              "responsive": true,
              "sPaginationType": "bootstrap",
              "iDisplayLength": 25,
              "start": 0,
              "bAutoWidth": true,
              "aaSorting": [[ 0, "desc" ]],
              "language": tableLanguage,
              });
            }

        if($('#history-charts-wrapper').length){
        renderCharts()
        }

    $('body').imagesLoaded( function() {
        $('.isotope').isotope({
            "layoutMode": "fitRows",
            "itemSelector": ".item"
        })
    });
} );


$('#streamModal').on('show.bs.modal', function (event) {
  var button = $(event.relatedTarget) // Button that triggered the modal
  $('#streamModal').load(button.data("link"));
})