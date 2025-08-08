const cards = document.querySelectorAll(".donation-card");
const closeBtn = document.querySelector(".close-expanded");
const detailsBox = document.querySelector(".donation-details-box");
const tabsSection = document.querySelector(".tabs-section");
const searchFilterSection = document.querySelector(".search-filter-section");
const paginationSections = document.querySelectorAll(".pagination-section");

// Handle card expand functionality
cards.forEach((card) => {
  const triggers = card.querySelectorAll(".toggle-expand");

  triggers.forEach((trigger) => {
    trigger.addEventListener("click", () => {
      // Hide other cards
      cards.forEach((other) => {
        if (other !== card) other.style.display = "none";
      });

      const cardContainer = document.querySelector(".card-container");

      // Remove grid layout when expanding
      cardContainer.classList.remove(
        "grid",
        "grid-cols-1",
        "md:grid-cols-2",
        "gap-4",
        "justify-items-center"
      );

      // Elements to modify
      const defaultHeading = card.querySelector(".default-heading");
      const expandedHeading = card.querySelector(".expanded-heading");
      const expandedPara = card.querySelector(".expanded-para");
      const donateWrapper = card.querySelector(".donate-button-wrapper");
      const topSection = card.querySelector(".top-section");
      const locationLine = card.querySelector(".location-line");

      // Get the specific elements we need to hide and show
      const donationAmount = card.querySelector(".donation-amount");
      const donateBtnContainer = card.querySelector(".donate-btn-container");
      const expandedButtons = card.querySelector(".expanded-buttons");

      // Show expanded content
      defaultHeading.classList.add("hidden");
      expandedHeading.classList.remove("hidden");
      expandedPara.classList.remove("hidden");
      detailsBox.classList.remove("hidden");
      closeBtn.classList.remove("hidden");

      // Hide donation amount and donate button
      donationAmount.classList.add("hidden");
      donateBtnContainer.classList.add("hidden");

      // Show visit website and pay buttons
      expandedButtons.classList.remove("hidden");

      // Adjust layout for expanded view
      topSection.classList.remove("flex");
      topSection.classList.add("block");

      donateWrapper.classList.remove(
        "ml-4",
        "mt-0",
        "flex-col",
        "items-center"
      );
      donateWrapper.classList.add("mt-4", "w-full", "flex", "justify-end");

      locationLine.classList.remove("mt-2");
      locationLine.classList.add("mt-4");

      // Make card fullscreen for expanded view
      card.classList.add(
        "fixed",
        "inset-0",
        "z-50",
        "h-screen",
        "w-screen",
        "overflow-y-auto",
        "rounded-none"
      );
      card.classList.remove("m-4", "rounded-lg");

      // Hide UI sections
      tabsSection?.classList.add("hidden");
      searchFilterSection?.classList.add("hidden");
      paginationSections.forEach((pagination) =>
        pagination.classList.add("hidden")
      );
    });
  });

  // Handle "Read More"
  const readMoreBtn = card.querySelector(".read-more-btn");
  const expandedPara = card.querySelector(".expanded-para");

  readMoreBtn?.addEventListener("click", (e) => {
    e.preventDefault();
    expandedPara?.classList.remove("hidden");
    readMoreBtn?.classList.add("hidden");

    // Get the specific elements we need to hide and show
    const donationAmount = card.querySelector(".donation-amount");
    const donateBtnContainer = card.querySelector(".donate-btn-container");
    const expandedButtons = card.querySelector(".expanded-buttons");
    const donateWrapper = card.querySelector(".donate-button-wrapper");

    // Hide donation amount and donate button
    donationAmount.classList.add("hidden");
    donateBtnContainer.classList.add("hidden");

    // Show visit website and pay buttons
    expandedButtons.classList.remove("hidden");

    // Adjust donation wrapper layout
    donateWrapper.classList.remove("ml-4", "mt-0", "flex-col", "items-center");
    donateWrapper.classList.add("mt-4", "w-full", "flex", "justify-end");

    tabsSection?.classList.add("hidden");
    searchFilterSection?.classList.add("hidden");
    paginationSections.forEach((pagination) =>
      pagination.classList.add("hidden")
    );
  });
});


 
function openPopup() {
  document.querySelector(".assignmentPopup").classList.remove("hidden");
}

function closePopup() {
  document.querySelector(".assignmentPopup").classList.add("hidden");
}

function openPopupDonation() {
  document.querySelector(".donationPopup").classList.remove("hidden");
}

function closePopupDonation() {
  document.querySelector(".donationPopup").classList.add("hidden");
}
console.log("Popup");

$(".filter-toggle-btn").on("click", function (e) {
  e.stopPropagation();
  $(".filter-popup").not($(this).siblings(".filter-popup")).addClass("hidden");
  $(this).siblings(".filter-popup").toggleClass("hidden");
});

$(document).on("click", function () {
  $(".filter-popup").addClass("hidden");
});

// Open the nested share popup
$(".openSharePopup").click(function () {
  $(".sharePopup").removeClass("hidden");
});

// Close the nested share popup
$(".closeSharePopup").click(function () {
  $(".sharePopup").addClass("hidden");
});


function openPostDetail(el) {
    document.getElementById('modalNgoName').textContent = el.getAttribute('data-ngo-name');
    document.getElementById('modalHeader').textContent = el.getAttribute('data-header');
    document.getElementById('modalDescription').textContent = el.getAttribute('data-description');
    var website = el.getAttribute('data-website-url');
    var websiteLink = document.getElementById('modalWebsite');
    if (website) {
      websiteLink.textContent = website;
      websiteLink.href = website.startsWith('http') ? website : 'https://' + website;
      websiteLink.style.display = 'block';
    } else {
      websiteLink.style.display = 'none';
    }
    document.getElementById('postDetailModal').classList.remove('hidden');
  }
  function closePostDetail() {
    document.getElementById('postDetailModal').classList.add('hidden');
  }
  function toggleExpand(btn) {
    const card = btn.closest('.donation-card');
    const para = card.querySelector('.expanded-para');
    const buttons = card.querySelector('.expanded-buttons');
    if (para && buttons) {
      para.classList.toggle('hidden');
      buttons.classList.toggle('hidden');
      btn.textContent = para.classList.contains('hidden') ? 'Read More' : 'Read Less';
    }
  }


//show donate history in tabla
document.addEventListener("DOMContentLoaded", () => {
  let debounceTimeout;
  let currentPage = 1;
  let totalPages = 1;

  const searchInput = document.getElementById("donation_search");
  const paginationWrapper = document.getElementById("paginationWrapper");

  function renderPagination(current, total) {
    let html = "";

    // Prev button
    html += `<button onclick="changePage(${current - 1})" class="px-3 py-1 border rounded" ${current === 1 ? "disabled" : ""}>Prev</button>`;

    for (let i = 1; i <= total; i++) {
      html += `<button onclick="changePage(${i})" class="px-3 py-1 border rounded ${i === current ? "bg-dark-blue text-white font-bold" : ""}">${i}</button>`;
    }

    // Next button
    html += `<button onclick="changePage(${current + 1})" class="px-3 py-1 border rounded" ${current === total ? "disabled" : ""}>Next</button>`;

    paginationWrapper.innerHTML = html;
  }

  function fetchDonations(page = 1) {
    const donation_query = searchInput?.value || "";

    fetch(`donation-history-ajax/?donation_query=${encodeURIComponent(donation_query)}&page=${page}`)
      .then(response => response.json())
      .then(data => {
        document.querySelector(".donate-history").innerHTML = data.html;
        currentPage = data.current_page;
        totalPages = data.total_pages;
        renderPagination(currentPage, totalPages);
      });
  }

  window.changePage = function (page) {
    if (page < 1 || page > totalPages) return;
    fetchDonations(page);
  };

  if (searchInput) {
    searchInput.addEventListener("keyup", function () {
      clearTimeout(debounceTimeout);
      debounceTimeout = setTimeout(() => {
        fetchDonations(1); // reset to first page on search
      }, 500);
    });
  }

  // Initial load
  fetchDonations(1);
});

// 50, 100, 200 filters 
function fetchDonations(page = 1) {
  const query = document.querySelector('input[name="donation_query"]').value;
  const limit = document.getElementById('limitSelect').value;

  fetch(`/donate/donation-history-ajax/?donation_query=${query}&page=${page}&limit=${limit}`)
    .then(response => response.json())
    .then(data => {
      document.querySelector('.donate-history').innerHTML = data.html;
      document.querySelector('.pagination-container').innerHTML = data.pagination;
    });
}

document.getElementById('limitSelect').addEventListener('change', () => {
  fetchDonations(1);
});

//export csv
document.addEventListener("DOMContentLoaded", function () {
  const exportBtn = document.getElementById("exportCSVBtn");
  exportBtn.addEventListener("click", function () {
    window.location.href = exportBtn.getAttribute("data-url");
  });
});

//dwnld bills
// function downloadBill() {
//     const downloadBtn = document.getElementById("downloadBillBtn");

//     if (!downloadBtn) {
//       console.error("Download button not found.");
//       return;
//     }

//     const imageUrl = downloadBtn.getAttribute("data-url");
//     const fileName = "platform_bill.svg";

//     fetch(imageUrl)
//       .then(response => {
//         if (!response.ok) {
//           throw new Error("Network response was not ok");
//         }
//         return response.blob();
//       })
//       .then(blob => {
//         const url = window.URL.createObjectURL(blob);
//         const a = document.createElement("a");
//         a.href = url;
//         a.download = fileName;
//         document.body.appendChild(a);
//         a.click();
//         a.remove();
//         window.URL.revokeObjectURL(url);
//       })
//       .catch(error => {
//         console.error("Download failed:", error);
//         alert("Download failed. Please try again.");
//       });
//   }

//img downloadDonationBill
// function downloadDonationBill() {
//     const downloadBtn = document.getElementById("downloadDonationBillBtn");

//     if (!downloadBtn) {
//       console.error("Download button not found.");
//       return;
//     }

//     const imageUrl = downloadBtn.getAttribute("data-url");
//     const fileName = "donation_bill.svg";

//     fetch(imageUrl)
//       .then(response => {
//         if (!response.ok) {
//           throw new Error("Network response was not ok");
//         }
//         return response.blob();
//       })
//       .then(blob => {
//         const url = window.URL.createObjectURL(blob);
//         const a = document.createElement("a");
//         a.href = url;
//         a.download = fileName;
//         document.body.appendChild(a);
//         a.click();
//         a.remove();
//         window.URL.revokeObjectURL(url);
//       })
//       .catch(error => {
//         console.error("Download failed:", error);
//         alert("Download failed. Please try again.");
//       });
// }

//open donate popup
function openDonatePopup(donationId) {
  fetch(`/donate/get-donate-bill/${donationId}/`)
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

    fetch(`/donate/get-platform-bill/${donationId}/`)
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

$(document).on('click', '.donate-bookmark-toggle', function() {
        console.log('Bookmark clicked!');
        var $icon = $(this);
        var donationId = $icon.data('donation-id');
        var isSaved = $icon.data('saved') === true || $icon.data('saved') === 'true';
        var action = isSaved ? 'unsave' : 'save';
    
        $.ajax({
            url: '/donate/toggle-saved/',
            type: 'POST',
            data: {
                donation_id: donationId,
                action: action,
                csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                if (response.success) {
                    $icon.data('saved', response.saved);
                    if (response.saved) {
                        $icon.addClass('material-filled text-living-coral');
                    } else {
                        $icon.removeClass('material-filled text-living-coral');
                        // If in Saved Donation table, remove the row
                        if ($icon.closest('.saved-donation').length || $icon.closest('table').closest('.saved-donation').length) {
                            $icon.closest('tr').remove();
                        }
                    }
                    window.showToaster('success', response.saved ? 'Donation saved!' : 'Donation unsaved!');
                } else {
                    window.showToaster('error', response.error || 'Could not update saved status.');
                }
            },
            error: function() {
                window.showToaster('error', 'Could not update saved status.');
            }
        });
    });