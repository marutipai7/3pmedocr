document.addEventListener("DOMContentLoaded", function () {
  const triggers = document.querySelectorAll(".viewPopupTrigger");
  const popup = document.querySelector(".viewPopup");

  if (triggers.length && popup) {
    triggers.forEach(trigger => {
      trigger.addEventListener("click", function () {
        popup.classList.remove("hidden");
      });
    });
  }
});

// const payBtn = document.querySelector(".pay-button");
//   const popup = document.querySelector(".subscription-popup");
//   const closeBtn = document.querySelector(".close-popup");

//   if (payBtn && popup && closeBtn) {
//     payBtn.addEventListener("click", function (e) {
//       e.preventDefault();
//       popup.classList.remove("hidden");
//     });

//   closeBtn.addEventListener("click", function () {
//     popup.classList.add("hidden");
//   });
// }

document.addEventListener("DOMContentLoaded", function () {
  const payBtnFail = document.querySelector(".pay-button-fail");
  const popupFail = document.querySelector(".subscription-popup-fail");
  const closeBtnFail = document.querySelector(".subscription-popup-fail .close-popup");

  if (payBtnFail && popupFail && closeBtnFail) {
    payBtnFail.addEventListener("click", function (e) {
      e.preventDefault();
      popupFail.classList.remove("hidden");
    });

    closeBtnFail.addEventListener("click", function () {
      popupFail.classList.add("hidden");
      location.reload();
    });
  }
});


const openInvoiceBtn = document.querySelector(".view-invoice-btn-in-popup");
  const invoicePopup = document.querySelector(".subscriptionTaxPopupInvoice");
  const closeInvoiceBtn = document.querySelector(".subscriptionTaxPopupInvoice .close-popup-invoice");
  const mainPopup = document.querySelector(".subscription-popup");

  if (openInvoiceBtn && invoicePopup && closeInvoiceBtn && mainPopup) {
    openInvoiceBtn.addEventListener("click", function () {
      invoicePopup.classList.remove("hidden");
      mainPopup.classList.add("hidden"); // Hide the background popup
    });

    closeInvoiceBtn.addEventListener("click", function () {
      invoicePopup.classList.add("hidden");
      //mainPopup.classList.remove("hidden"); // Show the background popup again
    });
  }
//Quaterly dropdown
 // Toggle dropdown on trigger click
document.querySelectorAll('.dropdown-trigger').forEach(trigger => {
  trigger.addEventListener('click', function (e) {
    e.stopPropagation(); // Prevent bubbling up
    const wrapper = this.closest('.dropdown-wrapper');
    const dropdown = wrapper.querySelector('.dropdown-menu');
    dropdown.classList.toggle('hidden');
  });
});

// Handle option selection and reflect in trigger box
document.querySelectorAll('.dropdown-wrapper').forEach(wrapper => {
  const dropdownItems = wrapper.querySelectorAll('.dropdown-item');
  const selectedTextElement = wrapper.querySelector('.selected-option');

  dropdownItems.forEach(item => {
    item.addEventListener('click', function () {
      selectedTextElement.textContent = this.textContent;
      wrapper.querySelector('.dropdown-menu').classList.add('hidden');
    });
  });
});

// Close dropdown when clicking outside
document.addEventListener('click', function (e) {
  document.querySelectorAll('.dropdown-wrapper').forEach(wrapper => {
    if (!wrapper.contains(e.target)) {
      const dropdown = wrapper.querySelector('.dropdown-menu');
      dropdown.classList.add('hidden');
    }
  });
});

// Close logic for .viewPopup popup
document.addEventListener("DOMContentLoaded", function () {
  const viewPopup = document.querySelector(".viewPopup");
  const closeBtnViewPopup = document.querySelector(".viewPopup .close-popup");

  if (closeBtnViewPopup && viewPopup) {
    closeBtnViewPopup.addEventListener("click", function () {
      viewPopup.classList.add("hidden");
    });
  }
});

document.addEventListener("DOMContentLoaded", function () {
  const subscriptionPopup = document.querySelector(".subscription-popup");
  const closeSubscriptionBtn = document.querySelector(".close-popup-subscription");

  if (subscriptionPopup && closeSubscriptionBtn) {
    closeSubscriptionBtn.addEventListener("click", function () {
      subscriptionPopup.classList.add("hidden");
    });
  }
});


$(document).ready(function () {
    let selectedPlan = null;
    let selectedOptions = {}; // 🔹 Stores user selection per plan

    // When dropdown option is selected
    $(".dropdown-item").on("click", function () {
        const option = $(this).text().trim();
        const planCard = $(this).closest("[data-plan-id]");
        selectedPlan = planCard.data("plan-id");

        // ✅ Save selected option for this plan
        selectedOptions[selectedPlan] = option;

        // Update UI
        planCard.find(".selected-option").text(option);

        // Fetch calculation
        calculatePrice(selectedPlan, option);
    });

    // Subscribe button click
    $(document).on("click", ".subscribe-btn", function () {
        selectedPlan = $(this).data("plan-id");

        // ✅ Use saved option if available, otherwise fallback
        let selectedOption = selectedOptions[selectedPlan] || "Monthly";

        calculatePrice(selectedPlan, selectedOption);
    });

    // Pay button click → save subscription
    $(document).on("click", ".pay-button", function (e) {
        e.preventDefault();

        $.ajax({
            url: "subscribe/",
            type: "POST",
            headers: {
                "X-CSRFToken": $("meta[name='csrf-token']").attr("content")
            },
            data: {
                plan_id: $(this).data("plan-id"),
                billing_option: $(this).data("option"),
            },
            success: function (data) {
                if (data.success) {
                    toastr.success(data.message);

                    // ✅ Inject company name & amount into popup
                    $(".subscription-popup .company-name").text(data.company_name);
                    $(".subscription-popup .amount").text(data.amount);

                    // ✅ Attach historyId to the invoice button
                    $(".subscription-popup .invoice-btn")
                        .off("click")  // remove any old handler
                        .on("click", function () {
                            openInvoicePopup(data.history_id);
                        });
                        
                    // ✅ Show popup instead of reloading
                    $(".subscription-popup").removeClass("hidden");

                    // ✅ Attach reload to close button
                    $(".close-popup-subscription").off("click").on("click", function () {
                        $(".subscription-popup").addClass("hidden");
                        location.reload();
                    });

                } else if (data.error) {
                    toastr.error(data.error);
                }
            },
            error: function (xhr) {
                let response = xhr.responseJSON;
                if (response && response.error) {
                    toastr.error(response.error);  // e.g. "You already have this plan active."
                } else {
                    toastr.error("Something went wrong. Please try again.");
                }
            }
        });
    });

    // 🔹 Extracted function for calculation
    function calculatePrice(planId, option) {
        $.get("calculate-price/", { plan_id: planId, billing_option: option }, function (data) {
            if (data.error) {
                alert(data.error);
                return;
            }

            $("#payment-details").html(`
                <div class="flex flex-col md:flex-row items-center justify-between">
                    <div class="text-lg font-semibold">Plan - ${data.plan_name}</div>
                    <div class="text-lg font-semibold">Start date - ${data.start_date} End date - ${data.end_date}</div>
                    <div class="text-lg font-semibold">${data.billing_option}</div>
                </div>

                <div class="flex justify-between mt-4">
                    <p>Total value before GST</p>
                    <p>${data.total_before_gst}</p>
                </div>

                <div class="flex justify-between mt-4">
                    <p>Add: GST @ 18%</p>
                    <p>${data.gst_amount}</p>
                </div>

                <div class="flex justify-between mt-4">
                    <p>Gross invoice amount</p>
                    <p>${data.gross_amount}</p>
                </div>

                <div class="flex justify-between mt-3">
                    <p>Net payable</p>
                    <p class="text-xl font-semibold text-dark-blue">${data.net_payable}</p>
                </div>
            `);

            // Show buttons and attach values
            $("#payment-actions").show();
            $(".pay-button").attr("data-plan-id", planId).attr("data-option", option);
        });
    }
});

let historyDataGlobal = [];  // store full history
let currentPage = 1;
let rowsPerPage = 5;  // adjust as needed

function loadSubscriptionHistory(target = "main") {
    $.get("subscription-history/", function (response) {
        if (response.history && response.history.length > 0) {
            // Store history globally
            historyDataGlobal = response.history;

            if (target === "popup") {
                // Show only latest 5 rows for popup
                renderHistoryTable(response.history.slice(0, 5), "popup");
            } else {
                // Show with pagination
                renderPaginatedHistory();
            }
        } else {
            let noDataRow =
                target === "popup"
                    ? `<tr><td colspan="7" class="text-center py-4">No history found</td></tr>`
                    : `<tr><td colspan="8" class="text-center py-4">No history found</td></tr>`;

            if (target === "popup") {
                $(".viewPopup .subscription-history-body").html(noDataRow);
            } else {
                $(".subscription-history-body").html(noDataRow);
                $(".subscription-pagination").html(""); // clear pagination
            }
        }
    });
}

function renderHistoryTable(data, target = "main") {
    let rows = "";

    data.forEach(item => {
        if (target === "popup") {
            rows += `
                <tr class="text-sm font-semibold text-black">
                    <td class="px-4 py-2.5 text-center">${item.payment_date}</td>
                    <td class="px-4 py-2.5 text-center">${item.plan_name}</td>
                    <td class="px-4 py-2.5 text-center">${item.package_type}</td>
                    <td class="px-4 py-2.5 text-center">${item.start_date}</td>
                    <td class="px-4 py-2.5 text-center">${item.end_date}</td>
                    <td class="px-4 py-2.5 text-center">${item.licenses}</td>
                    <td class="px-4 py-2.5 text-center">${item.amount}</td>
                </tr>`;
        } else {
            rows += `
                <tr class="text-sm font-semibold text-black">
                    <td class="px-4 py-2.5 text-center">${item.payment_date}</td>
                    <td class="px-4 py-2.5 text-center">${item.plan_name}</td>
                    <td class="px-4 py-2.5 text-center">${item.package_type}</td>
                    <td class="px-4 py-2.5 text-center">${item.start_date}</td>
                    <td class="px-4 py-2.5 text-center">${item.end_date}</td>
                    <td class="px-4 py-2.5 text-center">${item.licenses}</td>
                    <td class="px-4 py-2.5 text-center">${item.amount}</td>
                    <td class="px-4 py-2.5 text-center">
                        <div class="flex items-center justify-center">
                            <span class="subscription-bookmark-toggle cursor-pointer hover:bg-transparent-dark-blue rounded-full p-2 transition-all mr-2 
                                ${item.saved ? 'material-symbols-outlined material-filled text-dark-blue' : 'material-symbols-outlined text-dark-blue'}"
                                data-subscription-id="${item.id}"
                                data-saved="${item.saved ? 'true' : 'false'}">
                                bookmark
                            </span>
                            <span class="material-symbols-outlined viewPopupTrigger cursor-pointer hover:bg-transparent-dark-blue rounded-full p-2 transition-all mr-2">visibility</span>
                            <span class="material-symbols-outlined cursor-pointer hover:bg-transparent-dark-blue rounded-full p-2 transition-all mr-2">download</span>
                            <span class="mx-1">
                                <img src="/static/images/assignment.svg"
                                     alt="Invoice"
                                     title="Invoice"
                                     class="inline-block w-6 h-6 align-middle cursor-pointer"
                                     onclick="openInvoicePopup(${item.id})" />
                            </span>
                        </div>
                    </td>
                </tr>`;
        }
    });

    if (target === "popup") {
        $(".viewPopup .subscription-history-body").html(rows);
    } else {
        $(".subscription-history-body").html(rows);
    }
}

function renderPaginatedHistory() {
    let start = (currentPage - 1) * rowsPerPage;
    let end = start + rowsPerPage;
    let paginatedData = historyDataGlobal.slice(start, end);

    renderHistoryTable(paginatedData, "main");

    let totalPages = Math.ceil(historyDataGlobal.length / rowsPerPage);
    let paginationHtml = "";

    if (totalPages > 1) {
        paginationHtml += `<div class="flex justify-center mt-4 gap-2">`;

        // Prev button
        if (currentPage > 1) {
            paginationHtml += `<button class="px-3 py-1 border rounded-md bg-dark-blue text-white" onclick="changePage(${currentPage - 1})">Prev</button>`;
        }

        // Always show first two
        for (let i = 1; i <= Math.min(2, totalPages); i++) {
            paginationHtml += `
                <button class="px-3 py-1 border rounded-md ${i === currentPage ? 'bg-dark-blue text-white' : 'bg-white text-dark-blue'}"
                        onclick="changePage(${i})">${i}</button>`;
        }

        // Ellipsis after first two if needed
        if (currentPage > 4) {
            paginationHtml += `<span class="px-2">...</span>`;
        }

        // Middle neighbors (current -1, current, current +1)
        for (let i = Math.max(3, currentPage - 1); i <= Math.min(totalPages - 2, currentPage + 1); i++) {
            paginationHtml += `
                <button class="px-3 py-1 border rounded-md ${i === currentPage ? 'bg-dark-blue text-white' : 'bg-white text-dark-blue'}"
                        onclick="changePage(${i})">${i}</button>`;
        }

        // Ellipsis before last two if needed
        if (currentPage < totalPages - 3) {
            paginationHtml += `<span class="px-2">...</span>`;
        }

        // Always show last two
        for (let i = Math.max(totalPages - 1, 3); i <= totalPages; i++) {
            paginationHtml += `
                <button class="px-3 py-1 border rounded-md ${i === currentPage ? 'bg-dark-blue text-white' : 'bg-white text-dark-blue'}"
                        onclick="changePage(${i})">${i}</button>`;
        }

        // Next button
        if (currentPage < totalPages) {
            paginationHtml += `<button class="px-3 py-1 border rounded-md bg-dark-blue text-white" onclick="changePage(${currentPage + 1})">Next</button>`;
        }

        paginationHtml += `</div>`;
    }

    $(".subscription-pagination").html(paginationHtml);
}

function changePage(page) {
    currentPage = page;
    renderPaginatedHistory();
}


function loadSubscriptionSummary() {
    $.get("current-summary/", function(response) {
        if (response.summary) {
            const s = response.summary;
            $(".summary-status").text(s.status);
            $(".summary-plan").text(s.plan_name);
            $(".summary-licenses").text(s.license_count);
            $(".summary-payment").text(s.payment_date);
            $(".summary-start").text(s.start_date);
            $(".summary-end").text(s.end_date);
            $(".summary-days-left").text(`(${s.days_left} days left to go)`);
            $(".summary-package").text(s.package_type);
            $(".summary-amount").text(s.amount);
        }
    });
}
// 🔹 Load main table immediately on page load
$(document).ready(function () {
    loadSubscriptionHistory("main");
});

// 🔹 Load popup table only when user clicks the eye icon
$(document).on("click", ".viewPopupTrigger", function () {
    loadSubscriptionSummary();
    loadSubscriptionHistory("popup");
    $(".viewPopup").removeClass("hidden");
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

function openInvoicePopup(historyId) {
    $.get(`invoice/${historyId}/`, function(data) {
        if (data.error) {
            toastr.error(data.error);
            return;
        }

        // ✅ Fill invoice fields
        $("#invoice_no").text(data.invoice_no);
        $("#invoice_date").text(data.invoice_date);

        // Client details
        $("#client_name").text(data.client.company_name);
        $("#client_gstin").text(data.client.gstin);
        $("#client_address").text(data.client.address);
        $("#client_contact").text(data.client.contact_person);
        $("#client_email").text(data.client.email);

        // Supplier details
        $("#supplier_gstin").text(data.supplier.gstin);
        $("#supplier_name").text(data.supplier.name);
        $("#supplier_address").text(data.supplier.address);
        $("#supplier_contact").text(data.supplier.contact);
        $("#supplier_email").text(data.supplier.email);
        $("#signature_supplier_name").text(data.supplier.name);

        // Reset invoice items table
        $("#invoice_items").empty();

        // Pick only 4th feature (index 3)
        let featureText = "";
        if (data.features && data.features.length >= 4) {
            featureText = data.features[3].text;
        }

        // Insert plan row
        $("#invoice_items").append(`
            <tr>
                <td class="border border-gray-400 px-2 py-1">
                    ${data.package_type} Subscription – ${data.plan_name} (${data.licenses} Users)
                    ${featureText ? `<br><span class="text-sm text-gray-600">(${featureText})</span>` : ""}
                </td>
                <td class="border border-gray-400 px-2 py-1">998431</td>
                <td class="border border-gray-400 px-2 py-1">1</td>
                <td class="border border-gray-400 px-2 py-1">₹${data.base_price}</td>
                <td class="border border-gray-400 px-2 py-1">18%</td>
                <td class="border border-gray-400 px-2 py-1">₹${data.net_payable}</td>
            </tr>
        `);

        // Update amounts
        $(".invoice-subtotal").text(`₹${data.base_price}`);
        $(".invoice-gst").text(`₹${data.gst_amount}`);
        $(".invoice-total").text(`₹${data.net_payable}`);

        $("#txn_id").text(data.txn_id);

        // Convert to words
        $("#amount_words").text(`INR ${amountToWords(parseFloat(data.net_payable))} Only`);

        // Show popup
        $(".subscriptionTaxPopupInvoice").removeClass("hidden");
    });
}

// Close button
$(document).on("click", ".close-popup-invoice", function () {
    $(".subscriptionTaxPopupInvoice").addClass("hidden");
});

$(document).on("click", ".subscription-bookmark-toggle", function () {
    let $icon = $(this);
    let historyId = $icon.data("subscription-id");

    $.ajax({
        url: `/subscription/subscription-history/${historyId}/bookmark/`,
        type: "POST",
        headers: {
            "X-CSRFToken": $("meta[name='csrf-token']").attr("content")
        },
        success: function (response) {
            if (response.success) {
                if (response.saved) {
                    $icon.addClass("material-filled text-dark-blue");
                    $icon.removeClass("text-white");
                    toastr.success("Subscription saved");
                } else {
                    $icon.removeClass("material-filled text-dark-blue");
                    toastr.success("Subscription unsaved");
                }
                $icon.attr("data-saved", response.saved);
            } else if (response.error) {
                toastr.error(response.error);
            }
        },
        error: function () {
            toastr.error("Something went wrong. Please try again.");
        }
    });
});
