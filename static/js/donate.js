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
function downloadBill() {
    const downloadBtn = document.getElementById("downloadBillBtn");

    if (!downloadBtn) {
      console.error("Download button not found.");
      return;
    }

    const imageUrl = downloadBtn.getAttribute("data-url");
    const fileName = "platform_bill.svg";

    fetch(imageUrl)
      .then(response => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.blob();
      })
      .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      })
      .catch(error => {
        console.error("Download failed:", error);
        alert("Download failed. Please try again.");
      });
  }

//downloadDonationBill
function downloadDonationBill() {
    const downloadBtn = document.getElementById("downloadDonationBillBtn");

    if (!downloadBtn) {
      console.error("Download button not found.");
      return;
    }

    const imageUrl = downloadBtn.getAttribute("data-url");
    const fileName = "donation_bill.svg";

    fetch(imageUrl)
      .then(response => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.blob();
      })
      .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      })
      .catch(error => {
        console.error("Download failed:", error);
        alert("Download failed. Please try again.");
      });
  }

