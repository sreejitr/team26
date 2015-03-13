$(document).ready(function(){
        $.getJSON('/budgie/get_incvsexp', function(data){
            var chart = new Highcharts.Chart({
            chart: {
                type: 'areaspline',
                renderTo: 'incvsexp'
            },
            title: {
                text: 'Income VS Expenses'
            },
            legend: {
                layout: 'vertical',
                align: 'left',
                verticalAlign: 'top',
                x: 150,
                y: 100,
                floating: true,
                borderWidth: 1,
                backgroundColor: '#FFFFFF'
            },
            xAxis: {
                categories: data[1],
                plotBands: [{ 
                    from: 4.5,
                    to: 6.5,
                    color: 'rgba(68, 170, 213, .2)'
                }]
            },
            yAxis: {
                title: {
                    text: 'Amount'
                }
            },
            tooltip: {
                shared: true,
                valueSuffix: ' USD'
            },
            credits: {
                enabled: false
            },
            plotOptions: {
                areaspline: {
                    fillOpacity: 0.5
                }
            },
            series: data[0]
        });
    });
});
    
