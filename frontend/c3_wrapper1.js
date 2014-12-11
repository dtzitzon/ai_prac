function generateTimeIntervals(startDate, endDate, intervalLength) {
 function correctLength(s) { if (s.toString().length == 1) { s='0'+s } return s }
 var timeRange = endDate - startDate;
 intervalLength *= 60000;
 var numIntervals = timeRange / intervalLength;
 var intervals = new Array();
 for (var i=0; i<numIntervals+1; i++) {
   var date = new Date(startDate.getTime() + i*intervalLength);
   var month = correctLength(date.getMonth() + 1);
   var day = correctLength(date.getDate());
   var minutes = correctLength(date.getMinutes());
   var hours = correctLength(date.getHours());
   var dateString = date.getFullYear() + "-" + month + "-" + day + " " + hours + ':' + minutes
   intervals[i] = dateString
 }
 return intervals;
}


function make_chart(config) { 
	var x_axis_type = '';
	var x_axis_categories = '';
	var x = '';
	var xFormat = '';
	var legend_show = true;
	var y_axis_show = true;
	var axis_rotated = false;
	var adjusted_padding = {'left': 15, 'right': 15}

	if (config.hasOwnProperty('buckets')) {
		x_axis_type = 'category',
		x_axis_categories = config['buckets'] 
	}

	if (config.hasOwnProperty('legend')) {
		legend_show = config['legend']
	}

	if (config.hasOwnProperty('axis_rotated')) {
		axis_rotated = config['axis_rotated']
		adjusted_padding = {'left': 85, 'right': 15}
		y_axis_show = false;
	}

	if (config.hasOwnProperty('y_axis_show')) {
		y_axis_show = config['y_axis_show']
	}

	if (config['x_axis_type']=='timeseries') {
		x_axis_type = 'timeseries';
		x = 'x';
		xFormat = '%Y-%m-%d %I:%M'
		var date_range = config['date_range']
		var index = date_range.indexOf("-->");
		var start_date = new Date(date_range.slice(0,index-1));
		var end_date = new Date(date_range.slice(index+4));
		config['data']['x'] = generateTimeIntervals(start_date, end_date, config['time_interval'])
	}
	
	return c3.generate({
	    bindto: config['bindto'],
	    padding: adjusted_padding,
	    data: {
	    	x: x,
	    	xFormat: xFormat,
	    	type: config['graph_type'],
	    	json: config['data'],
	    	colors: config['colors'],
	    	groups: config['groups']
	    },
	    legend: {
	    	show: legend_show
	    },
	    point: {show: false},
	    axis: {
	    	rotated: axis_rotated,
	    	x: {
	    		type: x_axis_type,
	    		categories: x_axis_categories,
	    		tick: {
	                format: '',
	                count: config['x_axis_ticks']
	            }
	    	},
	    	y: {
	    		padding: {'left': 40, 'right': 10},
	    		show: y_axis_show
	    	}
	    }
	});
};