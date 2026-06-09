document.addEventListener("DOMContentLoaded", function () {

    // NAVBAR SCROLL
    const navbar = document.querySelector(".fi-navbar");
    if (navbar) {
        window.addEventListener("scroll", function () {
            navbar.classList.toggle("scrolled", window.scrollY > 10);
        });
    }

    // CONTACTO PANEL
    const btn = document.getElementById("btn-contactanos");
    const info = document.getElementById("contacto-info");

    if (btn && info) {

        btn.addEventListener("click", function (e) {
            e.preventDefault();
            info.classList.toggle("show");
        });

        document.addEventListener("click", function (e) {
            if (!btn.contains(e.target) && !info.contains(e.target)) {
                info.classList.remove("show");
            }
        });

        window.addEventListener("scroll", function () {
            info.classList.remove("show");
        });
    }

    // HERO LINKS
    document.querySelectorAll(".hero-link").forEach(link => {
        link.addEventListener("click", function (e) {
            e.stopPropagation();
        });
    });

});