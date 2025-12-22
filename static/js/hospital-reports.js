$(document).ready(function () {
  // --------- BAR CHART (Most Requested Test) ----------
  const barCtx = document.getElementById("barChart").getContext("2d");
  new Chart(barCtx, {
    type: "bar",
    data: {
      labels: [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "July",
        "Aug",
        "Sept",
        "Oct",
        "Nov",
        "Dec",
      ],
      datasets: [
        {
          label: "Requests",
          data: [120, 160, 70, 150, 100, 50, 80, 100, 59, 90, 150, 200],
          backgroundColor: [
            "#3b82f6",
            "#EF4444",
            "#FFB95A",
            "#84CC16",
            "#22C55E",
            "#1BC0C4",
            "#083684",
            "#8B5CF6",
            "#A855F7",
            "#6366F1",
            "#EC4899",
            "#3B82F6",
          ],
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
      labels: ["Direct (15%)", "NGO Referrals (35%)", "Ads (50%)"],
      datasets: [
        {
          data: [15, 35, 50],
          backgroundColor: ["#EF4444", "#155DFC", "#FFB95A"],
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
      labels: ["10:00", "10:30", "11:00", "11:30"],
      datasets: [
        {
          label: "CBC",
          data: [320, 340, 310, 360],
          borderColor: "#3b82f6",
          fill: false,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: { legend: { position: "top" } },
    },
  });

  const horizontalCtx = document
    .getElementById("horizontalBarChart")
    .getContext("2d");
  new Chart(horizontalCtx, {
    type: "bar",
    data: {
      labels: ["Leads", "Connect", "Booked", "Visited", "Feedback"],
      datasets: [
        {
          axis: "y",
          data: [6000, 5200, 3800, 3300, 1750],
          fill: false,
          backgroundColor: [
            "#3B82F6",
            "#EF4444",
            "#FABA23",
            "#84CC16",
            "#EC4899",
          ],
        },
      ],
    },
    options: {
      responsive: true,
      plugins: { legend: false },
      indexAxis: "y",
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
    max: chart.colors.getIndex(1).brighten(-0.3),
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
    { id: "IN-ML", value: 0 },
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
  $(document).on("click", ".dropdown-btn", function (e) {
    e.stopPropagation();
    const $dropdown = $(this).closest(".dropdown");
    $(".dropdown-menu")
      .not($dropdown.find(".dropdown-menu"))
      .addClass("hidden");
    $dropdown.find(".dropdown-menu").toggleClass("hidden");
  });

  // Handle selection
  $(document).on("click", ".dropdown-menu li", function (e) {
    const $dropdown = $(this).closest(".dropdown");
    const value = $(this).text();
    $dropdown.find(".dropdown-value").text(value);
    $dropdown.find(".dropdown-menu").addClass("hidden");
  });

  // Close dropdown when clicking outside
  $(document).click(function () {
    $(".dropdown-menu").addClass("hidden");
  });
});
