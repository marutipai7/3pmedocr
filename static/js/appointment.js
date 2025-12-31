/**
 * Appointment Module
 * ------------------
 * - AJAX-based appointment loading
 * - Static Bed Inventory tab
 * - Modal open / close (event delegation)
 * - AJAX-safe and production-ready
 */

$(document).ready(function () {

  /* ------------------------------
   * Load Appointments (AJAX)
   * ------------------------------ */
  function loadAppointments(status = "all") {
    $("#cards-container").html(
      `<p class="text-center mt-10 text-spanish-gray">Loading...</p>`
    );

    $.ajax({
      url: "/appointment/ajax/appointments/",
      type: "GET",
      data: { status },
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
  loadAppointments("all");

  /* ------------------------------
   * Tabs Handling
   * ------------------------------ */
  $(".tab-btn-hospital").on("click", function () {
    $(".tab-btn-hospital").removeClass("active-tab-hospital");
    $(this).addClass("active-tab-hospital");

    const tab = $(this).data("tab");

    if (tab === "equipment") {
      // ✅ Show equipment
      console.log("Loading equipment tab");
      $("#tab-content-area > div").addClass("hidden");
      $("#equipment-container").removeClass("hidden");

    } else {
      // ✅ Show appointments
      $("#tab-content-area > div").addClass("hidden");
      $("#appointments-container").removeClass("hidden");


      // ✅ Load appointments via AJAX
      loadAppointments(tab);
    }
  });

  /* ------------------------------
   * Open Modals (Event Delegation)
   * ------------------------------ */
  $("#cards-container")

    .on("click", ".card-all-pending", function () {
      $(".modal-pending").removeClass("hidden");
    })

    .on("click", ".card-all-completed", function () {
      $(".modal-all-completed").removeClass("hidden");
    })

    .on("click", ".card-all-cancelled", function () {
      $(".modal-canceled").removeClass("hidden");
    })

    .on("click", ".card-all-accepted", function () {
      $(".modal-all-accepted").removeClass("hidden");
    });

});


/* ------------------------------
 * Close Modals (Buttons)
 * ------------------------------ */
$(document).on("click", ".modal-close-pending", function () {
  $(".modal-pending").addClass("hidden");
});

$(document).on("click", ".modal-close-canceled", function () {
  $(".modal-canceled").addClass("hidden");
});

$(document).on("click", ".modal-close-all-completed", function () {
  $(".modal-all-completed").addClass("hidden");
});

$(document).on("click", ".modal-close-all-accepted", function () {
  $(".modal-all-accepted").addClass("hidden");
});


/* ------------------------------
 * Close Modals (Backdrop Click)
 * ------------------------------ */
$(document).on(
  "click",
  ".modal-pending, .modal-canceled, .modal-all-completed, .modal-all-accepted",
  function (e) {
    if ($(e.target).is(this)) {
      $(this).addClass("hidden");
    }
  }
);
