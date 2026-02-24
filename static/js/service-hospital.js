/* -------- SERVICE CARD HANDLER -------- */

const serviceCardTemplate = () => `
<div class="service-card rounded-lg px-4 py-6 relative bg-[#F9FAFB]">

    <button class="remove-service absolute top-3 right-3">✕</button>

    <!-- CATEGORY -->
    <div class="mb-4 custom-dropdown">
        <label class="font-semibold">Select Category</label>

        <div class="dropdown-trigger mt-2">
            <button type="button" class="dropdown-btn">
                <span class="selected-text">Select Category</span>
                <span class="material-symbols-outlined">keyboard_arrow_down</span>
            </button>

            <ul class="dropdown-menu category-options hidden absolute z-20 mt-1 w-1/2 bg-white shadow">
                ${renderCategoryOptions()}
            </ul>
        </div>
    </div>

    <!-- SERVICE -->
    <div class="custom-dropdown">
        <label class="font-semibold">Select Service</label>

        <div class="dropdown-trigger mt-2">
            <button type="button" class="dropdown-btn">
                <span class="selected-text">Select Service</span>
                <span class="material-symbols-outlined">keyboard_arrow_down</span>
            </button>

            <ul class="dropdown-menu service-options hidden absolute z-20 mt-1 w-1/2 bg-white shadow">
                <!-- services injected dynamically -->
            </ul>
        </div>
    </div>

    <!-- PRICE -->
    <input type="text" class="price-input mt-3" placeholder="₹ 0.00">
</div>
`;

/* ---------- ADD / REMOVE CARDS ---------- */

$(document).on("click", ".add-service", function () {
    $(".services-list").append(serviceCardTemplate());
});

$(document).on("click", ".remove-service", function () {
    $(this).closest(".service-card").remove();
});

/* ---------- CATEGORY CLICK ---------- */

$(document).on("click", ".category-options .dropdown-item", function () {
    const li = $(this);
    const card = li.closest(".service-card");

    // Set selected category text
    li.closest(".custom-dropdown")
        .find(".selected-text")
        .text(li.text());

    // Hide category dropdown
    li.closest(".dropdown-menu").addClass("hidden");

    const categoryId = li.data("id");

    // Load services for this category
    const servicesHTML = renderServiceOptions(categoryId);
    card.find(".service-options").html(servicesHTML);

    // Reset service selection
    card.find(".service-options")
        .closest(".custom-dropdown")
        .find(".selected-text")
        .text("Select Service");
});

/* ---------- SERVICE CLICK ---------- */

$(document).on("click", ".service-options .dropdown-item", function () {
    const li = $(this);

    li.closest(".custom-dropdown")
        .find(".selected-text")
        .text(li.text());

    li.closest(".dropdown-menu").addClass("hidden");
});

/* ---------- DROPDOWN TOGGLE ---------- */

$(document).on("click", ".dropdown-btn", function (e) {
    e.stopPropagation();
    $(".dropdown-menu").addClass("hidden");
    $(this).closest(".dropdown-trigger").find(".dropdown-menu").toggleClass("hidden");
});

$(document).on("click", function () {
    $(".dropdown-menu").addClass("hidden");
});

/* ---------- FILE UPLOAD ---------- */

$(document).on("click", ".upload-btn, .upload-box", function (e) {
    e.stopPropagation();
    $(this).closest(".file-upload-wrapper").find(".file-input").trigger("click");
});

$(document).on("change", ".file-input", function () {
    const wrapper = $(this).closest(".file-upload-wrapper");
    const file = this.files[0];
    if (!file) return;

    wrapper.find(".file-name").text(file.name);
    wrapper.find(".remove-file").removeClass("hidden");

    wrapper.find(".submit-btn")
        .prop("disabled", false)
        .removeClass("bg-light-gray cursor-not-allowed")
        .addClass("bg-primary-blue text-white");
});

$(document).on("click", ".remove-file", function (e) {
    e.stopPropagation();
    const wrapper = $(this).closest(".file-upload-wrapper");

    wrapper.find(".file-input").val("");
    wrapper.find(".file-name").text("Upload CSV File");
    $(this).addClass("hidden");

    wrapper.find(".submit-btn")
        .prop("disabled", true)
        .removeClass("bg-primary-blue text-white")
        .addClass("bg-light-gray cursor-not-allowed");
});

/* ---------- DATA RENDERERS ---------- */

function renderCategoryOptions() {
    return HOSPITAL_CATEGORIES.map(cat => `
        <li class="dropdown-item px-3 py-2 hover:bg-premium-light-blue cursor-pointer"
            data-id="${cat.id}">
            ${cat.name}
        </li>
    `).join("");
}

function renderServiceOptions(categoryId) {
    const services = HOSPITAL_SERVICES.filter(
        s => s.category_id == categoryId
    );

    if (!services.length) {
        return `<li class="px-3 py-2 text-gray-400">No services found</li>`;
    }

    return services.map(s => `
        <li class="dropdown-item px-3 py-2 hover:bg-premium-light-blue cursor-pointer"
            data-id="${s.id}">
            ${s.description}
        </li>
    `).join("");
}

/* ---------- BED ROOMS (if needed later) ---------- */

function renderBedRoomOptions() {
    return HOSPITAL_BED_ROOMS.map(b => `
        <li class="dropdown-item px-3 py-2 cursor-pointer"
            data-id="${b.id}">
            ${b.name}
        </li>
    `).join("");
}
