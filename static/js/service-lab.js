/* -------- SERVICE CARD HANDLER -------- */


const serviceCardTemplate = () => `
<div class="rounded-lg px-4 py-6 relative bg-[#F9FAFB] service-card animate-fade">
  <button class="remove-service absolute top-3 right-3 text-ebony hover:text-red-500">✕</button>

  <div class="mb-4 custom-dropdown">
    <label class="text-base sm:text-lg font-semibold">Select Category</label>
    <div class="dropdown-trigger mt-2">
      <button type="button" class="w-full border border-slate-gray rounded-md px-3 py-3 text-left flex justify-between items-center">
        <span class="selected-text text-sm sm:text-base font-normal text-dark-gray">Surgery</span>
        <span class="material-symbols-outlined">keyboard_arrow_down</span>
      </button>
      <ul class="dropdown-menu hidden absolute z-20 mt-1 w-1/2 bg-white border border-primary-blue rounded shadow text-sm sm:text-base text-dark-gray font-normal h-40 overflow-y-auto scroll">
        <li class="dropdown-item px-3 py-2 hover:bg-premium-light-blue cursor-pointer">Elective Surgery</li>
        <li class="dropdown-item px-3 py-2 hover:bg-premium-light-blue cursor-pointer">Emergency Surgery</li>
        <li class="dropdown-item px-3 py-2 hover:bg-premium-light-blue cursor-pointer">Day Care Surgery</li>
        <li class="dropdown-item px-3 py-2 hover:bg-premium-light-blue cursor-pointer">Notification log</li>
    </ul>
    </div>
  </div>

  <div class="mb-4 custom-dropdown">
      <label class="text-base sm:text-lg text-jet-black font-semibold">Select Test / Packages</label>

      <div class="dropdown-trigger mt-2">
          <button type="button" class="w-full border border-slate-gray rounded-md px-3 py-3 text-left flex justify-between items-center">
              <span class="selected-text text-sm sm:text-base font-normal text-dark-gray">Thyroid Profile</span>
              <span class="material-symbols-outlined">
                  keyboard_arrow_down
              </span>
          </button>

          <ul class="dropdown-menu hidden absolute z-20 mt-1 w-1/2 bg-white border border-primary-blue rounded shadow text-sm sm:text-base text-dark-gray font-normal h-40 overflow-y-auto scroll">
              <li class="dropdown-item px-3 py-2 hover:bg-premium-light-blue cursor-pointer">Surgery</li>
              <li class="dropdown-item px-3 py-2 hover:bg-premium-light-blue cursor-pointer">Diagnostics</li>
              <li class="dropdown-item px-3 py-2 hover:bg-premium-light-blue cursor-pointer">Consultation</li>
              <li class="dropdown-item px-3 py-2 hover:bg-premium-light-blue cursor-pointer">Donation</li>
          </ul>
      </div>
  </div>

  <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
    <div class="custom-dropdown">
      <label class="text-base sm:text-lg font-semibold">Days</label>
      <div class="dropdown-trigger mt-2">
        <button type="button" class="w-full border border-slate-gray rounded-md px-3 py-3 text-left flex justify-between items-center">
          <span class="selected-text text-sm sm:text-base font-normal text-dark-gray">Same Day</span>
          <span class="material-symbols-outlined">keyboard_arrow_down</span>
        </button>
        <ul class="dropdown-menu hidden absolute z-20 mt-1 w-1/2 bg-white border border-primary-blue rounded shadow text-sm sm:text-base text-dark-gray font-normal h-40 overflow-y-auto scroll">
            <li class="dropdown-item px-3 py-2 hover:bg-premium-light-blue cursor-pointer">Elective Surgery</li>
            <li class="dropdown-item px-3 py-2 hover:bg-premium-light-blue cursor-pointer">Emergency Surgery</li>
            <li class="dropdown-item px-3 py-2 hover:bg-premium-light-blue cursor-pointer">Day Care Surgery</li>
            <li class="dropdown-item px-3 py-2 hover:bg-premium-light-blue cursor-pointer">Notification log</li>
        </ul>
      </div>
    </div>

    <div>
      <label class="text-base sm:text-lg font-semibold">Price</label>
      <input type="text" class="w-full border rounded-md px-3 py-3 mt-2" value="₹ 0.00">
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

/* -------- SERVICE CARD HANDLER -------- */


const collectionServiceCardTemplate = () => `
<div class="service-card rounded-lg px-4 py-3 relative bg-[#F9FAFB]">
<button class="remove-service-collection absolute top-3 right-3 text-ebony hover:text-red-500">✕</button>
      <!-- Select Mode Dropdown -->
      <div class="mb-4 custom-dropdown">
          <label class="text-base sm:text-lg text-jet-black font-semibold">Select Mode Type</label>

          <div class="dropdown-trigger mt-2">
              <button type="button" class="w-full border border-slate-gray rounded-md px-3 py-3 text-left flex justify-between items-center">
                  <span class="selected-text text-sm sm:text-base font-normal text-dark-gray">Walk in city</span>
                  <span class="material-symbols-outlined">
                      keyboard_arrow_down
                  </span>
              </button>

              <ul class="dropdown-menu hidden absolute z-20 mt-1 w-1/2 bg-white border border-primary-blue rounded shadow text-sm sm:text-base text-dark-gray font-normal h-40 overflow-y-auto scroll">
                  <li class="dropdown-item px-3 py-2 hover:bg-premium-light-blue cursor-pointer">Surgery</li>
                  <li class="dropdown-item px-3 py-2 hover:bg-premium-light-blue cursor-pointer">Diagnostics</li>
                  <li class="dropdown-item px-3 py-2 hover:bg-premium-light-blue cursor-pointer">Consultation</li>
                  <li class="dropdown-item px-3 py-2 hover:bg-premium-light-blue cursor-pointer">Donation</li>
              </ul>
          </div>
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div class="custom-dropdown">
              <label class="text-base sm:text-lg text-jet-black font-semibold">Region (optional)</label>

              <div class="dropdown-trigger mt-2">
                  <button type="button" class="w-full border border-slate-gray rounded-md px-3 py-3 text-left flex justify-between items-center">
                      <span class="selected-text text-sm sm:text-base font-normal text-dark-gray">In-Clinic Visit</span>
                      <span class="material-symbols-outlined">
                          keyboard_arrow_down
                      </span>
                  </button>

                  <ul class="dropdown-menu hidden absolute z-20 mt-1 w-1/2 bg-white border border-primary-blue rounded shadow text-sm sm:text-base text-dark-gray font-normal h-40 overflow-y-auto scroll">
                      <li class="dropdown-item px-3 py-2 hover:bg-premium-light-blue cursor-pointer">In-Clinic Visit</li>
                      <li class="dropdown-item px-3 py-2 hover:bg-premium-light-blue cursor-pointer">Phone Consult</li>
                      <li class="dropdown-item px-3 py-2 hover:bg-premium-light-blue cursor-pointer">Home Visit</li>
                      <li class="dropdown-item px-3 py-2 hover:bg-premium-light-blue cursor-pointer">Notification log</li>
                  </ul>
              </div>
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

$(document).on('click', '.add-service-collection', function () {
  const stepContent = $(this).closest('.step-content');
  stepContent.find('.collection-services-list').append(collectionServiceCardTemplate());
});

$(document).on('click', '.remove-service-collection', function () {
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
;