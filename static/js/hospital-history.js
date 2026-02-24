$(document).ready(function () {
  const itemsPerPage = 5;

  // Toggle disease dropdown
  $(document).on(
    "click",
    ".disease-input-container, .disease-input-container input, .disease-input-container span",
    function (e) {
      e.stopPropagation();
      $(".disease-dropdown").toggleClass("hidden");
    }
  );

  // Select disease from dropdown
  $(document).on("click", ".disease-option", function () {
    const selectedDisease = $(this).text().trim();
    $('.assignPopup input[placeholder="Select Disease"]').val(selectedDisease);
    $(".disease-dropdown").addClass("hidden");
  });

  // Close disease dropdown when clicking outside
  $(document).on("click", function (e) {
    if (
      !$(e.target).closest(".disease-input-container").length &&
      !$(e.target).closest(".disease-dropdown").length
    ) {
      $(".disease-dropdown").addClass("hidden");
    }
  });

  // Initialize pagination for each tab
  function initializePagination() {
    const tabs = ["accepted", "pending", "canceled", "missed", "equipment"];

    tabs.forEach((tab) => {
      const container = $(`.${tab} #cards-container`);
      const cards = container.children();
      const totalPages = Math.ceil(cards.length / itemsPerPage);

      // Hide all cards initially
      cards.hide();

      // Create pagination HTML
      const paginationHTML = `
        <div class="pagination-${tab} flex justify-center items-center gap-3 mt-6">
          <button class="prev-btn text-spanish-gray font-normal text-xs px-4 py-2 rounded-lg  transition cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed">Previous</button>
          <div class="page-numbers flex gap-2"></div>
          <button class="next-btn text-spanish-gray font-normal text-xs px-4 py-2 rounded-lg  transition cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed">Next</button>
        </div>
      `;

      // Append pagination after cards container
      if ($(`.pagination-${tab}`).length === 0) {
        container.after(paginationHTML);
      }

      // Show first page
      showPage(tab, 1, cards, totalPages);
    });
  }

  // Show specific page
  function showPage(tab, page, cards, totalPages) {
    const start = (page - 1) * itemsPerPage;
    const end = start + itemsPerPage;

    // Hide all cards and show only current page cards
    cards.hide();
    cards.slice(start, end).show();

    // Update pagination buttons
    updatePaginationButtons(tab, page, totalPages);
  }

  // Update pagination buttons
  function updatePaginationButtons(tab, currentPage, totalPages) {
    const paginationContainer = $(`.pagination-${tab}`);
    const pageNumbersContainer = paginationContainer.find(".page-numbers");
    const prevBtn = paginationContainer.find(".prev-btn");
    const nextBtn = paginationContainer.find(".next-btn");

    // Clear existing page numbers
    pageNumbersContainer.empty();

    // Generate page number buttons
    for (let i = 1; i <= totalPages; i++) {
      const isActive = i === currentPage;
      const pageBtn = $(`
        <button class="page-btn w-8 h-8 rounded-lg font-normal text-xs transition cursor-pointer ${
          isActive
            ? "bg-dodger-blue text-white"
            : "bg-light-gray text-dark-gray  "
        }" data-page="${i}">
          ${i}
        </button>
      `);
      pageNumbersContainer.append(pageBtn);
    }

    // Enable/disable prev and next buttons
    prevBtn.prop("disabled", currentPage === 1);
    nextBtn.prop("disabled", currentPage === totalPages);

    // Store current page
    paginationContainer.data("current-page", currentPage);
    paginationContainer.data("total-pages", totalPages);
  }

  // Handle pagination clicks
  $(document).on("click", ".prev-btn, .next-btn, .page-btn", function () {
    const button = $(this);
    const paginationContainer = button.closest('[class*="pagination-"]');
    const tab = paginationContainer.attr("class").match(/pagination-(\w+)/)[1];
    const container = $(`.${tab} #cards-container`);
    const cards = container.children();
    const totalPages = paginationContainer.data("total-pages");
    let currentPage = paginationContainer.data("current-page");

    if (button.hasClass("prev-btn")) {
      currentPage = Math.max(1, currentPage - 1);
    } else if (button.hasClass("next-btn")) {
      currentPage = Math.min(totalPages, currentPage + 1);
    } else if (button.hasClass("page-btn")) {
      currentPage = parseInt(button.data("page"));
    }

    showPage(tab, currentPage, cards, totalPages);
  });

  // Initialize on page load
  initializePagination();

  // Open modal when any card is clicked
  // All Accepted
  $(document).on("click", ".card-all-accepted", function () {
    $(".modal-all-accepted").removeClass("hidden");
  });

  // Close modal when close button is clicked
  $(".modal-close-all-accepted").on("click", function () {
    $(".modal-all-accepted").addClass("hidden");
  });

  // All Completed
  $(document).on("click", ".card-all-completed", function () {
    $(".modal-all-completed").removeClass("hidden");
  });

  // Close modal when close button is clicked
  $(".modal-close-all-completed").on("click", function () {
    $(".modal-all-completed").addClass("hidden");
  });

  // For "missed" modal
  $(document).on("click", ".card-missed", function () {
    $(".modal-missed").removeClass("hidden");
  });

  // Close "missed" modal
  $(".modal-close-missed").on("click", function () {
    $(".modal-missed").addClass("hidden");
  });

  // For "canceled" modal
  $(document).on("click", ".card-canceled", function () {
    $(".modal-canceled").removeClass("hidden");
  });

  // Close "canceled" modal
  $(".modal-close-canceled").on("click", function () {
    $(".modal-canceled").addClass("hidden");
  });

  // For "pending" modal
  $(document).on("click", ".card-pending", function () {
    $(".modal-pending").removeClass("hidden");
  });

  // Close "pending" modal
  $(".modal-close-pending").on("click", function () {
    $(".modal-pending").addClass("hidden");
  });

  // Image Attachment Preview (for all)
  $(document).on("click", ".view-attachment", function () {
    $(".attachment-modal").removeClass("hidden");
  });

  // Close attachment modal
  $(".close-attachment-modal").on("click", function () {
    $(".attachment-modal").addClass("hidden");
  });

  // Close modal if background clicked
  $(".attachment-modal").on("click", function (e) {
    if ($(e.target).is(".attachment-modal")) {
      $(this).addClass("hidden");
    }
  });

  // Equipment - Handle all status buttons dynamically
  // Toggle dropdown visibility
  $(document).on("click", function (e) {
    const $clickedButton = $(e.target).closest(".status-btn");
    const $allDropdowns = $(".status-dropdown");

    // If clicked inside a status button
    if ($clickedButton.length) {
      const $dropdown = $clickedButton.next(".status-dropdown");
      // Close all other dropdowns
      $allDropdowns.not($dropdown).addClass("hidden");
      // Toggle current dropdown
      $dropdown.toggleClass("hidden");
      return;
    }

    // If clicked on a dropdown item
    if ($(e.target).hasClass("dropdown-item")) {
      const $parent = $(e.target).closest(".relative");
      $parent.find(".status-text").text($(e.target).text());
      $parent.find(".status-dropdown").addClass("hidden");
      return;
    }

    // If clicked outside dropdowns, close all
    $allDropdowns.addClass("hidden");
  });

  // Tab switching functionality
  $(".tab-btn-hospital").on("click", function () {
    const targetTab = $(this).data("tab");

    // Update active tab button
    $(".tab-btn-hospital")
      .removeClass("active-tab-hospital font-semibold")
      .addClass("font-medium");
    $(this)
      .addClass("active-tab-hospital font-semibold")
      .removeClass("font-medium");

    // Hide all tab contents
    $(".tab-content").addClass("hidden");

    // Show selected tab content
    $(`.${targetTab}`).removeClass("hidden");
  });

  // 1. Toggle Main Dropdown
  $(".filterToggle").on("click", function (e) {
    e.stopPropagation();
    const isHidden = $(".filterDropdown").hasClass("hidden");
    $(".filterDropdown, .submenu").addClass("hidden"); // Reset all
    if (isHidden) $(".filterDropdown").removeClass("hidden");
  });

  // 2. Open Date Submenu (Keep main open)
  $(".trigger-date").on("click", function (e) {
    e.stopPropagation();
    $(".submenu").not("#dateSubmenu").addClass("hidden"); // Close other submenus except date
    $("#calendarContainer").addClass("hidden"); // Close calendar if open
    $("#dateSubmenu").removeClass("hidden").css("top", $(this).position().top);
  });

  // Initialize the jQuery UI Datepicker inline
  $(".datepicker-inline").datepicker({
    onSelect: function (dateText) {
      console.log("Selected date: " + dateText);

      // Mark Custom option as selected
      $("#dateSubmenu .trigger-custom .material-symbols-outlined")
        .first()
        .removeClass("text-light-gray")
        .addClass("!text-dodger-blue");

      // Close everything after date selection
      $(".filterDropdown, .submenu").addClass("hidden");
      $("#calendarContainer").addClass("hidden");
    },
  });

  // 3. Open Calendar when clicking "Custom"
  $(".trigger-custom").on("click", function (e) {
    e.stopPropagation();

    // Position the calendar relative to the Custom menu item
    const topPos = $(this).position().top;

    // Show the calendar
    $("#calendarContainer").removeClass("hidden").css("top", topPos);
  });

  // 4. Status & Visit Submenus
  $(".trigger-status").on("click", function (e) {
    e.stopPropagation();
    $(".submenu").addClass("hidden");
    $("#calendarContainer").addClass("hidden"); // Close calendar if open
    $("#statusSubmenu")
      .removeClass("hidden")
      .css("top", $(this).position().top);
  });

  $(".trigger-visit").on("click", function (e) {
    e.stopPropagation();
    $(".submenu").addClass("hidden");
    $("#calendarContainer").addClass("hidden"); // Close calendar if open
    $("#visitSubmenu").removeClass("hidden").css("top", $(this).position().top);
  });

  // 5. Handle option selection in Date submenu (Week/Month only, not Custom)
  $("#dateSubmenu > div:not(.trigger-custom)").on("click", function (e) {
    e.stopPropagation();

    // Remove active state from all options in date submenu
    $("#dateSubmenu .material-symbols-outlined")
      .removeClass("!text-dodger-blue")
      .addClass("text-light-gray");

    // Add active state to clicked option
    $(this)
      .find(".material-symbols-outlined")
      .removeClass("text-light-gray")
      .addClass("!text-dodger-blue");

    // Close all dropdowns
    $(".filterDropdown, .submenu").addClass("hidden");
  });

  // 6. Handle option selection in Status and Visit submenus
  $("#statusSubmenu > div, #visitSubmenu > div").on("click", function (e) {
    e.stopPropagation();

    // Get the parent submenu
    const $submenu = $(this).closest(".submenu");

    // Remove active state from all options in this submenu
    $submenu
      .find(".material-symbols-outlined")
      .removeClass("!text-dodger-blue")
      .addClass("text-light-gray");

    // Add active state to clicked option
    $(this)
      .find(".material-symbols-outlined")
      .removeClass("text-light-gray")
      .addClass("!text-dodger-blue");

    // Close all dropdowns
    $(".filterDropdown, .submenu").addClass("hidden");
  });

  // 7. Global Close
  $(document).on("click", function () {
    $(".filterDropdown, .submenu").addClass("hidden");
    $("#calendarContainer").addClass("hidden");
  });

  // Prevent menu from closing when clicking inside
  $(".filterDropdown, .submenu, #calendarContainer").on("click", function (e) {
    e.stopPropagation();
  });

  // Variable to store the current assign button being clicked
  let currentAssignBtn = null;

  // Open assign popup and store reference to clicked button
  $(document).on("click", ".assign-btn", function () {
    currentAssignBtn = $(this);
    $(".assignPopup").removeClass("hidden");
  });

  // Close assign popup
  $(".closeAssignPopup").on("click", function () {
    $(".assignPopup").addClass("hidden");
    currentAssignBtn = null;
    // Clear input fields
    $('.assignPopup input[type="text"]').val("");
  });

  // Save button click handler
  $(".saveBtn").on("click", function () {
    // Get the entered patient name
    const patientName = $(
      '.assignPopup input[placeholder="Enter Patient Name"]'
    )
      .val()
      .trim();
    const selectedDisease = $(
      '.assignPopup input[placeholder="Select Disease"]'
    )
      .val()
      .trim();

    // Validate inputs
    if (!patientName) {
      // alert("Please enter patient name");
      return;
    }

    if (!selectedDisease) {
      // alert("Please select a disease");
      return;
    }

    // Update the assign button text with patient name
    if (currentAssignBtn) {
      currentAssignBtn.find(".status-text").text(patientName);

      // Update the card to show patient info instead of "Assign to" button
      const $card = currentAssignBtn.closest(".card-equipment");
      const $patientInfoDiv = $card.find(".flex.items-center.gap-3").first();

      // Replace the assign button container with patient info
      const $assignContainer = currentAssignBtn.closest(".relative");
      $assignContainer.replaceWith(`
            <div class="flex items-center gap-3">
                <div class="flex flex-col">
                    <p class="font-semibold text-sm text-jet-black">${patientName}</p>
                    <span class="text-xs text-spanish-gray">${selectedDisease}</span>
                </div>
            </div>
        `);
    }

    // Close popup and clear fields
    $(".assignPopup").addClass("hidden");
    $('.assignPopup input[type="text"]').val("");
    currentAssignBtn = null;
  });

  // Close popup when clicking outside
  $(".assignPopup").on("click", function (e) {
    if ($(e.target).is(".assignPopup")) {
      $(this).addClass("hidden");
      currentAssignBtn = null;
      $('.assignPopup input[type="text"]').val("");
    }
  });
});
