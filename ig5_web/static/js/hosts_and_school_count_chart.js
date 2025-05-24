function hosts_and_school_count_chart(data, chart_canvas_id) {
  // Credits: https://stackoverflow.com/q/70112637/4183498.
  const corsairPlugin = {
    id: "corsair",
    defaults: {
      width: 1,
      color: "grey",
      dash: [3, 3],
    },
    afterInit: (chart, args, opts) => {
      chart.corsair = {
        x: 0,
        y: 0,
      };
    },
    afterEvent: (chart, args) => {
      const { inChartArea } = args;
      const { type, x, y } = args.event;

      chart.corsair = { x, y, draw: inChartArea };
      chart.draw();
    },
    beforeDatasetsDraw: (chart, args, opts) => {
      const { ctx } = chart;
      const { top, bottom, left, right } = chart.chartArea;
      const { x, y, draw } = chart.corsair;
      if (!draw) return;

      ctx.save();

      ctx.beginPath();
      ctx.lineWidth = opts.width;
      ctx.strokeStyle = opts.color;
      ctx.setLineDash(opts.dash);
      ctx.moveTo(x, bottom);
      ctx.lineTo(x, top);
      ctx.moveTo(left, y);
      ctx.lineTo(right, y);
      ctx.stroke();

      ctx.restore();
    },
  };

  let ctx = document.getElementById(chart_canvas_id);
  let chart = new Chart(ctx, {
    data: {
      datasets: [
        {
          type: "line",
          label: "Organizátor",
          data: data.hosts,
          borderColor: "#db3041",
          backgroundColor: "#db3041",
          pointRadius: 5,
          pointHoverRadius: 7,
          yAxisID: "y_hosts",
        },
        {
          type: "line",
          label: "Počet zúčastnených škôl",
          data: data.school_count,
          borderColor: "#0093dd",
          backgroundColor: "#0093dd",
          pointRadius: 5,
          pointHoverRadius: 7,
          yAxisID: "y_schools",
        },
      ],
    },
    options: {
      interaction: {
        mode: "index",
        intersect: true,
      },
      scales: {
        x: {
          type: "category",
          labels: data.school_count.map((item) => item.x),
        },
        y_hosts: {
          type: "category",
          labels: data.hosts_labels,
          offset: true,
          grid: {
            display: false,
          },
          title: {
            display: true,
            text: "Organizátor",
          },
        },
        y_schools: {
          type: "linear",
          position: "right",
          grid: {
            display: false,
          },
          title: {
            display: true,
            text: "Počet zúčastnených škôl",
          },
        },
      },
    },
    plugins: [corsairPlugin],
  });
  return chart;
}
