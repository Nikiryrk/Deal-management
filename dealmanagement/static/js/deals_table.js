function toggleDealForm() {
    const formContainer = document.getElementById('dealFormContainer');
    const isHidden = window.getComputedStyle(formContainer).display === 'none';
    formContainer.style.display = isHidden ? 'block' : 'none';
}

document.addEventListener('DOMContentLoaded', function() {
    const begindateInput = document.getElementById('begindate');
    const closedateInput = document.getElementById('closedate');


    begindateInput.addEventListener('change', function() {
        closedateInput.min = this.value;
        if (closedateInput.value && new Date(closedateInput.value) < new Date(this.value)) {
            closedateInput.value = '';
        }
    });

});
