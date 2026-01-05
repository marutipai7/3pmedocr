/* =========================================================
   GLOBAL STATE
========================================================= */
let currentPage = 1;
let currentFilter = "";
let currentSearch = "";

/* =========================================================
   DOCUMENT READY — SINGLE ENTRY POINT
========================================================= */
$(document).ready(function () {

  /* ================================
     ADVANCE HISTORY INIT
  ================================ */
  if ($("#advanceHistoryBody").length) {
    loadAdvanceHistory(1);
  }

  /* ================================
     ADVANCE SUMMARY INIT
  ================================ */
  if ($("#summaryCurrentBalance").length) {
    loadAdvanceSummary();
  }

  /* ================================
     SEARCH
  ================================ */
  $(document).on("keyup", "input[placeholder*='Search']", function () {
    currentSearch = $(this).val();
    loadAdvanceHistory(1);
  });

  /* ================================
     FILTER
  ================================ */
  $(document).on("click", ".filterDropdown div", function () {
    const text = $(this).text().toLowerCase();

    currentFilter =
      text.includes("week") ? "week" :
      text.includes("month") ? "month" :
      text.includes("year") ? "year" : "";

    loadAdvanceHistory(1);
  });

  /* ================================
     PAGINATION CLICK
  ================================ */
  $(document).on("click", ".pagination-btn", function () {
    const page = $(this).data("page");
    loadAdvanceHistory(page);
  });

  /* ================================
     VIEW RECEIPT
  ================================ */
  $(document).on("click", ".view-receipt", function () {
    $(".viewModal").removeClass("hidden");
  });

  /* ================================
     CLOSE MODALS
  ================================ */
  $(document).on("click", ".closeModal", function () {
    $(".viewModal, .fileModal").addClass("hidden");
  });

  /* ================================
     BACK BUTTONS
  ================================ */
  $(document).on("click", ".closehistoryBtn, .closeadvance-btn, .cancelBtn", function () {
    window.history.back();
  });

  /* ================================
     ADVANCE INPUT
  ================================ */
  $(document).on("input", "#amountInput", function () {
    updateAdvanceTotal($(this).val());
  });

  $(document).on("click", ".amount-btn", function () {
    const amount = $(this).text().replace(/[^\d]/g, "");
    $("#amountInput").val(amount);
    updateAdvanceTotal(amount);
  });

  /* ================================
     ADVANCE RECHARGE
  ================================ */
  $(document).on("click", ".recharge-btn", function () {

    const amount = parseFloat($("#amountInput").val());
    const payment_method = $("input[name='payment_method']:checked").val();

    if (!amount || amount < 100) {
      toastr.error("Minimum amount is ₹100");
      return;
    }

    if (!payment_method) {
      toastr.error("Please select a payment method");
      return;
    }

    $.ajax({
      url: "/dashboard/advance/add/",
      type: "POST",
      data: {
        amount: amount,
        payment_method: payment_method,
        csrfmiddlewaretoken: $("input[name='csrfmiddlewaretoken']").val(),
      },

      beforeSend: function () {
        $(".recharge-btn").prop("disabled", true).text("Processing...");
      },

      success: function (res) {
        $(".recharge-btn").prop("disabled", false).text("Recharge");

        if (!res.success) {
          toastr.error(res.message);
          return;
        }

        toastr.success(res.message);

        $("#prevBalance").text("₹" + res.previous_balance);
        $("#addedAmount").text("₹" + res.added_amount);
        $("#currentBalance").text("₹" + res.current_balance);
        $("#earnedPoints").text(res.points);
        $("#walletBalance").text("₹" + res.current_balance);
        $("#walletLastUpdated").text("Last updated on " + formatDate(new Date()));

        $(".viewModal").removeClass("hidden");
      },

      error: function () {
        $(".recharge-btn").prop("disabled", false).text("Recharge");
        toastr.error("Server Error");
      }
    });
  });

});

/* =========================================================
   ADVANCE HISTORY AJAX
========================================================= */
function loadAdvanceHistory(page = 1) {

  $.ajax({
    url: "/dashboard/advance/history/ajax/",
    data: {
      page: page,
      filter: currentFilter,
      search: currentSearch
    },

    success: function (res) {
      if (!res.success) return;

      let html = "";

      if (!res.data || res.data.length === 0) {
        html = `
          <tr>
            <td colspan="7" class="py-6 text-center text-gray-400">
              No advance history found
            </td>
          </tr>`;
      } else {
        res.data.forEach(tx => {
          html += `
            <tr class="text-center">
              <td>${tx.date}</td>
              <td>${tx.tranx_id}</td>
              <td>${tx.type}</td>
              <td>${tx.description}</td>
              <td>${tx.amount}</td>
              <td>
                <div class="bg-mint-cream text-green py-2 rounded-md">
                  ${tx.status}
                </div>
              </td>
              <td>
                <span class="material-symbols-outlined cursor-pointer view-receipt">
                  visibility
                </span>
              </td>
            </tr>`;
        });
      }

      $("#advanceHistoryBody").html(html);
      renderPagination(res.pagination);
    },

    error: function () {
      $("#advanceHistoryBody").html(`
        <tr>
          <td colspan="7" class="py-6 text-center text-red-500">
            Failed to load history
          </td>
        </tr>
      `);
    }
  });
}

/* =========================================================
   PAGINATION UI
========================================================= */
function renderPagination(p) {
  if (!p) return;

  let html = "";

  html += `
    <button
      class="pagination-btn font-medium ${p.has_prev ? "text-black" : "text-gray-400 cursor-not-allowed"}"
      data-page="${p.current - 1}"
      ${!p.has_prev ? "disabled" : ""}
    >
      Previous
    </button>
  `;

  html += `
    <span class="bg-dodger-blue text-white w-8 h-8 flex items-center justify-center rounded-lg font-semibold">
      ${p.current}
    </span>
  `;

  html += `
    <button
      class="pagination-btn font-medium ${p.has_next ? "text-black" : "text-gray-400 cursor-not-allowed"}"
      data-page="${p.current + 1}"
      ${!p.has_next ? "disabled" : ""}
    >
      Next
    </button>
  `;

  $("#pagination").html(html);
}

/* =========================================================
   SUMMARY AJAX
========================================================= */
function loadAdvanceSummary() {
  $.ajax({
    url: "/dashboard/advance/summary/ajax/",
    data: { filter: currentFilter || "week" },

    success: function (res) {
      if (!res.success) return;

      $("#summaryCurrentBalance").text("₹" + res.current_balance);
      $("#summaryTotalCredit").text("₹" + res.total_credit);
      $("#summaryTotalDebit").text("₹" + res.total_debit);

      $(".summary-label").text(res.label);
      $(".summary-date-range").text(
        `(${res.from_date} to ${res.to_date})`
      );
    }
  });
}


/* =========================================================
   HELPERS
========================================================= */
function updateAdvanceTotal(amount) {
  $("#advanceTotal").text((parseFloat(amount) || 0).toFixed(0));
}

function formatDate(dateObj) {
  const day = dateObj.getDate();
  const month = dateObj.toLocaleString("en-IN", { month: "long" });
  const year = dateObj.getFullYear();
  const suffix =
    day % 10 === 1 && day !== 11 ? "st" :
    day % 10 === 2 && day !== 12 ? "nd" :
    day % 10 === 3 && day !== 13 ? "rd" : "th";
  return `${day}${suffix} ${month} ${year}`;
}
