
  const chartLabels = JSON.parse(document.getElementById('chartLabelsData').textContent);
  const chartData = JSON.parse(document.getElementById('chartDataData').textContent);

  const colors = ["#5182E3", "#28A745", "#3AAFA9"];
  const datasets = Object.keys(chartData).map((actionType, i) => ({
    label: actionType,
    data: chartData[actionType],
    borderColor: colors[i] || "#000000",
    borderWidth: 2,
    tension: 0,
    pointRadius: 3,
    pointBackgroundColor: '#FFFFFF',
    pointBorderColor: colors[i] || "#000000",
    pointHoverRadius: 5,
    pointHoverBackgroundColor: '#FFFFFF',
    pointHoverBorderColor: colors[i] || "#000000",
  }));
  const allValues = Object.values(chartData).flat();
  const maxValue = Math.max(...allValues, 0);
  let roundedMax = Math.ceil(maxValue / 5) * 5;

// Force minimum max of 20 so we get ticks like 0,5,10,15,20
if (roundedMax < 20) {
  roundedMax=20;
}
  const ctx = document.getElementById("referralChart").getContext("2d");
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: chartLabels,
      datasets: datasets
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          display: false
        }
    }
},
scales: {
      y: {
        beginAtZero: true,
        min: 0,
        suggestedMax: roundedMax,
        ticks: {
          stepSize: 5,
          precision: 0
       }
}
}
});
 // Create checkboxes dynamically
  const checkboxContainer = document.getElementById("referralCustomLegend");

  datasets.forEach((dataset, index) => {
    const label = document.createElement("label");
    label.style.marginRight = "10px";

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = true;
    checkbox.dataset.index = index;

    checkbox.addEventListener("change", function () {
      const i = this.dataset.index;
      referralChart.data.datasets[i].hidden = !this.checked;
      referralChart.update();
    });

    // label.appendChild(checkbox);
    // label.appendChild(document.createTextNode(dataset.label));
    // checkboxContainer.appendChild(label);
  });


  function applyDateFilter(filterType) {
    const filterInput = document.getElementById('dateFilterInput');
    filterInput.value = filterType;

    if (filterType === 'custom') {
      // Show date inputs
      document.getElementById('startDateInput').classList.remove('hidden');
      document.getElementById('endDateInput').classList.remove('hidden');
    } else {
      // Hide custom date inputs if not custom
      document.getElementById('startDateInput').classList.add('hidden');
      document.getElementById('endDateInput').classList.add('hidden');

      // Submit form immediately for non-custom filters
      document.getElementById('filterForm').submit();
    }
  }


  document.querySelectorAll('.badge-description').forEach(function(descElem) {
    const text = descElem.textContent;
    const listElem = descElem.nextElementSibling;

    // Split by period and trim
    const lines = text.split('.').map(line => line.trim()).filter(line => line.length > 0);

    // Add each line to the list
    lines.forEach(line => {
      const li = document.createElement('li');
      li.textContent = line;
      listElem.appendChild(li);
    });

    // Optionally hide original text
    descElem.style.display = 'none';
  });



  function allrewards(search=''){
    $.ajax({
        url: 'get-cards/',
        data:{
          search:search
        },  // your Django view URL
        method: 'GET',
        success: function (response) {
          $('#featured-rewards').html(response.html); // Replace card container HTML
        },
        error: function () {
          toastr.error("Failed to load rewards.");
        }
      });

  }
  $(document).ready(function () {
    // Listen for button click with data-tab="all-rewards"
    $('[data-tab="all-rewards"]').on('click', function () {
      allrewards();
      popular_coupons();
    });
    function popular_coupons(search=''){
       $.ajax({
        url: 'get-popular-coupons/',
        data:{
          search:search
        },  // your Django view URL
        method: 'GET',
        success: function(response) {
                $('#popular-coupons').html(response.html);
            },
            error: function() {
                $('#popular-coupons').html('<p>Error loading coupons.</p>');
            }
      });
    }
  $(document).on('input change', '#allrewardssearch', function() {
      const search = $(this).val().trim();
      allrewards(search);
      popular_coupons(search);
     
  });  
});




function fetchFilteredData(page = 1) {
    const search = $("input[name='search']").val();
    const startDate = $("#startDateInput").val();
    const endDate = $("#endDateInput").val();

    $.ajax({
        url: "history/",
        data: {
            search: search,
            start_date: startDate,
            end_date: endDate,
            page: page
        },
        success: function(data) {
            $("#pointsTable").html(data);
        }
    });
}

$("input[name='search']").on("input", function () {
    clearTimeout(window.searchTimeout);
    window.searchTimeout = setTimeout(fetchFilteredData, 400); // debounce
});

$("#startDateInput, #endDateInput").on("change", function () {
    fetchFilteredData();
});

function applyDateFilter(type) {
    const today = new Date();
    let start = "", end = "";

    if (type === "last_week") {
        start = new Date(today.setDate(today.getDate() - 7));
        end = new Date();
    } else if (type === "last_month") {
        start = new Date(today.setMonth(today.getMonth() - 1));
        end = new Date();
    } else if (type === "last_year") {
        start = new Date(today.setFullYear(today.getFullYear() - 1));
        end = new Date();
    } else if (type === "custom") {
        $("#startDateInput").removeClass("hidden");
        $("#endDateInput").removeClass("hidden");
        return;
    }

    if (start && end) {
        $("#startDateInput").val(start.toISOString().split('T')[0]);
        $("#endDateInput").val(end.toISOString().split('T')[0]);
        fetchFilteredData();
    }
}
  $('[data-tab="points-history"]').on('click', function () {
    fetchFilteredData();
  });
  $(document).on('click', '.pagination-btn', function (e) {
    e.preventDefault();
    let page = $(this).data('page');
    fetchFilteredData(page);
  });



  $(document).on("click",".claim-btn",function() {
    // $('.claim-btn').on('click', function() {
      const couponId = $(this).data('coupon-id');
      const code = $(this).data('code');

      $.ajax({
        url: '/points/claim-coupon/',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ coupon_id: couponId }),
        success: function(response) {
          if (response.status === 'success') {
            toastr.success('Coupon claimed! Code copied: ' + code);
            navigator.clipboard.writeText(code);
          } else if (response.status === 'already_claimed') {
            toastr.error('You have already claimed this coupon.');
          } else {
            toastr.error('Something went wrong.');
          }
        },
        error: function(xhr, status, error) {
          console.log(error);
          toastr.error('Server error.');
        }
      });
    });
  // });


  $(document).ready(function () {
    
  });
   $('[data-tab="rewards-claimed"]').on('click', function () {
    $.ajax({
      url: "/points/claimed-coupons/ajax/",
      method: "GET",
      success: function (response) {
        $("#claimedCouponsBody").html(response.html);
      },
      error: function () {
        toastr.error("Failed to load claimed coupons.");
      }
    });
    
    $(document).on("click", ".allRewardsCoupons .dateFilter", function() {
      alert($(this).data('range'));
    });
    //$('.daterange').on('click', function () {
    // console.log($(this));
    // toastr.info($(this).data('range'));
    //});
    });
 

  