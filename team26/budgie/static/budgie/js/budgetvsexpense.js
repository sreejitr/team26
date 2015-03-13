$(document).ready(function(){
    $.getJSON('/budgie/get_budgetvsexpense', function(data){
        var chart = new Highcharts.Chart({
            chart: {
                type: 'bar',
                renderTo: 'budgetvsexpense'
            },
            title: {
                text: data[2]
            },
            xAxis: {
                categories: ['Housing', 'Transportation', 'Food', 'Education', 'Health', 'Entertainment', 'Gift'],
                title: {
                    text: null
                }
            },
            yAxis: {
                min: 0,
                title: {
                    text: 'Amount (USD)',
                    align: 'high'
                },
                labels: {
                    overflow: 'justify'
                }
            },
            tooltip: {
                valueSuffix: ' USD'
            },
            plotOptions: {
                bar: {
                    dataLabels: {
                        enabled: true
                    }
                }
            },
            legend: {
                layout: 'vertical',
                align: 'right',
                verticalAlign: 'top',
                x: -40,
                y: 100,
                floating: true,
                borderWidth: 1,
                backgroundColor: '#FFFFFF',
                shadow: true
            },
            credits: {
                enabled: false
            },
            series: [{
                name: 'Actual Expense',
                data: data[1]
            }, {
                name: 'Budget',
                data: data[0]
            }]
        });
    });
});
    
