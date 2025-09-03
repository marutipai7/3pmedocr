// 1. Tab switching logic
$('.share-tabs-button-pharmacy').click(function () {
    const target = $(this).data('tab');

    // Show/hide tab content and style
    $('.tab-sub-content').addClass('hidden').removeClass('block');
    $('.' + target).removeClass('hidden').addClass('block');

    $('.share-tabs-button-pharmacy').removeClass('bg-light-sea-green text-dark-gray text-white shadow-md');
    $(this).addClass('bg-light-sea-green text-white text-dark-gray shadow-md');

    if (target === "upload-database") {
        $('.selection-inputs').addClass("hidden")
    } else {
        $('.selection-inputs').removeClass("hidden")
    }
});

// 2. Upload area click to trigger file input
$('.upload-area').on('click', function (e) {
    const previewVisible = $(this).find('.upload-preview').is(':visible');
    if (
        !previewVisible &&
        !$(e.target).is('input[type="file"]') &&
        !$(e.target).hasClass('cancel-upload')
    ) {
        $(this).find('input[type="file"]').trigger('click');
    }
});

// 3. Drag and drop handling
$('.upload-area').on('dragover', function (e) {
    e.preventDefault();
});

$('.upload-area').on('dragleave', function (e) {
    e.preventDefault();
});

$('.upload-area').on('drop', function (e) {
    e.preventDefault();
    const file = e.originalEvent.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
        const fileInput = $(this).find('input[type="file"]')[0];
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        fileInput.files = dataTransfer.files;
        $(fileInput).trigger('change');
    }
});

// 4. Change image
$('.upload-area').on('click', '.change-image-btn', function (e) {
    e.stopPropagation();
    const area = $(this).closest('.upload-area');
    area.find('input[type="file"]').trigger('click');
});

// 5. File input change handler
$('.upload-input').on('change', function () {
    const file = this.files[0];
    const area = $(this).closest('.upload-area');
    const preview = area.find('.upload-preview');
    const placeholder = area.find('.upload-placeholder');

    if (file && file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = function (e) {
            preview.find('.uploaded-img').attr('src', e.target.result);
            placeholder.addClass('hidden');
            preview.removeClass('hidden').addClass("flex");

            if (area.closest('.upload-database').length > 0) {
                $('.upload-database .get-btn').removeClass('hidden');
            } else if (area.closest('.prescription').length > 0) {
                $('.prescription .prescription-form-section').removeClass('hidden');
            } else if (area.closest('.bills').length > 0) {
                $('.bills .bill-form-section').removeClass('hidden');
            }
        };
        reader.readAsDataURL(file);
    }
});

// 6. Cancel upload
$('.upload-area').on('click', '.cancel-upload', function (e) {
    e.stopPropagation(); // Prevent triggering upload
    const area = $(this).closest('.upload-area');
    const input = area.find('input[type="file"]');
    const preview = area.find('.upload-preview');
    const placeholder = area.find('.upload-placeholder');

    // Reset
    input.val('');
    preview.addClass('hidden').removeClass("flex");
    placeholder.removeClass('hidden');

    if (area.closest('.upload-database').length > 0) {
        const medicineUploads = $('.upload-database .upload-input').filter(function () {
            return this.files.length > 0;
        }).length;
        if (medicineUploads === 0) {
            $('.upload-form-section').addClass('hidden').removeClass('block');
            $('.upload-database .get-btn').addClass('hidden').removeClass('bg-gray-300 text-gray-600 cursor-not-allowed');
        }
    } else if (area.closest('.prescription').length > 0) {
        $('.prescription .prescription-form-section').addClass('hidden');
    } else if (area.closest('.bills').length > 0) {
        $('.bills .bill-form-section').addClass('hidden');
    }
});

// Fetch button click to show form and disable itself (Medicine Section)
$('.upload-database .get-btn').on('click', function () {
    $('.upload-form-section').removeClass('hidden').addClass('block');
    $(this).addClass('bg-gray-300 text-gray-600 cursor-not-allowed');
});;

$('.upload-cancel').click(function () {
    $('.upload-form-section').addClass('hidden').removeClass('block');
    $('.upload-database .get-btn').removeClass('bg-gray-300 text-gray-600 cursor-not-allowed').addClass('bg-vivid-orange text-white');
});

// Upload File Modal Functionality
$(".file-share-btn").click(function () {
    $(".share-success-modal").removeClass("hidden").addClass("flex");;
});

$(".modal-close").click(function () {
    $(".share-success-modal").removeClass("flex").addClass("hidden");
});

$('.file-share-form, .prescription-share-form, .bill-share-form').submit(function (e) {
    e.preventDefault();
});


// Prescription

$('.prescription-share-cancel').click(function () {
    $('.prescription-form-section').addClass('hidden').removeClass('block');
});

// Bills

$('.bill-share-cancel').click(function () {
    $('.bill-form-section').addClass('hidden').removeClass('block');
});

$(".bill-share-btn").click(function () {
    $(".bill-success-modal").removeClass("hidden").addClass("flex");;
});

$(".bill-modal-close").click(function () {
    $(".bill-success-modal").removeClass("flex").addClass("hidden");
});

function toggleSharePoints() {
    if ($('.tab-btn-pharmacy[data-tab="share"]').hasClass('active-tab-pharmacy')) {
        $('.share-points').removeClass('hidden').addClass('block');
    } else {
        $('.share-points').removeClass('block').addClass('hidden');
    }
}

toggleSharePoints();

$('.tab-btn-pharmacy').on('click', function () {
    $('.tab-btn-pharmacy').removeClass('active-tab-pharmacy');
    $(this).addClass('active-tab-pharmacy');

    toggleSharePoints();
});

$(document).on('click', '.dropdown-input', function (e) {
    e.stopPropagation();
    const $input = $(this);
    const $wrapper = $input.closest('.dropdown-wrapper');
    const $dropdown = $wrapper.find('.dropdown-list');

    // Don't toggle dropdown if input is editable (i.e., Custom is selected)
    if (!$input.prop('readonly')) return;

    // Hide other dropdowns and show current one
    $('.dropdown-list').not($dropdown).hide();
    $dropdown.toggle();
});

// Select option
$(document).on('click', '.dropdown-list div', function (e) {
    e.stopPropagation();
    const $item = $(this);
    const selectedText = $item.text().trim();
    const $wrapper = $item.closest('.dropdown-wrapper');
    const $input = $wrapper.find('.dropdown-input');
    const $dropdown = $wrapper.find('.dropdown-list');

    if (selectedText.startsWith('Custom')) {
        $input.val('').prop('readonly', false).focus(); // Allow typing
    } else {
        $input.val(selectedText).prop('readonly', true); // Make readonly again
    }

    $dropdown.hide();
});

// Hide dropdown on outside click
$(document).on('click', function () {
    $('.dropdown-list').hide();
});

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

// Doctor Name Dropdown
const availableDoctors = [
    "Dr. John Doe",
    "Dr. Alice Smith",
    "Dr. Bob Brown",
    "Dr. Emma Davis",
];

let tags = [];
const maxTags = 1;
let isCustomTypingEnabled = false;

// Populate dropdown
function renderDoctorDropdown() {
    const dropdown = $('#doctor-dropdown');
    dropdown.empty();

    availableDoctors.forEach(doctor => {
        const item = $(`
        <div
          class="px-5 py-4 hover:bg-transparent-light-sea-green cursor-pointer text-dark-gray text-16-fs"
          data-doctor="${doctor}"
        >
          ${doctor}
        </div>
      `);
        dropdown.append(item);
    });

    // Add "Custom" option
    const customItem = $(`
      <div
        class="px-5 py-4 hover:bg-transparent-light-sea-green cursor-pointer text-dark-gray text-16-fs"
        data-custom="true"
      >
        Custom : _______
      </div>
    `);
    dropdown.append(customItem);
}

renderDoctorDropdown();

// Toggle dropdown
$('#doctor-input, #doctor-dropdown-toggle').on('click', function (e) {
    e.stopPropagation();
    $('#doctor-dropdown').toggle();
});

// Hide dropdown on outside click
$(document).on('click', function (e) {
    if (!$(e.target).closest('#doctor-dropdown').length) {
        $('#doctor-dropdown').hide();
    }
});

// Handle doctor selection or custom trigger
$('#doctor-dropdown').on('click', '[data-doctor], [data-custom]', function () {
    $('#doctor-dropdown').hide();

    if ($(this).data('custom')) {
        // Enable custom input
        $('#doctor-input')
            .prop('readonly', false)
            .focus()
            .attr('placeholder', 'Type doctor name');
        isCustomTypingEnabled = true;
    } else {
        const selectedDoctor = $(this).data('doctor');

        if (tags.length >= maxTags) {
            window.showToaster?.('error', 'Only 8 tags can be selected.');
        } else if (tags.includes(selectedDoctor)) {
            window.showToaster?.('error', 'Doctor already selected.');
        } else {
            tags.push(selectedDoctor);
            renderTags();
        }
    }
});

// Handle Enter for custom tag
$('#doctor-input').on('keypress', function (e) {
    if (e.which === 13 && isCustomTypingEnabled) {
        e.preventDefault();
        const customTag = $(this).val().trim();

        if (!customTag) return;

        if (tags.length >= maxTags) {
            window.showToaster?.('error', 'Only 8 tags can be selected.');
        } else if (tags.includes(customTag)) {
            window.showToaster?.('error', 'Tag already selected.');
        } else {
            tags.push(customTag);
            renderTags();
        }

        // Reset input
        $(this)
            .val('')
            .prop('readonly', true)
            .attr('placeholder', 'Click here or arrow to select');
        isCustomTypingEnabled = false;
    }
});

// Render tags
function renderTags() {
    $('#doctor-input-container').children('.doctor-chip').remove();

    tags.forEach((tag, index) => {
        const tagEl = $(`
        <div class="doctor-chip inline-flex items-center bg-white text-jet-black px-2 py-2 rounded-[16px] shadow-(--box-shadow-6) text-14-fs">
          ${tag}
          <button type="button" class="ml-2 text-dark-gray text-lg hover:text-red-600" data-index="${index}">&times;</button>
        </div>
      `);
        $('#doctor-input').before(tagEl);
    });
}

// Remove tag
$('#doctor-input-container').on('click', 'button', function () {
    const index = $(this).data('index');
    tags.splice(index, 1);
    renderTags();
});

// Patient Name Dropdown
const patientName = [
    "Krunal",
    "Arshiya",
    "Vighnesh",
    "Madhumita",
];

let chips = [];
const maxChips = 2;
let isCustomPatientTypingEnabled = false;

// Populate dropdown
function renderPatientDropdown() {
    const dropdown = $('#patient-dropdown');
    dropdown.empty();

    patientName.forEach(patient => {
        const isSelected = chips.includes(patient);

        const item = $(`
          <div
            class="flex items-center gap-3 px-5 py-4 hover:bg-transparent-light-sea-green cursor-pointer text-16-fs ${isSelected ? 'text-light-sea-green' : 'text-dark-gray'}"
            data-patient="${patient}"
          >
          ${isSelected ? '<span class="material-symbols-outlined">check</span>' : ''}
            <span>${patient}</span>
          </div>
        `);
        dropdown.append(item);
    });

    // Add "Custom" option
    const customItem = $(`
      <div
        class="px-5 py-4 hover:bg-transparent-light-sea-green cursor-pointer text-dark-gray text-16-fs"
        data-custom="true"
      >
        Custom : _______
      </div>
    `);
    dropdown.append(customItem);
}

renderPatientDropdown();

// Toggle dropdown
$('#patient-input, #patient-dropdown-toggle').on('click', function (e) {
    e.stopPropagation();
    $('#patient-dropdown').toggle();

    if ($('#patient-dropdown').is(':visible')) {
        $('#patient-input-container')
            .addClass('border border-light-sea-green bg-white').removeClass('border-none');
    } else {
        $('#patient-input-container')
            .removeClass('border border-light-sea-green bg-white').addClass('border-none');
    }
});

// Hide dropdown on outside click
$(document).on('click', function (e) {
    if (!$(e.target).closest('#patient-dropdown').length) {
        $('#patient-dropdown').hide();
        $('#patient-input-container')
            .removeClass('border border-light-sea-green bg-white').addClass('border-none');
    }
});

// Handle doctor selection or custom trigger
$('#patient-dropdown').on('click', '[data-patient], [data-custom]', function () {
    $('#patient-dropdown').hide();

    if ($(this).data('custom')) {
        // Enable custom input
        $('#patient-input')
            .prop('readonly', false)
            .focus()
            .attr('placeholder', 'Type patient name');
        isCustomPatientTypingEnabled = true;
    } else {
        const selectedPatient = $(this).data('patient');

        if (chips.includes(selectedPatient)) {
            // Toggle OFF
            chips = chips.filter(name => name !== selectedPatient);
        } else {
            if (chips.length >= maxChips) {
                window.showToaster?.('error', 'Only 3 Patients can be selected.');
                return;
            }
            chips.push(selectedPatient);
        }

        renderSelectedCount();
        renderPatientDropdown();
    }
});

// Handle Enter for custom tag
$('#patient-input').on('keypress', function (e) {
    if (e.which === 13 && isCustomPatientTypingEnabled) {
        e.preventDefault();
        const customTag = $(this).val().trim();

        if (!customTag) return;

        if (chips.includes(customTag)) {
            window.showToaster?.('error', 'Patient already selected.');
            return;
        }

        if (chips.length >= maxChips) {
            window.showToaster?.('error', 'Only 3 patients can be selected.');
            return;
        }

        // Add custom patient
        chips.push(customTag);
        renderSelectedCount();
        renderPatientDropdown();

        $(this).prop('readonly', true);
        isCustomPatientTypingEnabled = false;
    }
});


// Render Selection
function renderSelectedCount() {
    const count = chips.length;
    let text = "";

    if (count === 0) {
        text = "";
        $('#patient-input-container')
            .val(text)
            .css({
                'background-color': 'bg-light-grayish-orange',
            });
    } else if (count === 1) {
        text = "1 Patient Selected";
        $('#patient-input-container')
            .val(text)
            .css({
                'background-color': 'white',
            }).addClass('border-2 border-light-sea-green');
    } else {
        text = `${count} Patients Selected`;
        $('#patient-input-container')
            .val(text)
            .css({
                'background-color': 'white',
            });
    }

    $('#patient-input').val(text);
}

//Select File type

const availableFileType = [
    "Excel",
    "PDF",
    "CSV",
];

let types = [];
const maxTypes = 1;

// Populate dropdown
function renderFileTypeDropdown() {
    const dropdown = $('#file-dropdown');
    dropdown.empty();

    availableFileType.forEach(file => {
        const item = $(`
        <div
          class="px-5 py-4 hover:bg-transparent-light-sea-green cursor-pointer text-dark-gray text-16-fs"
          data-file="${file}"
        >
          ${file}
        </div>
      `);
        dropdown.append(item);
    });
}

renderFileTypeDropdown();

// Toggle dropdown
$('#file-input, #file-dropdown-toggle').on('click', function (e) {
    e.stopPropagation();
    $('#file-dropdown').toggle();
});

// Hide dropdown on outside click
$(document).on('click', function (e) {
    if (!$(e.target).closest('#file-dropdown').length) {
        $('#file-dropdown').hide();
    }
});

// Handle selection
$('#file-dropdown').on('click', '[data-file]', function () {
    $('#file-dropdown').hide();

    const selectedFile = $(this).data('file');

    if (types.length >= maxTypes) {
        window.showToaster?.('error', 'Only one File can be selected.');
    } else if (types.includes(selectedFile)) {
        window.showToaster?.('error', 'File already selected.');
    } else {
        types.push(selectedFile);
        renderFileTags();
    }
});

// Render tags
function renderFileTags() {
    $('#file-type-container').children('.file-chip').remove();

    types.forEach((tag, index) => {
        const tagEl = $(`
        <div class="file-chip inline-flex items-center bg-white text-jet-black px-2 py-2 rounded-[16px] shadow-(--box-shadow-6) text-14-fs">
          ${tag}
          <button type="button" class="ml-2 text-dark-gray text-lg hover:text-red-600" data-index="${index}">&times;</button>
        </div>
      `);
        $('#file-input').before(tagEl);
    });
}

// Remove tag
$('#file-type-container').on('click', 'button', function () {
    const index = $(this).data('index');
    types.splice(index, 1);
    renderFileTags();
});

const recordOptions = ["100", "10", "200"];
let selectedRecord = null;
let isCustomTyping = false;

function renderRecordsDropdown() {
    const dropdown = $('#records-dropdown');
    dropdown.empty();

    recordOptions.forEach(option => {
        const isSelected = selectedRecord === option;

        const item = $(`
            <div
                class="flex items-center gap-3 px-5 py-4 hover:bg-transparent-light-sea-green cursor-pointer text-16-fs ${isSelected ? 'text-light-sea-green' : 'text-dark-gray'}"
                data-record="${option}"
            >
                ${isSelected ? '<span class="material-symbols-outlined">check</span>' : ''}
                <span>${option}</span>
            </div>
        `);

        dropdown.append(item);
    });

    const isCustomSelected = selectedRecord && !recordOptions.includes(selectedRecord);
    const customItem = $(`
        <div
            class="flex items-center gap-3 px-5 py-4 hover:bg-transparent-light-sea-green cursor-pointer text-16-fs ${isCustomSelected ? 'text-light-sea-green' : 'text-dark-gray'}"
            data-custom="true"
        >
            ${isCustomSelected ? '<span class="material-symbols-outlined">check</span>' : ''}
            <span>Custom : _______</span>
        </div>
    `);
    dropdown.append(customItem);
}

// Initial render
renderRecordsDropdown();

// Open dropdown
$('#records-input, #records-dropdown-toggle').on('click', function (e) {
    e.stopPropagation();

    renderRecordsDropdown(); // <--- Always refresh right before showing
    $('#records-dropdown').toggle();

    if ($('#records-dropdown').is(':visible')) {
        $('#records-input-container')
            .addClass('border border-light-sea-green bg-white').removeClass('border-none');
    } else {
        $('#records-input-container')
            .removeClass('border border-light-sea-green bg-white').addClass('border-none');
    }
});

// Outside click closes dropdown
$(document).on('click', function (e) {
    if (!$(e.target).closest('#records-dropdown').length) {
        $('#records-dropdown').hide();
        $('#records-input-container')
            .removeClass('border border-light-sea-green bg-white').addClass('border-none');
    }
});

// Handle dropdown selection
$('#records-dropdown').on('click', '[data-record], [data-custom]', function () {
    $('#records-dropdown').hide();

    if ($(this).data('custom')) {
        $('#records-input')
            .prop('readonly', false)
            .focus()
            .val('')
            .attr('placeholder', 'Enter custom value');
        isCustomTyping = true;
    } else {
        selectedRecord = String($(this).data('record'));
        $('#records-input')
            .val(selectedRecord)
            .prop('readonly', true)
            .attr('placeholder', 'Click here or arrow to select');
        isCustomTyping = false;

        renderRecordsDropdown();
    }
});

// Handle Enter key for custom value
$('#records-input').on('keypress', function (e) {
    if (e.which === 13 && isCustomTyping) {
        e.preventDefault();
        const customVal = $(this).val().trim();

        if (!customVal) return;

        selectedRecord = customVal;
        $('#records-input')
            .val(selectedRecord)
            .prop('readonly', true)
            .attr('placeholder', 'Click here or arrow to select');
        isCustomTyping = false;

        renderRecordsDropdown();
    }
});

// Checkmark for Virus

$('.virus-scan').each(function () {
    let virusScanChecked = true;

    $(this).find('.virus-scan-box').on('click', function () {
        virusScanChecked = !virusScanChecked;

        const container = $(this).closest('.virus-scan');
        const textEl = container.find('.virus-scan-text');
        const iconEl = container.find('.virus-scan-icon');

        if (virusScanChecked) {
            textEl.removeClass('text-strong-red').addClass('text-bright-green');
            $(this)
                .removeClass('bg-strong-red')
                .addClass('bg-bright-green');
            iconEl.text('check');
        } else {
            textEl.removeClass('text-bright-green').addClass('text-strong-red');
            $(this)
                .removeClass('bg-bright-green')
                .addClass('bg-strong-red');
            iconEl.text('close');
        }
    });
});

// For Table Dropdown

const dropdownData = {
    medicineFrequency : ["Once", "Twice", "Every 4 hrs", "Every 6 hrs", "As Needed", "Before meal", "After meal", "Others"],
    method: ["By mouth", "By Injection", "On skin", "Breathe in", "Under the tongue", "In the eyes", "In the ears", "In Private parts", "In the nose", "Others"],
    instruction: ["Before meal", "After meal", "With food", "On empty stomach", "At bedtime", "In the morning", "In the evening", "At night", "As needed", "Everyday", "Every 2nd day", "Others"]
};

// Handle dropdown toggle click
$(document).on('click', '.dropdown-toggle', function (e) {
    e.stopPropagation();

    const container = $(this).closest('.dropdown-input-container');
    const dropdown = container.find('.dropdown-menu');
    const dropdownType = container.data('dropdown-type');

    $('.dropdown-menu').not(dropdown).hide();

    if (dropdown.is(':visible')) {
        dropdown.hide();
    } else {
        dropdown.empty(); // Always refresh
        const options = dropdownData[dropdownType] || [];

        options.forEach(option => {
            dropdown.append(`
        <div class="px-4 py-2 hover:bg-transparent-light-sea-green cursor-pointer text-dark-gray dropdown-item">
          ${option}
        </div>
      `);
        });

        dropdown.css({
            display: 'block',
            visibility: 'hidden'
        });

        const dropdownHeight = dropdown.outerHeight();
        const containerOffset = container.offset();
        const containerHeight = container.outerHeight();
        const viewportHeight = $(window).height();

        const spaceBelow = viewportHeight - (containerOffset.top + containerHeight);
        const spaceAbove = containerOffset.top;

        // Determine if we should flip upward
        if (spaceBelow < dropdownHeight && spaceAbove > dropdownHeight) {
            // Flip upward
            dropdown
                .removeClass('mt-1')
                .addClass('mb-1')
                .css({
                    top: 'auto',
                    bottom: `${containerHeight}px`
                });
        } else {
            // Keep dropdown below
            dropdown
                .removeClass('mb-1')
                .addClass('mt-1')
                .css({
                    top: `${containerHeight}px`,
                    bottom: 'auto'
                });
        }

        // Finally show visible
        dropdown.css({
            display: 'block',
            visibility: 'visible'
        });
    }
});


// Handle dropdown option click
$(document).on('click', '.dropdown-item', function () {
    const container = $(this).closest('.dropdown-input-container');
    const input = container.find('.dropdown-input');
    const value = $(this).text().trim();

    // Replace the input value completely
    input.val(value);

    // Optionally, move cursor to the end
    const el = input.get(0);
    if (el) {
        el.setSelectionRange(value.length, value.length);
    }

    container.find('.dropdown-menu').hide();
});

// Hide dropdowns on outside click
$(document).on('click', function () {
    $('.dropdown-menu').hide();
});

$(".dropdown-input").on('click', function () {
    $('.dropdown-menu').hide();
});

$('.saved-icon').on('click', function () {
    $(this).toggleClass('material-filled text-light-sea-green');
});