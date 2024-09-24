// main.js
function adjustPadding() {
    const header = document.querySelector('.header');
    const mainContent = document.querySelector('.main-content');
    
    if (header && mainContent) {
        const headerHeight = header.offsetHeight;
        mainContent.style.paddingTop = `${headerHeight}px`;
    }
}

function initDropdown() {
    const dropdownButton = document.querySelector('.category-button');
    const dropdownMenu = document.getElementById('category-dropdown');
    
    if (dropdownButton && dropdownMenu) {
        dropdownButton.addEventListener('click', function() {
            dropdownMenu.classList.toggle('hidden');
        });
    }
}

function initPriceRange() {
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
}
