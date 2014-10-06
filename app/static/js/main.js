function currentActivity() {
			$('#activity').load('/load/activity');
		}
		setInterval('currentActivity()', 15000);



$(document).ready(function() {
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