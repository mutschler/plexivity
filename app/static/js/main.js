function currentActivity() {
			$('#activity').load('/load/activity');
		}
		setInterval('currentActivity()', 15000);