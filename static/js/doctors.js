$(document).ready(function () {
  // Define all doctors data
  const allDoctors = [
    {
      name: "Dr. Coolen Smith",
      phone: "+91 7568412234",
      specialty: "Neurologist",
      rating: "4.2",
      image: "/static/images/coolen-Smith.jpg",
    },
    {
      name: "Dr. Sarah Johnson",
      phone: "+91 7568412235",
      specialty: "Cardiologist",
      rating: "4.5",
      image: "/static/images/doctor-2.jpg",
    },
    {
      name: "Dr. Michael Chen",
      phone: "+91 7568412236",
      specialty: "Pediatrician",
      rating: "4.3",
      image: "/static/images/doctor-3.jpg",
    },
    {
      name: "Dr. Emily Brown",
      phone: "+91 7568412237",
      specialty: "Dermatologist",
      rating: "4.4",
      image: "/static/images/doctor-4.jpg",
    },
    {
      name: "Dr. James Wilson",
      phone: "+91 7568412238",
      specialty: "Orthopedic",
      rating: "4.1",
      image: "/static/images/doctor-5.jpg",
    },
    {
      name: "Dr. Lisa Anderson",
      phone: "+91 7568412239",
      specialty: "ENT Specialist",
      rating: "4.6",
      image: "/static/images/doctor-6.jpg",
    },
    {
      name: "Dr. Robert Taylor",
      phone: "+91 7568412240",
      specialty: "Gastroenterologist",
      rating: "4.2",
      image: "/static/images/doctor-2.jpg",
    },
    {
      name: "Dr. Maria Garcia",
      phone: "+91 7568412241",
      specialty: "Psychiatrist",
      rating: "4.7",
      image: "/static/images/doctor-7.jpg",
    },
    // Page 2
    {
      name: "Dr. David Martinez",
      phone: "+91 7568412242",
      specialty: "Ophthalmologist",
      rating: "4.3",
      image: "/static/images/doctor-8.jpg",
    },
    {
      name: "Dr. Jennifer Lee",
      phone: "+91 7568412243",
      specialty: "Neurologist",
      rating: "4.4",
      image: "/static/images/coolen-Smith.jpg",
    },
    {
      name: "Dr. William Harris",
      phone: "+91 7568412244",
      specialty: "Cardiologist",
      rating: "4.5",
      image: "/static/images/doctor-2.jpg",
    },
    {
      name: "Dr. Amanda White",
      phone: "+91 7568412245",
      specialty: "Pediatrician",
      rating: "4.2",
      image: "/static/images/doctor-3.jpg",
    },
    {
      name: "Dr. Christopher Moore",
      phone: "+91 7568412246",
      specialty: "Dermatologist",
      rating: "4.6",
      image: "/static/images/doctor-4.jpg",
    },
    {
      name: "Dr. Patricia Clark",
      phone: "+91 7568412247",
      specialty: "Orthopedic",
      rating: "4.3",
      image: "/static/images/doctor-5.jpg",
    },
    {
      name: "Dr. Daniel Lewis",
      phone: "+91 7568412248",
      specialty: "ENT Specialist",
      rating: "4.4",
      image: "/static/images/doctor-6.jpg",
    },
    {
      name: "Dr. Nancy Walker",
      phone: "+91 7568412249",
      specialty: "Gastroenterologist",
      rating: "4.5",
      image: "/static/images/doctor-2.jpg",
    },
    // Page 3
    {
      name: "Dr. Kevin Hall",
      phone: "+91 7568412250",
      specialty: "Psychiatrist",
      rating: "4.2",
      image: "/static/images/doctor-7.jpg",
    },
    {
      name: "Dr. Betty Allen",
      phone: "+91 7568412251",
      specialty: "Ophthalmologist",
      rating: "4.7",
      image: "/static/images/doctor-8.jpg",
    },
    {
      name: "Dr. George Young",
      phone: "+91 7568412252",
      specialty: "Neurologist",
      rating: "4.3",
      image: "/static/images/coolen-Smith.jpg",
    },
    {
      name: "Dr. Helen King",
      phone: "+91 7568412253",
      specialty: "Cardiologist",
      rating: "4.4",
      image: "/static/images/doctor-2.jpg",
    },
    {
      name: "Dr. Steven Wright",
      phone: "+91 7568412254",
      specialty: "Pediatrician",
      rating: "4.5",
      image: "/static/images/doctor-3.jpg",
    },
    {
      name: "Dr. Sandra Scott",
      phone: "+91 7568412255",
      specialty: "Dermatologist",
      rating: "4.6",
      image: "/static/images/doctor-4.jpg",
    },
    {
      name: "Dr. Brian Green",
      phone: "+91 7568412256",
      specialty: "Orthopedic",
      rating: "4.2",
      image: "/static/images/doctor-5.jpg",
    },
    {
      name: "Dr. Carol Adams",
      phone: "+91 7568412257",
      specialty: "ENT Specialist",
      rating: "4.3",
      image: "/static/images/doctor-6.jpg",
    },
  ];

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

  // Pagination functionality
  let currentPage = 1;
  const totalPages = 3;
  const itemsPerPage = 8;

  function renderDoctors(page) {
    const startIndex = (page - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const doctorsToShow = allDoctors.slice(startIndex, endIndex);

    const doctorCards = doctorsToShow
      .map(
        (doctor) => `
          <div class="border border-cool-slate-gray rounded-lg py-4 shadow-appointments relative flex flex-col items-center gap-4 cursor-pointer doctorCard">
            <img src="${doctor.image}" alt="Doctor Image" class="w-[104px] h-[104px] rounded-full object-cover shadow-doctor">
            <div class="flex flex-col">
              <span class="font-semibold text-sm">${doctor.name}</span>
              <span class="font-normal text-sm text-spanish-gray">${doctor.phone}</span>
            </div>
            <span class="font-semibold text-sm text-dodger-blue">${doctor.specialty}</span>
            
            <div class="bg-soft-peach-cream rounded-tr-full rounded-br-full absolute left-0 top-8 flex items-center gap-1.5 justify-center p-2.5">
              <span class="material-symbols-outlined material-filled text-warm-apricot-orange">star</span>
              <span class="text-warm-apricot-orange font-semibold text-sm">${doctor.rating}</span>
            </div>
          </div>
        `
      )
      .join("");

    $("#doctorGrid").html(doctorCards);
  }

  function renderPagination() {
    let pageButtons = "";
    for (let i = 1; i <= totalPages; i++) {
      const activeClass =
        i === currentPage ? "bg-dodger-blue text-white " : "bg-gray-200 ";
      pageButtons += `<button class="w-8 h-8 cursor-pointer rounded-lg font-medium transition-all ${activeClass} page-btn" data-page="${i}">${i}</button>`;
    }
    $("#pageNumbers").html(pageButtons);

    // Update Previous/Next button states
    $("#prevBtn").prop("disabled", currentPage === 1);
    $("#nextBtn").prop("disabled", currentPage === totalPages);
  }

  function goToPage(page) {
    if (page >= 1 && page <= totalPages) {
      currentPage = page;
      renderDoctors(currentPage);
      renderPagination();
      $("html, body").animate({ scrollTop: 0 }, 300);
    }
  }

  // Event handlers
  $("#prevBtn").on("click", function () {
    goToPage(currentPage - 1);
  });

  $("#nextBtn").on("click", function () {
    goToPage(currentPage + 1);
  });

  $(document).on("click", ".page-btn", function () {
    const page = parseInt($(this).data("page"));
    goToPage(page);
  });

  // Initial render
  renderDoctors(currentPage);
  renderPagination();

  $(".popup-btn").on("click", function () {
    let popupId = $(this).data("popup");
    $("." + popupId)
      .removeClass("hidden")
      .addClass("flex");
  });

  // Close popup
  $(".close-popup").on("click", function () {
    let popupId = $(this).data("popup");
    $(this)
      .closest("." + popupId)
      .addClass("hidden")
      .removeClass("flex");
  });

  $(".doctorCard").on("click", function () {
    $(".docInfoPopup").removeClass("hidden");
  });

  $(".closeInfoPopup").on("click", function () {
    $(".docInfoPopup").addClass("hidden");
  });

  $(".historyBtn").on("click", function () {
    $(".docInfoPopup").addClass("hidden");
    $(".attendancePopup").removeClass("hidden");
  });

  $(".closeAttendance").on("click", function () {
    $(".docInfoPopup").removeClass("hidden");
    $(".attendancePopup").addClass("hidden");
  });

  // Toggle dropdown
  $(".status-btn").on("click", function (e) {
    e.stopPropagation();
    const dropdown = $(this).siblings(".status-dropdown");
    const arrow = $(this).find(".material-symbols-outlined");

    dropdown.toggleClass("hidden");

    // Rotate arrow
    if (dropdown.hasClass("hidden")) {
      arrow.css("transform", "rotate(0deg)");
    } else {
      arrow.css("transform", "rotate(180deg)");
    }
  });

  // Handle dropdown item selection
  $(".dropdown-item").on("click", function () {
    const selectedText = $(this).text().trim();
    const button = $(this).closest(".relative").find(".status-btn");
    const statusText = button.find(".status-text");
    const arrow = button.find(".material-symbols-outlined");
    const dropdown = $(this).closest(".status-dropdown");

    // Update button text
    statusText.text(selectedText);

    // Apply styles based on selection using inline styles
    if (selectedText === "Present") {
      button.css({
        "background-color": "#EEF6FF",
        color: "#007BFF",
      });
      arrow.css("color", "#007BFF");
    } else if (selectedText === "Absent") {
      button.css({
        "background-color": "#FBE7E8",
        color: "#B00020",
      });
      arrow.css("color", "#B00020");
    }

    // Hide dropdown and reset arrow
    dropdown.addClass("hidden");
    arrow.css("transform", "rotate(0deg)");
  });

  // Close dropdown when clicking outside
  $(document).on("click", function (e) {
    if (!$(e.target).closest(".relative").length) {
      $(".status-dropdown").addClass("hidden");
      $(".material-symbols-outlined").css("transform", "rotate(0deg)");
    }
  });
    $('.material-symbols-outlined').css('transition', 'transform 0.3s ease');
});
