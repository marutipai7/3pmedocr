$(document).ready(function () {
  //closing widgets
  $(".close-widget-btn").on("click", function () {
    $(this).closest(".widget").hide();
  });

  const regionalSalesChart = new Chart($("#regionalSalesChart"), {
    type: "bar",
    data: {
      labels: ["North", "South", "East", "West"],
      datasets: [
        {
          label: "Sales",
          data: [120, 200, 150, 110],
          backgroundColor: "#3B82F6",
          borderRadius: 5,
          barThickness: 40,
        },
      ],
    },
    options: {
      plugins: {
        legend: { display: false },
        datalabels: {
          anchor: "end",
          align: "end",
          color: "#A1A9BC",
          font: { weight: "normal" },
          formatter: (value) => value,
        },
      },
      scales: {
        x: {
          grid: {
            display: false,
          },
        },
        y: {
          beginAtZero: true,
          grid: {
            drawBorder: false,
            color: "rgba(0,0,0,0.1)",
            borderDash: [4, 4],
          },
        },
      },
    },
    plugins: [ChartDataLabels],
  });

  // Monthly Buyers
  new Chart($("#monthlyBuyersChart"), {
    type: "bar",
    data: {
      labels: [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
      ],
      datasets: [
        {
          label: "Buyers",
          data: [110, 160, 140, 100, 90, 80, 120, 150, 170, 190, 130, 160],
          backgroundColor: [
            "#F87171",
            "#FBBF24",
            "#34D399",
            "#60A5FA",
            "#A78BFA",
            "#F472B6",
            "#F97316",
            "#10B981",
            "#6366F1",
            "#EF4444",
            "#22D3EE",
            "#D946EF",
          ],
          borderRadius: 5,
          barThickness: 15,
        },
      ],
    },
    options: {
      plugins: {
        legend: { display: false },
      },
      scales: {
        x: {
          grid: {
            display: false,
          },
          ticks: {
            maxRotation: 0,
            minRotation: 0,
            autoSkip: false,
          },
        },
        y: {
          beginAtZero: true,
          grid: {
            drawBorder: false,
            color: "rgba(0,0,0,0.1)",
            borderDash: [4, 4],
          },
        },
      },
    },
  });

  const ctx1 = document.getElementById("monthlySellersChart").getContext("2d");
  new Chart(ctx1, {
    type: "line",
    data: {
      labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
      datasets: [
        {
          label: "Monthly Sellers",
          data: [60, 30, 75, 60, 70, 65],
          borderColor: "#EF4444",
          backgroundColor: "rgba(239, 68, 68, 0.15)",
          fill: true,
          tension: 0,
          pointRadius: 0,
          borderWidth: 2,
        },
      ],
    },
    options: {
      plugins: {
        legend: { display: false },
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: { stepSize: 30 },
          grid: { color: "#eee" },
        },
        x: {
          grid: { display: false },
        },
      },
    },
  });

  const ctx2 = document.getElementById("monthlyRevenueChart").getContext("2d");
  new Chart(ctx2, {
    type: "line",
    data: {
      labels: [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
      ],
      datasets: [
        {
          label: "Monthly Sellers",
          data: [120, 200, 80, 150, 110, 200, 50, 80, 200, 100, 60, 25],
          borderColor: "#FFB95A",
          backgroundColor: "rgba(239, 68, 68, 0.15)",
          fill: false,
          tension: 0,
          pointRadius: 0,
          borderWidth: 2,
        },
      ],
    },
    options: {
      plugins: {
        legend: { display: false },
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: { stepSize: 30 },
          grid: { color: "#eee" },
        },
        x: {
          grid: { display: false },
        },
      },
    },
  });

  const graphPreviewChart = initChart("graphPreviewChart", {
    type: "line",
    data: {
      labels: ["0", "1", "2", "3", "4", "5", "6", "7"],
      datasets: [
        {
          label: "Sale",
          data: [600, 400, 590, 650, 800, 400, 160, 570],
          borderColor: "#CD6200",
          borderWidth: 2,
          tension: 0,
          yAxisID: "yLeft",
          pointRadius: 3,
          pointBackgroundColor: "#FFFFFF",
          pointBorderColor: " #CD6200",
          pointHoverRadius: 5,
          pointHoverBackgroundColor: "#FFFFFF",
          pointHoverBorderColor: " #CD6200",
        },
        {
          label: "Reven",
          data: [600, 700, 300, 250, 200, 600, 180, 700],
          borderColor: "#3AAFA9",
          borderWidth: 2,
          tension: 0,
          yAxisID: "yRight",
          pointRadius: 3,
          pointBackgroundColor: "#FFFFFF",
          pointBorderColor: "#3AAFA9",
          pointHoverRadius: 5,
          pointHoverBackgroundColor: "#FFFFFF",
          pointHoverBorderColor: "#3AAFA9",
        },
      ],
    },
    options: getChartOptions(),
  });

  //  View Report Popup chart
  const viewReportChartCustom = initChart("viewReportChartCustom", {
    type: "line",
    data: {
      labels: ["0", "1", "2", "3", "4", "5", "6", "7"],
      datasets: [
        {
          label: "Sales Volume",
          data: [600, 400, 590, 650, 800, 400, 160, 570],
          borderColor: "#CD6200",
          borderWidth: 2,
          tension: 0,
          yAxisID: "yLeft",
          pointRadius: 3,
          pointBackgroundColor: "#FFFFFF",
          pointBorderColor: " #CD6200",
          pointHoverRadius: 5,
          pointHoverBackgroundColor: "#FFFFFF",
          pointHoverBorderColor: " #CD6200",
        },
        {
          label: "Revenue",
          data: [600, 700, 300, 250, 200, 600, 180, 700],
          borderColor: "#3AAFA9",
          borderWidth: 2,
          tension: 0,
          yAxisID: "yRight",
          pointRadius: 3,
          pointBackgroundColor: "#FFFFFF",
          pointBorderColor: "#3AAFA9",
          pointHoverRadius: 5,
          pointHoverBackgroundColor: "#FFFFFF",
          pointHoverBorderColor: "#3AAFA9",
        },
      ],
    },
    options: getChartOptions(),
  });

  //custom legend
  const charts = [
    {
      chart: viewReportChartCustom,
      legendId: "#viewReportCustomLegend",
      tabsId: "#viewReportCustomTabs",
    },
    {
      chart: graphPreviewChart,
      legendId: "#graphPreviewLegend",
      tabsId: "#graphPreviewTabs",
    },
  ];
  charts.forEach(({ chart, legendId, tabsId }) => {
    $(`${legendId} .legend-checkbox`).on("change", function () {
      const datasetIndex = $(this).data("index");
      const visible = $(this).is(":checked");
      chart.setDatasetVisibility(datasetIndex, visible);
      chart.update();
    });

    // Time Range Tabs
    $("[data-active-class] p").click(function () {
      const $section = $(this).closest("[data-active-class]");
      const activeClass = $section.data("active-class");
      $section.find("p").removeClass(activeClass);
      $(this).addClass(activeClass);
    });
  });

  // Opening all Popups
  $(".popup-btn").on("click", function () {
    let popupId = $(this).data("popup");
    $("." + popupId)
      .removeClass("hidden")
      .addClass("flex");
  });

  // Closing all popups
  $(".close-popup").on("click", function () {
    let popupId = $(this).data("popup");
    $(this)
      .closest("." + popupId)
      .addClass("hidden")
      .removeClass("flex");
  });

  //Selecting single checkbox at a time
  $(".file-checkbox").on("change", function () {
    $(".file-checkbox").each(function () {
      if (this !== event.target) {
        $(this).prop("checked", false);
      }
    });
  });

  // Function to add a metric to the selected list for Report filter popup on standard tab section
  function addMetricToSelected(metricText) {
    const newMetricHtml = `
    <div class="flex items-center gap-3 selected-metric-item" data-metric="${metricText}">
       <input type="checkbox" class="text-dark-blue ring-1 ring-dark-blue focus:ring-offset-0 rounded-xs cursor-pointer" checked disabled>
        <p class="font-normal text-base text-dark-gray">${metricText}</p>
    </div>`;
    $("#selectedMetricsDisplay").append(newMetricHtml);
  }
  function removeMetricFromSelected(metricText) {
    $("#selectedMetricsDisplay")
      .find(`.selected-metric-item[data-metric="${metricText}"]`)
      .remove();
  }
  $('#availableMetrics input[type="checkbox"]').on("change", function () {
    const metricText = $(this).data("metric");
    if ($(this).is(":checked")) {
      addMetricToSelected(metricText);
    } else {
      removeMetricFromSelected(metricText);
    }
  });

  // Dropdowns
  const dropdownConfig = {
    "report-period-dropdown": {
      options: ["Historical", "Real-Time"],
      selected: "",
    },
    "gender-dropdown": {
      options: ["Male", "Female", "Others"],
      selected: "",
    },
    "section-dropdown": {
      options: ["Pharma", "Activity", "Platform"],
      selected: "",
    },
    "country-dropdown": {
      options: ["China", "Ireland", "India", "Indonesia"],
      slected: "",
    },
    "state-dropdown": {
      options: ["Karnataka", "Maharashtra", "Kerala", "Gujarat"],
      selected: "",
    },
    "city-dropdown": {
      options: ["Mumbai", "Pune", "Chennai", "Hyderabad"],
      selected: "",
    },
    "pincode-dropdown": {
      options: ["411001", "411002", "411003", "411004"],
      selected: "",
    },
    "payments-dropdown": {
      options: ["Payment Gateway", "UPI", "Cards"],
      selected: [],
    },
    "chart-type-dropdown": {
      options: [
        "Bar",
        "Line",
        "Pie",
        "Area",
        "Scatter",
        "Candle",
        "Non-Conventional",
        "Heatmap",
        "Bubble",
        "Radar",
        "Funnel",
        "Sankey",
      ],
      selected: "",
    },
    "primary-X-axis-metrics-dropdown": {
      options: ["Metrics 1", "Metrics 2", "Metrics 3", "Metrics 4"],
      selected: "",
    },
    "primary-Y-axis-metrics-dropdown": {
      options: ["Metrics 1", "Metrics 2", "Metrics 3", "Metrics 4"],
      selected: "",
    },
    "secondary-X-axis-metrics-dropdown": {
      options: ["Metrics 1", "Metrics 2", "Metrics 3", "Metrics 4"],
      selected: "",
    },
    "secondary-Y-axis-metrics-dropdown": {
      options: ["Metrics 1", "Metrics 2", "Metrics 3", "Metrics 4"],
      selected: "",
    },
    "widget-dropdown": {
      options: ["Card", "Bar Graph", "Line Graph", "Area Graph", "Pie chart"],
      selected: "",
    },
    "dashboard-section-dropdown": {
      options: ["Pharma", "Activity", "Platform"],
      selected: "",
    },
    "dashboard-metric-dropdown": {
      options: ["Metrics 1", "Metrics 2", "Metrics 3", "Metrics 4"],
      selected: "",
    },
    "dashboard-period-dropdown": {
      options: ["Historical", "Real-Time"],
      selected: "",
    },
    "dashboard-notification-dropdown": {
      options: [
        "In-App Notifications",
        "Push Notification",
        "Email Notification",
      ],
      selected: "",
    },
    "map-type-dropdown": {
      options: ["Grid View", "Map Icon View", "Geo Heat View", "Bubble View"],
      selected: "",
    },
    "heatmap-section-dropdown": {
      options: ["Pharma", "Activity", "Platform"],
      selected: "",
    },
    "heatmap-metric-dropdown": {
      options: ["Metrics 1", "Metrics 2", "Metrics 3", "Metrics 4"],
      selected: "",
    },
    "heatmap-period-dropdown": {
      options: ["Historical", "Real-Time"],
      selected: "",
    },
    "heatmap-country-dropdown": {
      options: ["China", "Ireland", "India", "Indonesia"],
      slected: "",
    },
    "heatmap-state-dropdown": {
      options: ["Karnataka", "Maharashtra", "Kerala", "Gujarat"],
      selected: "",
    },
    "heatmap-city-dropdown": {
      options: ["Mumbai", "Pune", "Chennai", "Hyderabad"],
      selected: "",
    },
    "heatmap-pincode-dropdown": {
      options: ["411001", "411002", "411003", "411004"],
      selected: "",
    },
    "heatmap-notification-dropdown": {
      options: [
        "In-App Notifications",
        "Push Notification",
        "Email Notification",
      ],
      selected: "",
    },
    "report-real-time-dropdown":{
      options:['Last 6 Hrs','Last 12 Hrs','Last 24 Hrs','Custom : (Last ____ mins / Last ___ Hrs Max 48 Hrs)'],
      selected:"",
    },
     "dashboard-real-time-dropdown":{
      options:['Last 6 Hrs','Last 12 Hrs','Last 24 Hrs','Custom : (Last ____ mins / Last ___ Hrs Max 48 Hrs)'],
      selected:"",
    },
     "heatmap-real-time-dropdown":{
      options:['Last 6 Hrs','Last 12 Hrs','Last 24 Hrs','Custom : (Last ____ mins / Last ___ Hrs Max 48 Hrs)'],
      selected:"",
    }
  };
  function renderDropdown(dropdownId) {
  
  const $wrapper = $("#" + dropdownId);
  const $menu = $wrapper.find(".dropdown-menu");
  const { options, selected } = dropdownConfig[dropdownId];

  // Check if this is a real-time dropdown based on the presence of the input field
  const $realTimeInput = $wrapper.find('.real-time-input');
  const isRealTimeDropdown = $realTimeInput.length > 0;

  $menu.empty();

  // Dynamically render the options for all dropdowns
  options.forEach((opt) => {
    const isSelected = Array.isArray(selected)
      ? selected.includes(opt)
      : selected === opt;

    const item = $(`
      <div
        class="dropdown-option flex items-center gap-1 py-2 cursor-pointer text-base ${
          isSelected ? "text-dark-blue font-bold" : "text-dark-gray font-normal"
        }"
        data-value="${opt}"
        data-dropdown="${dropdownId}"
      >
        ${isSelected ? '<span class="material-symbols-outlined text-sm pl-3">check</span>' : '<span class="w-[18px]"></span>'}
        <span>${opt}</span>
      </div>
    `);
    $menu.append(item);
  });

  // --- Logic for Real-Time Dropdowns ---
  if (isRealTimeDropdown) {
  
    if (typeof selected === "string" && selected.includes("Custom")) {
      // If "Custom" is selected, enable the input and set its value
      $realTimeInput.val('').prop('readonly', false).focus();
    } else if (typeof selected === "string" && selected !== "") {
      // If a non-custom option is selected, update the input value and make it readonly
       $realTimeInput.val(selected).prop('readonly', true);
      
         
    } else {
      // If nothing is selected, clear the input and keep it readonly
      const placeholder = $wrapper.data("placeholder") || "Select Period";
      $realTimeInput.val("").prop('readonly', true).attr('placeholder', placeholder);
    }
    
  } 
  // --- Logic for Standard Dropdowns ---
  else {
    const $display = $wrapper.find(".dropdown-display");
    $display.empty();

    if (Array.isArray(selected) && selected.length > 0) {
      if (dropdownId === "payments-dropdown") {
        const text = selected.length === 1 ? "1 Method Selected" : `${selected.length} Methods Selected`;
        $display.append(`<span class="dropdown-placeholder text-dark-gray text-xs font-semibold">${text}</span>`);
      } else {
        selected.forEach((val) => {
          const chip = `
            <span class="selected-chip bg-white text-dark-gray font-semibold text-sm rounded-full px-3 py-1 shadow flex items-center gap-2">
              ${val}
              <button class="remove-chip text-xl font-bold leading-none cursor-pointer" data-dropdown="${dropdownId}" data-value="${val}">&times;</button>
            </span>`;
          $display.append(chip);
        });
      }
    } else if (typeof selected === "string" && selected !== "") {
      const chip = `
        <span class="selected-chip bg-white text-dark-gray font-semibold text-sm rounded-full px-3 py-1 shadow flex items-center gap-2">
          ${selected}
          <button class="remove-chip text-xl font-bold leading-none cursor-pointer" data-dropdown="${dropdownId}">&times;</button>
        </span>`;
      $display.append(chip);
    } else {
      const placeholder = $wrapper.data("placeholder") || "Select Option";
      $display.append(`<span class="dropdown-placeholder text-dark-gray text-xs font-semibold">${placeholder}</span>`);
    }
  }
}
  $(document).on("click", ".dropdown-toggle", function (e) {
    e.stopPropagation();
    const $wrapper = $(this).closest(".dropdown-wrapper");
    const $menu = $wrapper.find(".dropdown-menu");
    $(".dropdown-menu").not($menu).addClass("hidden");
    $menu.toggleClass("hidden");
  });
$(document).on("click", ".dropdown-option", function () {
  const value = String($(this).data("value")).trim();
  const dropdownId = $(this).data("dropdown");
  const current = dropdownConfig[dropdownId].selected;

  if (Array.isArray(current)) {
    const index = current.indexOf(value);
    if (index > -1) {
      current.splice(index, 1);
    } else {
      current.push(value);
    }
  } else {
    // If a custom option is selected, store the value and make the input editable
    if (value.includes("Custom")) {
      dropdownConfig[dropdownId].selected = value;
    } else {
      // For all other options, just set the selected value
      dropdownConfig[dropdownId].selected = value;
    }
  }
  
  renderDropdown(dropdownId);
  $(".dropdown-menu").addClass("hidden");

  // Keep your existing logic for showing/hiding other elements based on the period type
  const baseClass = dropdownId.replace("-period-dropdown", "");
  const fromWrapper = baseClass ? `.${baseClass}-from-wrapper` : `.from-wrapper`;
  const toWrapper = baseClass ? `.${baseClass}-to-wrapper` : `.to-wrapper`;
  const realTimeDropdown = baseClass ? `.${baseClass}-real-time-dropdown` : `.real-time-dropdown`;

  if (value === "Historical") {
    $(fromWrapper).removeClass("hidden");
    $(toWrapper).removeClass("hidden");
    $(realTimeDropdown).addClass("hidden");
  } else if (value.includes("Real-Time")) {
    $(fromWrapper).addClass("hidden");
    $(toWrapper).addClass("hidden");
    $(realTimeDropdown).removeClass("hidden");
  }
});
$(document).on("input", ".real-time-input", function() {
  const $wrapper = $(this).closest(".dropdown-wrapper");
  const dropdownId = $wrapper.attr("id");
  const inputValue = $(this).val();

  // Only update the selected value if the input belongs to a custom-selected dropdown
  
    dropdownConfig[dropdownId].selected = `Custom : ${inputValue}`;
  
});
  $(document).on("click", ".remove-chip", function () {
    const dropdownId = $(this).data("dropdown");
    const value = $(this).data("value");
    const current = dropdownConfig[dropdownId].selected;

    if (Array.isArray(current)) {
      const index = current.indexOf(value);
      if (index > -1) current.splice(index, 1);
    } else {
      dropdownConfig[dropdownId].selected = "";
    }

    renderDropdown(dropdownId);
  });
  $(document).on("click", function (e) {
    if (!$(e.target).closest(".dropdown-wrapper").length) {
      $(".dropdown-menu").addClass("hidden");
    }
  });
  Object.keys(dropdownConfig).forEach(renderDropdown);

  //Section dropdown on standard,custom and saved tabs
  $(".section-dropdown-toggle").on("click", function () {
    $(this).siblings(".section-dropdown-menu").toggleClass("hidden");
  });
  $(".section-dropdown-option").on("click", function () {
    const selectedText = $(this).text().trim();
    const $container = $(this).closest(".section-dropdown-container");

    $container.find(".section-dropdown-input").val(selectedText);
    $container.find(".section-dropdown-menu").addClass("hidden");
  });
  $(document).on("click", function (e) {
    if (!$(e.target).closest(".section-dropdown-container").length) {
      $(".section-dropdown-menu").addClass("hidden");
    }
  });

  // Save icon
  $('.material-symbols-outlined:contains("bookmark")').on("click", function () {
    $(this).toggleClass("material-filled text-dark-blue");
  });

  //Adding receipents
  const availableTags = [
    "john.doe@gmail.com",
    "jane.smith@gmail.com",
    "alex.jordan@gmail.com",
    "emma.wilson@gmail.com",
    "chris.brown@gmail.com",
    "linda.white@gmail.com",
    "michael.scott@gmail.com",
    "sara.connor@gmail.com",
    "peter.parker@gmail.com",
    "tony.stark@gmail.com",
  ];
  let tags = [];
  const maxTags = 8;
  function renderTags() {
    $(".tag-box .tag-chip").remove();

    tags.forEach((tag, index) => {
      const tagEl = $(`
      <span class="tag-chip inline-flex items-center bg-[#F1F8FF] text-dark-gray px-2 py-0.5 rounded-full text-sm font-normal">
        ${tag}
        <button type="button" class="ml-1 text-jet-black text-sm cursor-pointer" data-index="${index}">&times;</button>
      </span>
    `);

      $(".tag-input").before(tagEl);
    });
  }
  $(".tag-input").on("input", function () {
    const query = $(this).val().trim().toLowerCase();
    const $suggestions = $(".tag-suggestions");

    if (!query) {
      $suggestions.empty().css("visibility", "hidden");
      return;
    }

    const matches = availableTags
      .filter((tag) => tag.toLowerCase().includes(query) && !tags.includes(tag))
      .slice(0, 5);

    if (matches.length === 0) {
      $suggestions.empty().css("visibility", "hidden");
      return;
    }

    const html = matches
      .map(
        (tag) => `
    <div class="px-4 py-2 hover:bg-dark-blue hover:text-white cursor-pointer" data-tag="${tag}">
      ${tag}
    </div>
  `
      )
      .join("");

    $suggestions.html(html).css("visibility", "visible");
  });
  $(".tag-suggestions").on("mousedown", "[data-tag]", function (e) {
    e.stopPropagation();

    const selectedTag = $(this).data("tag");

    if (tags.includes(selectedTag)) {
      window.showToaster?.("error", "Tag already selected.");
      return;
    }

    if (tags.length >= maxTags) {
      window.showToaster?.("error", "Only 8 tags can be selected.");
      return;
    }

    tags.push(selectedTag);
    renderTags();
    $(".tag-input").val("");
    $(".tag-suggestions").empty().css("visibility", "hidden");
  });
  $(".tag-input").on("keypress", function (e) {
    if (e.which === 13) {
      e.preventDefault();
      const newTag = $(this).val().trim();
      if (newTag && !tags.includes(newTag)) {
        if (tags.length < maxTags) {
          tags.push(newTag);
          renderTags();
          $(this).val("");
          $(".tag-suggestions").empty().css("visibility", "hidden");
        } else {
          window.showToaster?.("error", "Only 8 tags can be selected.");
        }
      } else {
        $(".tag-suggestions").empty().css("visibility", "hidden");
      }
    }
  });
  $(".tag-box").on("click", "button", function () {
    const index = $(this).data("index");
    tags.splice(index, 1);
    renderTags();
  });

  //Adding Email in Popup of Dashboard Section
  $(".email-tag-input").each(function () {
    const input = $(this);
    const container = input.closest(".tag-container");

    function addTag(text) {
      if (!text) return;

      const tag = $(`
      <div class="flex items-center bg-white border border-gray-300 px-3 py-1 rounded-full shadow text-sm">
        <span class="mr-2">${text}</span>
        <button class="remove-tag   focus:outline-none cursor-pointer">&times;</button>
      </div>
    `);

      tag.find(".remove-tag").click(function () {
        tag.remove();
      });

      tag.insertBefore(input);
    }

    input.on("keydown", function (e) {
      if (e.key === "Enter" || e.key === "," || e.key === " ") {
        e.preventDefault();
        const text = input.val().trim().replace(/,$/, "");
        addTag(text);
        input.val("");
      }
    });
  });

  // jquery ui calendar for report scheduler popup
  $(".calendar-wrapper").each(function () {
    const $wrapper = $(this);
    const $input = $wrapper.find(".start-date-range");
    const $label = $wrapper.find(".selected-date");
    const $trigger = $wrapper.find(".custom-date-trigger");

    $input.datepicker({
      dateFormat: "dd/mm/yy",
      changeYear:true,
      changeMonth:true,
       yearRange:'2015:'+ new Date().getFullYear(),
      onSelect: function (dateText) {
        $label.text(dateText);
      },
    });

    $trigger.on("click", function () {
      $input.datepicker("show");
    });
  });

  //Custom date time selector
  function renderCalendar(year, month) {
    const monthNames = [
      "January",
      "February",
      "March",
      "April",
      "May",
      "June",
      "July",
      "August",
      "September",
      "October",
      "November",
      "December",
    ];
    const $label = $("#monthYearLabel");
    const $calendarDays = $("#calendarDays");
    const today = new Date();
    const isCurrentMonth =
      today.getFullYear() === year && today.getMonth() === month;
    const currentDate = today.getDate();
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const startDay = (firstDay + 6) % 7;
    const prevMonthDays = new Date(year, month, 0).getDate();
    $label.text(`${monthNames[month]} ${year}`);
    $calendarDays.empty();
    for (let i = startDay - 1; i >= 0; i--) {
      $calendarDays.append(
        `<span class="opacity-50">${prevMonthDays - i}</span>`
      );
    }
    for (let i = 1; i <= daysInMonth; i++) {
      const isToday = isCurrentMonth && i === currentDate;
      const todayClass = isToday
        ? "bg-dark-blue text-white font-semibold rounded-full"
        : "";
      $calendarDays.append(
        `<span class="calendar-day cursor-pointer hover:bg-dark-blue hover:text-white rounded-full  ${todayClass}" data-day="${i}">${i}</span>`
      );
    }
    const totalCells = startDay + daysInMonth;
    const remaining = (7 - (totalCells % 7)) % 7;
    for (let i = 1; i <= remaining; i++) {
      $calendarDays.append(`<span class="opacity-50">${i}</span>`);
    }
  }
  // Selected date logic
  $(document).on("click", ".calendar-day", function () {
    $(".calendar-day").removeClass(
      "bg-dark-blue text-white font-semibold selected-date"
    );
    $(this).addClass("bg-dark-blue text-white font-semibold selected-date");
    const selectedDay = $(this).data("day");
    const selectedMonth = $("#monthYearLabel").text();
    console.log(`Selected Date: ${selectedDay} ${selectedMonth}`);
  });
  let currentDate = new Date();
  let currentYear = currentDate.getFullYear();
  let currentMonth = currentDate.getMonth();
  renderCalendar(currentYear, currentMonth);

  // Event Listeners
  $("#prevMonth").on("click", function () {
    currentMonth--;
    if (currentMonth < 0) {
      currentMonth = 11;
      currentYear--;
    }
    renderCalendar(currentYear, currentMonth);
  });
  $("#nextMonth").on("click", function () {
    currentMonth++;
    if (currentMonth > 11) {
      currentMonth = 0;
      currentYear++;
    }
    renderCalendar(currentYear, currentMonth);
  });

  // Switch tab
  $("#gotoTimeTab").on("click", function () {
    $(".tabs-btn[data-tab='time']").trigger("click");
  });
  let selectedDay = null;
  let selectedMonthIndex = null;
  let selectedYear = null;
  // Handle calendar day click
  $(document).on("click", ".calendar-day", function () {
    $(".calendar-day").removeClass(
      "bg-dark-blue text-white font-semibold selected-date"
    );
    $(this).addClass("bg-dark-blue text-white font-semibold selected-date");

    selectedDay = $(this).data("day");
    const [monthText, yearText] = $("#monthYearLabel").text().split(" ");
    selectedMonthIndex = new Date(`${monthText} 1, ${yearText}`).getMonth();
    selectedYear = parseInt(yearText);
  });

  //setting date and time
  $('#time-tab button:contains("Set")').on("click", function () {
    if (selectedDay && selectedMonthIndex !== null && selectedYear) {
      // Format date: DD/MM/YYYY
      const formattedDate =
        `${selectedDay.toString().padStart(2, "0")}/` +
        `${(selectedMonthIndex + 1).toString().padStart(2, "0")}/` +
        `${selectedYear}`;

      // Convert to 12-hour time with AM/PM
      let hour = parseInt(selectedHour);
      const minute = selectedMinute.padStart(2, "0");
      const ampm = hour >= 12 ? "PM" : "AM";
      hour = hour % 12 || 12;
      const formattedTime = `${hour
        .toString()
        .padStart(2, "0")}:${minute} ${ampm}`;
      // Get target: "from" or "to"
      const target = $("#dateTimePopup").attr("data-target");
      // Update correct input field
      const $targetInput = $("#dateTimePopup").data("targetInput");
      $targetInput.val(`${formattedDate}, ${formattedTime}`);
      // Hide popup
      $("#dateTimePopup").addClass("hidden");
    } else {
      alert("Please select a full date and time.");
    }
  });
  // Show popup
  $("#calendarOpen").on("click", function () {
    $("#dateTimePopup").removeClass("hidden");
  });
  // Cancel popup
  $(".cancel-popup").on("click", function () {
    $("#dateTimePopup").addClass("hidden");
  });
  // Clear date
  $("#clearDate").on("click", function () {
    $("#selectedDate").text("");
  });

  $(document).on("click", ".date-time-selector", function () {
    const $wrapper = $(this).closest(".dropdown-wrapper");
    const $input = $wrapper.find("input");
    const label = $wrapper.find("label").text().trim();
    $("#dateTimePopup")
      .removeClass("hidden")
      .data("targetInput", $input)
      .data("targetWrapper", $wrapper);
    $("#date-tab").removeClass("hidden");
    $("#time-tab").addClass("hidden");
  });
  $(".tabs-btn").on("click", function () {
    $(".tabs-btn").removeClass("active-tab-client");
    $(this).addClass("active-tab-client");
    const tab = $(this).data("tab");
    $(".tabs-content").addClass("hidden");
    $(`#${tab}-tab`).removeClass("hidden");
  });

  // Time Selection
  let selectedHour = "00";
  let selectedMinute = "00";
  let selectedSecond = "00";
  function populateTimeOptions(id, range) {
    const $container = $("#" + id + " > .space-y-1");
    for (let i = 0; i < range; i++) {
      const value = i.toString().padStart(2, "0");
      $container.append(
        `<div class="py-2 text-center text-base cursor-pointer">${value}</div>`
      );
    }
  }
  populateTimeOptions("hours", 24);
  populateTimeOptions("minutes", 60);
  populateTimeOptions("seconds", 60);
  function highlightCenteredItem(containerId) {
    const $container = $("#" + containerId);
    const container = $container[0];
    const items = $container.find("> div > div");
    const containerHeight = container.offsetHeight;
    const scrollTop = container.scrollTop;
    const center = scrollTop + containerHeight / 2;
    let closest = null;
    let minDist = Infinity;
    items.each(function () {
      const offsetTop = this.offsetTop;
      const height = this.offsetHeight;
      const centerY = offsetTop + height / 2;
      const dist = Math.abs(center - centerY);
      if (dist < minDist) {
        minDist = dist;
        closest = $(this);
      }
    });
    items.removeClass("text-dark-blue");
    if (closest) {
      closest.addClass("text-dark-blue");
      const selectedValue = closest.text().trim();
      if (containerId === "hours") {
        selectedHour = selectedValue;
      } else if (containerId === "minutes") {
        selectedMinute = selectedValue;
      } else if (containerId === "seconds") {
        selectedSecond = selectedValue;
      }
    }
  }
  function debounce(fn, delay) {
    let timer = null;
    return function () {
      clearTimeout(timer);
      timer = setTimeout(fn, delay);
    };
  }
  ["hours", "minutes", "seconds"].forEach((id) => {
    const $container = $("#" + id);
    $container.on(
      "scroll",
      debounce(function () {
        highlightCenteredItem(id);
      }, 100)
    );
    setTimeout(() => highlightCenteredItem(id), 100);
  });

  // Color Picker for add heat-map,threshold and Notification popup on het-map tab section
  $(".colorPickerTrigger").each(function () {
    const $trigger = $(this);
    const defaultColor = $trigger.css("background-color") || "#2A3652";

    const pickr = Pickr.create({
      el: $trigger[0], // Pass the raw DOM element
      theme: "classic",
      default: defaultColor,
      components: {
        preview: true,
        opacity: true,
        hue: true,
        interaction: {
          hex: true,
          rgba: true,
          input: true,
          save: true,
        },
      },
    });

    pickr.on("save", (color) => {
      const hex = color.toHEXA().toString();
      $trigger.css("background-color", hex);
      pickr.hide();
    });
  });

  // Custom range selectors on Report Designer Tab Section
  $(".custom-slider .slider-thumb").on("click", function () {
    const $thumb = $(this);
    const index = parseInt($thumb.attr("data-index"));
    const $slider = $thumb.closest(".custom-slider");
    const $dots = $slider.find(".slider-thumb");
    const $lines = $slider.find(".range-hr");
    let firstSelectedIndex = $slider.attr("data-first-selected");
    if (firstSelectedIndex === "") {
      $slider.attr("data-first-selected", index);
      $dots.removeClass("bg-dark-blue").addClass("bg-soft-light-gray");
      $lines.removeClass("border-dark-blue").addClass("border-soft-light-gray");
      $thumb.removeClass("bg-soft-light-gray").addClass("bg-dark-blue");
    } else {
      firstSelectedIndex = parseInt(firstSelectedIndex);
      const start = Math.min(firstSelectedIndex, index);
      const end = Math.max(firstSelectedIndex, index);
      $dots.each(function () {
        const i = parseInt($(this).attr("data-index"));
        if (i >= start && i <= end) {
          $(this).removeClass("bg-soft-light-gray").addClass("bg-dark-blue");
        } else {
          $(this).removeClass("bg-dark-blue").addClass("bg-soft-light-gray");
        }
      });
      $lines.each(function () {
        const i = parseInt($(this).attr("data-index"));
        if (i >= start && i < end) {
          $(this)
            .removeClass("border-soft-light-gray")
            .addClass("border-dark-blue");
        } else {
          $(this)
            .removeClass("border-dark-blue")
            .addClass("border-soft-light-gray");
        }
      });
      $slider.attr("data-first-selected", "");
    }
  });

  // Select icon dropdown of add heat-map,threshold and Notification popup on heat-map tab section
  $(".icon-dropdown-toggle").on("click", function () {
    $(this).siblings(".icon-dropdown-menu").toggleClass("hidden");
  });
  $(".icon-dropdown-option").on("click", function () {
    const $svg = $(this).clone();
    const iconId = $svg.find("use").attr("xlink:href");
    const $wrapper = $(this).closest(".icon-dropdown-wrapper");
    const $display = $wrapper.find(".icon-dropdown-display");
    if ($display.find(`.icon-chip[data-icon="${iconId}"]`).length) return;
    $display.find(".icon-dropdown-placeholder").remove();
    const $chip = $(`
      <span class="icon-chip flex items-center gap-1 px-1 py-1 rounded-full bg-white  shadow text-xs font-medium " data-icon="${iconId}">
        ${$("<span>").append($svg).html()}
        <span class="remove-chip text-gray-600 font-bold cursor-pointer ml-1">&times;</span>
      </span>
    `);
    $display.append($chip);
    $wrapper.find(".icon-dropdown-menu").addClass("hidden");
  });
  $(document).on("click", ".remove-chip", function () {
    const $chip = $(this).closest(".icon-chip");
    const $display = $chip.closest(".icon-dropdown-display");
    $chip.remove();
    if ($display.find(".icon-chip").length === 0) {
      $display.append(
        `<span class="icon-dropdown-placeholder text-dark-gray text-xs font-semibold">Select The Icon For Your Representation</span>`
      );
    }
  });
  $(document).on("click", function (e) {
    if (!$(e.target).closest(".icon-dropdown-wrapper").length) {
      $(".icon-dropdown-menu").addClass("hidden");
    }
    $(".download-report-btn").on("click", function () {
      $(".toast-success").removeClass("hidden");
      setTimeout(function () {
        $(".toast-success").addClass("hidden");
      }, 1000);
    });
  });

  // Common chart options function
  function getChartOptions() {
    return {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          enabled: false,
          yAlign: "bottom",
          backgroundColor: "#3AAFA9",
          displayColors: true,
          callbacks: {
            title: () => "",
            label: function (tooltipItem) {
              return `${tooltipItem.dataset.label}: ${tooltipItem.raw}`;
            },
          },
        },
      },
      scales: {
        x: { title: { display: false } },
        yLeft: {
          type: "linear",
          position: "left",
          beginAtZero: true,
          min: 0,
          max: 800,
          ticks: { stepSize: 200 },
        },
        yRight: {
          type: "linear",
          position: "right",
          beginAtZero: true,
          min: 0,
          max: 800,
          ticks: { display: false },
          grid: { drawOnChartArea: false },
        },
      },
    };
  }

  // Initialize chart helper
  function initChart(canvasId, config) {
    const canvas = document.getElementById(canvasId);
    if (canvas) {
      return new Chart(canvas.getContext("2d"), config);
    }
    return null;
  }

  // Function to synchronize checkboxes and lists for Report Designer Tab Section
  function syncMetrics() {
    // Handle checkboxes in "Sections & Metrics"
    $("#available-metrics-list .metric-checkbox").on("change", function () {
      const $this = $(this);
      const metricId = $this.closest(".metric-item").data("metric-id");
      const metricName = $this.siblings(".metric-name").text();
      if ($this.is(":checked")) {
        // Add to "Selected Metrics"
        if (
          $("#selected-metrics-list").find(`[data-metric-id="${metricId}"]`)
            .length === 0
        ) {
          const selectedMetricHtml = 
          ` <div class="flex items-center gap-2 metric-item" data-metric-id="${metricId}">
              <input type="checkbox" class="selected-metric-checkbox text-dark-blue ring-1 ring-dark-blue focus:ring-offset-0 rounded-xs cursor-pointer" checked/>
                <p class="metric-name">${metricName}</p>
            </div>  `;
          $("#selected-metrics-list").append(selectedMetricHtml);
        }
      } else {
        // Remove from "Selected Metrics"
        $("#selected-metrics-list")
          .find(`[data-metric-id="${metricId}"]`)
          .remove();
      }
    });

    // Handle checkboxes in "Selected Metrics" (delegated event for dynamically added elements)
    $("#selected-metrics-list").on(
      "change",
      ".selected-metric-checkbox",
      function () {
        const $this = $(this);
        const metricId = $this.closest(".metric-item").data("metric-id");

        // If unchecked in "Selected Metrics", remove it and uncheck original
        if (!$this.is(":checked")) {
          $this.closest(".metric-item").remove();
          // Uncheck the corresponding checkbox in "Sections & Metrics"
          $(
            `#available-metrics-list [data-metric-id="${metricId}"] .metric-checkbox`
          ).prop("checked", false);
        }
      }
    );
    $("#available-metrics-list .metric-checkbox:checked").each(function () {
      const $this = $(this);
      const metricId = $this.closest(".metric-item").data("metric-id");
      const metricName = $this.siblings(".metric-name").text();
      if (
        $("#selected-metrics-list").find(`[data-metric-id="${metricId}"]`)
          .length === 0
      ) {
        const selectedMetricHtml = 
        `<div class="flex items-center gap-2 metric-item" data-metric-id="${metricId}">
           <input type="checkbox" class="selected-metric-checkbox text-dark-blue ring-1 ring-dark-blue focus:ring-offset-0 rounded-xs cursor-pointer" checked />
             <p class="metric-name">${metricName}</p>
           </div> `;
        $("#selected-metrics-list").append(selectedMetricHtml);
      }
    });
  }
  function setupSearch(searchInputId, listContainerId) {
    $(searchInputId).on("keyup", function () {
      const searchText = $(this).val().toLowerCase();
      $(listContainerId)
        .find(".metric-item")
        .each(function () {
          const metricName = $(this).find(".metric-name").text().toLowerCase();
          if (metricName.includes(searchText)) {
            $(this).show();
          } else {
            $(this).hide();
          }
        });

      // For the available metrics list, also hide/show report sections if all their metrics are hidden
      if (listContainerId === "#available-metrics-list") {
        $(listContainerId)
          .find(".report-section")
          .each(function () {
            const $reportSection = $(this);
            const $metricsInReport = $reportSection.find(".metric-item");
            let allMetricsHidden = true;

            $metricsInReport.each(function () {
              if ($(this).css("display") !== "none") {
                allMetricsHidden = false;
                return false; // Break out of inner loop
              }
            });

            if (allMetricsHidden) {
              $reportSection.hide();
            } else {
              $reportSection.show();
            }
          });
      }
    });
  }
  syncMetrics();
  setupSearch("#search-available-metrics", "#available-metrics-list");
  setupSearch("#search-selected-metrics", "#selected-metrics-list");

  $('.remove-schedule-btn').on('click', function () {
  const popup = $('.reportSchedulerPopup');
  if (!popup.length) return;
  // popup.find('.dropdown-display').each(function () {
  //   const placeholder = $(this).closest('.dropdown-wrapper').data('placeholder') || 'Select';
  //   $(this).html(`<span class="dropdown-placeholder text-dark-gray text-xs font-semibold">${placeholder}</span>`);
  // });
  popup.find('.section-dropdown-input').val('');
  popup.find('input[type="checkbox"]').prop('checked', false);
  popup.find('input[type="text"], input[type="number"]').not('.custom-date-range').val('');
  popup.find('.selected-date').text('DD/MM/YY');
  popup.find('.dropdown-menu, .section-dropdown-menu').addClass('hidden');
  $('.tag-box .tag-chip').remove();
  $('.tag-input').val('');
  $('.tag-suggestions').addClass('invisible');
  tags = [];
});

$('.save-schedule-btn').on('click',function (e){
  $('.reportSchedulerPopup').addClass('hidden')
   $('.successPopup').removeClass('hidden')
  setTimeout(()=>{
     $('.successPopup').addClass('hidden')
  },1000)
 
})

$('.close-success-popup').on('click',function (e){
  $('.successPopup').addClass('hidden')
})

$(document).on('click', '.select-button-group .select-btn', function () {
  const $group = $(this).closest('.select-button-group');

  // Remove highlight from all buttons in this group
  $group.find('.select-btn').removeClass('bg-dark-blue text-white').addClass('bg-gray-100 text-gray-700');

  // Highlight the clicked button
  $(this).removeClass('bg-gray-100 text-gray-700').addClass('bg-dark-blue text-white');
});
 $('.widget').each(function () {
    const $widget = $(this);
    const $img = $widget.find('.map-image');
    const $slider = $widget.find('input[type="range"]');
    let scale = 1;
    function updateZoom(newScale) {
      scale = newScale;
      $img.css('transform', `scale(${scale})`);
    }

    // Slider control
    $slider.on('input', function () {
      const val = $(this).val();
      const newScale = val / 50; 
      updateZoom(newScale);
    });

    // Plus button
    $widget.find('span:contains("add")').closest('button').on('click', function () {
      scale = Math.min(scale + 0.1, 3); 
      $slider.val(scale * 50).trigger('input');
    });

    // Minus button
    $widget.find('span:contains("remove")').closest('button').on('click', function () {
      scale = Math.max(scale - 0.1, 0.5); 
      $slider.val(scale * 50).trigger('input');
    });

    // Center (reset zoom)
    $widget.find('span:contains("my_location")').closest('button').on('click', function () {
      scale = 1;
      $slider.val(50).trigger('input');
    });
  });


});
