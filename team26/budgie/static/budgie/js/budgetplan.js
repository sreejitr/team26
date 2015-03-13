$(document).ready(function(){
    $.getJSON('/budgie/get_budgetplan', function(data){
    	
    	// Radialize the colors
		Highcharts.getOptions().colors = Highcharts.map(Highcharts.getOptions().colors, function(color) {
		    return {
		        radialGradient: { cx: 0.5, cy: 0.3, r: 0.7 },
		        stops: [
		            [0, color],
		            [1, Highcharts.Color(color).brighten(-0.3).get('rgb')] // darken
		        ]
		    }; 
		});
		
		// Build the chart
        var budgData = new Array();
        var budgTotal = 0.0;
        for (var i = 0; i < data.length - 1; i++) {
            budgTotal = budgTotal + data[i];
            budgData[i] = 0.0;
            console.log(budgTotal);
        }
        for (var i = 0; i < data.length - 1; i++) {
            budgData[i] = ( data[i] / budgTotal ) * 100;
            budgData[i] = Math.round(budgData[i]*100) / 100;
            console.log(budgData[i]);
        }

        var title_text = data[7] + budgTotal.toString() + " USD";
        var chart = new Highcharts.Chart({
            chart: {
                type: 'pie',
                renderTo: 'budgetplan',
                plotBackgroundColor: null,
                plotBorderWidth: null,
                plotShadow: false
            },
            title: {
                text: title_text
            },
            tooltip: {
        	    pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
            },
            plotOptions: {
                pie: {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    dataLabels: {
                        enabled: true,
                        color: '#000000',
                        connectorColor: '#000000',
                        formatter: function() {
                            return '<b>'+ this.point.name +'</b>: '+ (this.percentage).toFixed(2) +' %';
                        }
                    }
                }
            },
            series: [{
                type: 'pie',
                name: 'Budget',
                data: [
                    ['Housing', budgData[0]],
                    ['Transportation', budgData[1]],
                    ['Food', budgData[2]],
                    ['Education', budgData[3]],
                    ['Health', budgData[4]],
                    {
                        name: 'Entertainment',
                        y: budgData[5],
                        sliced: true,
                        selected: true
                    },
                    ['Other', budgData[6]]
                ]
            }]
        });
    });
});
    
