$(document).ready(function () {

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    // Country code js
   $('.code-dropdown').each(function() {
        const $dropdown = $(this);
        const $btn = $dropdown.find('.code-btn');
        const $options = $dropdown.find('.code-option');
        const $selectedCode = $btn.find('.selected-code');

        $.ajax({
            url: "https://restcountries.com/v3.1/all?fields=name,idd", 
            method: "GET",
            success: function (data) {
                const countryList = data
                    .filter(c => c.idd && c.idd.root)
                    .map(c => {
                        const name = c.name.common;
                        const code = c.idd.root + (c.idd.suffixes ? c.idd.suffixes[0] : "");
                        return { name, code };
                    })
                    .sort((a, b) => a.name.localeCompare(b.name));

                countryList.forEach(({ name, code }) => {
                    const isIndia = name === "India";
                    const optionHtml = `<div class="px-4 py-2 hover:bg-gray-100 cursor-pointer" data-code="${code}">${name} (${code})</div>`;
                    $options.append(optionHtml);

                    if (isIndia) {
                        $selectedCode.text(code);
                    }
                });
            },
            error: function () {
                $options.append(`<div class="px-4 py-2 text-red-500">Failed to load country codes</div>`);
            }
        });

        $options.on('click', 'div', function () {
            const code = $(this).data('code');
            $selectedCode.text(code);
            $options.addClass('hidden');
        });
    });
    // dropdown js
    // $('.dropdown-btn').on('click', function (e) {
    //     e.stopPropagation(); 
    //     const $dropdown = $(this).closest('.dropdown');
    //     $('.dropdown-option').not($dropdown.find('.dropdown-option')).hide(); 
    //     $dropdown.find('.dropdown-option').toggle(); 
    //     $(this).find(".dropdown-arrow").toggleClass("rotate-180");
    // });    
    
    // $('.dropdown-option div').on('click', function() {
    //     const selectedText = $(this).text();
    //     $(this).closest('.dropdown').find('.dropdown-btn .selected-value').text(selectedText);
    //     $(this).closest('.dropdown').find('.select-dropdown').val(selectedText);
    //     $('.dropdown-option').hide();
    //     $(".dropdown-arrow").removeClass("rotate-180");
    // });
    // $(document).on('click', function () {
    //     $('.dropdown-option').hide();
    //     $(".dropdown-arrow").removeClass("rotate-180");
    // });
    // resend
    $('.resend').on('click', function () {
        toastr.success("OTP Resent on Mail");
        const $btn = $(this);
        let timeLeft = 30;
        $btn.off('click');
        const timer = setInterval(function () {
            const minutes = String(Math.floor(timeLeft / 60)).padStart(2, '0');
            const seconds = String(timeLeft % 60).padStart(2, '0');
            $btn.html(`Resend in ${minutes}:${seconds}`);
            timeLeft--;
            if (timeLeft < 0) {
                clearInterval(timer);
                $(".otp").html("Code resent").addClass("!text-bright-green");
                setTimeout(function () {
                    $(".otp").html("Try again in 60 seconds").addClass("!text-dark-red");
                    $btn.on('click', arguments.callee);
                }, 2000);
            }
        }, 1000);
    });
    // Send OTP
    $(".send-otp").click(function () {
        const $btn = $(this);
        if ($btn.hasClass("disabled")) return;
        let email = $('input[name="email"]').val();
        console.log(email)
        if (!email) {
            toastr.error("Please enter your email address.");
            console.log(email.type)
            return;
        }
        $.ajax({
            url: "/user/otp/send",
            type: "POST",
            headers: { 'X-CSRFToken': csrftoken },
            data: { "email": email },
            beforeSend: function(){
                $btn.addClass("!bg-Dark-Cornflower-Blue disabled");
            },
            success: function (response) {
                console.log("Success")
                toastr.success(response.message);
                // Store token in hidden field
                if ($("#otp_token").length === 0) {
                    $("form").append('<input type="hidden" id="otp_token" value="' + response.token + '">');
                } else {
                    $("#otp_token").val(response.token);
                }
                // ✅ Make email readonly immediately after OTP is sent
                $('input[name="email"]').prop("readonly", true);

                $(".otp").removeClass("hidden");
            },
            error: function (response) {
                console.error("Failed to send OTP:", response);
                if (response.responseJSON && response.responseJSON.message) {
                    toastr.error(response.responseJSON.message);
                } else {
                    toastr.error("Something went wrong while sending OTP.");
                }
            }
        });
    });
    // Verify OTP button
    $(".verify-otp").click(function () {
        let otp = $('input[name="otp1"]').val();
        let token = $("#otp_token").val();
        let email = $('input[name="email"]').val();

        if (!otp) {
            toastr.error("Please enter the OTP.");
            return;
        }

        if (!token) {
            toastr.error("OTP token missing. Please request OTP again.");
            return;
        }

        $.ajax({
            url: "/user/otp/verify",
            type: "POST",
            headers: { 'X-CSRFToken': csrftoken },
            data: {
                "otp": otp,
                "token": token
            },
            success: function (response) {
                toastr.success(response.message);

                // Disable verify button to avoid re-clicks
                $(".verify-otp").prop("disabled", true).addClass("opacity-50 cursor-not-allowed");
            },
            error: function (response) {
                console.error("OTP verification failed:", response);
                if (response.responseJSON && response.responseJSON.message) {
                    toastr.error(response.responseJSON.message);
                } else {
                    toastr.error("Something went wrong while verifying OTP.");
                }
            }
        });
    });
    //Permission Access
    // Show popup on upload trigger click
    let lastClickedTrigger = null;
    let uploadConfirmShown = false;

    // Show popup on upload trigger click
    document.querySelectorAll(".uploadTrigger").forEach((trigger) => {
        trigger.addEventListener("click", function () {
        lastClickedTrigger = this; // store the clicked trigger
        if (!uploadConfirmShown) {
            // Show popup only once
            document.querySelector(".file-access-popup").classList.remove("hidden");
        } else {
            // Directly trigger input if already allowed
            const uploadSection = lastClickedTrigger.closest(".upload-section");
            const input = uploadSection.querySelector(".uploadInput");
            input.click();
            lastClickedTrigger = null;
        }
        });
    });

    // Hide popup on "No" click
    document.querySelector(".deny-access").addEventListener("click", function () {
        document.querySelector(".file-access-popup").classList.add("hidden");
        lastClickedTrigger = null; // reset
    });

    // Allow file access and trigger file input on "Yes" click
    document.querySelector(".allow-access").addEventListener("click", function () {
        document.querySelector(".file-access-popup").classList.add("hidden");
        uploadConfirmShown = true;

        if (lastClickedTrigger) {
            const uploadSection = lastClickedTrigger.closest(".upload-section");
            const input = uploadSection.querySelector(".uploadInput");
            input.click();
            lastClickedTrigger = null;
        }
        });

    $('.uploadInput').on('change', function () {
        const file = this.files[0];
        if (!file) return;

        const $section = $(this).closest('.upload-section');
        const $display = $section.find('.upload-label-main');
        const $trigger = $section.find('.uploadTrigger');
        const $label = $trigger.find('.upload-label');
        const $icon = $trigger.find('.upload-icon');
            
        if (file.name) {
            // Show a success toaster when file is chosen
            toastr.success(`File uploaded successfully.`);
        } else {
            // Optional: show error toaster if no file selected
            toastr.error('No file selected.');
        }
        $label.text(file.name);
        $display.text(file.name)

        $icon.text('imagesmode').removeClass('text-primary-color').addClass('text-bright-green');
        
        $section.find('.remove-file-btn').removeClass('hidden');
        $('.remove-file-btn').on('click', function () {
            const $wrapper = $(this).closest('.upload-section');
            const $fileInput = $wrapper.find('.uploadInput');

            
            $fileInput.val('');

            
            $wrapper.find('.upload-label').text('');
            $wrapper.find('.upload-icon')
                .text('upload')
                .removeClass('text-green-600')
                .addClass('text-primary-color');

            $(this).addClass('hidden');
        });
    });

    // Toggle dropdown time trigger visibility
//Dropdowns code
  const dropdownConfig = {
  singleSelect: ["Timing", "Opening Time", "Closing Time", "Opening Days", "Type of Medical Provider", "Home Visit", "Experience", "Gender", "Specialization","Advertiser Type"],
  multiSelect: ["Services", "Facilities"],
};
function isSingleSelect($dropdown) {
  const labelText = $dropdown.find("> label").text();
  return dropdownConfig.singleSelect.some((keyword) =>
    labelText.includes(keyword)
  );
}
function getPlaceholderText($dropdown) {
  const labelText = $dropdown.find("> label").text();
  if (labelText.includes("Timing") || labelText.includes("Time")) {
    return "Select Time";
  }
  if (labelText.includes("Services") || labelText.includes("Service")) {
    return "Select Service";
  }
  if (labelText.includes("Facilities") || labelText.includes("Facility")) {
    return "Select Facility";
  }
  return "Select Option";
}
$(".dropdown-btn").on("click", function (e) {
  e.stopPropagation();
  const $dropdown = $(this).closest(".dropdown");
  const $currentOption = $dropdown.find(".dropdown-option");
  $(".dropdown-option").not($currentOption).hide();
  $(".dropdown-arrow")
    .not($(this).find(".dropdown-arrow"))
    .removeClass("rotate-180");
  $currentOption.toggle();
  $(this).find(".dropdown-arrow").toggleClass("rotate-180");
});

// Handle checkbox selection
$(document).on("change", ".dropdown-option input[type='checkbox']", function (e) {
  e.stopPropagation();
  const $dropdown = $(this).closest(".dropdown");
  if (isSingleSelect($dropdown)) {
    $dropdown.find("input[type='checkbox']").not(this).prop("checked", false);
  }

  updateSelectedText($dropdown);
});


$(".dropdown-option").on("click", function (e) {
  e.stopPropagation();
});
$(document).on("click", ".dropdown-option label", function (e) {
  e.stopPropagation();
  if ($(this).text().trim() === "Type...") {
    showCustomInput($(this).closest(".dropdown"));
    return;
  }
  let checkbox = $(this).prev('input[type="checkbox"]');
  if (checkbox.length === 0) {
    checkbox = $(this).next('input[type="checkbox"]');
  }
  if (checkbox.length) {
    checkbox.prop("checked", !checkbox.prop("checked")).trigger("change");
  }
});
function showCustomInput($dropdown) {
  const $typeOption = $dropdown.find("label:contains('Type...')").parent();
  if ($typeOption.find("input[type='text']").length > 0) {
    $typeOption.find("input[type='text']").focus();
    return;
  }
  const $input = $(
    '<input type="text" class="custom-input flex-1 px-2 py-1 border border-gray-300 rounded focus:outline-none focus:border-Royal-indigo" placeholder="Enter custom service...">'
  );

  $typeOption.html("").append($input);
  $input.focus();
  $input.on("blur keypress", function (e) {
    if (e.type === "blur" || (e.type === "keypress" && e.which === 13)) {
      const value = $(this).val().trim();

      if (value) {
        const customId = "custom_" + Date.now();
        const $newOption = $(`
          <div class="px-4 py-2 flex items-center hover:bg-gray-100 cursor-pointer custom-service">
            <input type="checkbox" id="${customId}" class="mr-2 accent-Royal-indigo" checked>
            <label for="${customId}" class="flex-1">${value}</label>
            <span class="material-symbols-outlined text-sm text-red-500 remove-custom cursor-pointer">close</span>
          </div>
        `);
        $typeOption.before($newOption);
        $typeOption.html('<label class="flex-1">Type...</label>');
        attachCustomOptionHandlers($newOption, $dropdown);
        updateSelectedText($dropdown);
      } else {
        $typeOption.html('<label class="flex-1">Type...</label>');
      }
    }
  });

  // Prevent input click from closing dropdown
  $input.on("click", function (e) {
    e.stopPropagation();
  });
}

// Attach handlers to custom options
function attachCustomOptionHandlers($option, $dropdown) {
  $option.find("input[type='checkbox']").on("change", function (e) {
    e.stopPropagation();
    if (isSingleSelect($dropdown)) {
      $dropdown
        .find("input[type='checkbox']")
        .not(this)
        .prop("checked", false);
    }

    updateSelectedText($dropdown);
  });

  // Handle label click
  $option.find("label").on("click", function (e) {
    e.stopPropagation();
    let checkbox = $(this).prev('input[type="checkbox"]');
    if (checkbox.length === 0) {
      checkbox = $(this).next('input[type="checkbox"]');
    }
    if (checkbox.length) {
      checkbox.prop("checked", !checkbox.prop("checked")).trigger("change");
    }
  });

  // Handle remove button
  $option.find(".remove-custom").on("click", function (e) {
    e.stopPropagation();
    $option.remove();
    updateSelectedText($dropdown);
  });
}

// Update selected text based on checked items
function updateSelectedText($dropdown) {
  const $checkedBoxes = $dropdown.find(
    ".dropdown-option input[type='checkbox']:checked"
  );
  const $selectedValue = $dropdown.find(".dropdown-btn .selected-value");

  if ($checkedBoxes.length === 0) {
    $selectedValue.text(getPlaceholderText($dropdown));
  } else if ($checkedBoxes.length === 1) {
    let labelText = $checkedBoxes.first().prev("label").text().trim();
    if (!labelText) {
      labelText = $checkedBoxes.first().next("label").text().trim();
    }
    $selectedValue.text(labelText);
  } else {
    $selectedValue.text($checkedBoxes.length + " selected");
  }
}

// Handle simple dropdown (non-checkbox) selection
$('.dropdown-option div:not(:has(input[type="checkbox"]))').on('click', function(e) {
  e.stopPropagation();
  const selectedText = $(this).text().trim();
  const $dropdown = $(this).closest('.dropdown');
  $dropdown.find('.dropdown-btn .selected-value').text(selectedText);
  $dropdown.find('.select-dropdown').val(selectedText);
  $dropdown.find('.dropdown-option').hide();
  $dropdown.find(".dropdown-arrow").removeClass("rotate-180");
});

// Close dropdowns when clicking outside
$(document).on("click", function () {
  $(".dropdown-option").hide();
  $(".dropdown-arrow").removeClass("rotate-180");
});

    // Time picker trigger
    document.querySelectorAll(".trigger-time").forEach(function (trigger) {
        trigger.addEventListener("click", function (e) {
        e.stopPropagation();
        const targetId = this.getAttribute("data-target");
        const timeInput = document.getElementById(targetId);
        if (timeInput) {
            timeInput.showPicker();
        }
        });
    });

    // Update dropdown display when time is selected (using input event for immediate update)
    document.querySelectorAll('input[type="time"]').forEach(function (timeInput) {
        console.log('Setting up time input listener for:', timeInput.id, timeInput.value);
        
        timeInput.addEventListener("input", function () {
        updateTimeDisplay(this);
        console.log('Time input changed:', this.id, this.value);
        });

        // Also handle change event for browser compatibility
        timeInput.addEventListener("change", function () {
        updateTimeDisplay(this);
        console.log('Time input changed:', this.id, this.value);
        });
    });

    function updateTimeDisplay(timeInput) {
        const dropdown = timeInput.closest(".dropdown");
        if (dropdown) {
        const selectedValue = dropdown.querySelector(".selected-value");
        if (selectedValue && timeInput.value) {
            // Format the time for display (e.g., "09:00 AM")
            const timeParts = timeInput.value.split(":");
            let hours = parseInt(timeParts[0]);
            const minutes = timeParts[1];
            const ampm = hours >= 12 ? "PM" : "AM";
            hours = hours % 12;
            hours = hours ? hours : 12; // Convert 0 to 12
            const formattedTime = hours + ":" + minutes + " " + ampm;

            selectedValue.textContent = formattedTime;
        }
        }
  }

    // Close dropdown when clicking outside
    document.addEventListener("click", function (e) {
        if (!e.target.closest(".dropdown")) {
        document.querySelectorAll(".dropdown-option").forEach(function (option) {
            option.classList.add("hidden");
        });
        }
    });

    // Close dropdown when time is selected (optional)
    document.querySelectorAll('input[type="time"]').forEach(function (timeInput) {
        timeInput.addEventListener("change", function () {
        const dropdownOption = this.closest(".dropdown-option");
        if (dropdownOption) {
            setTimeout(() => {
            dropdownOption.classList.add("hidden");
            }, 200); // Small delay to ensure time is displayed
        }
        });
    });

  // Open popup when camera icon is clicked
  $('#selfie-icon').on('click', function () {
    $('#camera-popup').removeClass('hidden');
    startCamera();
    $('#capture-btn').next("p").text('Capture'); 
  });

  // Close popup when X button is clicked
  $('#close-popup').on('click', function () {
    $('#camera-popup').addClass('hidden');
    stopCamera();
    resetCapture(); 
  });

  $('#upload-btn').on('click', function() {
    $('#upload-input').click();
    });

  // Handle file upload
  $('#upload-input').on('change', function (event) {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = function (e) {
        $('#captured-photo').attr('src', e.target.result);
        $('#uploaded-photo').removeClass('hidden');
        $('#save-btn').removeClass('hidden');
        $(".capture-polygon").hide();
        $('#capture-btn').next("p").text('Camera');
        // Stop camera and hide video
        stopCamera();
        $('#video').hide();
      };
      reader.readAsDataURL(file);
    }
  });

  // Capture the photo
  $('#capture-btn').on('click', function () {
    if ($(this).next("p").text() === 'Capture') {
      const video = document.getElementById('video');
      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d');
      
      // Set canvas size to match the video dimensions
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      
      // Draw the current frame from the video onto the canvas
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      
      // Get the image data URL from the canvas
      const dataURL = canvas.toDataURL('image/png');
      $('#captured-photo').attr('src', dataURL);
      $('#uploaded-photo').removeClass('hidden');
      $('#save-btn').removeClass('hidden');

      // Stop camera and hide video
      stopCamera();
      $('#video').hide();
      
      // Change button text to 'Retake'
      $('#capture-btn').next("p").text('Retake');
      $(".capture-polygon").hide();
    } else if ($(this).next("p").text() === 'Retake' || $(this).next("p").text() === 'Camera') {
      // If the button says 'Retake', start the camera and reset the form
      $('#captured-photo').attr('src', ''); // Clear previous photo
      $('#uploaded-photo').addClass('hidden');
      $('#save-btn').addClass('hidden');
      $('#capture-btn').next("p").text('Capture');
      $(".capture-polygon").show();
      $('#video').show();
      startCamera();  // Start camera again
    }
  });

  // Save the captured/uploaded photo and show the filename in the label
  $('#save-btn').on('click', function () {
    const fileName = $('#upload-input')[0]?.files[0]?.name || 'Captured Photo';
    $('#selfie-label').text(`${fileName}`).addClass("!text-green-400");
    $('#camera-popup').addClass('hidden');
    stopCamera();
  });

  // Start the camera
  function startCamera() {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      navigator.mediaDevices.getUserMedia({ video: true })
        .then(function (stream) {
          const video = document.getElementById('video');
          video.srcObject = stream;
          video.play();
        })
        .catch(function (err) {
          console.log('Error accessing the camera: ' + err);
        });
    } else {
      alert('Camera not supported on this device.');
    }
  }

  // Stop the camera
  function stopCamera() {
    const video = document.getElementById('video');
    const stream = video.srcObject;
    const tracks = stream?.getTracks();
    if (tracks) {
      tracks.forEach(track => track.stop());
    }
    video.srcObject = null;
  }

  // Reset the capture state for next use
  function resetCapture() {
    $('#upload-input').val('');
    $('#captured-photo').attr('src', '');
    $('#uploaded-photo').addClass('hidden');
    $('#save-btn').addClass('hidden');
    $('#capture-btn').text('Capture');
    $('#video').show();
  }

});

