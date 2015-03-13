    $(document).ready(function(){
        $.getJSON('/budgie/get_allaccounts', function(data){
            var chart = new Highcharts.Chart({
            chart: {
                type: 'series',
                renderTo: 'allaccounts'
            },
            title: {
                text: 'Account Balances'
            },
            xAxis: {
                categories: data[1]
            },
            yAxis: {
                maxPadding: 0.8
            },
            tooltip: {
                formatter: function() {
                    var s;
                    if (this.point.name) { // the pie chart
                        s = ''+
                            this.point.name +': '+ this.y +' USD';
                    } else {
                        s = ''+
                            this.x  +': '+ this.y +' USD';
                    }
                    return s;
                }
            },
            labels: {
                items: [{
                    html: 'Current Total Account Balances',
                    style: {
                        left: '40px',
                        top: '8px',
                        color: 'black'
                    }
                }]
            },
            series: data[0], 
        });
    });
});

    
    
