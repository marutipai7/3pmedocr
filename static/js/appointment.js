/**
 * Appointment Module
 * ------------------
 * - AJAX-based appointment loading
 * - Pagination + tab filtering
 * - Single dynamic modal
 * - AJAX-safe and production-ready
 */

let currentStatus = "all";

$(document).ready(function () {

  /* ------------------------------
   * Load Appointments (AJAX)
   * ------------------------------ */
  function loadAppointments(status = "all", page = 1) {
    currentStatus = status;

    $("#cards-container").html(
      `<p class="text-center mt-10 text-spanish-gray">Loading...</p>`
    );

    $.ajax({
      url: "/appointment/ajax/appointments/",
      type: "GET",
      data: { status, page },
      success: function (res) {
        $("#cards-container").html(res.html);
      },
      error: function () {
        $("#cards-container").html(
          `<p class="text-center text-red-500 mt-10">
            Failed to load appointments
          </p>`
        );
      }
    });
  }

  /* ------------------------------
   * Initial Load
   * ------------------------------ */
  loadAppointments("all", 1);

  /* ------------------------------
   * Tabs Handling
   * ------------------------------ */
  $(".tab-btn-hospital").on("click", function () {
    $(".tab-btn-hospital").removeClass("active-tab-hospital");
    $(this).addClass("active-tab-hospital");

    const tab = $(this).data("tab");

    if (tab === "equipment") {
      $("#tab-content-area > div").addClass("hidden");
      $("#equipment-container").removeClass("hidden");
    } else {
      $("#tab-content-area > div").addClass("hidden");
      $("#appointments-container").removeClass("hidden");

      // reset to page 1 on tab switch
      loadAppointments(tab, 1);
    }
  });

  /* ------------------------------
   * Pagination
   * ------------------------------ */
  $("#cards-container").on("click", ".pagination-btn", function () {
    const page = $(this).data("page");
    loadAppointments(currentStatus, page);
  });

  /* ------------------------------
   * Open Appointment Modal (Dynamic)
   * ------------------------------ */
$("#cards-container").on(
  "click",
  ".card-all-pending, .card-all-accepted, .card-all-completed, .card-all-cancelled",
  function () {

    const card = $(this);

    $("#modal-name").text(card.data("name") || "-");
    $("#modal-profile-img").attr("src", card.data("profile-img"));

    $("#modal-gender").text(card.data("gender") || "-");
    $("#modal-age").text(card.data("age") || "-");
    $("#modal-phone").text(card.data("phone") || "-");

    $("#modal-visit-type").text(card.data("visit-type") || "Visit");
    $("#modal-date").text(card.data("date") || "-");
    $("#modal-address").text(card.data("address") || "-");

    $("#modal-test").text(card.data("test") || "-");
    $("#modal-details").text(card.data("details") || "-");

    const budget = card.data("budget");
    $("#modal-budget").text(budget ? "₹" + budget : "-");

    $("#modal-order-id").text("Order #" + (card.data("order-id") || "-"));

    $(".modal-pending").removeClass("hidden");
  }
);
});

/* ------------------------------
 * Close Modal (Button)
 * ------------------------------ */
$(document).on("click", ".modal-close-pending", function () {
  $(".modal-pending").addClass("hidden");
});

/* ------------------------------
 * Close Modal (Backdrop)
 * ------------------------------ */
$(document).on("click", ".modal-pending", function (e) {
  if ($(e.target).is(this)) {
    $(this).addClass("hidden");
  }
});
