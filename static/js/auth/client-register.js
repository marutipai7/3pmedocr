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

    let uploadConfirmShown = false;
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
    $('.dropdown-btn').on('click', function (e) {
        e.stopPropagation(); 
        const $dropdown = $(this).closest('.dropdown');
        $('.dropdown-option').not($dropdown.find('.dropdown-option')).hide(); 
        $dropdown.find('.dropdown-option').toggle(); 
        $(this).find(".dropdown-arrow").toggleClass("rotate-180");
    });    
    
    $('.dropdown-option div').on('click', function() {
        const selectedText = $(this).text();
        $(this).closest('.dropdown').find('.dropdown-btn .selected-value').text(selectedText);
        $(this).closest('.dropdown').find('.select-dropdown').val(selectedText);
        $('.dropdown-option').hide();
        $(".dropdown-arrow").removeClass("rotate-180");
    });
    $(document).on('click', function () {
        $('.dropdown-option').hide();
        $(".dropdown-arrow").removeClass("rotate-180");
    });
    
    // password hide/unhide
    $('.togglePassword').on('click', function () {
        const targetId = $(this).data('target');
        const passwordField = $('#' + targetId);
        if (passwordField.length) {
            const type = passwordField.attr('type') === 'password' ? 'text' : 'password';
            passwordField.attr('type', type);     
            $(this).text(type === 'password' ? 'visibility' : 'visibility_off');
        }
      }); 
    // resend
    $('.resend').on('click', function () {
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
        $(this).addClass("!bg-Dark-Cornflower-Blue");
        let email = $('input[name="email"]').val();

        if (!email) {
            toastr.error("Please enter your email address.");
            return;
        }

        $.ajax({
            url: "/user/otp/send",
            type: "POST",
            headers: { 'X-CSRFToken': csrftoken },
            data: { "email": email },
            success: function (response) {
                toastr.success(response.message);

                // Store token in hidden field
                if ($("#otp_token").length === 0) {
                    $("form").append('<input type="hidden" id="otp_token" value="' + response.token + '">');
                } else {
                    $("#otp_token").val(response.token);
                }

                // ✅ Make email readonly immediately after OTP is sent
                $('input[name="email"]').prop("readonly", true);
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
        let token = $("#otp_token").val(); // ✅ Correct bearer token
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
    $('.uploadTrigger').on('click', function () {
        if (!uploadConfirmShown) {
            if (confirm("This site wants to access your files to upload an image. Do you allow?")) {
                uploadConfirmShown = true;
                $(this).closest('.upload-section').find('.uploadInput').trigger('click');
            }
        } else {
            $(this).closest('.upload-section').find('.uploadInput').trigger('click');
        }
    });

    $('.uploadInput').on('change', function () {
        const file = this.files[0];
        if (!file) return;

        const $section = $(this).closest('.upload-section');
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
    document.querySelectorAll(".dropdown-btn").forEach(function (btn) {
        btn.addEventListener("click", function () {
        const dropdown = this.closest(".dropdown");
        const options = dropdown.querySelector(".dropdown-option");
        options.classList.toggle("hidden");

        // Close other open dropdowns
        document.querySelectorAll(".dropdown-option").forEach(function (option) {
            if (option !== options) {
            option.classList.add("hidden");
            }
        });
        });
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
});

