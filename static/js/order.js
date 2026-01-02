$(document).ready(function () {

/* ================================
   TICKET + CHAT
================================ */
  $(".issue-item").on("click", function () {
    const chatId = $(this).data("chat-id");
    $(".issue-item").removeClass("bg-teal-veil");
    $(this).addClass("bg-teal-veil");
    $(this).find("title").addClass("text-teal-veil");

    $(".chat-profile").addClass("hidden");
    $('.chat-profile[data-id="' + chatId + '"]').removeClass("hidden");

    if (window.innerWidth < 1024) {
      $(".ticket-list").addClass("hidden");
    }
  });

  $(".ticket-menu").on("click", function (e) {
    e.stopPropagation();
    $(".ticket-list").toggle();
  });

  $(document).on("click", function (event) {
    const $target = $(event.target);
    if (
      !$target.closest(".ticket-menu").length &&
      !$target.closest(".ticket-list").length
    ) {
      $(".ticket-list").addClass("hidden");
    }
  });


/* ================================
   ORDER TRACKING
================================ */
  const addedStatuses = new Set();

  function addStatus(statusText, timestamp) {
    if (addedStatuses.has(statusText)) return;

    addedStatuses.add(statusText);
    let dotsCount = $('#statusDots div').length;

    if (dotsCount > 0) {
      $('#statusDots').append(`<hr class="text-light-sea-green h-6 w-0 ml-1.5 border-2">`);
    }

    $('#statusDots').append(`<div class="bg-light-sea-green rounded-full h-4 w-4"></div>`);
    $('#statusLabels').append(`<p class="font-normal text-base">${statusText}</p>`);
    $('#statusTimes').append(`<p class="font-semibold text-base">${timestamp}</p>`);
  }

  $(".order-tracking-btn").on("click", function () {
    let status = $(this).data("status");
    let color = $(this).data("color");
    addStatus(status, "02/05/2025, 16:30");
    $(".order-current-status").html(status).addClass(`text-${color}`);
    $(".trackingPopup").removeClass("hidden").addClass("flex");
  });


/* ================================
   POPUPS
================================ */
  $(".popup-btn").on("click", function () {
    let popupId = $(this).data("popup");
    $("." + popupId).removeClass("hidden").addClass("flex");
  });

  $(".close-popup").on("click", function () {
    let popupId = $(this).data("popup");
    $(this).closest("." + popupId).addClass("hidden").removeClass("flex");
  });


/* ================================
   STATUS DROPDOWN
================================ */
  $(".status-btn").on("click", function () {
    $(".status-dropdown").toggle();
  });

  $(document).on("click", function (e) {
    if (!$(e.target).closest(".status-btn, .status-dropdown").length) {
      $(".status-dropdown").hide();
    }
  });


/* ================================
   IMAGE UPLOAD
================================ */
  let maxImages = 4;

  $("#image-upload").on("change", function (e) {
    let files = Array.from(e.target.files);
    let currentImages = $("#preview img").length;

    if ((files.length + currentImages) > maxImages) {
      toastr.error("You can only upload up to 4 images.");
      return;
    }

    files.forEach(file => {
      let reader = new FileReader();
      reader.onload = function (e) {
        $('#preview').append(`
          <div class="image-thumb relative mb-4">
            <img src="${e.target.result}" class="w-16 h-16 object-cover rounded" />
            <span class="remove-btn material-symbols-outlined cursor-pointer material-filled text-jet-black absolute right-0 top-0 -mt-2 -mr-3">cancel</span>
          </div>`);
      };
      reader.readAsDataURL(file);
    });

    $(this).val('');
  });

  $(document).on("click", ".remove-btn", function () {
    $(this).closest(".image-thumb").remove();
  });


/* ================================
   STAR RATING
================================ */
  $("#starRating span").click(function () {
    const index = $(this).index();
    $("#starRating span").removeClass("material-filled text-star-yellow");
    $("#starRating span").each(function (i) {
      if (i <= index) $(this).addClass("material-filled text-star-yellow");
    });
  });


/* ================================
   NOTIFICATION DROPDOWN
================================ */
  const $bellIcon = $("#bell-icon");
  const $popup = $("#popup");
  const $closePopup = $("#close-popup");
  const $viewDetailsDropdown = $("#viewDetailsDropdown");
  const $openViewDetails = $(".openViewDetails");
  const $closeViewDetailsDropdown = $(".closeViewDetailsDropdown");

  $bellIcon.on("click", function (e) {
    e.stopPropagation();
    $popup.toggleClass("hidden");
    $viewDetailsDropdown.addClass("hidden");
  });

  $closePopup.on("click", function () {
    $popup.addClass("hidden");
  });

  $openViewDetails.on("click", function (e) {
    e.stopPropagation();
    $popup.addClass("hidden");
    $viewDetailsDropdown.removeClass("hidden");
  });

  $closeViewDetailsDropdown.on("click", function () {
    $viewDetailsDropdown.addClass("hidden");
    $popup.removeClass("hidden");
  });

  $(document).on("click", function (e) {
    const $target = $(e.target);

    if (!$target.closest("#popup").length && !$target.is("#bell-icon")) {
      $popup.addClass("hidden");
    }

    if (
      !$target.closest("#viewDetailsDropdown").length &&
      !$target.closest(".openViewDetails").length
    ) {
      $viewDetailsDropdown.addClass("hidden");
    }
  });

/* ================================
   RECEIPT & FILE VIEW
================================ */
  $(".view-receipt").on("click", function () {
    $(".viewModal").removeClass("hidden");
  });

  $(".view-file").on("click", function () {
    $(".fileModal").removeClass("hidden");
  });

  $(".closeModal").on("click", function () {
    $(".viewModal").addClass("hidden");
    $(".fileModal").addClass("hidden");
  });


/* ================================
   HISTORY + CLOSE BUTTONS
================================ */
  $(".closehistoryBtn, .closeadvance-btn, .cancelBtn").on("click", function () {
    window.history.back();
  });


/* ================================
   SUMMARY POPUP
================================ */
  $(".view-detailsBtn").on("click", function (e) {
    e.preventDefault();
    $(".viewModal").removeClass("hidden");
  });

  $(".closeSummaryPopup").on("click", function () {
    $(".viewModal").addClass("hidden");
  });

  $(document).on("click", function (e) {
    if (
      !$(e.target).closest(".viewModal > div").length &&
      !$(e.target).is(".view-detailsBtn")
    ) {
      $(".viewModal").addClass("hidden");
    }
  });


/* ================================
   BOOKMARK
================================ */
  $(".bookmark-fill").click(function () {
    $(this).addClass(`material-filled text-light-sea-green`);
  });


/* =========================================================
   🔥  ADVANCE RECHARGE — MAIN WORKING LOGIC
========================================================= */
  $(".recharge-btn").on("click", function () {

    let amount = parseFloat($("#amountInput").val());
    let payment_method = $("input[name='payment_method']:checked").val();

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
        toastr.success(res.message);

        if (res.success) {
          $("#prevBalance").text("₹" + res.previous_balance);
          $("#addedAmount").text("₹" + res.added_amount);
          $("#currentBalance").text("₹" + res.current_balance);
          $("#earnedPoints").text(res.points);
          $("#walletBalance").text("₹" + res.current_balance);
          const today = new Date();
          $("#walletLastUpdated").text(
            "Last updated on " + formatDate(today)
          );


          $(".viewModal").removeClass("hidden");
        } else {
          toastr.error(res.message);
        }
      },

      error: function () {
        $(".recharge-btn").prop("disabled", false).text("Recharge");
        toastr.error("Server Error");
      },
    });
  });

});

/* ================================
   ADVANCE TOTAL SYNC
================================ */
function updateAdvanceTotal(amount) {
  amount = parseFloat(amount) || 0;
  $("#advanceTotal").text(amount.toFixed(0));
}

/* When user types amount manually */
$("#amountInput").on("input", function () {
  updateAdvanceTotal($(this).val());
});

/* When user clicks recommended amount buttons */
$(".amount-btn").on("click", function () {
  const amount = $(this).text().replace(/[^\d]/g, "");
  $("#amountInput").val(amount);
  updateAdvanceTotal(amount);
});


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


function loadAdvanceHistory() {
  $.ajax({
    url: "/dashboard/advance/history/ajax/",
    type: "GET",

    success: function (res) {
      if (!res.success) return;

      let html = "";

      if (res.data.length === 0) {
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
              <td class="py-2 px-4">${tx.date}</td>
              <td class="py-2 px-4">${tx.tranx_id}</td>
              <td class="py-2 px-4">${tx.type}</td>
              <td class="py-2 px-4">${tx.description}</td>
              <td class="py-2 px-4">${tx.amount}</td>
              <td class="px-4 py-2">
                <div class="bg-mint-cream text-green py-2 rounded-md">
                  ${tx.status}
                </div>
              </td>
              <td class="px-4 py-2">
                <span class="material-symbols-outlined cursor-pointer view-receipt">
                  visibility
                </span>
              </td>
            </tr>`;
        });
      }

      $("#advanceHistoryBody").html(html);
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

$(document).ready(function () {
  loadAdvanceHistory();
});
