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
          height: ({ chart }) => (chart.chartArea || {}).height / data.chart_labels_y.length - 3,
        },
      ],
    },
    options: {
      plugins: {
        legend: false,
        tooltip: {
          callbacks: {
            label: function (context) {
              let school = context.dataset.data[context.dataIndex].y;

              let cat1 = context.dataset.data[context.dataIndex].data.cat1;
              let cat2 = context.dataset.data[context.dataIndex].data.cat2;

              let text = [school];
              let cat1Text = "";
              if (cat1[1] === true) {
                cat1Text += "1. miesto, ";
              }
              if (cat1[2] === true) {
                cat1Text += "2. miesto, ";
              }
              if (cat1[3] === true) {
                cat1Text += "3. miesto, ";
              }
              if (cat1Text) {
                text.push(`1. Kategória: ${cat1Text.slice(0, -2)}`);
              }

              let cat2Text = "";
              if (cat2[1] === true) {
                cat2Text += "1. miesto, ";
              }
              if (cat2[2] === true) {
                cat2Text += "2. miesto, ";
              }
              if (cat2[3] === true) {
                cat2Text += "3. miesto, ";
              }
              if (cat2Text) {
                text.push(`2. Kategória: ${cat2Text.slice(0, -2)}`);
              }

              return text;
            },
          },
        },
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
    plugins: [
      {
        id: "cat1_and_cat2_results",
        afterDatasetsDraw(chart) {
          const ctx = chart.ctx;
          const meta = chart.getDatasetMeta(0);

          meta.data.forEach((rect) => {
            let data = rect.$context.raw.data;

            const gold = "gold";
            const silver = "silver";
            const bronze = "#cd7f32";

            if (data.cat1[1] === true) {
              ctx.fillStyle = gold;
              ctx.fillRect(rect.x + 1, rect.y + 1, rect.width / 2 - 2, rect.height / 2 - 2);
            }
            if (data.cat1[2] === true) {
              ctx.fillStyle = silver;
              ctx.fillRect(rect.x + 1 + rect.width / 2, rect.y + 1, rect.width / 2 - 2, rect.height / 2 - 2);
            }
            if (data.cat1[3] === true) {
              ctx.fillStyle = bronze;
              ctx.fillRect(rect.x + 1 + rect.width / 2, rect.y + 1, rect.width / 2 - 2, rect.height / 2 - 2);
            }

            if (data.cat2[1] === true) {
              ctx.fillStyle = gold;
              ctx.fillRect(rect.x + 1, rect.y + 1 + rect.height / 2, rect.width / 2 - 2, rect.height / 2 - 2);
            }
            if (data.cat2[2] === true) {
              ctx.fillStyle = silver;
              ctx.fillRect(
                rect.x + 1 + rect.width / 2,
                rect.y + 1 + rect.height / 2,
                rect.width / 2 - 2,
                rect.height / 2 - 2
              );
            }
            if (data.cat2[3] === true) {
              ctx.fillStyle = bronze;
              ctx.fillRect(
                rect.x + 1 + rect.width / 2,
                rect.y + 1 + rect.height / 2,
                rect.width / 2 - 2,
                rect.height / 2 - 2
              );
            }
          });
        },
      },
    ],
  });
  return chart;
}
