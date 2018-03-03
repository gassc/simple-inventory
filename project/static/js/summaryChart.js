function dateify(rec) {
    return {
        x: new Date(rec.x),
        y: rec.y
    };
}

window.chartColors = {
    red: "rgb(255, 99, 132)",
    orange: "rgb(255, 159, 64)",
    yellow: "rgb(255, 205, 86)",
    green: "rgb(75, 192, 192)",
    blue: "rgb(54, 162, 235)",
    purple: "rgb(153, 102, 255)",
    grey: "rgb(201, 203, 207)"
};

// var summaryChartDataCount = summaryChartData.chart_count.map(function(rec) {
//     return dateify(rec);
// });
// console.log(summaryChartDataCount);
// var summaryChartDataProfit = summaryChartData.chart_gross.map(function(rec) {
//     return dateify(rec);
// });
// console.log(summaryChartDataProfit);

var color = Chart.helpers.color;
var timeFormat = "MM/DD/YYYY";
var summaryCountChart = new Chart(
    document.getElementById("summaryCountChart"), {
        type: "bar",
        data: {
            datasets: [{
                label: "Total",
                type: "line",
                backgroundColor: color(window.chartColors.green)
                    .alpha(0.5)
                    .rgbString(),
                borderColor: window.chartColors.green,
                data: summaryChartData.chart_count.map(function(rec) {
                    return dateify(rec);
                })
            }]
        },
        options: {
            title: {
                text: "Transactions Per Day"
            },
            scales: {
                xAxes: [{
                    type: "time",
                    display: true,
                    time: {
                        format: timeFormat
                    }
                }]
            },
            elements: {
                line: {
                    tension: 0 // disables bezier curves
                }
            }
        }
    }
);

var summarySalesChart = new Chart(
    document.getElementById("summarySalesChart"), {
        type: "bar",
        data: {
            datasets: [{
                label: "Daily Profits ($)",
                type: "bar",
                backgroundColor: color(window.chartColors.green)
                    .alpha(0.5)
                    .rgbString(),
                borderColor: window.chartColors.green,
                data: summaryChartData.chart_gross.map(function(rec) {
                    return dateify(rec);
                })
            }]
        },
        options: {
            title: {
                text: "Gross Sales per Day"
            },
            scales: {
                xAxes: [{
                    type: "time",
                    display: true,
                    time: {
                        format: timeFormat
                    }
                }]
            },
            elements: {
                line: {
                    tension: 0 // disables bezier curves
                }
            }
        }
    }
);