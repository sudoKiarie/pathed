// Function to handle flash messages for alerts
function hideFlashMessage() {
    const flashMessage = document.querySelector('.flash-message');
    if (flashMessage) {
        setTimeout(() => {
            flashMessage.style.display = 'none';
        }, 5000); // Hide after 5 seconds
    }
}

// Run the hideFlashMessage function when the page loads
window.onload = function() {
    hideFlashMessage();
};

// Function to add smooth scrolling effect
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();

        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Function to handle form validation (client-side)
function validateLoginForm() {
    const phoneNumber = document.querySelector('#phone_number');
    if (phoneNumber.value === '') {
        alert('Please enter your phone number.');
        return false;
    }
    return true;
}

// Attach validation to patient login form
const patientLoginForm = document.querySelector('#patientLoginForm');
if (patientLoginForm) {
    patientLoginForm.addEventListener('submit', function(event) {
        if (!validateLoginForm()) {
            event.preventDefault(); // Prevent form submission if validation fails
        }
    });
}
