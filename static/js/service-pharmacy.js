let PHARMACY_DATA = {
    categories: [],
    medicines: [],
    types: []
};

function loadPharmacyData() {
    return fetch("/services/pharmacy/dropdowns/")
        .then(res => res.json())
        .then(data => {
            PHARMACY_DATA = data;
        });
}

$(document).ready(function () {
    loadPharmacyData();
});

/* -------- SERVICE CARD HANDLER -------- */
const serviceCardTemplate = () => `
<div class="service-card rounded-lg px-4 py-6 relative bg-[#F9FAFB]">
      <button class="remove-service absolute top-3 right-3 text-ebony hover:text-red-500">✕</button>

      <!-- Category Dropdown -->
    <div class="mb-4 custom-dropdown">
        <label class="text-base sm:text-lg text-jet-black font-semibold">Select Category</label>

        <div class="dropdown-trigger mt-2">
            <button type="button" class="w-full border border-slate-gray rounded-md px-3 py-3 text-left flex justify-between items-center">
                <span class="selected-text text-sm sm:text-base font-normal text-dark-gray">Surgery</span>
                <span class="material-symbols-outlined">
                    keyboard_arrow_down
                </span>
            </button>

            <ul class="dropdown-menu hidden absolute z-20 mt-1 w-1/2 bg-white border border-primary-blue rounded shadow text-sm sm:text-base text-dark-gray font-normal h-40 overflow-y-auto scroll">

            </ul>
        </div>
    </div>

    <!-- Medicine name Dropdown -->
    <div class="mb-4 custom-dropdown">
        <label class="text-base sm:text-lg text-jet-black font-semibold">Select Medicine Name</label>

        <div class="dropdown-trigger mt-2">
            <button type="button" class="w-full border border-slate-gray rounded-md px-3 py-3 text-left flex justify-between items-center">
                <span class="selected-text text-sm sm:text-base font-normal text-dark-gray">Surgery</span>
                <span class="material-symbols-outlined">
                    keyboard_arrow_down
                </span>
            </button>

            <ul class="dropdown-menu hidden absolute z-20 mt-1 w-1/2 bg-white border border-primary-blue rounded shadow text-sm sm:text-base text-dark-gray font-normal h-40 overflow-y-auto scroll">

            </ul>
        </div>
    </div>

    <!-- Medicine type Dropdown -->
    <div class="mb-4 custom-dropdown">
        <label class="text-base sm:text-lg text-jet-black font-semibold">Select Medicine Type</label>

        <div class="dropdown-trigger mt-2">
            <button type="button" class="w-full border border-slate-gray rounded-md px-3 py-3 text-left flex justify-between items-center">
                <span class="selected-text text-sm sm:text-base font-normal text-dark-gray">Surgery</span>
                <span class="material-symbols-outlined">
                    keyboard_arrow_down
                </span>
            </button>

            <ul class="dropdown-menu hidden absolute z-20 mt-1 w-1/2 bg-white border border-primary-blue rounded shadow text-sm sm:text-base text-dark-gray font-normal h-40 overflow-y-auto scroll">
    
            </ul>
        </div>
    </div>

    <div class="grid grid-col-1 sm:grid-cols-2 gap-4">

        <!-- Quantity -->
        <div>
            <label class="text-base sm:text-lg text-jet-black font-semibold">Quantity</label>
            <input type="text"
                class="w-full border border-slate-gray rounded-md px-3 py-3 mt-2 focus:outline-none"
                value="10 tablets">
        </div>

        <!-- Price -->
        <div>
            <label class="text-base sm:text-lg text-jet-black font-semibold">Price</label>
            <input type="text"
                class="w-full border border-slate-gray rounded-md px-3 py-3 mt-2 focus:outline-none"
                value="₹ 0.00">
        </div>
    </div>
  </div>
`;

$(document).on('click', '.add-service', function () {
    const stepContent = $(this).closest('.step-content');
    stepContent.find('.services-list').append(serviceCardTemplate());
});

$(document).on('click', '.remove-service', function () {
    $(this).closest('.service-card').remove();
});


/* ---------------- OPEN FILE MANAGER ---------------- */
$(document).on('click', '.upload-btn, .upload-box', function (e) {
    e.stopPropagation();
    $(this).closest('.file-upload-wrapper').find('.file-input').trigger('click');
});

$(document).on('change', '.file-input', function () {
    const wrapper = $(this).closest('.file-upload-wrapper');
    const file = this.files[0];

    if (!file) return;

    wrapper.find('.file-name').text(file.name);
    wrapper.find('.remove-file').removeClass('hidden');

    // Enable submit
    wrapper.find('.submit-btn')
        .prop('disabled', false)
        .removeClass('bg-light-gray cursor-not-allowed')
        .addClass('bg-primary-blue text-white');
});

$(document).on('click', '.remove-file', function (e) {
    e.stopPropagation();

    const wrapper = $(this).closest('.file-upload-wrapper');

    // Reset input
    wrapper.find('.file-input').val('');

    // Reset UI
    wrapper.find('.file-name').text('Upload CSV File');
    $(this).addClass('hidden');

    // Disable submit again
    wrapper.find('.submit-btn')
        .prop('disabled', true)
        .removeClass('bg-primary-blue text-white')
        .addClass('bg-light-gray cursor-not-allowed');
});

function fillDropdown(menu, items, key = null) {
    menu.empty();

    items.forEach(item => {
        const value = key ? item[key] : item;
        menu.append(`
            <li class="dropdown-item px-3 py-2 hover:bg-premium-light-blue cursor-pointer"
                data-value="${value}">
                ${value}
            </li>
        `);
    });
}

$(document).on("click", ".add-service", function () {
    const container = $(this).closest(".step-content").find(".services-list");
    const card = $(serviceCardTemplate());

    // Category dropdown
    fillDropdown(
        card.find(".category-menu"),
        PHARMACY_DATA.categories
    );

    // Medicine dropdown
    fillDropdown(
        card.find(".medicine-menu"),
        PHARMACY_DATA.medicines,
        "name"
    );

    // Type dropdown
    fillDropdown(
        card.find(".type-menu"),
        PHARMACY_DATA.types
    );

    container.append(card);
});

$(document).on("click", ".dropdown-item", function () {
    const value = $(this).data("value");
    const dropdown = $(this).closest(".custom-dropdown");

    dropdown.find(".selected-text").text(value);
    dropdown.find(".dropdown-menu").addClass("hidden");
});

$(document).on("click", ".dropdown-trigger button", function (e) {
    e.stopPropagation();
    $(".dropdown-menu").addClass("hidden");
    $(this).siblings(".dropdown-menu").toggleClass("hidden");
});

$(document).on("click", function () {
    $(".dropdown-menu").addClass("hidden");
});
