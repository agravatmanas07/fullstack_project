document.addEventListener("DOMContentLoaded", () => {
    // Add to Cart
    document.querySelectorAll(".add-to-cart").forEach(button => {
        button.addEventListener("click", () => {
            const clothingId = button.getAttribute("data-id");
            fetch("/add_to_cart", {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: `clothing_id=${clothingId}`
            })
            .then(response => response.json())
            .then(data => {
                const cartList = document.getElementById("cart-items");
                cartList.innerHTML = "";
                data.cart.forEach(item => {
                    const li = document.createElement("li");
                    li.textContent = item;
                    cartList.appendChild(li);
                    gsap.from(li, { opacity: 0, y: 20, duration: 0.5 });
                });
            });
        });
    });

    // Rating Functions
    const rateUserId = document.getElementById("rate-user-id");
    const rateClothingId = document.getElementById("rate-clothing-id");
    const rateRating = document.getElementById("rate-rating");

    document.getElementById("add-rating").addEventListener("click", () => {
        fetch("/rate", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: `user_id=${rateUserId.value}&clothing_id=${rateClothingId.value}&rating=${rateRating.value}`
        }).then(response => response.json()).then(data => alert("Rating added!"));
    });

    document.getElementById("update-rating").addEventListener("click", () => {
        fetch("/update_rating", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: `user_id=${rateUserId.value}&clothing_id=${rateClothingId.value}&rating=${rateRating.value}`
        }).then(response => response.json()).then(data => alert("Rating updated!"));
    });

    document.getElementById("delete-rating").addEventListener("click", () => {
        fetch("/delete_rating", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: `user_id=${rateUserId.value}&clothing_id=${rateClothingId.value}`
        }).then(response => response.json()).then(data => alert("Rating deleted!"));
    });

    // Animations
    gsap.utils.toArray(".product-item").forEach(item => {
        gsap.from(item, { opacity: 0, y: 30, duration: 0.8, scrollTrigger: { trigger: item, start: "top 80%" } });
    });

    // Filter Function
    window.applyFilters = function() {
        const category = document.getElementById("category-filter").value;
        const rating = document.getElementById("rating-filter").value;
        window.location.href = `/?category=${category}&rating=${rating}`;
    };
});