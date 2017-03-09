/*
Highcharts.chart('container', {
    chart: {
        marginRight: 80 // like left
    },
    xAxis: {
        categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    },
    yAxis: [{
        lineWidth: 1,
        title: {
            text: 'Primary Axis'
        }
    }, {
        lineWidth: 1,
        opposite: true,
        title: {
            text: 'Secondary Axis'
        }
    }],

    series: [{
        data: [29.9, 71.5, 106.4, 129.2, 144.0, 176.0, 135.6, 148.5, 216.4, 194.1, 95.6, 54.4]
    }, {
        data: [144.0, 176.0, 135.6, 148.5, 216.4, 194.1, 95.6, 54.4, 29.9, 71.5, 106.4, 129.2],
        yAxis: 1
    }]
});

*/

$(function () {
    var id = $("#container").data("id");
    $.getJSON("/track/curve-data/" + id + "/", function(data){

            for (cat in data){
                for (el in data[cat]){
                    var date_el = data[cat][el][0].split('-');
                    date_el[1] = parseInt(date_el[1]) - 1
                   data[cat][el][0] = Date.UTC.apply(null, date_el);
                }
            }

            $('#container').highcharts({
                chart: {
                    type: 'line'
                },
                plotOptions: {
                    line: {
                        connectNulls: true
                    }
                },
                xAxis: {
                    type: 'datetime',
                    dateTimeLabelFormats: { // don't display the dummy year
                        month: '%e. %b',
                        year: '%b'
                    },
                    title: {
                        text: 'Date'
                    }
                },
                yAxis: [{
                    min: 0,
                    max: data.upper,
                    lineWidth: 1,
                    title: {
                        text: 'Alerts'
                    }
                }, {
                    min: 0,
                    max: data.upper,
                    lineWidth: 1,
                    opposite: true,
                    title: {
                        text: 'Activity'
                    }
                }],
                title: {
                    text: 'Tracker Activity'
                },
                rangeSelector:{
                    enabled:true
                },
                series: [{
                    name: "alerts",
                    data: data.alerts

                }, {
                    name: "activity",
                    data: data.activity,
                    yAxis: 1
                }]
            }); // end line curve

            // pie chart

            var monthNames = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"
                ];


            Highcharts.chart('container-pie', {
                chart: {
                    plotBackgroundColor: null,
                    plotBorderWidth: null,
                    plotShadow: false,
                    type: 'pie'
                },
                title: {
                    text: 'Activity breakdown, ' + data.starts + ' to ' + data.ends,
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
                            format: '<b>{point.name}</b>: {point.percentage:.1f} %',
                            style: {
                                color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
                            }
                        }
                    }
                },
                series: [{
                    name: 'Activity Type',
                    colorByPoint: true,
                    data: [{
                        name: 'alerts',
                        y: data.percent_alerts
                    }, {
                        name: 'cleared',
                        y: 100 - data.percent_alerts,
                        sliced: true,
                        selected: true
                    }]
                }]
            });


        });
    });