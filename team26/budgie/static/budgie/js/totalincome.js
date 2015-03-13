$(document).ready(function(){
    $.getJSON('/budgie/get_totalincome', function(data){
        var sal = (data[1]/data[0]) * 100;
        var gft = (data[2]/data[0]) * 100;
        var chart = new Highcharts.Chart({
        chart: { 
            type: 'pie',
            renderTo: 'totalincome',
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false
        },
        title: {
            text: data[3]
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
            name: 'Income share',
            data: [
                    ['Salary', sal],
                    { 
                        name: 'Gifts', 
                        y: gft, 
                        sliced: true, 
                        selected: true 
                    }

                ]
            }]
        });
    });
});
    
