document.addEventListener("DOMContentLoaded", function () {

    // Donation Popup Functions
    window.openPopup = function (event) {
        if (event) event.preventDefault();
        const popup = document.querySelector(".donation-popup");
        if (popup) {
            popup.classList.remove("hidden", "pointer-events-none");
            popup.classList.add("flex");
        }
    };

    window.closePopup = function () {
        const popup = document.querySelector(".donation-popup");
        if (popup) {
            popup.classList.remove("flex");
            popup.classList.add("hidden", "pointer-events-none");
        }
    };

    window.goToDonatePage = function () {
        window.location.href = "/donate/";
        // window.location.href = "donate.html";
    };

    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape") {
            closePopup();
        }
    });

    const popup = document.querySelector(".donation-popup");
    if (popup) {
        popup.addEventListener("click", function (e) {
            if (e.target === popup) {
                closePopup();
            }
        });
    }

    // Dynamic calculation for donation breakdown
    const donationInput = document.getElementById('donation-amount');
    const amountToNGOField = document.querySelector('[data-amount-to-ngo]');
    const platformFeeField = document.querySelector('[data-platform-fee]');
    const gstField = document.querySelector('[data-gst]');
    const totalAmountField = document.querySelector('[data-total-amount]');

    function updateBreakdown() {
        let amount = parseFloat(donationInput.value) || 0;
        if (amount < 100) amount = 100;
        const platformFee = +(amount * 0.02).toFixed(2);
        const gst = +(platformFee * 0.18).toFixed(2);
        const amountToNGO = +(amount - platformFee - gst).toFixed(2);
        if (amountToNGOField) amountToNGOField.textContent = `₹${amountToNGO}`;
        if (platformFeeField) platformFeeField.textContent = `₹${platformFee}`;
        if (gstField) gstField.textContent = `₹${gst}`;
        if (totalAmountField) totalAmountField.textContent = `₹${amount}`;
    }

    if (donationInput) {
        donationInput.addEventListener('input', updateBreakdown);
        donationInput.addEventListener('change', updateBreakdown);
        updateBreakdown();
    }

    // CSRF helper function
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const payBtn = document.getElementById('pay-btn');
    if (payBtn) {
        payBtn.addEventListener('click', function(e) {
            e.preventDefault();

            // Collect values
            const amount = document.getElementById('donation-amount').value;
            const panNumber = document.getElementById('pan-number') ? document.getElementById('pan-number').value : '';
            const panDocument = document.getElementById('pan_document') ? document.getElementById('pan_document').files[0] : null;

            // Build FormData
            const formData = new FormData();
            formData.append('donation_amount', amount);
            formData.append('pan_number', panNumber);
            if (panDocument) formData.append('pan_document', panDocument);

            fetch(window.location.pathname, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    toastr.success('Donation successful');
                    // showToast('Donation successful!', 'success');

                    // --- DYNAMIC POPUP UPDATE START ---
                    // Calculate values
                    const platformFee = (parseFloat(amount) * 0.02).toFixed(2);
                    const gst = (platformFee * 0.18).toFixed(2);
                    const amountToNGO = (parseFloat(amount) - platformFee - gst).toFixed(2);

                    // Update popup fields
                    const popup = document.querySelector('.donation-popup');
                    if (popup) {
                        const txId = popup.querySelector('[data-popup-transaction-id]');
                        const amtNGO = popup.querySelector('[data-popup-amount-to-ngo]');
                        const pf = popup.querySelector('[data-popup-platform-fee]');
                        const gstField = popup.querySelector('[data-popup-gst]');
                        const totalAmt = popup.querySelector('[data-popup-total-amount]');
                        if (txId) txId.textContent = data.transaction_id || '';
                        if (amtNGO) amtNGO.textContent = '₹' + amountToNGO;
                        if (pf) pf.textContent = '₹' + platformFee;
                        if (gstField) gstField.textContent = '₹' + gst;
                        if (totalAmt) totalAmt.textContent = '₹' + amount;
                    }
                    // --- DYNAMIC POPUP UPDATE END ---

                    openPopup();
                } else {
                    toastr.error(data.error || 'Donation failed');
                    // showToast(data.error || 'Donation failed', 'error');
                }
            })
            .catch(() => {
                toastr.error('Something went wrong!');
                // showToast('Something went wrong!', 'error');
            });
        });
    }

    // Toast function
    window.showToast = function(message, type) {
        if (window.toaster && typeof window.toaster.show === 'function') {
            window.toaster.show(message, type);
        } else {
            toastr.error(message);
            // alert(message); // fallback
        }
    }

    //close success page after pay
    const openBtn = document.getElementById("openDonatePopup");
    const popupClose = document.getElementById("donatePopup");

    openBtn.addEventListener("click", function () {
        popupClose.classList.remove("hidden");
        popupClose.classList.add("flex");
    });
    // Attach event to all close buttons inside the modal
    popupClose.addEventListener("click", function (e) {
        if (
            e.target.classList.contains("donate-close-btn") ||
            e.target.id === "donatePopup"
        ) {
            popupClose.classList.remove("flex");
            popupClose.classList.add("hidden");
        }
    });
})


// Show popup on upload icon click
document.querySelector('.pan-upload-trigger').addEventListener('click', function () {
  document.querySelector('.pan-file-access-popup').classList.remove('hidden');
});

// Hide popup on Deny click
document.querySelector('.pan-deny-access-btn').addEventListener('click', function () {
  document.querySelector('.pan-file-access-popup').classList.add('hidden');
});

// Allow file access and trigger file input
document.querySelector('.pan-allow-access-btn').addEventListener('click', function () {
  document.querySelector('.pan-file-access-popup').classList.add('hidden');
  document.querySelector('.pan-upload-input').click();
});

// On file selection, update virus scan status
document.querySelector('.pan-upload-input').addEventListener('change', function () {
  const checkbox = document.querySelector('.scan-toggle');
  const statusText = document.querySelector('.status-text');

  if (this.files && this.files.length > 0) {
    checkbox.checked = true;
    checkbox.classList.remove('border-dark-gray');
    checkbox.classList.add('border-green');
    statusText.textContent = 'Virus Scan';
    statusText.className = 'status-text text-green text-16-nr';
  }
});

// Fix: Trigger file input on upload button click
var uploadTrigger = document.querySelector('.uploadTrigger');
var panInput = document.getElementById('pan_document');
if (uploadTrigger && panInput) {
    uploadTrigger.addEventListener('click', function () {
        panInput.click();
    });
    // Optional: Show file name after selection
    panInput.addEventListener('change', function() {
        var fileNameSpan = document.getElementById('pan-file-name');
        if (fileNameSpan) {
            fileNameSpan.textContent = this.files[0] ? this.files[0].name : '';
        }
    });
}
