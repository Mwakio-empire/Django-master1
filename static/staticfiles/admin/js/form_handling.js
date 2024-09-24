// form-handling.js

document.addEventListener('DOMContentLoaded', function() {
    const paymentForm = document.getElementById('payment-form');
    const commentForm = document.getElementById('comment-form');
    
    if (paymentForm) {
        paymentForm.addEventListener('submit', handlePaymentFormSubmit);
    }
    
    if (commentForm) {
        commentForm.addEventListener('submit', handleCommentFormSubmit);
    }
});

function handlePaymentFormSubmit(event) {
    event.preventDefault();
    // Handle payment form submission
}

function handleCommentFormSubmit(event) {
    event.preventDefault();
    // Handle comment form submission
}
