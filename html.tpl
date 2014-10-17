<html>
<head>
	<title>{{title}}</title>
	<link href='http://fonts.googleapis.com/css?family=Source+Sans+Pro|Source+Code+Pro' rel='stylesheet' type='text/css'>
	<style  type="text/css">
		body{
			background: #1f1f1f;
			color: #bbb;
			font-family: "Source Sans Pro";
			font-size: 14px;
			margin-top: 20px;
		}

		h1{
			margin-left: 150px;
		}

		.version ul{
			list-style: none;
			margin: 0;
			padding: 0;
			border: 1px solid #3c3c3c;
			border-radius: 5px;
			float: left;
			width: 600px;
		}

		.version h2{
			float: left;
			width: 150px;
			margin-top: 0;
		}

		.version h2 small{
			font-size: 14px;
		}

		.version ul li{
			padding: 5px 5px 9px 5px;
			background: #2c2c2c;
			border-bottom: 1px solid #3c3c3c;
		}
		span.badge{
			color: #fff;
			border-radius: 3px;
			padding: 3px 5px;
			text-transform: uppercase;
			font-size: 10px;
			font-weight: bold;
			margin-right: 10px;
			font-family: "Source Code Pro"
		}

		span.badge.fix{
			background: #F9AA03
		}

		span.badge.chg{
			background: #999
		}

		span.badge.new{
			background: #50B300
		}

		span.badge.chg{
			background: #50B300
		}
	</style>
</head>
<body>
<h1>{{title}}</h1>


	{{#versions}}
<div class="version">
	<h2>{{label}}</h2>
	<ul>
	{{#sections}}
	{{#commits}}
		<li><span class="badge {{label}}">{{label}}</span>{{subject}}</li>
	{{/commits}}
{{/sections}}
	</ul>
</div>
{{/versions}}

</body>
</html>