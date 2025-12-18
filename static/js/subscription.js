/* =========================
   CSRF TOKEN (Django Safe)
========================= */
function getCSRFToken() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith('csrftoken=')) {
                cookieValue = decodeURIComponent(
                    cookie.substring('csrftoken='.length)
                );
                break;
            }
        }
    }
    return cookieValue;
}

/* =========================
   POPUP HANDLERS
========================= */
$(document).on("click", ".popup-btn", function () {
    const popupId = $(this).data("popup");
    $("." + popupId).removeClass("hidden").addClass("flex");
});

$(document).on("click", ".close-popup", function () {
    const popupId = $(this).data("popup");
    $(this).closest("." + popupId).addClass("hidden").removeClass("flex");
});

$(document).on("click", ".close-payment-success-popup", function () {
    $(".paymentSuccessPopup").addClass("hidden");
});

$(document).on("click", ".close-insufficient-balance-popup", function () {
    $(".insufficientBalancePopup").addClass("hidden");
});

$(document).on("click", ".close-payment-failed-popup", function () {
    $(".paymentFailedPopup").addClass("hidden");
});

$(document).on("click", ".try-again-btn", function () {
    $(".paymentFailedPopup").addClass("hidden");
    $(".paymentDetailsPopup").removeClass("hidden");
});

/* =========================
   INFO TOOLTIP
========================= */
function setupInfoTooltip() {
    if ($(window).width() > 768) {
        $('.info-container').hover(
            function () {
                $(this).find('.info-section').removeClass('hidden');
            },
            function () {
                $(this).find('.info-section').addClass('hidden');
            }
        );
    } else {
        $('.info-icon-subscription').on('click', function (e) {
            e.stopPropagation();
            $(this).siblings('.info-section').toggleClass('hidden');
        });

        $(document).on('click', function (e) {
            if (!$(e.target).closest('.info-container').length) {
                $('.info-section').addClass('hidden');
            }
        });
    }
}

$(window).on('resize', function () {
    $('.info-section').addClass('hidden');
});

/* =========================
   SUBSCRIPTION STATUS
========================= */
$(document).ready(function () {
    setupInfoTooltip();

    $.ajax({
        url: "/settings/subscription/status/",
        method: "GET",
        success: function (res) {
            if (!res.has_subscription) {
                $(".free-plan-section").removeClass("hidden");
                $(".premium-plan-section").addClass("hidden");
            } else {
                $(".free-plan-section").addClass("hidden");
                $(".premium-plan-section").removeClass("hidden");

                $(".premium-plan-section p:contains('Active Plan')")
                    .text("Active Plan : " + res.plan);

                $(".premium-plan-section p:contains('Expiry Date')")
                    .html(`Expiry Date : ${res.expiry_date}
                        <span class="text-strong-red">
                            (${res.days_left} days left to go)
                        </span>`);

                $(".premium-plan-section .font-bold.text-base")
                    .html("&#8377;" + res.price);
            }
        },
        error: function () {
            console.error("Failed to fetch subscription status");
        }
    });
});

/* =========================
   PAY NOW (SUBSCRIBE)
========================= */
$(document).on("click", ".pay-now-btn", function () {
    $.ajax({
        url: "/settings/subscription/subscribe/",
        type: "POST",
        headers: {
            "X-CSRFToken": getCSRFToken()
        },
        success: function () {
            $(".paymentDetailsPopup").addClass("hidden");
            $(".paymentSuccessPopup").removeClass("hidden");
            $(".free-plan-section").addClass("hidden");
            $(".premium-plan-section").removeClass("hidden");
            location.reload();
        },
        error: function () {
            $(".paymentFailedPopup").removeClass("hidden");
        }
    });
});

/* =========================
   CANCEL SUBSCRIPTION
========================= */
$(document).on("click", ".end-subs-btn", function () {
    $.ajax({
        url: "/settings/subscription/cancel/",
        type: "POST",
        headers: {
            "X-CSRFToken": getCSRFToken()
        },
        success: function () {
            $(".cancelSubscriptionPopup").addClass("hidden");
            location.reload();
        },
        error: function () {
            toastr.error("Failed to cancel subscription");
        }
    });
});
