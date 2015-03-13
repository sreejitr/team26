$(document).ready(function(){
    $.getJSON('/budgie/get_totalexpenses', function(data){
        var expData = new Array();
        var expTotal = 0.0;
        for (var i = 0; i < data.length - 1; i++) {
            expTotal = expTotal + data[i];
            expData[i] = 0.0;
        }
        for (var i = 0; i < data.length - 1; i++) {
            expData[i] = ( data[i] / expTotal ) * 100;
            expData[i] = Math.round(expData[i]*100)/100;
        }
        var title_text = data[7] + expTotal.toString() + " USD";
        var chart = new Highcharts.Chart({
            chart: { 
                type: 'pie',
                renderTo: 'totalexpenses',
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
                        format: '<b>{point.name}</b>: {point.percentage:.1f} %'
                    }
                }
            },
            series: [{
                type: 'pie',
                name: 'Expense share',
                data: [
                    ['Housing', expData[0]],
                    ['Transportation', expData[1]],
                    ['Food', expData[2]],
                    ['Education', expData[3]],
                    ['Health', expData[4]],
                    {
                        name: 'Entertainment',
                        y: expData[5],
                        sliced: true,
                        selected: true
                    },
                    ['Utilities', expData[6]]
                ]
            }]
        });
    });
});
    
