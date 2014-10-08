function currentActivity() {
	$('#activity').load('/load/activity');
}




$(document).ready(function() {

	//only set the interval if we are on a page that contains activity feed
	if($('#activity').length){
		setInterval('currentActivity()', 15000);
	}

			$('#globalHistory').dataTable( {
				"bPaginate": true,
				"bLengthChange": true,
				"iDisplayLength": 25,
				"bFilter": true,
				"bSort": true,
				"bInfo": true,
				"bAutoWidth": true,
				"aaSorting": [[ 0, "desc" ]],
				"bStateSave": false,
				"bSortClasses": false,
				"sPaginationType": "bootstrap",
				"aoColumns": [
				{"sSortDataType": "dom-data-order", "sType": "numeric"},
				null,
				null,
				null,
				null,
				null,
				null,
				null,
				null,
				null,
				null
				]
			} );
		} );