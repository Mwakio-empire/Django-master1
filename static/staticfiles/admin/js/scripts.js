document.addEventListener('DOMContentLoaded', function() {
    // Payment Form Handling
    const form = document.getElementById('payment-form');
    const popup = document.getElementById('popup');
    const popupMessage = document.getElementById('popup-message');

    if (form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault(); // Prevent form submission

            const formData = new FormData(form);

            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showPopup('Payment successful! Redirecting...', 'success', data.redirect_url);
                } else {
                    showPopup('Payment failed. Please try again.', 'error');
                }
            })
            .catch(error => {
                showPopup('An error occurred. Please try again.', 'error');
            });
        });
    }

    function showPopup(message, type, redirectUrl = '') {
        if (popupMessage && popup) {
            popupMessage.textContent = message;
            popup.className = `popup ${type}`;
            popup.classList.remove('hidden');

            setTimeout(() => {
                popup.classList.add('hidden');
                if (type === 'success' && redirectUrl) {
                    window.location.href = redirectUrl;
                }
            }, 5000); // Show popup for 5 seconds
        }
    }

    // Category Dropdown
    const categoryButton = document.querySelector('.category-button');
    const dropdown = document.getElementById('category-dropdown');

    if (categoryButton && dropdown) {
        categoryButton.addEventListener('click', function() {
            dropdown.classList.toggle('hidden');
        });
    }

    // Comment Form Handling
    const commentForm = document.getElementById('comment-form');
    const commentsList = document.getElementById('comments-list');

    if (commentForm) {
        commentForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const formData = new FormData(commentForm);
            
            fetch(window.location.href, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.text())
            .then(data => {
                if (commentsList) {
                    commentsList.innerHTML = data;
                    commentForm.reset();
                }
            })
            .catch(error => console.error('Error:', error));
        });
    }

    // Dropdown Toggle
    const dropdownToggle = document.querySelector('.dropdown-toggle');
    const dropdownMenu = document.querySelector('.dropdown-menu');

    if (dropdownToggle && dropdownMenu) {
        dropdownToggle.addEventListener('click', function() {
            dropdownMenu.style.display = (dropdownMenu.style.display === 'block') ? 'none' : 'block';
        });
    } else {
        console.error('Dropdown elements not found.');
    }

    // Adjust Padding Based on Header Height
    const adjustPadding = () => {
        const header = document.querySelector('.header');
        const mainContent = document.querySelector('.main-content');
        if (header && mainContent) {
            const headerHeight = header.offsetHeight;
            mainContent.style.paddingTop = headerHeight + 'px';
        }
    };

    window.addEventListener('load', adjustPadding);
    window.addEventListener('resize', adjustPadding);

    // Price Range Handling
    const minRange = document.getElementById('price-range-min');
    const maxRange = document.getElementById('price-range-max');
    const minValueDisplay = document.getElementById('price-min-value');
    const maxValueDisplay = document.getElementById('price-max-value');

    function updateRange() {
        if (minRange && maxRange && minValueDisplay && maxValueDisplay) {
            const minValue = minRange.value;
            const maxValue = maxRange.value;

            minValueDisplay.textContent = `Kshs ${minValue}`;
            maxValueDisplay.textContent = `Kshs ${maxValue}`;

            if (parseInt(minValue) > parseInt(maxValue)) {
                minRange.value = maxValue;
            }
        }
    }

    if (minRange && maxRange) {
        minRange.addEventListener('input', updateRange);
        maxRange.addEventListener('input', updateRange);

        updateRange(); // Initialize display
    }
});
