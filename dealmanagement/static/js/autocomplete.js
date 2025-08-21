    document.addEventListener("DOMContentLoaded", function() {
    const input = document.getElementById("product-search");
    const list = document.getElementById("autocomplete-list");

    function debounce(func, delay) {
        let timer;
        return function(...args) {
            clearTimeout(timer);
            timer = setTimeout(() => func.apply(this, args), delay);
        };
    }

    function fetchAutocomplete(query) {
        if (query.length < 2) {
            list.innerHTML = "";
            return;
        }

        fetch(`/autocomplete/?q=${encodeURIComponent(query)}`)
            .then(res => res.json())
            .then(data => {
                list.innerHTML = "";
                data.forEach(item => {
                    const li = document.createElement("li");
                    li.textContent = `${item.name} (ID: ${item.id}) - ${item.price || "0"} ₽`;
                    li.onclick = () => {
                        input.value = item.id;
                        list.innerHTML = "";
                    };
                    list.appendChild(li);
                });
            })
            .catch(err => {
                console.error("Ошибка автокомплита:", err);
            });
    }

    const debouncedFetch = debounce(function() {
        fetchAutocomplete(input.value);
    }, 300);

    input.addEventListener("input", debouncedFetch);

    document.addEventListener("click", function(e) {
        if (!list.contains(e.target) && e.target !== input) {
            list.innerHTML = "";
        }
    });
});