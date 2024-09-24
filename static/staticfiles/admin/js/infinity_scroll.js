document.addEventListener('DOMContentLoaded', function() {
    let page = 1;
    const loading = document.getElementById('loading');
    const productsGrid = document.getElementById('products-grid');
    let isLoading = false;
    let hasMoreProducts = true;

    if (!loading || !productsGrid) {
        console.error('Required elements are missing.');
        return;
    }

    function loadMoreProducts() {
        if (isLoading || !hasMoreProducts) return;

        isLoading = true;
        loading.style.display = 'block';
        page += 1;

        fetch(`/products/?page=${page}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (!response.ok) {
                hasMoreProducts = false;
                throw new Error('Network response was not ok.');
            }
            return response.text();
        })
        .then(data => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(data, 'text/html');
            const newProducts = doc.getElementById('products-grid').innerHTML;

            if (newProducts.trim() === '') {
                hasMoreProducts = false;
            } else {
                productsGrid.insertAdjacentHTML('beforeend', newProducts);
            }

            loading.style.display = 'none';
            isLoading = false;
        })
        .catch(error => {
            console.error('Error loading more products:', error);
            loading.style.display = 'none';
            isLoading = false;
        });
    }

    function debounce(func, wait) {
        let timeout;
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }

    window.addEventListener('scroll', debounce(() => {
        if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 500) {
            loadMoreProducts();
        }
    }, 200));
});
