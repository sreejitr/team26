    $(document).ready(function(){
        $.getJSON('/budgie/get_checking_accounts', function(data){
            var chart = new Highcharts.Chart({
           chart: {
                type: 'column',
                renderTo: 'checkingaccounts'
            },
            title: {
                text: 'Checking Accounts - Month End Balances'
            },
            xAxis: {
                categories: data[1]
            },
            yAxis: {
                min: 0,
                title: {
                    text: 'Balances (USD)'
                }
            },
            tooltip: {
                headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
                pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                    '<td style="padding:0"><b>{point.y:.1f} USD</b></td></tr>',
                footerFormat: '</table>',
                shared: true,
                useHTML: true
            },
            plotOptions: {
                column: {
                    pointPadding: 0.2,
                    borderWidth: 0
                }
            },
            series: data[0]
        });
    });
});
    
    
