function currentActivity() {
	$('#activity').load('/load/activity');
}




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