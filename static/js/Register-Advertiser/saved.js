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

    function amountToWords(amount) {
    const ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"];
    const tens = ["", "Ten", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"];
    const teens = ["Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", 
                   "Sixteen", "Seventeen", "Eighteen", "Nineteen"];

    function getWords(num) {
        let result = "";

        const crore = Math.floor(num / 10000000);
        num = num % 10000000;
        const lakh = Math.floor(num / 100000);
        num = num % 100000;
        const thousand = Math.floor(num / 1000);
        num = num % 1000;
        const hundred = Math.floor(num / 100);
        const rest = num % 100;

        if (crore > 0) result += `${getTwoDigits(crore)} Crore `;
        if (lakh > 0) result += `${getTwoDigits(lakh)} Lakh `;
        if (thousand > 0) result += `${getTwoDigits(thousand)} Thousand `;
        if (hundred > 0) result += `${ones[hundred]} Hundred `;
        if (rest > 0) result += `and ${getTwoDigits(rest)} `;

        return result.trim();
    }

    function getTwoDigits(num) {
        if (num < 10) return ones[num];
        else if (num >= 10 && num < 20) return teens[num - 10];
        else return tens[Math.floor(num / 10)] + (num % 10 ? " " + ones[num % 10] : "");
    }

    const parts = amount.toFixed(2).split('.');
    const rupees = parseInt(parts[0]);
    const paise = parseInt(parts[1]);

    const rupeesWords = rupees === 0 ? "Zero Rupees" : getWords(rupees) + " Rupees";
    const paiseWords = paise === 0 ? "" : ` and ${getTwoDigits(paise)} Paise`;

    return rupeesWords + paiseWords;
}
//Platform bill Popup
$(document).on('click', '.platform-bill-view', function () {
    const couponId = $(this).data('id');

    $.ajax({
        url: `platform-bill/${couponId}`,
        type: 'GET',
        success: function(data){
            // Inject data into modal
            const quantity = Number(data.quantity);
            const rate = Number(data.rate_per_display);
            const subtotal = quantity * rate * 10;
            $('#invoice-id').text(data.id);
            $('#invoice-name').text(data.company_name);
            $('#invoice-address').text(data.company_address);
            $('#invoice-phone').text(data.phone_number);
            $('#invoice-email').text(data.uploaded_by);
            $('#invoice-date').text(data.uploaded_on);
            $('#invoice-quantity').text(data.quantity);
            $('#invoice-title').text(data.title);
            $('#invoice-rate').text(`₹${Number(data.rate_per_display).toFixed(2)}`);
            $('#invoice-amount').text(`₹${Number(data.rate_per_display).toFixed(2)}`);
            $('#invoice-subtotal').text(`₹${subtotal.toFixed(2)}`);
            $('#invoice-gst').text(`₹${Number(data.gst_amount).toFixed(2)}`);
            $('#invoice-total').text(`₹${Number(data.final_paid_amount).toFixed(2)}`);
            
            //Platform Company Details
            $('#platform-name').text(data.company);
            $('#platform-address').text(data.address);
            $('#platform-gstin').text(data.gstin);
            $('#platform-signature').text(data.company);
            // You can add conversion to amount in words too
            $('#invoice-words').text(`INR ${amountToWords(Number(data.final_paid_amount))} Only`);

            $('.platform-bill-modal').removeClass('hidden').addClass('flex');
        },
        error: function (xhr) {
            alert("Error loading invoice: " + xhr.responseJSON?.error || "Unknown error");
        }
    });
});

    $('.close-platform-bill').on('click', function () {
        $('.platform-bill-modal').removeClass('flex').addClass('hidden');
    });

    // for exporting saved coupon
    $('.view-saved-history-btn').on('click', function () {
        $('.view-saved-history-popup').addClass('flex').removeClass('hidden');
        $.ajax({
            url: "/dashboard/export-saved-coupon-history/",
            type: "GET",
            success: function (response) {
                $('#savedcouponHistoryTableExport').html(response.html);
            },
            error: function () {
                alert("Failed to load coupon history.");
            }
        });
    });
    $('.close-saved-history-popup').on('click', function () {
        $('.view-saved-history-popup').removeClass('flex').addClass('hidden');
    });

function loadSavedCouponHistory(page = 1, range = '') {
        const query = $('input[name=saved_coupon_history_query]').val();
        const limit = $('#filter-limit').val() || 5;
        const startDate = $('#filter-start-date').val();
        const endDate = $('#filter-end-date').val();
        const daterange = range || "";

        $.ajax({
            url: "/dashboard/saved-coupon-history/",
            type: "GET",
            data: {
                query: query,
                limit: limit,
                page: page,
                daterange: daterange,
            },
            success: function (response) {
                $('.couponSavedHistoryTable tbody').html(response.html);
                renderSavedCouponPagination(response.current_page, response.total_pages);
            },
            error: function () {
                alert("Failed to load saved coupon history.");
            }
        });
    }
    function renderSavedCouponPagination(current, total) {
        let html = '';
        for (let i = 1; i <= total; i++) {
            html += `<button class="saved-coupon-pagination-btn px-2 py-1 border ${i === current ? 'bg-violet-sky text-white' : ''}" data-page="${i}">${i}</button>`;
        }
        $('#saved-coupon-pagination-container').html(html);
    }

    $('[data-tab="coupon-history"]').on('click', function () {
        loadCouponHistory();
    });

    $('[data-tab="saved-coupon-history"]').on('click', function () {
        loadSavedCouponHistory();
    });

    $(document).on('click', '.coupondaterange', function () {
        $('.coupondaterange').removeClass('font-bold');
        $(this).addClass('font-bold');
        loadCouponHistory(1, $(this).data('range'));
    });

    $(document).on('click', '.savedcoupondaterange', function () {
        $('.savedcoupondaterange').removeClass('font-bold');
        $(this).addClass('font-bold');
        loadSavedCouponHistory(1, $(this).data('range'));
    });

    $(document).on('input change', '#coupon_history_query, #filter-limit, #filter-start-date, #filter-end-date', function () {
        loadCouponHistory(1);
    });

    $(document).on('input change', '#saved_coupon_history_query, #filter-limit, #filter-start-date, #filter-end-date', function () {
        loadSavedCouponHistory(1);
    });

    $(document).on('click', '.coupon-pagination-btn', function () {
        const page = $(this).data('page');
        loadCouponHistory(page);
    });

    $(document).on('click', '.saved-coupon-pagination-btn', function () {
        const page = $(this).data('page');
        loadSavedCouponHistory(page);
    });

    $('.history_filter').on('submit', function (e) {
        e.preventDefault();
        loadCouponHistory(1);
    });

    $('.saved-history_filter').on('submit', function (e) {
        e.preventDefault();
        loadSavedCouponHistory(1);
    });
    loadSavedCouponHistory(1, '');

        // CSRF helper
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
$(document).on('click', '.saved-icon', function () {
        const $icon = $(this);
        const couponId = $icon.data('coupon-id');
        const isSaved = $icon.attr('data-saved') === 'true';
        const action = isSaved ? 'unsave' : 'save';

        // Optimistic UI toggle
        if (isSaved) {
            $icon.removeClass('material-filled text-living-coral').addClass('text-dark-blue');
            $icon.attr('data-saved', 'false');
        } else {
            $icon.addClass('material-filled text-living-coral').removeClass('text-dark-blue');
            $icon.attr('data-saved', 'true');
        }

        $.ajax({
            url: '/coupons/coupon-history/',
            type: 'POST',
            headers: { 'X-CSRFToken': getCookie('csrftoken') },
            data: {
                coupon_id: couponId,
                action: action,
            },
            success: function (response) {
                if (response.success) {
                    const message = response.saved ? 'Post saved!' : 'Post unsaved!';
                    window.showToaster('success', message);
                    // Optional: refresh table
                    // loadCouponHistory(); 
                } else {
                    window.showToaster('error', response.error || 'Could not update saved status.');
                }
            },
            error: function () {
                // Rollback UI on error
                if (action === 'save') {
                    $icon.removeClass('material-filled text-living-coral').addClass('text-dark-blue');
                    $icon.attr('data-saved', 'false');
                } else {
                    $icon.addClass('material-filled text-living-coral').removeClass('text-dark-blue');
                    $icon.attr('data-saved', 'true');
                }
                window.showToaster('error', 'Could not update saved status.');
            }
        });
    });
$(document).on('click', '[data-popup]', function (e) {
    e.stopPropagation();
    var popupType = $(this).data('popup');

    // Always hide all popups first
    $('.download-popup').addClass('hidden').removeClass("flex");
    $('.preview-popup').addClass('hidden').removeClass("flex");

    if (popupType === 'preview') {
        var couponId = $(this).data('coupon-id');
        if (couponId) {
            $.get('/dashboard/coupon_detail/' + couponId + '/', function(data) {
                // Populate preview popup
                $('.preview-popup .popup-id').text(data.id);
                $('.preview-popup .popup-issued-by').text(data.uploaded_by);
                $('.preview-popup .popup-uploaded-on').text(data.uploaded_on);
                $('.preview-popup .popup-title').text(data.title);
                $('.preview-popup .popup-image').attr('src', data.image_url);
                $('.preview-popup .popup-age').text(data.age_group);
                $('.preview-popup .popup-gender').text(data.gender);
                $('.preview-popup .popup-city').text(data.city);
                $('.preview-popup .popup-spending').text(data.spending_power);
                $('.preview-popup .popup-category').text(data.category);
                $('.preview-popup .popup-brand').text(data.brand_name);
                $('.preview-popup .popup-offer-type').text(data.offer_type);
                $('.preview-popup .popup-issued').text(data.max_redemptions);
                $('.preview-popup .popup-redeemed').text(data.redeemed_count);
                $('.preview-popup .popup-validity').text(data.validity);
                $('.preview-popup .popup-status').text(data.status);
                $('.preview-popup .popup-description').text(data.description);

                // Show the preview popup
                $('.preview-popup').removeClass('hidden').addClass('flex');
            });
        }
    } else if (popupType === 'download') {
        var couponId = $(this).data('coupon-id');
        if (couponId) {
            $.get('/dashboard/coupon_detail/' + couponId + '/', function(data) {
                // Populate download popup
                $('.download-popup .popup-id').text(data.id);
                $('.download-popup .popup-issued-by').text(data.uploaded_by);
                $('.download-popup .popup-uploaded-on').text(data.uploaded_on);
                $('.download-popup .popup-title').text(data.title);
                $('.download-popup .popup-image').attr('src', data.image_url);
                $('.download-popup .popup-age').text(data.age_group);
                $('.download-popup .popup-gender').text(data.gender);
                $('.download-popup .popup-city').text(data.city);
                $('.download-popup .popup-spending').text(data.spending_power);
                $('.download-popup .popup-category').text(data.category);
                $('.download-popup .popup-brand').text(data.brand_name);
                $('.download-popup .popup-offer-type').text(data.offer_type);
                $('.download-popup .popup-issued').text(data.max_redemptions);
                $('.download-popup .popup-redeemed').text(data.redeemed_count);
                $('.download-popup .popup-validity').text(data.validity);
                $('.download-popup .popup-status').text(data.status);
                $('.download-popup .popup-description').text(data.description);

                // Show the download popup
                $('.download-popup').removeClass('hidden').addClass('flex');
            });
        }
    }
    });

    // Close popup on close button click
    $(document).on('click', '.close-popup', function () {
        $(this).closest('.popup').addClass('hidden').removeClass("flex");
    });

    // Close popup on outside click
    $(document).on('click', function (e) {
        if (!$(e.target).closest('.download-popup, [data-popup]').length) {
            $('.download-popup').addClass('hidden').removeClass("flex");
        }
    });

    const exportBtn = $('.export-btn');

    exportBtn.on('click', function () {
        $('.preview-popup').removeClass('hidden').addClass('flex');
    })

    $(document).on('click', '.download-btn', function (event) {
        event.stopPropagation();
        // Find the next sibling with class 'download-container'
        const $container = $(this).closest('.popup').find('.download-container');

        if ($container.length === 0) {
            console.error('[ERROR] download-container not found');
            return;
        }

        // Clone the element properly
        const clone = $container[0].cloneNode(true);
        clone.style.position = 'static';
        clone.style.visibility = 'visible';
        clone.style.display = 'block';
        clone.style.zIndex = '1';
        clone.id = 'download-container-clone';
        document.body.appendChild(clone);
    
        const opt = {
            margin:       0,
            filename:     'details.pdf',
            image:        { type: 'jpeg', quality: 0.98 },
            html2canvas: { scale: 2, useCORS: true, scrollY: 0, scrollX: 0 },
            jsPDF:        { unit: 'in', format: 'letter', orientation: 'portrait' }
        };
    
        html2pdf().set(opt).from(clone).save()
            .then(() => {
                document.body.removeChild(clone);
            })
            .catch(err => {
                console.error('[ERROR] PDF generation failed:', err);
                document.body.removeChild(clone);
            });
    });

// for exporting donation history
    $('.view-saved-donation-history-btn').on('click', function () {
      console.log("View donation history button clicked");
        $('.view-saved-donation-history-popup').addClass('flex').removeClass('hidden');
        console.log("Loading donation history...");
        $.ajax({
            url: "/dashboard/export-donation-history/",
            type: "GET",
            success: function (response) {
                console.log("Donation history loaded successfully.");
                $('#donatesavedHistoryTableExport').html(response.html);
            },
            error: function () {
                console.error("Failed to load donation history.");
                alert("Failed to load donation history.");
            }
        });
    });
    $('.close-saved-donation-history-popup').on('click', function () {
        $('.view-saved-donation-history-popup').removeClass('flex').addClass('hidden');
    });

    $(document).on('click', '.download-btn', function (event) {
        event.stopPropagation();
        // Find the next sibling with class 'download-container'
        const $container = $(this).closest('.popup').find('.download-container');

        if ($container.length === 0) {
            console.error('[ERROR] download-container not found');
            return;
        }

        // Clone the element properly
        const clone = $container[0].cloneNode(true);
        clone.style.position = 'static';
        clone.style.visibility = 'visible';
        clone.style.display = 'block';
        clone.style.zIndex = '1';
        clone.id = 'download-container-clone';
        document.body.appendChild(clone);
    
        const opt = {
            margin:       0,
            filename:     'donation-details.pdf',
            image:        { type: 'jpeg', quality: 0.98 },
            html2canvas: { scale: 2, useCORS: true, scrollY: 0, scrollX: 0 },
            jsPDF:        { unit: 'in', format: 'letter', orientation: 'portrait' }
        };
    
        html2pdf().set(opt).from(clone).save()
            .then(() => {
                document.body.removeChild(clone);
            })
            .catch(err => {
                console.error('[ERROR] PDF generation failed:', err);
                document.body.removeChild(clone);
            });
    });
function loadDonationHistory(page = 1, $container = $('#donationSaved')) {
    const query = $container.find('input[name="donation_history_query"]').val();
    const startDate = $container.data("start-date") || "";
    const endDate = $container.data("end-date") || "";
    const dateRange = $container.data("range-label") || ""; // NEW: store daterange
    const saved = $container.attr('id') === 'donationSaved' ? 'true' : 'false';
    console.log("Your query: ", query);
    $.ajax({
        url: "/dashboard/donation-history/",
        type: "GET",
        data: {
            query: query,
            page: page,
            start_date: startDate,
            end_date: endDate,
            daterange: dateRange, // match Django param
            saved_only: saved,
        },
        success: function (response) {
            $container.find('tbody').html(response.html);
            renderPagination(response.current_page, response.total_pages, $container);
        },
        error: function () {
            toastr.error("Failed to load donation history.");
        }
    });
}

function renderPagination(current, total, $container) {
    let html = '';

    if (current > 1) {
        html += `<button class="pagination-btn rounded-[8px] px-3 py-1 border" data-page="${current - 1}">Previous</button>`;
    }

    for (let i = 1; i <= total; i++) {
        html += `<button class="pagination-btn rounded-[8px] px-3 py-1 border ${i === current ? 'bg-violet-sky text-white' : ''}" data-page="${i}">${i}</button>`;
    }

    if (current < total) {
        html += `<button class="pagination-btn rounded-[8px] px-3 py-1 border" data-page="${current + 1}">Next</button>`;
    }

    $container.find('#pagination-container-saved').html(html);
}

// Initial tab click to load data
$('[data-tab="donationSaved"]').on('click', function () {
    loadDonationHistory(1, $('#donationSaved'));
});

// Search typing
$(document).on('input', 'input[name="donation_history_query"]', function () {
    const $container = $(this).closest('.donationDiv');
    loadDonationHistory(1, $container);
});

// Pagination click
$(document).on('click', '.pagination-btn', function () {
    const page = $(this).data('page');
    const $container = $(this).closest('.donationDiv');
    loadDonationHistory(page, $container); // fixed typo
});

// Date range selection
$(document).on("click", ".saveddonationdaterange", function () {
    $(".saveddonationdaterange").removeClass("font-bold");
    $(this).addClass("font-bold");
    
    const rangeLabel = $(this).data("range");
    const { start, end } = calculateDateRange(rangeLabel);

    const $tabDiv = $(this).closest(".donationDiv");
    $tabDiv.data("start-date", start);
    $tabDiv.data("end-date", end);
    $tabDiv.data("range-label", rangeLabel.toLowerCase()); // store for backend

    loadDonationHistory(1, $tabDiv);
});

function calculateDateRange(rangeLabel) {
    const endDate = new Date();
    let startDate = new Date();

    switch (rangeLabel) {
        case "1 Week":
            startDate.setDate(endDate.getDate() - 7);
            break;
        case "1 Month":
            startDate.setMonth(endDate.getMonth() - 1);
            break;
        case "1 Year":
            startDate.setFullYear(endDate.getFullYear() - 1);
            break;
        default:
            return { start: "", end: "" };
    }

    const formatDate = (d) => d.toISOString().split("T")[0];
    return {
        start: formatDate(startDate),
        end: formatDate(endDate),
    };
}

function openDonatePopup(donationId) {
  fetch(`/dashboard/get-donate-bill/${donationId}/`)
    .then(response => response.json())
    .then(data => {
      document.getElementById("receiptNo").innerText = data.receipt_no;
      document.getElementById("paymentDate").innerText = data.payment_date;
      document.getElementById("ngoName").innerText = data.ngo_name;
      document.getElementById("sign").innerText = data.ngo_name;
      document.getElementById("panNumber").innerText = data.pan;
      document.getElementById("address").innerText = data.address;
      document.getElementById("name").innerText = data.name;
      document.getElementById("email").innerText = data.email;
      document.getElementById("amount").innerText = data.amount;
      document.getElementById("payMode").innerText = data.pay_mode;
      
      document.getElementById("donateReceiptModal").style.display = 'block'; 
    })
    .catch(err => {
      console.error("Error loading receipt:", err);
      alert("Unable to load receipt.");
    });
}

//close donate popup
function closeDonatePopup() {
  const modal = document.querySelector(".donateReceiptPopup");
  modal.classList.add("hidden");
  modal.style.display = "none"; // This ensures it hides regardless of inline flex
}

//download donate pdf 
function downloadDonatePDF() {
  const element = document.getElementById('donateReceiptContent');
  const opt = {
    margin:       0.5,
    filename:     'donate-receipt.pdf',
    image:        { type: 'jpeg', quality: 0.98 },
    html2canvas:  { scale: 2 },
    jsPDF:        { unit: 'in', format: 'a4', orientation: 'portrait' }
  };

  html2pdf().set(opt).from(element).save();
}




////////////
// open platform popup
function openPlatformPopup(donationId) {
    console.log("Opening platform popup for donation ID:", donationId);

    fetch(`/dashboard/get-platform-bill/${donationId}/`)
        .then(response => {
            console.log("Fetch completed. Status:", response.status);
            return response.text();
        })
        .then(text => {
            console.log("Raw fetch response:", text);

            let data;
            try {
                data = JSON.parse(text);
            } catch (e) {
                console.error("JSON parse error:", e);
                return;
            }

            // ✅ Fill modal content
            document.getElementById("receiptNoPlatform").textContent = data.receipt_no || "";
            document.getElementById("paymentDatePlatform").textContent = data.payment_date || "";
            document.getElementById("ngoNamePlatform").textContent = data.ngo_name || "";
            document.getElementById("addressPlatform").textContent = data.address || "";
            document.getElementById("namePlatform").textContent = data.name || "";
            document.getElementById("emailPlatform").textContent = data.email || "";
            document.getElementById("amountPlatform").textContent = data.amount || "";
            document.getElementById("subTotalPlatform").textContent = data.amount || "";
            document.getElementById("gstPlatform").textContent = data.gst || "";
            document.getElementById("finalTotalPlatform").textContent = data.finalTotal || "";
            document.getElementById("actualAmountPlatform").textContent = data.amount || "";
            document.getElementById("signPlatform").textContent = data.ngo_name || "";

            // ✅ Open modal
            const modal = document.getElementById("platformReceiptModal");
            console.log("Modal found:", !!modal);

            if (!modal) {
                console.error("Modal not found in DOM!");
                return;
            }

            modal.classList.remove("hidden");
            modal.style.display = "flex";  // Force visible
            modal.style.visibility = "visible";

            console.log("Modal visibility class removed.");
            console.log("Modal computed display:", window.getComputedStyle(modal).display);
            console.log("Modal computed visibility:", window.getComputedStyle(modal).visibility);
        })
        .catch(err => {
            console.error("Error loading receipt:", err);
        });
}

// close platform popup
function closePlatformPopup() {
    const modal = document.querySelector(".platformReceiptPopup");
    modal.classList.add("hidden");
    modal.style.display = "none"; // ensures it hides regardless of inline flex
}


//download platform pdf 
function downloadPlatformPDF() {
  const element = document.getElementById('platformReceiptContent');
  const opt = {
    margin:       0.5,
    filename:     'platform-bill.pdf',
    image:        { type: 'jpeg', quality: 0.98 },
    html2canvas:  { scale: 2 },
    jsPDF:        { unit: 'in', format: 'a4', orientation: 'portrait' }
  };

  html2pdf().set(opt).from(element).save();
}