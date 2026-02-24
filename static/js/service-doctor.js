/* =========================================================
   CSRF
========================================================= */
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie) {
    document.cookie.split(';').forEach(cookie => {
      cookie = cookie.trim();
      if (cookie.startsWith(name + '=')) {
        cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
      }
    });
  }
  return cookieValue;
}

/* =========================================================
   DROPDOWN UTILS
========================================================= */
function populateDropdown(dropdown, items) {
  const menu = dropdown.find('.dropdown-menu');
  menu.empty();

  items.forEach(item => {
    menu.append(`
      <li class="dropdown-item px-3 py-2 hover:bg-premium-light-blue cursor-pointer"
          data-id="${item.id}">
        ${item.name}
      </li>
    `);
  });
}

/* =========================================================
   CARD INITIALIZERS
========================================================= */
function initDoctorServiceCard(card) {
  const categoryDropdown = card.find('.custom-dropdown').eq(0);
  const serviceDropdown  = card.find('.custom-dropdown').eq(1);

  populateDropdown(categoryDropdown, window.DOCTOR_DATA.categories);
  populateDropdown(serviceDropdown, window.DOCTOR_DATA.services);

  categoryDropdown.find('.selected-text')
    .text('Select Category')
    .removeAttr('data-id');

  serviceDropdown.find('.selected-text')
    .text('Select Service')
    .removeAttr('data-id');
}

function initDoctorVisitCard(card) {
  const dropdown = card.find('.custom-dropdown');

  populateDropdown(dropdown, window.DOCTOR_DATA.visit_types);

  dropdown.find('.selected-text')
    .text('Select Visit Type')
    .removeAttr('data-id');
}

/* =========================================================
   PAGE LOAD
========================================================= */
$(document).ready(function () {
  $('.services-list .service-card').each(function () {
    initDoctorServiceCard($(this));
  });

  $('.visit-services-list .service-card').each(function () {
    initDoctorVisitCard($(this));
  });
});

/* =========================================================
   ADD / REMOVE CARDS
========================================================= */
$(document).on('click', '.add-service', function () {
  const card = $(serviceCardTemplate());
  $('.services-list').append(card);
  initDoctorServiceCard(card);
});

$(document).on('click', '.add-service-visit', function () {
  const card = $(visitServiceCardTemplate());
  $('.visit-services-list').append(card);
  initDoctorVisitCard(card);
});

$(document).on('click', '.remove-service, .remove-service-visit', function () {
  $(this).closest('.service-card').remove();
});

/* =========================================================
   CATEGORY → SERVICE FILTER
========================================================= */
$(document).on('mousedown', '.dropdown-item', function (e) {
  e.preventDefault();
  e.stopPropagation();

  const item = $(this);
  const dropdown = item.closest('.custom-dropdown');
  const card = item.closest('.service-card');

  const selectedId = item.data('id');
  const selectedText = item.text().trim();

  // set selected value
  dropdown.find('.selected-text')
    .text(selectedText)
    .attr('data-id', selectedId);

  dropdown.find('.dropdown-menu').addClass('hidden');

  // 🔥 IF CATEGORY DROPDOWN → FILTER SERVICES
  if (dropdown.is(card.find('.custom-dropdown').eq(0))) {

    const filteredServices = window.DOCTOR_DATA.services.filter(
      s => String(s.category_id) === String(selectedId)
    );

    const serviceDropdown = card.find('.custom-dropdown').eq(1);

    populateDropdown(serviceDropdown, filteredServices);

    serviceDropdown.find('.selected-text')
      .text('Select Service')
      .removeAttr('data-id');
  }
});


/* =========================================================
   FILE UPLOAD UI
========================================================= */
$(document).on('click', '.upload-btn, .upload-box', function (e) {
  e.stopPropagation();
  $(this).closest('.file-upload-wrapper')
         .find('.file-input')
         .trigger('click');
});

$(document).on('change', '.file-input', function () {
  const wrapper = $(this).closest('.file-upload-wrapper');
  const file = this.files[0];
  if (!file) return;

  wrapper.find('.file-name').text(file.name);
  wrapper.find('.remove-file').removeClass('hidden');

  wrapper.find('.submit-btn')
    .prop('disabled', false)
    .removeClass('bg-light-gray cursor-not-allowed')
    .addClass('bg-primary-blue text-white');
});

$(document).on('click', '.remove-file', function (e) {
  e.stopPropagation();
  const wrapper = $(this).closest('.file-upload-wrapper');

  wrapper.find('.file-input').val('');
  wrapper.find('.file-name').text('Upload CSV File');
  $(this).addClass('hidden');

  wrapper.find('.submit-btn')
    .prop('disabled', true)
    .removeClass('bg-primary-blue text-white')
    .addClass('bg-light-gray cursor-not-allowed');
});

/* =========================================================
   COLLECT DATA
========================================================= */
function collectDoctorServices() {
  const services = [];

  $('.services-list .service-card').each(function () {
    const card = $(this);

    const categoryId = card.find('.custom-dropdown').eq(0)
                           .find('.selected-text').data('id');
    const serviceId  = card.find('.custom-dropdown').eq(1)
                           .find('.selected-text').data('id');

    let price = card.find('input').val() || "0";
    price = price.replace(/[₹,]/g, '').trim();

    if (!categoryId || !serviceId) return;

    services.push({
      category_id: categoryId,
      service_id: serviceId,
      price: price || "0"
    });
  });

  return services;
}

function collectVisitCharges() {
  const visits = [];

  $('.visit-services-list .service-card').each(function () {
    const card = $(this);

    const visitTypeId = card.find('.selected-text').data('id');
    let price = card.find('input').val() || "0";
    price = price.replace(/[₹,]/g, '').trim();

    if (!visitTypeId) return;

    visits.push({
      visit_type_id: visitTypeId,
      price: price || "0"
    });
  });

  return visits;
}

/* =========================================================
   STEP 2 → STEP 3 (SUMMARY)
========================================================= */
$(document).on('click', '#step-2 .step-btn[data-target="3"]', function () {
  const services = collectDoctorServices();
  const visits   = collectVisitCharges();

  if (!services.length) {
    toastr.error("Please add at least one service");
    return;
  }

  renderDoctorSummary(services, visits);

  $('#step-1, #step-2').addClass('hidden');
  $('#step-3').removeClass('hidden');
});

/* =========================================================
   SUMMARY RENDER
========================================================= */
function renderDoctorSummary(services, visits) {
  const serviceBox = $('.summary-services').empty();
  const visitBox   = $('.summary-visits').empty();

  services.forEach(s => {
    serviceBox.append(`
      <div class="service-card bg-white border rounded-md p-4">
        <h3 class="font-semibold">${s.service_id}</h3>
        <span class="font-bold text-blue-600">₹${s.price}</span>
      </div>
    `);
  });

  visits.forEach(v => {
    visitBox.append(`
      <div class="service-card bg-white border rounded-md p-4">
        <h3 class="font-semibold">${v.visit_type_id}</h3>
        <span class="font-bold text-blue-600">₹${v.price}</span>
      </div>
    `);
  });
}

/* =========================================================
   SAVE (SINGLE SUBMIT)
========================================================= */
$(document).on('click', '#step-3 .step-btn[data-target="3"]', function () {
  const services = collectDoctorServices();
  const visits   = collectVisitCharges();

  if (!services.length) {
    toastr.error("Please add at least one service");
    return;
  }

  $.ajax({
    url: "/services/add-doctor-services/",
    method: "POST",
    headers: { "X-CSRFToken": getCookie("csrftoken") },
    contentType: "application/json",
    data: JSON.stringify({ services, visits }),
    success(res) {
      if (res.success) {
        toastr.success("Doctor services saved successfully");
        window.location.href = "/services/";
      } else {
        toastr.error("Failed to save services");
      }
    },
    error() {
      toastr.error("Something went wrong");
    }
  });
});

