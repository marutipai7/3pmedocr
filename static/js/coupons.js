$(document).ready(function () {
  $(".createCouponBtn").on("click", function () {
    $(".myCoupons").hide();
    $(".createCouponSection").removeClass("hidden");
  });

  $("#expiryDate").datepicker({
    dateFormat: "dd/mm/yy",
    minDate: 0,
    onSelect: function (dateText) {
      $("#expiryDateError").addClass("hidden");
    },
  });
  $("#calendarIcon").on("click", function () {
    $("#expiryDate").datepicker("show");
  });
  $("#percentageCheck").on("change", function () {
    if ($(this).is(":checked")) {
      $("#fixedAmountCheck").prop("checked", false);
      $("#percentIcon").show();
    }
  });

  $("#fixedAmountCheck").on("change", function () {
    if ($(this).is(":checked")) {
      $("#percentageCheck").prop("checked", false);
      $("#percentIcon").hide();
    }
  });

  $("#couponName").on("input blur", function () {
    const value = $(this).val().trim();
    if (!value) {
      $("#couponNameError").removeClass("hidden");
    } else {
      $("#couponNameError").addClass("hidden");
    }
  });

  $("#couponCode").on("input blur", function () {
    const value = $(this).val().trim();
    if (!value) {
      $("#couponCodeError").removeClass("hidden");
    } else {
      $("#couponCodeError").addClass("hidden");
    }
  });

  $("#discountValue").on("input blur", function () {
    const value = $(this).val().trim();
    if (!value) {
      $("#discountValueError").removeClass("hidden");
    } else {
      $("#discountValueError").addClass("hidden");
    }
  });

  $("#expiryDate").on("change blur", function () {
    const value = $(this).val().trim();
    if (!value) {
      $("#expiryDateError").removeClass("hidden");
    } else {
      $("#expiryDateError").addClass("hidden");
    }
  });

  $("#usagesLimit").on("input blur", function () {
    const value = $(this).val().trim();
    if (!value) {
      $("#usagesLimitError").removeClass("hidden");
    } else {
      $("#usagesLimitError").addClass("hidden");
    }
  });

  $(".createCouponForm").on("submit", function (e) {
    e.preventDefault();
    $(".error-message").addClass("hidden");

    let isValid = true;
    const couponName = $("#couponName").val().trim();
    if (!couponName) {
      $("#couponNameError").removeClass("hidden");
      isValid = false;
    }
    const couponCode = $("#couponCode").val().trim();
    if (!couponCode) {
      $("#couponCodeError").removeClass("hidden");
      isValid = false;
    }
    const discountValue = $("#discountValue").val().trim();
    if (!discountValue) {
      $("#discountValueError").removeClass("hidden");
      isValid = false;
    }
    const expiryDate = $("#expiryDate").val().trim();
    if (!expiryDate) {
      $("#expiryDateError").removeClass("hidden");
      isValid = false;
    }
    const usagesLimit = $("#usagesLimit").val().trim();
    if (!usagesLimit) {
      $("#usagesLimitError").removeClass("hidden");
      isValid = false;
    }

    if (isValid) {
      const discountType = $("#percentageCheck").is(":checked")
        ? "Percentage"
        : "Fixed Amount";
      $("#successMessage").removeClass("hidden");
      $(".createCouponForm")[0].reset();
      $("#percentageCheck").prop("checked", true);
      setTimeout(function () {
        $("#successMessage").addClass("hidden");
      }, 3000);
    }
  });

  // Cancel button functionality
  $("#cancelBtn").on("click", function () {
    $(".createCouponForm")[0].reset();
    $("#percentageCheck").prop("checked", true);
    $(".error-message").addClass("hidden");
    $("#successMessage").addClass("hidden");
    $(".myCoupons").show();
    $(".createCouponSection").addClass("hidden");
  });
});
