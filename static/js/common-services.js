/* -------- TABS HANDLER -------- */
$('.tabs').each(function () {
    const $tabsWrapper = $(this);
    const $buttons = $tabsWrapper.find('.tab-btn');
    const $indicator = $tabsWrapper.find('.tab-indicator');

    function moveIndicator($btn) {
        $indicator.css({
            left: $btn.position().left + 'px',
            width: $btn.outerWidth() + 'px',
            height: $btn.outerHeight() + 'px'
        });
    }

    // Init
    const $activeBtn = $buttons.filter('.active');
    moveIndicator($activeBtn);

    showTabContent($activeBtn.data('type'), $tabsWrapper);

    $buttons.on('click', function () {
        const $btn = $(this);
        const type = $btn.data('type');

        $buttons.removeClass('active');
        $btn.addClass('active');

        moveIndicator($btn);
        showTabContent(type, $tabsWrapper);
    });

    $(window).on('resize', function () {
        moveIndicator($buttons.filter('.active'));
    });
});

// Scoped content handler
function showTabContent(type, $tabsWrapper) {
    const group =
        $tabsWrapper.hasClass('tabs-home') ? '.tabs-home-content' : '.tabs-inner-content';

    $(group).addClass('hidden');
    $(group).filter(`[data-type="${type}"]`).removeClass('hidden');
}

/* -------- DROPDOWN HANDLER -------- */

// Toggle dropdown
$(document).on('click', '.dropdown-trigger button', function (e) {
    e.stopPropagation();
    $('.dropdown-menu').not($(this).next()).addClass('hidden');
    $(this).next('.dropdown-menu').toggleClass('hidden');
});

// Select item
$(document).on('click', '.dropdown-item', function () {
    const value = $(this).text();
    const dropdown = $(this).closest('.custom-dropdown');

    dropdown.find('.selected-text').text(value);
    dropdown.find('.dropdown-menu').addClass('hidden');
});

// Close on outside click
$(document).on('click', function () {
    $('.dropdown-menu').addClass('hidden');
});

/* -------- STEPS HANDLER -------- */

$(document).ready(function () {
    goToStep(1);
});


function goToStep(stepNumber) {

    // Hide all step content
    $('.step-content').addClass('hidden');
    const $currentStep = $('#step-' + stepNumber).removeClass('hidden');

    const $container = $('.main-section');

    setTimeout(() => {
        $container.animate({ scrollTop: 0 }, 300);
    }, 50);

    // Reset all
    $('.step-circle').removeClass('active-step');
    $('.step-label').removeClass('active-heading');
    $('.step-line').removeClass('active-line');

    // Activate current + previous steps
    $('.step-circle').each(function () {
        if ($(this).data('step') <= stepNumber) {
            $(this).addClass('active-step');
        }
    });

    $('.step-label').each(function () {
        if ($(this).data('step') <= stepNumber) {
            $(this).addClass('active-heading');
        }
    });

    // Activate completed lines
    $('.step-line').each(function () {
        if ($(this).data('step') < stepNumber) {
            $(this).addClass('active-line');
        }
    });
}

$(document).on('click', '.step-btn', function () {
    const targetStep = $(this).data('target');
    goToStep(targetStep);
});

$(document).on('click', '.home-add-service', function () {
    $('.services-section').removeClass('hidden');
    $('.home-section').addClass('hidden')
    goToStep(1);
});

$(document).on('click', '#cancel-steps', function () {
    $('.services-section').addClass('hidden');
    $('.home-section').removeClass('hidden')
});

/* -------- MORE BUTTON HANDLER -------- */
$(document).on('click', '.more-btn', function (e) {
    e.stopPropagation();

    const card = $(this).closest('.service-card');

    // Close other open dropdowns
    $('.more-dropdown').not(card.find('.more-dropdown')).addClass('hidden');

    // Toggle current dropdown
    card.find('.more-dropdown').toggleClass('hidden');
});

$(document).on('click', function () {
    $('.more-dropdown').addClass('hidden');
});

$(document).on('click', '.delete-btn', function () {
    const card = $(this).closest('.service-card');
    card.remove();
});