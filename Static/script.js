document.addEventListener("DOMContentLoaded", () => {
    // Loader
    setTimeout(() => document.querySelector(".loader").style.display = "none", 2000);

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

    // Animate product items
    gsap.utils.toArray(".product-item").forEach(item => {
        gsap.from(item, { opacity: 0, y: 30, duration: 0.8, scrollTrigger: { trigger: item, start: "top 80%" } });
    });

    // Animate recommendations (if on recommendations page)
    if (document.querySelector(".recommendation-list")) {
        gsap.from(".rec-item", { opacity: 0, y: 20, duration: 0.8, stagger: 0.2 });
    }
});