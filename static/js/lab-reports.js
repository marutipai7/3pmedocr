$(document).ready(function () {
  // --------- BAR CHART (Most Requested Test) ----------
  const barCtx = document.getElementById("barChart").getContext("2d");
  new Chart(barCtx, {
    type: "bar",
    data: {
      labels: ["CBC", "RT-PCR", "Lipid", "Thyroid", "HBAC"],
      datasets: [
        {
          label: "Requests",
          data: [120, 160, 70, 150, 100],
          backgroundColor: ["#3b82f6", "#f97316", "#22c55e", "#8b5cf6", "#a855f7"],
        },
      ],
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
    },
  });

  // --------- PIE CHART (Revenue by Test Type) ----------
  const pieCtx = document.getElementById("pieChart").getContext("2d");
  new Chart(pieCtx, {
    type: "pie",
    data: {
      labels: ["CBC (30%)", "RT-PCR (25%)", "Lipid (18%)", "Thyroid (12%)", "Others (12%)"],
      datasets: [
        {
          data: [30, 25, 18, 12, 12],
          backgroundColor: ["#3b82f6", "#f97316", "#22c55e", "#ef4444", "#eab308"],
        },
      ],
    },
    options: {
      responsive: true,
      plugins: { legend: { position: "top" } },
    },
  });

  // --------- LINE CHART (Bid Trend Price) ----------
  const lineCtx = document.getElementById("lineChart").getContext("2d");
  new Chart(lineCtx, {
    type: "line",
    data: {
      labels: ["Week 1", "Week 2", "Week 3", "Week 4"],
      datasets: [
        {
          label: "CBC",
          data: [320, 340, 310, 360],
          borderColor: "#3b82f6",
          fill: false,
        },
        {
          label: "RT-PCR",
          data: [420, 380, 460, 400],
          borderColor: "#f97316",
          fill: false,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: { legend: { position: "top" } },
    },
  });

  // --------- USER RATINGS ----------
  const ratingData = [
    { stars: 5, percent: 74 },
    { stars: 4, percent: 54 },
    { stars: 3, percent: 38 },
    { stars: 2, percent: 18 },
    { stars: 1, percent: 3 },
  ];

  ratingData.forEach((r) => {
    $("#ratings").append(`
      <div class="flex items-center justify-between">
        <span  class="text-dodger-blue">${r.stars} star</span>
        <div class="w-3/4 bg-[#D3D3D3] rounded-full h-2">
          <div class="bg-[#FFCC48] h-2 rounded-full" style="width:${r.percent}%;"></div>
        </div>
        <span>${r.percent}%</span>
      </div>
    `);
  });

  // --------- DOWNLOAD AS PDF ----------
  $(".download-btn").on("click", function () {
    const targetId = $(this).data("target");
    const { jsPDF } = window.jspdf;
    const pdf = new jsPDF();
    pdf.html(document.getElementById(targetId), {
      callback: function (doc) {
        doc.save(`${targetId}.pdf`);
      },
      x: 10,
      y: 10,
    });
  });

    // --------- HEATMAP ----------
    // Wait for DOM to be ready using jQuery
  
    am4core.useTheme(am4themes_animated);

    // Create map instance
    var chart = am4core.create("heatmap", am4maps.MapChart);

    // Set map definition
    chart.geodata = am4geodata_india2019High;

    // Create map polygon series
    var polygonSeries = chart.series.push(new am4maps.MapPolygonSeries());

    // Set min/max fill color for each area
    polygonSeries.heatRules.push({
        property: "fill",
        target: polygonSeries.mapPolygons.template,
        min: chart.colors.getIndex(1).brighten(1),
        max: chart.colors.getIndex(1).brighten(-0.3)
    });

    // Make map load polygon data (state shapes and names) from GeoJSON
    polygonSeries.useGeodata = true;

    // Set heatmap values for each state
    polygonSeries.data = [
        { id: "IN-JK", value: 0 },
        { id: "IN-MH", value: 6269321325 },
        { id: "IN-UP", value: 0 },
        { id: "US-AR", value: 0 },
        { id: "IN-RJ", value: 0 },
        { id: "IN-AP", value: 0 },
        { id: "IN-MP", value: 0 },
        { id: "IN-TN", value: 0 },
        { id: "IN-JH", value: 0 },
        { id: "IN-WB", value: 0 },
        { id: "IN-GJ", value: 0 },
        { id: "IN-BR", value: 0 },
        { id: "IN-TG", value: 0 },
        { id: "IN-GA", value: 0 },
        { id: "IN-DN", value: 0 },
        { id: "IN-DL", value: 0 },
        { id: "IN-DD", value: 0 },
        { id: "IN-CH", value: 0 },
        { id: "IN-CT", value: 0 },
        { id: "IN-AS", value: 0 },
        { id: "IN-AR", value: 0 },
        { id: "IN-AN", value: 0 },
        { id: "IN-KA", value: 0 },
        { id: "IN-KL", value: 0 },
        { id: "IN-OR", value: 0 },
        { id: "IN-SK", value: 0 },
        { id: "IN-HP", value: 0 },
        { id: "IN-PB", value: 0 },
        { id: "IN-HR", value: 0 },
        { id: "IN-UT", value: 0 },
        { id: "IN-LK", value: 0 },
        { id: "IN-MN", value: 0 },
        { id: "IN-TR", value: 0 },
        { id: "IN-MZ", value: 0 },
        { id: "IN-NL", value: 0 },
        { id: "IN-ML", value: 0 }
    ];

    // Configure series tooltip
    var polygonTemplate = polygonSeries.mapPolygons.template;
    polygonTemplate.tooltipText = "{name}: {value}";
    polygonTemplate.nonScalingStroke = true;
    polygonTemplate.strokeWidth = 0.5;

    // Create hover state and set alternative fill color
    var hs = polygonTemplate.states.create("hover");
    hs.properties.fill = am4core.color("#3c5bdc");

    // Toggle dropdown visibility
    $(document).on('click', '.dropdown-btn', function (e) {
      e.stopPropagation();
      const $dropdown = $(this).closest('.dropdown');
      $('.dropdown-menu').not($dropdown.find('.dropdown-menu')).addClass('hidden');
      $dropdown.find('.dropdown-menu').toggleClass('hidden');
    });

    // Handle selection
    $(document).on('click', '.dropdown-menu li', function (e) {
      const $dropdown = $(this).closest('.dropdown');
      const value = $(this).text();
      $dropdown.find('.dropdown-value').text(value);
      $dropdown.find('.dropdown-menu').addClass('hidden');
    });

    // Close dropdown when clicking outside
    $(document).click(function () {
      $('.dropdown-menu').addClass('hidden');
    });
});
