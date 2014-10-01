function currentActivity() {
			$('#activity').load('/stats/activity');
		}
		setInterval('currentActivity()', 15000);