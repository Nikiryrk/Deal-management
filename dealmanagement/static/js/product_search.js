document.addEventListener("DOMContentLoaded", function() {

    const searchForm = document.querySelector('.search-form');
    const searchInput = document.getElementById('product-search');

    if (searchForm && searchInput) {
        searchForm.addEventListener('submit', function(e) {
            if (searchInput.value.trim() === '') {
                e.preventDefault();
                searchInput.focus();
            }
        });
    }

    const productImages = document.querySelectorAll('.product-images img');
    productImages.forEach(img => {
        img.addEventListener('click', function() {
            const fullSizeImage = document.createElement('div');
            fullSizeImage.style.position = 'fixed';
            fullSizeImage.style.top = '0';
            fullSizeImage.style.left = '0';
            fullSizeImage.style.width = '100%';
            fullSizeImage.style.height = '100%';
            fullSizeImage.style.backgroundColor = 'rgba(0,0,0,0.8)';
            fullSizeImage.style.display = 'flex';
            fullSizeImage.style.justifyContent = 'center';
            fullSizeImage.style.alignItems = 'center';
            fullSizeImage.style.zIndex = '10000';
            fullSizeImage.style.cursor = 'pointer';

            const imgElement = document.createElement('img');
            imgElement.src = this.src;
            imgElement.style.maxWidth = '90%';
            imgElement.style.maxHeight = '90%';
            imgElement.style.objectFit = 'contain';

            fullSizeImage.appendChild(imgElement);
            fullSizeImage.addEventListener('click', function() {
                document.body.removeChild(fullSizeImage);
            });

            document.body.appendChild(fullSizeImage);
        });
    });

    const qrLinks = document.querySelectorAll('.qr-link');
    qrLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (e.ctrlKey || e.metaKey) {
                return;
            }

            e.preventDefault();
            const url = this.href;

            // Копирование в буфер обмена
            navigator.clipboard.writeText(url).then(() => {
                const originalText = this.textContent;
                this.textContent = 'Ссылка скопирована!';

                setTimeout(() => {
                    this.textContent = originalText;
                    window.open(url, '_blank');
                }, 1500);
            }).catch(err => {
                console.error('Ошибка при копировании: ', err);
                window.open(url, '_blank');
            });
        });
    });
});