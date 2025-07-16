$(document).ready(function () {
    // Toggle dropdown on input click
    $(document).on('click', '.dropdown-input, .material-symbols-outlined:contains("keyboard_arrow_down")', function (e) {
        e.stopPropagation(); // Prevent triggering document click
        const $wrapper = $(this).closest('.dropdown-wrapper');
        $('.dropdown-list').not($wrapper.find('.dropdown-list')).hide(); // Hide other dropdowns
        $wrapper.find('.dropdown-list').toggle();
    });

    // Select option
    $(document).on('click', '.dropdown-list div', function (e) {
        e.stopPropagation();
        const $wrapper = $(this).closest('.dropdown-wrapper');
        const selectedText = $(this).text();
        const selectedID = $(this).attr('data-value');
        $wrapper.find('.dropdown-input').val(selectedText);
        $wrapper.find('.dropdown-input-hidden').val(selectedID);
        $wrapper.find('.dropdown-list').hide();
        console.log('Selected:', selectedID);
    });

    // Hide dropdown on outside click
    $(document).on('click', function () {
        $('.dropdown-list').hide();
    });


    // Calendar
    let selectedDate = null;

    $('.custom-date-trigger').on('click', function () {
        var $wrapper = $(this).closest('.calendar-wrapper');
        var $input = $wrapper.find('.custom-date-range');

        // Destroy any previous instance
        if ($input.data('daterangepicker')) {
            $input.data('daterangepicker').remove();
        }

        // Initialize daterangepicker correctly inside the wrapper
        $input.daterangepicker({
            singleDatePicker: true,
            showDropdowns: true,
            autoUpdateInput: false,
            parentEl: $wrapper,  
            drops: 'up',
            opens: 'center',
            locale: {
                format: 'DD/MM/YYYY',
                cancelLabel: 'Clear'
            }
        });

        // Open the picker safely
        $input.trigger('click');

        // Clean and re-bind
        $input.off('apply.daterangepicker cancel.daterangepicker');

        $input.on('apply.daterangepicker', function (e, picker) {
            const formattedDate = picker.startDate.format('DD/MM/YYYY');
            selectedDate = formattedDate;
            $wrapper.find('.selected-date').text(formattedDate);
            // Set the value in the validity input
            $('input[name="validity"]').val(formattedDate);
            console.log('DEBUG: Validity set to', formattedDate);
        });

        $input.on('cancel.daterangepicker', function (e, picker) {
            selectedDate = null;
            $wrapper.find('.selected-date').text('DD/MM/YY');
            $('input[name="validity"]').val('');
            console.log('DEBUG: Validity cleared');
        });
    });

    // 1. Upload area click to trigger file input
    $('.upload-area').on('click', function (e) {
        const previewVisible = $(this).find('.upload-preview').is(':visible');
        if (
            !previewVisible &&
            !$(e.target).is('input[type="file"]') &&
            !$(e.target).hasClass('cancel-upload')
        ) {
            $(this).find('input[type="file"]').trigger('click');
        }
    });

    // 2. Drag and drop handling
    $('.upload-area').on('dragover', function (e) {
        e.preventDefault();
    });

    $('.upload-area').on('dragleave', function (e) {
        e.preventDefault();
    });

    $('.upload-area').on('drop', function (e) {
        e.preventDefault();
        const file = e.originalEvent.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) {
            const fileInput = $(this).find('input[type="file"]')[0];
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            fileInput.files = dataTransfer.files;
            $(fileInput).trigger('change');
        }
    });

    // 3. Change image
    $('.upload-area').on('click', '.change-image-btn', function (e) {
        e.stopPropagation();
        const area = $(this).closest('.upload-area');
        area.find('input[type="file"]').trigger('click');
    });

    // 4. File input change handler
    $('.upload-input').on('change', function () {
        const file = this.files[0];
        const area = $(this).closest('.upload-area');
        const preview = area.find('.upload-preview');
        const placeholder = area.find('.upload-placeholder');

        if (file && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function (e) {
                preview.find('.uploaded-img').attr('src', e.target.result);
                placeholder.addClass('hidden');
                preview.removeClass('hidden').addClass("flex");
            };
            reader.readAsDataURL(file);
        }
    });

    // 5. Cancel upload
    $('.upload-area').on('click', '.cancel-upload', function (e) {
        e.stopPropagation(); // Prevent triggering upload
        const area = $(this).closest('.upload-area');
        const input = area.find('input[type="file"]');
        const preview = area.find('.upload-preview');
        const placeholder = area.find('.upload-placeholder');

        // Reset
        input.val('');
        preview.addClass('hidden').removeClass("flex");
        placeholder.removeClass('hidden');
    });

    // Title and Description Change

    const tabData = {
        "new-coupon": {
            icon: "upload",
            title: "Coupons",
            description: "Boost Your Sales—Post New Coupons for Users!"
        },
        "coupon-history": {
            icon: "upload",
            title: "Coupons",
            description: "Boost Your Sales—Post New Coupons for Users!"
        },
        "saved-coupon": {
            icon: "upload",
            title: "Coupons",
            description: "Boost Your Sales—Post New Coupons for Users!"
        }
    };

    // Click event for tabs
    $('.tab-btn-adv').click(function () {

        // Get data-tab
        const tabKey = $(this).data('tab');

        // Update icon, title, description
        if (tabData[tabKey]) {
            $('.tab-icon').text(tabData[tabKey].icon);
            $('.tab-title').text(tabData[tabKey].title);
            $('.tab-description').text(tabData[tabKey].description);
        }
    });

    // Open popup on icon click
    $(document).on('click', '[data-popup]', function (e) {
        e.stopPropagation();
        var popupType = $(this).data('popup');

        // Always hide all popups first
        $('.download-popup').addClass('hidden').removeClass("flex");
        $('.preview-popup').addClass('hidden').removeClass("flex");

        if (popupType === 'preview') {
            var couponId = $(this).data('coupon-id');
            if (couponId) {
                $.get('/coupons/coupon_detail/' + couponId + '/', function(data) {
                    // Populate popup fields
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

                    // Show the popup
                    $('.preview-popup').removeClass('hidden').addClass('flex');
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

    $('.saved-icon').on('click', function () {
        const $icon = $(this);
        const couponId = $icon.data('coupon-id');
        const isSaved = $icon.attr('data-saved') === 'true';
        const action = isSaved ? 'unsave' : 'save';

        // Toggle UI immediately
        if (isSaved) {
            $icon.removeClass('material-filled text-living-coral').addClass('text-dark-blue');
            $icon.attr('data-saved', 'false');
        } else {
            $icon.addClass('material-filled text-living-coral').removeClass('text-dark-blue');
            $icon.attr('data-saved', 'true');
        }

        // AJAX request to backend
        $.ajax({
            url: '/coupons/toggle-saved/',
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

    
    //Platform bill Popup

    $('.platform-bill-view').on('click', function () {
        $('.platform-bill-modal').removeClass('hidden').addClass('flex');
    });

    $('.close-platform-bill').on('click', function () {
        $('.platform-bill-modal').removeClass('flex').addClass('hidden');
    });

    /**** Add new coupon funcationality with step form*****/

    // Validates form, previews image, sets redemptions, and updates summary.
    $('.pay-btn').click(function(e) {
        e.preventDefault();

        let valid = true;

        $('.required-field').removeClass('error');

        $('.required-field').each(function() {
            if (!$(this).val().trim() || $(this).val() === 'Select') {
                valid = false;
                $(this).addClass('error');
            }
        });

        const imageFile = $('.upload-input')[0]?.files[0];
        if (!imageFile) {
            valid = false;
            $('.upload-area').addClass('error');
        } else {
            $('.upload-area').removeClass('error');
        }

        if (!valid) {
            window.showToaster('error','Please fill all required fields.');
            return;
        }

        if (imageFile) {
            const reader = new FileReader();
            reader.onload = function(e) {
                $('#pay-preview-img').attr('src', e.target.result);
            };
            reader.readAsDataURL(imageFile);
        }
        
        $('#pay-title').html($('input[name="title"]').val());
        $('#pay-description').html($('textarea[name="description"]').val()); 
        $('#pay-category').html($('input[name="category"]').val());
        $('#pay-code').html($('input[name="code"]').val());
        $('#pay-brand').html($('input[name="brand_name"]').val());

        const maxRedemptions = $('input[name="max_redemptions"]').val();
        $('#couponInput').val(maxRedemptions);

        if (typeof updateSummary === 'function') updateSummary();
        else if (window.updateSummary) window.updateSummary();
    });

    // Validates step 1, then shows step 2 if valid.
    $('#next-step').click(function(e) {
        e.preventDefault();

        let valid = true;

        $('#step-1 .required-field').each(function() {
            if (!$(this).val().trim() || $(this).val() === 'Select') {
                valid = false;
                $(this).addClass('error');
            } else {
                $(this).removeClass('error');
            }
        });

        if (!valid) {
            return;
        }

        $('#step-1').addClass('hidden');
        $('#step-2').removeClass('hidden');
    });

    // Hides step 2 and shows step 1 on previous button click.
    $('#prev-step').click(function(e) {
        e.preventDefault();
        $('#step-2').addClass('hidden');
        $('#step-1').removeClass('hidden');
    });

    // Calculates and displays coupon summary with GST and net payable on input.
    const CONFIG = {
        displaysPerCoupon: 10,
        ratePerDisplay: 100.00,
        gstRate: 0.18,
        advanceReceived: 0.00,
        minimumCoupons: 5
    };

    const couponInput = document.getElementById('couponInput');
    if (couponInput) {
        const couponsCountSpan = document.getElementById('coupons-count');
        const displaysPerCouponSpan = document.getElementById('displays-per-coupon');
        const ratePerDisplaySpan = document.getElementById('rate-per-display');
        const totalBeforeGstSpan = document.getElementById('total-before-gst');
        const gstAmountSpan = document.getElementById('gst-amount');
        const grossAmountSpan = document.getElementById('gross-amount');
        const advanceReceivedSpan = document.getElementById('advance-received');
        const netPayableSpan = document.getElementById('net-payable');

        function formatCurrency(amount) {
            return `₹${amount.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        }

        function updateSummary() {
            const numberOfCoupons = parseInt(couponInput.value) || 0;
            if (numberOfCoupons < CONFIG.minimumCoupons) {
                couponInput.value = CONFIG.minimumCoupons;
                return updateSummary();
            }
            const totalDisplays = numberOfCoupons * CONFIG.displaysPerCoupon;
            const totalBeforeGst = totalDisplays * CONFIG.ratePerDisplay;
            const gstAmount = totalBeforeGst * CONFIG.gstRate;
            const grossAmount = totalBeforeGst + gstAmount;
            const netPayable = grossAmount - CONFIG.advanceReceived;
            couponsCountSpan.textContent = numberOfCoupons;
            displaysPerCouponSpan.textContent = CONFIG.displaysPerCoupon;
            ratePerDisplaySpan.textContent = formatCurrency(CONFIG.ratePerDisplay);
            totalBeforeGstSpan.textContent = formatCurrency(totalBeforeGst);
            gstAmountSpan.textContent = formatCurrency(gstAmount);
            grossAmountSpan.textContent = formatCurrency(grossAmount);
            advanceReceivedSpan.textContent = formatCurrency(CONFIG.advanceReceived);
            netPayableSpan.textContent = formatCurrency(netPayable);
            netPayableSpan.classList.add('animate-pulse');
            setTimeout(() => {
                netPayableSpan.classList.remove('animate-pulse');
            }, 300);
            document.getElementById('purchased_count_field').value = numberOfCoupons;
            document.getElementById('displays_per_coupon_field').value = CONFIG.displaysPerCoupon;
            document.getElementById('rate_per_display_field').value = CONFIG.ratePerDisplay;
            document.getElementById('advance_received_field').value = CONFIG.advanceReceived;
            document.getElementById('gst_amount_field').value = gstAmount.toFixed(2);
            document.getElementById('final_paid_amount_field').value = netPayable.toFixed(2);
        }
        couponInput.addEventListener('input', updateSummary);
        couponInput.addEventListener('change', updateSummary);
        couponInput.addEventListener('keydown', function(e) {
            if (e.key === '-' || e.key === 'e' || e.key === 'E') {
                e.preventDefault();
            }
        });
        updateSummary();
    }

    // Validates form, prepares data, and submits via AJAX for coupon creation.
    $('#main-coupon-form').on('submit', function (e) {
        e.preventDefault();

        const csrftoken = $('[name="csrfmiddlewaretoken"]').val();

        const couponCount = parseInt($('#couponInput').val());
        const imageFile = $('.upload-input')[0].files[0];
        const offerType = $('input[name="offer_type"]').val();
        const spendingPower = $('input[name="spending_power"]').val();
        const maxRedemptions = $('input[name="max_redemptions"]').val();
        const validity = $('input[name="validity"]').val();

        if (!couponCount || couponCount < 5) {
            window.showToaster('error',"Please enter at least 5 coupons.");
            return;
        }

        if (!imageFile) {
            window.showToaster('error',"Please upload a coupon image.");
            return;
        }

        if (!offerType) {
            window.showToaster('error',"Please select an Offer Type.");
            return;
        }

        if (!spendingPower) {
            window.showToaster('error',"Please select Spending Power.");
            return;
        }

        if (!maxRedemptions || parseInt(maxRedemptions) < 5) {
            window.showToaster('error',"Maximum redemptions should be at least 5.");
            return;
        }

        if (!validity || validity === 'DD/MM/YY') {
            window.showToaster('error',"Please select coupon validity date.");
            return;
        }

        const formUrl = $(this).attr('action');
        const formType = $(this).attr('method');
        const formData = new FormData(this);

        formData.set('purchased_count', couponCount);
        formData.set('displays_per_coupon', 10);
        formData.set('rate_per_display', 100.00);
        formData.set('advance_received', 100.00);
        const totalBeforeGst = couponCount * 10 * 100.00;
        const gstAmount = totalBeforeGst * 0.18;
        const finalAmount = totalBeforeGst + gstAmount - 100.00;
        formData.set('gst_amount', gstAmount.toFixed(2));
        formData.set('final_paid_amount', finalAmount.toFixed(2));

        $.ajax({
            url: formUrl,
            type: formType,
            headers: { 'X-CSRFToken': csrftoken },
            data: formData,
            processData: false,
            contentType: false,
            success: function (resp) {
                if (resp.success) {
                    window.showToaster('success',resp.message);
                    setTimeout(() => {
                        window.location.href = resp.redirect;
                    }, 1000);
                } else {
                    window.showToaster('error', resp.message || "Validation failed on server.");
                }
            },
            error: function () {
                window.showToaster('error',"Server error. Try again.");
            }
        });
    });
});