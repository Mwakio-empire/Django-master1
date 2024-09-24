function showComingSoon() {
    alert("Coming soon!");
}

document.getElementById('mpesa-btn').addEventListener('click', function() {
    alert("Proceeding with M-Pesa payment...");
    document.getElementById('thank-you-message').style.display = 'block';
    document.getElementById('track-order').style.display = 'block';
});

document.getElementById('contact-seller-btn').addEventListener('click', function() {
    var contactInfo = document.getElementById('seller-contact-info');
    contactInfo.style.display = 'block';
});
