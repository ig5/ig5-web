function schools_matrix_chart(data, chart_canvas_id) {
  let ctx = document.getElementById(chart_canvas_id);
  let chart = new Chart(ctx, {
    type: "matrix",
    data: {
      datasets: [
        {
          data: data.chart_data,
          borderColor: "#0093dd",
          backgroundColor: "#0093dd",
          borderWidth: 0,
          width: ({ chart }) => (chart.chartArea || {}).width / data.chart_labels_y.length - 1,
          height: ({ chart }) => (chart.chartArea || {}).height / data.chart_labels_y.length - 1,
        },
      ],
    },
    options: {
      plugins: {
        legend: false,
      },
      scales: {
        x: {
          type: "category",
          labels: data.chart_labels_x,
        },
        x_top: {
          position: "top",
          type: "category",
          labels: data.chart_labels_x,
        },
        y: {
          type: "category",
          labels: data.chart_labels_y,
          offset: true,
          grid: {
            display: false,
          },
        },
      },
    },
  });
  return chart;
}
