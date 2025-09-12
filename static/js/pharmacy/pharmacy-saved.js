$(document).ready(function () {
    const directionBtn = $(".direction-trigger");

    // Show the modal when trigger is clicked
    directionBtn.on('click', function (e) {
        $(".direction-modal").removeClass('hidden').addClass('flex');
    });

    // Hide the modal when clicking outside of it
    $(document).on('click', function (event) {
        const $modal = $(".direction-modal");
        const $popupBox = $modal.find("> div"); // direct child is the popup

        if (
            $modal.is(":visible") &&
            !$popupBox.is(event.target) &&
            $popupBox.has(event.target).length === 0 &&
            !$(event.target).closest(".direction-trigger").length
        ) {
            $modal.removeClass("flex").addClass("hidden");
        }
    });

    //Place View Popup Functionality

    const placeViewBtn = $(".place-view-btn");
    const placeCloseBtn = $('.place-view-close');

    placeViewBtn.on("click", function () {
        $('.place-view-modal').removeClass('hidden').addClass('flex');
    })

    placeCloseBtn.on('click', function () {
        $('.place-view-modal').removeClass('flex').addClass('hidden');
    })

    //Order View Popup Functionality

    const orderViewBtn = $(".order-view-btn");
    const orderCloseBtn = $('.order-view-close');

    orderViewBtn.on("click", function () {
        $('.order-view-modal').removeClass('hidden').addClass('flex');
    })

    orderCloseBtn.on('click', function () {
        $('.order-view-modal').removeClass('flex').addClass('hidden');
    })

    //Post View of popup of share
    $('.material-symbols-outlined:contains("visibility")').on('click', function () {
        $('.share-post-view-modal').removeClass('hidden').addClass('flex');
    });

    $('.share-post-view-close').on('click', function () {
        $('.share-post-view-modal').removeClass('flex').addClass('hidden');
    });

    const shareViewBtn = $(".share-view-btn");
    const shareCloseBtn = $('.share-view-close');

    shareViewBtn.on("click", function () {
        $('.share-view-modal').removeClass('hidden').addClass('flex');
    })

    shareCloseBtn.on('click', function () {
        $('.share-view-modal').removeClass('flex').addClass('hidden');
    })

    // //Donation View Popup Functionality

    // const donationViewBtn = $(".donation-view-btn");
    // const donationCloseBtn = $('.donation-view-close');

    // donationViewBtn.on("click", function () {
    //     $('.donation-view-modal').removeClass('hidden').addClass('flex');
    // })

    // donationCloseBtn.on('click', function () {
    //     $('.donation-view-modal').removeClass('flex').addClass('hidden');
    // })
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
                toastr.error("Failed to load donation history.");
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
      toastr.error("Unable to load receipt.");
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
                toastr.error("Unable to load receipt.");
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
            toastr.error("Unable to load receipt.");
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
    
$(document).on('click', '.donate-bookmark-toggle', function() {
        console.log('Bookmark clicked!');
        var $icon = $(this);
        var donationId = $icon.data('donation-id');
        var isSaved = $icon.data('saved') === true || $icon.data('saved') === 'true';
        var action = isSaved ? 'unsave' : 'save';
    
        $.ajax({
            url: '/dashboard/toggle-saved/donation/',
            type: 'POST',
            data: {
                donation_id: donationId,
                action: action,
                csrfmiddlewaretoken: getCookie('csrftoken')
            },
            success: function(response) {
                if (response.success) {
                    $icon.data('saved', response.saved);
                    if (response.saved) {
                        $icon.addClass('material-filled text-light-sea-green');
                        // $icon.removeClass('text-living-coral');
                    } else {
                        $icon.removeClass('material-filled text-light-sea-green');
                        // If in Saved Donation table, remove the row
                        if ($icon.closest('.saved-donation').length || $icon.closest('table').closest('.saved-donation').length) {
                            $icon.closest('tr').remove();
                        }
                    }
                    // Use toastr if available, otherwise show alert
                    if (typeof toastr !== 'undefined') {
                        toastr.success(response.saved ? 'Donation saved!' : 'Donation unsaved!');
                    } else {
                        alert(response.saved ? 'Donation saved!' : 'Donation unsaved!');
                    }
                } else {
                    if (typeof toastr !== 'undefined') {
                        toastr.error(response.error || 'Could not update saved status.');
                    } else {
                        alert(response.error || 'Could not update saved status.');
                    }
                }
            },
            error: function(xhr, status, error) {
                console.error('AJAX Error:', xhr.responseText);
                if (typeof toastr !== 'undefined') {
                    toastr.error('Could not update saved status.');
                } else {
                    alert('Could not update saved status.');
                }
            }
        });
    });