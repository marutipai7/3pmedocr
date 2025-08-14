$(document).ready(function(){
  let rowToDelete = null;

$(document).ready(function () {

// Navbar User Dropdown
    $('.profile-btn').on('click', function () {
        $('.profile-dropdown').toggle();
    });

    // Hide dropdown when clicking outside
    $(document).on('click', function (e) {
        if (!$(e.target).closest('.profile-btn, .profile-dropdown').length) {
            $('.profile-dropdown').hide();
        }
    });

// Table row Delete Icon Modal Functionality
    $(".material-symbols-outlined.delete-icon").click(function () {
        rowToDelete = $(this).closest("tr");
        $(".deleteModal").removeClass("hidden").addClass("flex");;
    });

    $("#cancelDelete").click(function () {
        rowToDelete = null;
        $(".deleteModal").removeClass("flex").addClass("hidden");
    });

    $("#confirmDelete").click(function () {
        if (rowToDelete) {
            rowToDelete.remove();
        }
        $(".deleteModal").removeClass("flex").addClass("hidden");
    });


    //Code For copying referral code to clipboard
    $('.copy-btn').on('click',function(){
        const code=$("#referral-code").text().trim();
        navigator.clipboard.writeText(code).then(function(){
            console.log("Copied to Clipboard" + code)
        }).catch(function(err){
            console.log("Failed to copy",err)
        })
    })

    // Copy Code Functionality
 $('.copy-btn').click(async function (e) {
  e.preventDefault();

  const targetSelector = $(this).data('target');
  const $target = $(targetSelector);

  if ($target.length === 0) {
    console.log('Target not found!');
    return;
  }

  let textToCopy = '';
  if ($target.is('input') || $target.is('textarea')) {
    textToCopy = $target.val();
  } else {
    textToCopy = $target.text();
  }

  try {
    await navigator.clipboard.writeText(textToCopy);
    console.log('Copied: ' + textToCopy);
  } catch (err) {
    console.error('Failed to copy: ', err);
   
  }
});

    // Scan Virus Functionality
    const checkbox = $('.scan-toggle');
    const statusText = $('.status-text');


    checkbox.on('change', function () {
        if (checkbox.is(':checked')) {
            checkbox.prop('indeterminate', false);
            statusText.text('Safe to upload').removeClass().addClass('text-green text-16-nr');
        } else if (!checkbox.is(':checked') && checkbox.prop('indeterminate') !== true) {
            checkbox.prop('indeterminate', true);
            statusText.text('This file may contain viruses').removeClass().addClass('text-strong-red text-16-nr');
        }
    });
    
    $('.closecart-btn').on("click",function(){
        window.history.back();
    })

     //Notification Dropdown on  Home Page of All Sections
  $("#bell-icon").on("click", function (e) {
    e.stopPropagation(); 
    $("#notificationDropdown").toggleClass("hidden");
  });
  $(".close-notifications").on("click", function () {
    $("#notificationDropdown").toggleClass("hidden");
  });
  $(document).on("click", function (e) {
    if (
      !$(e.target).closest("#notificationDropdown").length &&
      !$(e.target).is("#bell-icon")
    ) {
      $("#notificationDropdown").addClass("hidden");
    }
  });

  //Share Popup on  Home Page of All Sections 
  $(".open-share-modal").on("click", function () {
    $("#shareModal").removeClass("hidden").addClass("flex");
  });
  $(".close-share-modal").on("click", function () {
    $("#shareModal").addClass("hidden").removeClass("flex");
  });
  $("#shareModal").on("click", function (e) {
    if ($(e.target).is("#shareModal")) {
      $("#shareModal").addClass("hidden").removeClass("flex");
    }
  });
 
  $('.close-avatar-btn').on('click',function(){
    $('.avatar').hide();
  })
});


// Scan Virus Functionality
const checkbox = $('.scan-toggle-donate');
const statusText = $('.status-text-donate');

checkbox.on('change', function () {
    if (checkbox.is(':checked')) {
        checkbox.prop('indeterminate', false);
        statusText.text('Virus Scan').removeClass().addClass('text-green text-16-nr');
    } else if (!checkbox.is(':checked') && checkbox.prop('indeterminate') !== true) {
        checkbox.prop('indeterminate', true);
        statusText.text('This file may contain viruses').removeClass().addClass('text-strong-red text-16-nr');
    }
});

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
$('#register-form').on('submit', function(e) {
    e.preventDefault();
    $('.border-dark-red').removeClass('border-dark-red');
    $('.placeholder\\:text-semi-transparent-red').removeClass('placeholder:text-semi-transparent-red');
    $('label.text-dark-red').removeClass('text-dark-red');
    $('.field-error').remove();
    $('[data-error-for]').text('').removeClass('text-xs text-dark-red'); // <-- Clear all data-error-for spans

    var pwd = $('[name="password"]').val();
    var cpwd = $('[name="confirm_password"]').val();
    
    // Debug logging
    console.log('Password validation:', {
        password: pwd,
        confirmPassword: cpwd,
        match: pwd === cpwd,
        passwordLength: pwd ? pwd.length : 0,
        confirmLength: cpwd ? cpwd.length : 0
    });
    
    if (pwd !== cpwd) {
        var $field = $('[name="confirm_password"]');
        $field.next('.field-error').remove();
        $('<span class="field-error text-xs text-dark-red"></span>')
            .text('Passwords do not match.')
            .insertAfter($field);
        $field
            .addClass('border-dark-red placeholder:text-semi-transparent-red')
            .removeClass('border-primary-color placeholder:text-blue-teal');
        $field.prev('label').addClass('text-dark-red');

        toastr.error('Passwords do not match.');
        return;
    }

    var $terms = $('[name="terms"]');
    $terms.next('.field-error').remove();

    if (!$terms.is(':checked')) {
        $('<span class="field-error text-xs text-dark-red"></span>')
            .text('You must agree to the terms.')
            .insertAfter($terms);

        toastr.error('You must agree to the terms.');
        return;
    }

    var formType = $(this).data('type');
    var formUrl = $(this).attr('action');

    console.log('Form Url:', formUrl);

    if (formUrl == '/user/save/advertiser') {
        let selectValue = $('.advertiser-type-selected').text().trim();
        $('input[name="advertiser_type"]').val(selectValue);
        let adServiceValue = $('.ad-service-selected').text().trim();
        $('input[name="ad_service_req"]').val(adServiceValue);
    } else if (formUrl == '/user/save/medical_provider') {
        var providerType = $('#provider_type_input').val();
        var servicesOffered = $('#services_offered_input').val();
        var workingDays = $('#working_days_input').val();
        var openingTime = $('#opening_time').val();
        var closingTime = $('#closing_time').val();
        var valid = true;
        // Remove previous errors
        $('.field-error.provider_type, .field-error.services_offered, .field-error.working_days, .field-error.opening_time, .field-error.closing_time').remove();
        if (!providerType) {
            valid = false;
            $('<span class="field-error provider_type text-xs text-dark-red">Please select a provider type.</span>')
                .insertAfter($('#provider_type_input'));
        }
        if (!servicesOffered) {
            valid = false;
            $('<span class="field-error services_offered text-xs text-dark-red">Please select at least one service.</span>')
                .insertAfter($('#services_offered_input'));
        }
        if (!workingDays) {
            valid = false;
            $('<span class="field-error working_days text-xs text-dark-red">Please select at least one working day.</span>')
                .insertAfter($('#working_days_input'));
        }
        if (!openingTime) {
            valid = false;
            $('<span class="field-error opening_time text-xs text-dark-red">Please select an opening time.</span>')
                .insertAfter($('#opening_time'));
        }
        if (!closingTime) {
            valid = false;  
            $('<span class="field-error closing_time text-xs text-dark-red">Please select a closing time.</span>')
                .insertAfter($('#closing_time'));
        }
        if (!valid) {
            e.preventDefault();
            toastr.error('Please fill all required dropdowns.');
            return false;
        }
        let selectService = $('.selected-services').text().trim();
        $('input[name="services_offered"]').val(selectService);
        let selectProviderType = $('.selected-provider-type').text().trim();
        $('input[name="provider_type"]').val(selectProviderType);
        let selectWorkingDays = $('.selected-working-days').text().trim();
        $('input[name="working_days"]').val(selectWorkingDays);
    } else if (formUrl == '/user/save/client') {
        let selectValue = $('.company-type-selected').text().trim();
        $('input[name="company_type"]').val(selectValue);
        let adServiceValue = $('.company-service-selected').text().trim();
        $('input[name="company_service"]').val(adServiceValue);
    } else if (formUrl == '/user/save/ngo') {
        let selectValue = $('.ngo-service-selected').text().trim();
        $('input[name="ngo_service"]').val(selectValue);
    }
    var formData = new FormData(this);

    $.ajax({
        url: formUrl,
        type: 'POST',
        headers: { 'X-CSRFToken': csrftoken },
        data: formData,
        processData: false,
        contentType: false,
        success: function(resp) {
            $('.field-error').remove();
            $('[data-error-for]').text('').removeClass('text-xs text-dark-red');
            $('.border-dark-red').removeClass('border-dark-red');
            $('.placeholder\\:text-semi-transparent-red').removeClass('placeholder:text-semi-transparent-red');
            $('label.text-dark-red').removeClass('text-dark-red');
            
            if (resp.success) {
                toastr.success(resp.message || 'Registration successful!');
                setTimeout(function() {
                    window.location.href = "login";
                }, 1200);
            } else if (resp.errors) {
                // Loop through errors, apply classes/styles just like jQuery Validate
                $.each(resp.errors, function(field, message) {
                    var $input = $('[name="' + field + '"]');
                    $('[data-error-for="' + field + '"]')
                        .text(message)
                        .addClass('text-xs text-dark-red');
                    $input
                        .addClass('border-dark-red placeholder:text-semi-transparent-red')
                        .removeClass('border-primary-color placeholder:text-blue-teal');
                    $input.prev('label').addClass('text-dark-red');
                });
                console.log(resp.errors);
                toastr.error("Please correct the highlighted errors.");
            } else {
                toastr.error(resp.error || "Registration failed.");
            }
        },
        error: function(xhr) {
            $('.field-error').remove();
            $('[data-error-for]').text('').removeClass('text-xs text-dark-red');
            $('.border-dark-red').removeClass('border-dark-red');
            $('.placeholder\\:text-semi-transparent-red').removeClass('placeholder:text-semi-transparent-red');
            $('label.text-dark-red').removeClass('text-dark-red');

            if (xhr.responseJSON && xhr.responseJSON.errors) {
                $.each(xhr.responseJSON.errors, function(field, message) { 
                    var $input = $('[name="' + field + '"]');
                    $input.next('.field-error').remove();
                    $('<span class="field-error text-xs text-dark-red"></span>')
                        .text(message)
                        .insertAfter($input);
                    $input
                        .addClass('border-dark-red placeholder:text-semi-transparent-red')
                        .removeClass('border-primary-color placeholder:text-blue-teal');
                    $input.prev('label').addClass('text-dark-red');
                });
                toastr.error("Please correct the highlighted errors.");
            } else {
                toastr.error("Server error. Try again.");
            }
        }
    });
});
// Optional: Remove error style when field is corrected
$('#register-form input').on('input change', function() {
    var $input = $(this);
    $input.removeClass('border-dark-red placeholder:text-semi-transparent-red');
    $input.prev('label').removeClass('text-dark-red');
    $input.next('.field-error').remove();
    $('[data-error-for="' + $input.attr('name') + '"]').text('').removeClass('text-xs text-dark-red');
});

$('#login-form').on('submit', function(e) {
    e.preventDefault();
    $('#email-error').text('');
    $('#password-error').text('');
    var email = $('#email').val().trim();
    var password = $('#password').val().trim();
    if (!email) {
        $('#email-error').text('Email is required.');
        toastr.error('Email is required.');
        return;
    }
    if (!password) {
        $('#password-error').text('Password is required.');
        toastr.error('Password is required.');
        return;
    }
    var formUrl = $(this).attr('action');

    $.ajax({
        url: formUrl,
        type: 'POST',
        headers: { 'X-CSRFToken': csrftoken },
        data: { email: email, password: password },
        success: function(resp) {
            if (resp.success) {
                toastr.success('Login successful!');
                setTimeout(function() {
                    window.location.href = resp.redirect;
                }, 1000);
            } else {
                if (resp.errors) {
                    if (resp.errors.email) $('#email-error').text(resp.errors.email);
                    if (resp.errors.password) $('#password-error').text(resp.errors.password);
                    if (resp.errors.account) toastr.error(resp.errors.account);
                        else toastr.error('Please correct the errors.');
                } else {
                    toastr.error(resp.error || "Login failed.");
                }
            }
        },
        error: function(xhr) {
            toastr.error("Server error. Try again.");
        }
    });
});

$('.submit-form').on('submit', function(e) {
    e.preventDefault();
    var formUrl = $(this).attr('action');
    var formType = $(this).attr('method');
    var formData = new FormData(this);
    console.log('Form Data:', formData);
    console.log('Form URL:', formUrl);
    console.log('Form Type:', formType);
    $.ajax({
        url: formUrl,
        type: formType,
        headers: { 'X-CSRFToken': csrftoken },
        data: formData,
        processData: false,
        contentType: false,
        success: function(resp) {
            if (resp.success) {
                toastr.success(resp.message);

                setTimeout(function() {
                    window.location.href = resp.redirect;
                }, 1000);
            } else {
                if (resp.errors) {
                    toastr.error(resp.message);
                } else {
                    toastr.error(resp.message);
                }
            }
        },
        error: function(xhr) {
            toastr.error("Server error. Try again.");
        }
    });
});
})


//closeShareModal
function closeShareModal() {
  const modal = document.querySelector(".shareModal");
  modal.classList.add("hidden");
}

//closeShareModal
function closeNotificationModal() {
  const modal = document.querySelector(".notificationDropdown");
  modal.classList.add("hidden");
}