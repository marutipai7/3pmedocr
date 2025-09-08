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

const payBtn = document.querySelector(".pay-button");
  const popup = document.querySelector(".subscription-popup");
  const closeBtn = document.querySelector(".close-popup");

  if (payBtn && popup && closeBtn) {
    payBtn.addEventListener("click", function (e) {
      e.preventDefault();
      popup.classList.remove("hidden");
    });

  closeBtn.addEventListener("click", function () {
    popup.classList.add("hidden");
  });
}

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
      mainPopup.classList.remove("hidden"); // Show the background popup again
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








