(function () {
    const body = document.body;
    const navToggle = document.querySelector("[data-menu-toggle]");
    const navMenu = document.querySelector("[data-nav-menu]");
    const moonCursor = document.querySelector("[data-moon-cursor]");
    const swordCursor = document.querySelector("[data-sword-cursor]");
    const revealElements = document.querySelectorAll(".reveal");
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const canUseCustomCursor = window.matchMedia("(hover: hover) and (pointer: fine)").matches;

    if (navToggle && navMenu) {
        navToggle.addEventListener("click", function () {
            const isOpen = navMenu.classList.toggle("is-open");
            navToggle.setAttribute("aria-expanded", String(isOpen));
        });
    }

    document.querySelectorAll("[data-password-toggle]").forEach(function (button) {
        button.addEventListener("click", function () {
            const targetId = button.getAttribute("data-target");
            const input = document.getElementById(targetId);
            if (!input) {
                return;
            }

            const nextType = input.type === "password" ? "text" : "password";
            input.type = nextType;
            button.textContent = nextType === "password" ? "Show" : "Hide";
        });
    });

    document.querySelectorAll("[data-scroll-target]").forEach(function (button) {
        button.addEventListener("click", function (event) {
            const selector = button.getAttribute("data-scroll-target");
            const target = selector ? document.querySelector(selector) : null;
            if (!target) {
                return;
            }

            event.preventDefault();
            target.scrollIntoView({ behavior: prefersReducedMotion ? "auto" : "smooth", block: "start" });
        });
    });

    if (!prefersReducedMotion && "IntersectionObserver" in window) {
        const observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add("is-visible");
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.12 });

        revealElements.forEach(function (element) {
            observer.observe(element);
        });
    } else {
        revealElements.forEach(function (element) {
            element.classList.add("is-visible");
        });
    }

    if (!canUseCustomCursor || !moonCursor || !swordCursor) {
        return;
    }

    const sections = Array.from(document.querySelectorAll("[data-cursor-mode]"));
    let currentMode = null;
    let pointerX = window.innerWidth / 2;
    let pointerY = window.innerHeight / 2;
    let moonX = pointerX;
    let moonY = pointerY;
    let swordX = pointerX;
    let swordY = pointerY;
    let lastPointerTarget = null;

    function applyMode(mode) {
        if (currentMode === mode) {
            return;
        }

        currentMode = mode;
        body.classList.remove("cursor-moon", "cursor-sword");
        moonCursor.classList.remove("is-active");
        swordCursor.classList.remove("is-active");

        if (mode === "moon") {
            body.classList.add("cursor-moon");
            moonCursor.classList.add("is-active");
        } else {
            body.classList.add("cursor-sword");
            swordCursor.classList.add("is-active");
        }
    }

    function getModeFromTarget(target) {
        const activeSection = target && target.closest ? target.closest("[data-cursor-mode]") : null;
        return activeSection ? activeSection.getAttribute("data-cursor-mode") || "moon" : "moon";
    }

    function animate() {
        moonX += (pointerX - moonX) * 0.16;
        moonY += (pointerY - moonY) * 0.16;
        swordX += (pointerX - swordX) * 0.22;
        swordY += (pointerY - swordY) * 0.22;

        moonCursor.style.transform = "translate(" + moonX + "px, " + moonY + "px) translate(-50%, -50%)";
        swordCursor.style.transform = "translate(" + (swordX - 18) + "px, " + (swordY - 16) + "px)";

        window.requestAnimationFrame(animate);
    }

    window.addEventListener("mousemove", function (event) {
        pointerX = event.clientX;
        pointerY = event.clientY;
        lastPointerTarget = event.target;
        applyMode(getModeFromTarget(event.target));
    });

    document.addEventListener("mouseleave", function () {
        body.classList.remove("cursor-moon", "cursor-sword");
        moonCursor.classList.remove("is-active");
        swordCursor.classList.remove("is-active");
        currentMode = null;
    });

    window.addEventListener("mouseenter", function () {
        applyMode(getModeFromTarget(lastPointerTarget));
    });

    window.addEventListener("resize", function () {
        applyMode(getModeFromTarget(lastPointerTarget));
    });

    applyMode(sections.some(function (section) {
        return section.getAttribute("data-cursor-mode") === "moon";
    }) ? "moon" : "sword");
    animate();
})();
