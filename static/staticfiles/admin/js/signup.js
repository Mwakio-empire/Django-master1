document.addEventListener('DOMContentLoaded', function() {
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm_password');
    const emailInput = document.getElementById('email');
    const messageDiv = document.getElementById('message');
    const feedbackElement = document.getElementById('password-feedback');
    const requirements = {
        minLength: document.getElementById('min-length'),
        uppercase: document.getElementById('uppercase'),
        lowercase: document.getElementById('lowercase'),
        number: document.getElementById('number')
    };

    function validatePassword() {
        const password = passwordInput.value;
        requirements.minLength.style.color = password.length >= 8 ? 'green' : 'red';
        requirements.uppercase.style.color = /[A-Z]/.test(password) ? 'green' : 'red';
        requirements.lowercase.style.color = /[a-z]/.test(password) ? 'green' : 'red';
        requirements.number.style.color = /\d/.test(password) ? 'green' : 'red';
        
        let feedback = '';

        if (password.length < 8) {
            feedback += 'Password must be at least 8 characters long.<br>';
        }
        if (!/[a-z]/.test(password)) {
            feedback += 'Password must include at least one lowercase letter.<br>';
        }
        if (!/[A-Z]/.test(password)) {
            feedback += 'Password must include at least one uppercase letter.<br>';
        }
        if (!/[0-9]/.test(password)) {
            feedback += 'Password must include at least one number.<br>';
        }

        feedbackElement.innerHTML = feedback ? feedback : 'Password meets the requirements.';
        feedbackElement.style.color = feedback ? 'red' : 'green';
    }

    function validateForm(event) {
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;
        const email = emailInput.value;
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!emailPattern.test(email)) {
            event.preventDefault();
            showMessage('Invalid email address!', 'error');
        } else if (password !== confirmPassword) {
            event.preventDefault();
            showMessage('Passwords do not match!', 'error');
        } else if (requirements.minLength.style.color !== 'green' ||
                   requirements.uppercase.style.color !== 'green' ||
                   requirements.lowercase.style.color !== 'green' ||
                   requirements.number.style.color !== 'green') {
            event.preventDefault();
            showMessage('Password does not meet requirements!', 'error');
        } else {
            showMessage('Form submitted successfully!', 'success');
        }
    }

    function showMessage(message, type) {
        messageDiv.textContent = message;
        messageDiv.className = `message ${type}`;
        setTimeout(() => {
            messageDiv.textContent = '';
        }, 3000);
    }

    passwordInput.addEventListener('input', validatePassword);
    confirmPasswordInput.addEventListener('input', validatePassword);
    document.getElementById('signup-form').addEventListener('submit', validateForm);
});

function togglePasswordVisibility(id) {
    const passwordField = document.getElementById(id);
    const type = passwordField.type === 'password' ? 'text' : 'password';
    passwordField.type = type;
}
