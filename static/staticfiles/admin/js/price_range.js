// price-range.js

document.addEventListener('DOMContentLoaded', function() {
    const minRange = document.getElementById('price-range-min');
    const maxRange = document.getElementById('price-range-max');
    const minValue = document.getElementById('min-value');
    const maxValue = document.getElementById('max-value');

    if (minRange && maxRange && minValue && maxValue) {
        minRange.addEventListener('input', updateRange);
        maxRange.addEventListener('input', updateRange);
        updateRange(); // Initialize display
    }
});

function updateRange() {
    const minRange = document.getElementById('price-range-min');
    const maxRange = document.getElementById('price-range-max');
    const minValue = document.getElementById('min-value');
    const maxValue = document.getElementById('max-value');

    if (minRange && maxRange && minValue && maxValue) {
        minValue.textContent = `Kshs ${minRange.value}`;
        maxValue.textContent = `Kshs ${maxRange.value}`;
    }
}
