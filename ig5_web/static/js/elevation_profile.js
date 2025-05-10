function renderElevationProfileChart(elevation_data, elevation_data_sites) {
  const distances = elevation_data[0];
  const elevations = elevation_data[1];
  if (distances.length === 0) {
    return;
  }

  const distances_sites = elevation_data_sites[0];
  const elevations_sites = elevation_data_sites[1];
  const sites_scatter_data = elevations_sites.map((site, index) => ({
    x: distances_sites[index],
    y: site.elevation,
  }));

  const yLabel = "Nadmorská výška (m n.m.)";
  const ctx = document.getElementById("elevationChart").getContext("2d");
  const elevationChart = new Chart(ctx, {
    data: {
      labels: distances,
      datasets: [
        {
          type: "scatter",
          label: "Stanoviská",
          data: sites_scatter_data,
          borderColor: "#db3041",
          backgroundColor: "#db3041",
          pointStyle: "circle",
          pointRadius: 5,
          pointHoverRadius: 7,
        },
        {
          type: "line",
          label: yLabel,
          data: elevations,
          borderColor: LINE_COLOR,
          backgroundColor: "rgba(0,147,221,0.5)",
          borderWidth: 5,
          fill: true,
          tension: 0.4,
          pointRadius: 0,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        tooltip: {
          callbacks: {
            label: function (context) {
              if (context.dataset.type === "scatter") {
                let site = elevations_sites[context.dataIndex];
                return ` ${site.name}: ${site.description}`;
              }
              return ` Nadmorská výška: ${context.raw} m n.m.`;
            },
            title: function (context) {
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
          type: "category",
          title: {
            display: true,
            text: "Vzdialenosť od štartu (m)",
          },
          ticks: {
            display: true,
            maxTicksLimit: 10,
          },
          grid: {
            maxTicksLimit: 5,
            tickLength: 0,
          },
        },
        y: {
          title: {
            display: true,
            text: "Nadmorská výška (m n.m.)",
          },
        },
      },
    },
  });
  return elevationChart;
}
