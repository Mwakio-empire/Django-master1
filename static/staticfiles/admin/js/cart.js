// staticfiles/admin/js/cart.js

// Example: Handle form submission for updating quantity or removing items
document.addEventListener('DOMContentLoaded', function () {
    const updateForms = document.querySelectorAll('form[action*="update_cart_item"]');
    const removeForms = document.querySelectorAll('form[action*="remove_from_cart"]');

    updateForms.forEach(form => {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            const quantity = form.querySelector('input[name="quantity"]').value;
            if (quantity < 1) {
                alert('Quantity must be at least 1.');
                return;
            }
            form.submit();
        });
    });

    removeForms.forEach(form => {
        form.addEventListener('submit', function (e) {
            if (!confirm('Are you sure you want to remove this item?')) {
                e.preventDefault();
            }
        });
    });
});
