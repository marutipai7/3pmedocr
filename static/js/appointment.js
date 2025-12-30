document.addEventListener("DOMContentLoaded", function () {

  // ---------- Helper functions ----------
  function qs(selector) {
    return document.querySelector(selector);
  }

  function qsa(selector) {
    return document.querySelectorAll(selector);
  }

  function openModal(selector) {
    const modal = qs(selector);
    if (modal) modal.classList.remove("hidden");
  }

  function closeModal(selector) {
    const modal = qs(selector);
    if (modal) modal.classList.add("hidden");
  }

  function safeClick(selector, callback) {
    const el = qs(selector);
    if (el) el.addEventListener("click", callback);
  }

  // ---------- All Accepted ----------
  qsa(".card-all-accepted").forEach(card => {
    card.addEventListener("click", () => openModal(".modal-all-accepted"));
  });

  safeClick(".modal-close-all-accepted", () =>
    closeModal(".modal-all-accepted")
  );

  // ---------- All Completed ----------
  qsa(".card-all-completed").forEach(card => {
    card.addEventListener("click", () => openModal(".modal-all-completed"));
  });

  safeClick(".modal-close-all-completed", () =>
    closeModal(".modal-all-completed")
  );

  // ---------- Missed ----------
  qsa(".card-missed").forEach(card => {
    card.addEventListener("click", () => openModal(".modal-missed"));
  });

  safeClick(".modal-close-missed", () =>
    closeModal(".modal-missed")
  );

  // ---------- Canceled ----------
  qsa(".card-canceled").forEach(card => {
    card.addEventListener("click", () => openModal(".modal-canceled"));
  });

  safeClick(".modal-close-canceled", () =>
    closeModal(".modal-canceled")
  );

  qsa(".card-all-cancelled").forEach(card => {
      card.addEventListener("click", () => openModal(".modal-canceled"));
    });

  safeClick(".modal-close-canceled", () =>
    closeModal(".modal-canceled")
  );

  // ---------- Pending ----------
  qsa(".card-all-pending").forEach(card => {
    card.addEventListener("click", () => openModal(".modal-pending"));
  });

  safeClick(".modal-close-pending", () =>
    closeModal(".modal-pending")
  );

  // ---------- Attachment Preview ----------
  qsa(".view-attachment").forEach(button => {
    button.addEventListener("click", () => openModal(".attachment-modal"));
  });

  safeClick(".close-attachment-modal", () =>
    closeModal(".attachment-modal")
  );

  const attachmentModal = qs(".attachment-modal");
  if (attachmentModal) {
    attachmentModal.addEventListener("click", (e) => {
      if (e.target === attachmentModal) {
        closeModal(".attachment-modal");
      }
    });
  }

  // ---------- Status Dropdown ----------
  document.addEventListener("click", function (e) {
    const clickedButton = e.target.closest(".status-btn");
    const allDropdowns = qsa(".status-dropdown");

    if (clickedButton) {
      const dropdown = clickedButton.nextElementSibling;
      allDropdowns.forEach(d => {
        if (d !== dropdown) d.classList.add("hidden");
      });
      if (dropdown) dropdown.classList.toggle("hidden");
      return;
    }

    if (e.target.classList.contains("dropdown-item")) {
      const parent = e.target.closest(".relative");
      if (!parent) return;

      const text = parent.querySelector(".status-text");
      const dropdown = parent.querySelector(".status-dropdown");

      if (text) text.textContent = e.target.textContent;
      if (dropdown) dropdown.classList.add("hidden");
      return;
    }

    allDropdowns.forEach(d => d.classList.add("hidden"));
  });

});