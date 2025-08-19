function toggleDealForm() {
    const formContainer = document.getElementById('dealFormContainer');
    const isHidden = window.getComputedStyle(formContainer).display === 'none';
    formContainer.style.display = isHidden ? 'block' : 'none';
}

// Валидация дат
document.addEventListener('DOMContentLoaded', function() {
    const begindateInput = document.getElementById('begindate');
    const closedateInput = document.getElementById('closedate');
    const dateError = document.getElementById('dateError');
    const submitBtn = document.getElementById('submitBtn');
    const dealForm = document.getElementById('dealForm');

    function validateDates() {
        const startDate = new Date(begindateInput.value);
        const endDate = new Date(closedateInput.value);

        if (startDate && endDate && endDate < startDate) {
            dateError.style.display = 'block';
            submitBtn.disabled = true;
            closedateInput.value = '';
            return false;
        } else {
            dateError.style.display = 'none';
            submitBtn.disabled = false;
            return true;
        }
    }

    begindateInput.addEventListener('change', function() {
        closedateInput.min = this.value;
        if (closedateInput.value && new Date(closedateInput.value) < new Date(this.value)) {
            closedateInput.value = '';
            validateDates();
        }
    });

    closedateInput.addEventListener('change', validateDates);

    dealForm.addEventListener('submit', function(e) {
        if (!validateDates()) {
            e.preventDefault();
        }
    });
});
