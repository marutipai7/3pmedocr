
function normalizeStatus(status) {
  return String(status || "")
    .toLowerCase()
    .trim()
    .replace("canceled", "cancelled");
}

$(document).ready(function () {

  let currentStatus = "all";
  let currentPage = 1;

  /* ------------------------------
   * Load Appointments (AJAX)
   * ------------------------------ */
  function loadAppointments(status = "all", page = 1) {
    currentStatus = status;
    currentPage = page;

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

  // Initial load
  loadAppointments("all", 1);

  /* ------------------------------
   * Tabs
   * ------------------------------ */
  $(".tab-btn-hospital").on("click", function () {
    $(".tab-btn-hospital").removeClass("active-tab-hospital");
    $(this).addClass("active-tab-hospital");

    const tab = $(this).data("tab");
    loadAppointments(tab, 1);
  });

  /* ------------------------------
   * Pagination
   * ------------------------------ */
  $("#cards-container").on("click", ".pagination-btn", function () {
    const page = $(this).data("page");
    loadAppointments(currentStatus, page);
  });

  /* ------------------------------
   * Open Appointment Modal
   * ------------------------------ */
  $("#cards-container").on("click", ".card-all-pending, .card-all-accepted, .card-all-completed, .card-all-cancelled", function () {

    const card = $(this);

    $("#modal-name").text(card.data("name") || "-");
    $("#modal-gender").text(card.data("gender") || "-");
    $("#modal-age").text(card.data("age") || "-");
    $("#modal-phone").text(card.data("phone") || "-");
    $("#modal-visit-type").text(card.data("visit-type") || "Visit");
    $("#modal-date").text(card.data("date") || "-");
    $("#modal-address").text(card.data("address") || "-");
    $("#modal-details").text(card.data("details") || "-");
    $("#modal-order-id").text("Order #" + (card.data("order-id") || "-"));
    $("#modal-budget").text(
      card.data("budget") ? "₹" + card.data("budget") : "-"
    );

    $(".modal-pending").removeClass("hidden");
  });

});

/* ------------------------------
 * Close Modal
 * ------------------------------ */
$(document).on("click", ".modal-close-pending", function () {
  $(".modal-pending").addClass("hidden");
});

$(document).on("click", ".modal-pending", function (e) {
  if ($(e.target).is(this)) {
    $(this).addClass("hidden");
  }
});
