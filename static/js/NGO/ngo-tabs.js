// $(document).ready(function () {
//     $('.tab-btn-ngo').click(function () {
//         alert('ok');
//         var target = $(this).data('tab');

//         $('.tab-btn-ngo').removeClass('active-tab-ngo');
//         $(this).addClass('active-tab-ngo');

//         $('.tab-content').addClass('hidden');
//         $('.' + target).removeClass('hidden');
//     });
// })

//code for open post histroy tab from home
window.onload = function () {
    const params = new URLSearchParams(window.location.search);
    const tab = params.get('tab');

    if (tab) {
      const targetBtn = document.querySelector(`.tab-btn-ngo[data-tab="${tab}"]`);
      if (targetBtn) {
        targetBtn.click();  
      }
    }
  };