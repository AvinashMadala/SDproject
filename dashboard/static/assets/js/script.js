// alert("heolo")

console.log('read data')
$.get("../data/all_data/", function (resp) {
    let stats = JSON.parse(resp.stats);
    let country_aggs = JSON.parse(resp.country_aggs);
    let month_aggs = JSON.parse(resp.month_aggs);
    // debugger
    // console.log("resp >> ", resp)

    $("#total_count").html(stats.total_confirmed.toLocaleString("en"));
    $("#death_count").html(stats.total_deaths.toLocaleString("en"));
    $("#active_count").html(stats.active.toLocaleString("en"));

    let active_percent = (stats.active / stats.total_confirmed) * 100
    let deaths_percent = (stats.total_deaths / stats.total_confirmed) * 100;

    $("#active_percentage").html(active_percent.toFixed(1) + '%');
    $("#death_percentage").html(deaths_percent.toFixed(1) + "%");
    $("#daily_average").html(stats.daily_avg.toFixed().toLocaleString("en"));


} );

$.get("../data/get_age_data/", function (resp) {
    let data = JSON.parse(resp.data),
      chart_id = "age_donut";
    plot_donut(data, chart_id)
});


function plot_donut(data, chart_id) {
    let _labels = _.map(data, "age_group"),
        _data = _.map(data, "percentage")
    var ctx = document.getElementById(chart_id).getContext("2d");
    var config = {
      type: "doughnut",
      data: {
        labels: [
              'Age: Lessthan 5 years',
              'Age: 5 - 20 years',
              'Age: 20 - 40 years',
              'Age: 40 - 60 years',
              'Age: More than 60 years'],
        datasets: [
          {
            label: "",
            data: _data,
            backgroundColor: [
              "#5cbacc",
              "#66d185",
              "#4e73df",
              "#f5cd54",
              "#ee9e3d",
            ],
          },
        ],
      },
      options: {
        responsive: true,
        legend: {
        //   position: "top",
            display: false
        },
        title: {
          display: false,
        },
        animation: {
          animateScale: true,
          animateRotate: true,
        },
      },
    };

    // plot chart
    new Chart(ctx, config);

}


// MBHE WB22 SLC4 78942