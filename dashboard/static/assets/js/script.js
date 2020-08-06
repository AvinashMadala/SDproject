

// Card info text boxes
// Default values
var card_info_total_cases = $("#card-info-total-cases .text-value");
var card_info_active_cases = $("#card-info-active-cases .text-value");
var card_info_recovered_cases = $("#card-info-recovered-cases .text-value");
var card_info_death_cases = $("#card-info-death-cases .text-value");
var card_info_country_name = $("#card-info-country-name");

// get all data
$.get("data/all_data/", function (resp) {
    let stats = JSON.parse(resp.stats);
    let country_aggs = JSON.parse(resp.country_aggs);
    let month_aggs = JSON.parse(resp.month_aggs);

    $(".display_total_count").html(stats.total_confirmed.toLocaleString("en"));
    $(".display_death_count").html(stats.total_deaths.toLocaleString("en"));
    $(".display_active_count").html(stats.active.toLocaleString("en"));

    let active_percent = (stats.active / stats.total_confirmed) * 100
    let deaths_percent = (stats.total_deaths / stats.total_confirmed) * 100;

    $(".display_active_percentage").html(active_percent.toFixed(1) + "%");
    $(".display_death_percentage").html(deaths_percent.toFixed(1) + "%");
    $(".display_daily_average").html((stats.daily_avg.toFixed()).toLocaleString("en"));

    // plot line chart
    plot_line_chart(month_aggs, "line_chart");
    plot_progress_bars(country_aggs)

} );

$.get("data/get_age_data/", function (resp) {
    let data = JSON.parse(resp.data),
      chart_id = "age_donut";
    plot_donut(data, chart_id)
});

$("body")
  .on("click", "#accordionSidebar .nav-link", function () {
    let content_id = $(this).attr("nav-controll");
    $("#accordionSidebar .nav-link").removeClass("active")
    $(this).addClass("active")
    $("#content-wrapper .nav-controller").addClass("d-none");
    $(content_id).removeClass("d-none");
    $(content_id).trigger("shown")
  })
  .on("keyup", "#searchCountry", function () {
    let input_text = $(this).val().trim();
    if (input_text == "") {
      $(".country-card").css("display", "block");
    } else {
      $(".country-card").css("display", function () {
        let card_info = this.getAttribute("data-search").toLowerCase();
        return card_info.indexOf(input_text) >= 0 ? "block" : "none";
      });
    }
  })
  .on("click", ".country-card, .fixed-country-card", function () {
    let card_data = $(this).attr("data");
    card_data = JSON.parse(unescape(card_data));
    card_data.active =
      card_data.Confirmed - (card_data.Deaths + card_data.Recovered);
    let country = card_data.country.toUpperCase();
    country = country == "WORLD" ? "All Countries" : country;

    card_info_country_name.html(country);
    card_info_total_cases.html(card_data.Confirmed.toLocaleString("en"));
    card_info_active_cases.html(card_data.active.toLocaleString("en"));
    card_info_death_cases.html(card_data.Deaths.toLocaleString("en"));
    card_info_recovered_cases.html(card_data.Recovered.toLocaleString("en"));
  })
  .on("shown", "#analytics", function () {
    console.log("--> ")
    render_analytics()
  })


function plot_donut(data, chart_id) {
    let _labels = _.map(data, "age_group"),
        _data = _.map(data, "percentage")
    var ctx = document.getElementById(chart_id).getContext("2d");
    var config = {
      type: "doughnut",
      data: {
        labels: [
          "Age: Lessthan 5 years",
          "Age: 5 - 20 years",
          "Age: 20 - 40 years",
          "Age: 40 - 60 years",
          "Age: More than 60 years",
        ],
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
          display: false,
        },
        title: {
          display: false,
        },
        animation: {
          animateScale: true,
          animateRotate: true,
        },
        tooltips: {
          callbacks: {
            title: function (tooltipItem, data) {
              return data["labels"][tooltipItem[0]["index"]];
            },
            label: function (tooltipItem, data) {var dataset = data["datasets"][0];
              var percent = Math.round(
                (dataset["data"][tooltipItem["index"]] /
                  dataset["_meta"][0]["total"]) *
                  100
              );
              return "(" + percent + "%)";
            }
          },
          backgroundColor: "#FFF",
          titleFontSize: 16,
          titleFontColor: "#4e73df",
          bodyFontColor: "#000",
          bodyFontSize: 14,
          displayColors: false,
        },
      },
    };

    // plot chart
    new Chart(ctx, config);

}

function plot_line_chart(data, chart_id) {

    let _labels = _.map(data, "month"),
      _data_confirmed = _.map(data, "Confirmed"),
      _data_death = _.map(data, "Deaths");
    var ctx = document.getElementById(chart_id).getContext("2d");

    var config = {
      type: "line",
      data: {
        labels: _labels,
        datasets: [
          {
            label: "Death cases",
            backgroundColor: "#e96082",
            borderColor: "#e96082",
            data: _data_death,
            fill: true,
          },
          {
            label: "Confirmed cases",
            fill: false,
            backgroundColor: "#52a2ec",
            borderColor: "#52a2ec",
            data: _data_confirmed,
          },
        ],
      },
      options: {
        responsive: true,
        title: {
          display: false,
          text: "Month Wise Cases Ccunt",
        },
        tooltips: {
          mode: "index",
          intersect: false,
        },
        hover: {
          mode: "nearest",
          intersect: true,
        },
        legend: {
          position: "bottom",
          //   display: false,
        },
        scales: {
          xAxes: [
            {
              display: true,
              scaleLabel: {
                display: true,
                labelString: "Month",
              },
            },
          ],
          yAxes: [
            {
              display: true,
              scaleLabel: {
                display: true,
                labelString: "Cases Count",
              },
              ticks: {
                callback: function (label, index, labels) {
                  return Intl.NumberFormat().format(label);
                },
              },
            },
          ],
        },
      },
    };

    // plot chart
    new Chart(ctx, config);
}

function plot_progress_bars(data) {

    var chart_div = $("#bar_charts");
    var progressScale = d3
      .scaleLinear()
      .range([5, 100])
      .domain([
        _.minBy(data, "Confirmed")["Confirmed"],
        _.maxBy(data, "Confirmed")["Confirmed"]
      ]);

    let world_data = {
      country: "world",
      Confirmed: _.sumBy(data, "Confirmed"),
      Deaths: _.sumBy(data, "Deaths"),
      Recovered: _.sumBy(data, "Recovered"),
    };

    card_info_total_cases.html(world_data.Confirmed.toLocaleString("en"));
    card_info_active_cases.html((world_data.Confirmed - (world_data.Recovered + world_data.Deaths)).toLocaleString("en"));
    card_info_recovered_cases.html(world_data.Recovered.toLocaleString("en"));
    card_info_death_cases.html(world_data.Deaths.toLocaleString("en"));

    let bar = `<div class="fixed-country-card p-3 bg-white" title="Click to view details" data="${escape(JSON.stringify(world_data))}" style="position: sticky; top: 0; cursor: pointer; z-index: 1000;" >
                    <h4 class="small font-weight-bold"> World <span class="float-right">${world_data.Confirmed.toLocaleString("en")}</span></h4>
                    <div class="progress mb-4">
                        <div class="progress-bar bg-primary" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100" style="width: 100%;  ">
                            <span class="sr-only">100%</span>
                        </div>
                    </div>
                </div>`;
    chart_div.append(bar)

    _.each(data, d => {
        let country = d.country,
          cases_count = d["Confirmed"],
          display_cases_count = d["Confirmed"].toLocaleString("en"),
          bar_value = progressScale(cases_count),
          data = JSON.stringify(d);

        var bar = `
            <div class="country-card p-3" data-search="${country}" title="Click to view details"  data="${escape(data)}" style="cursor: pointer;" >

                    <h4 class="small font-weight-bold">${country} <i class="float-right fas fa-chevron-right"></i><i class="float-right fas fa-chevron-right ml-2"></i> <span class="float-right">${display_cases_count}</span> </h4>
                    <div class="progress mb-4">
                        <div class="progress-bar bg-primary" aria-valuenow="${bar_value}" aria-valuemin="0" aria-valuemax="100" style="width: ${bar_value}%;  ">
                            <span class="sr-only">${bar_value}%</span>
                        </div>
                    </div>

            </div>`;

        chart_div.append(bar)
    })

}

function render_analytics() {
  $.get("get_analytics/", function (resp) {

    console.log("---> ", resp)
    $("#analytics_chart_1").html(resp.html)

  });
}

