// ✅ Define globally so tabs.js can access it
function loadSavedCoupons(query = '', limit = '50') {
    const currentUrl = new URL(window.location);
    currentUrl.searchParams.set('query', query);
    currentUrl.searchParams.set('limit', limit);

    $.ajax({
        url: currentUrl.toString(),
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        },
        success: function (response) {
            if (response.html) {
                $('#saved-coupon-history-body').html('<tr><td colspan="9" class="text-center py-4">Failed to load saved coupons.</td></tr>');
                console.log('AJAX response:', response);

                // Reinitialize pagination after AJAX success
                if (typeof initPagination === 'function') {
                    initPagination($('.saved-coupon'));
                }
            }
        },
        error: function (xhr, status, error) {
            console.error('Error loading saved coupons:', error);
        }
    });
}

$(document).ready(function () {
    // -----------------------------
    // Direction Modal
    // -----------------------------
    $(".direction-trigger").on('click', function () {
        $(".direction-modal").removeClass('hidden').addClass('flex');
    });

    $(document).on('click', function (event) {
        const $modal = $(".direction-modal");
        const $popupBox = $modal.find("> div");

        if (
            $modal.is(":visible") &&
            !$popupBox.is(event.target) &&
            $popupBox.has(event.target).length === 0 &&
            !$(event.target).closest(".direction-trigger").length
        ) {
            $modal.removeClass("flex").addClass("hidden");
        }
    });

    // -----------------------------
    // Place View Popup
    // -----------------------------
    $(".place-view-btn").on("click", () => {
        $('.place-view-modal').removeClass('hidden').addClass('flex');
    });

    $(".place-view-close").on("click", () => {
        $('.place-view-modal').removeClass('flex').addClass('hidden');
    });

    // -----------------------------
    // Medicine View Popup
    // -----------------------------
    $(".medicine-view-btn").on("click", () => {
        $('.medicine-view-modal').removeClass('hidden').addClass('flex');
    });

    $(".medicine-view-close").on("click", () => {
        $('.medicine-view-modal').removeClass('flex').addClass('hidden');
    });

    // -----------------------------
    // Saved Coupon Preview Popup
    // -----------------------------
    $(".preview-view").on("click", () => {
        $('.preview-popup').removeClass('hidden').addClass('flex');
    });

    $(".preview-close").on("click", () => {
        $('.preview-popup').removeClass('flex').addClass('hidden');
    });

    // -----------------------------
    // Saved Coupon View Modal
    // -----------------------------
    $(".saved-view-btn").on("click", () => {
        $('.saved-view-modal').removeClass('hidden').addClass('flex');
    });

    $(".saved-view-close").on("click", () => {
        $('.saved-view-modal').removeClass('flex').addClass('hidden');
    });

    // -----------------------------
    // Donation View Modal
    // -----------------------------
    $(".donation-view-btn").on("click", () => {
        $('.donation-view-modal').removeClass('hidden').addClass('flex');
    });

    $(".donation-view-close").on("click", () => {
        $('.donation-view-modal').removeClass('flex').addClass('hidden');
    });

    // -----------------------------
    // Search functionality for Saved Coupon
    // -----------------------------
    $('.saved-coupon input[placeholder="Search by name or categories"]').on('input', function () {
        const query = $(this).val().trim();
        const limit = $('.saved-coupon .filterDropdown .active').data('limit') || '50';
        loadSavedCoupons(query, limit);
    });

    // -----------------------------
    // Filter dropdown for Saved Coupon
    // -----------------------------
    $('.saved-coupon .filterDropdown div').on('click', function () {
        const limit = $(this).data('limit');
        const query = $('.saved-coupon input[placeholder="Search by name or categories"]').val().trim();

        $('.saved-coupon .filterDropdown div').removeClass('active');
        $(this).addClass('active');

        $('.saved-coupon .filterToggle').text(`Show ${limit}`);
        loadSavedCoupons(query, limit);
    });

    // Coupon view click
    $('.coupon-view-btn').on('click', function () {
        console.log('Coupon view button clicked');
    });

    // Toggle filter dropdown
    $('.filterToggle').on('click', function () {
        $(this).siblings('.filterDropdown').toggleClass('hidden');
    });

    // Hide dropdown if clicking outside
    $(document).on('click', function (e) {
        if (!$(e.target).closest('.dropdown').length) {
            $('.filterDropdown').addClass('hidden');
        }
    });
});
