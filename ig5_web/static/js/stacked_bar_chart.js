function stacked_bar_chart(category_stats, chart_canvas_id, x_scale_max) {
  const labels = Object.keys(category_stats);
  const gold = labels.map((school) => category_stats[school][1]?.length || 0);
  const silver = labels.map((school) => category_stats[school][2]?.length || 0);
  const bronze = labels.map((school) => category_stats[school][3]?.length || 0);
  const placeMap = {
    "1. miesto": 1,
    "2. miesto": 2,
    "3. miesto": 3,
  };

  let ctx = document.getElementById(chart_canvas_id);
  let chart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "1. miesto",
          data: gold,
          backgroundColor: "gold",
          stack: "medals",
        },
        {
          label: "2. miesto",
          data: silver,
          backgroundColor: "silver",
          stack: "medals",
        },
        {
          label: "3. miesto",
          data: bronze,
          backgroundColor: "#cd7f32",
          stack: "medals",
        },
      ],
    },
    options: {
      indexAxis: "y",
      responsive: true,
      plugins: {
        tooltip: {
          callbacks: {
            label: function (context) {
              const school = context.label;
              const datasetLabel = context.dataset.label;
              const data = category_stats[school];
              const years = data[placeMap[datasetLabel]] || [];
              if (years.length != 0) {
                return `${datasetLabel}: ${years.length} (${years.join(", ")})`;
              }
              return "";
            },
          },
        },
      },
      interaction: {
        mode: "index",
        intersect: true,
      },
      scales: {
        x: {
          stacked: true,
          beginAtZero: true,
          ticks: {
            stepSize: 2,
          },
          max: x_scale_max,
        },
        y: {
          stacked: true,
          beginAtZero: true,
        },
      },
    },
  });
  return chart;
}
