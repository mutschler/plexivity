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


$(document).ready(function() {

	//only set the interval if we are on a page that contains activity feed
	if($('#activity').length){
		setInterval('currentActivity()', 15000);
	}

			$('#globalHistory').dataTable( {
				"paging": true,
				"responsive": true,
				"sPaginationType": "bootstrap",
				"iDisplayLength": 25,
				"bAutoWidth": true,
				"aaSorting": [[ 0, "desc" ]],
				"language": tableLanguage
			} );
		} );