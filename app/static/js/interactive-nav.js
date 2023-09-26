document.addEventListener("DOMContentLoaded", () => {
    // nav animation on mobile devices
    const accordionToggle = document.querySelector("[data-toggle='accordion']")
    const scrollTopButton = document.getElementById("scroll-top-button")
    const closeAccordionButton = document.querySelector(
        "[data-toggle='accordionCloseOnly']",
    )
    const accordionList = document.getElementById("accordion-list")
    const navLinkClick = document.querySelectorAll(
        "[data-toggle='click-nav-link']",
    )

    if (accordionToggle && accordionList && scrollTopButton) {
        accordionToggle.addEventListener("click", () => {
            accordionList.classList.toggle("max-h-screen")
            scrollTopButton.classList.toggle("translate-x-full")
        })
    }

    if (closeAccordionButton && accordionList) {
        closeAccordionButton.addEventListener("click", () => {
            accordionList.classList.remove("max-h-screen")
            scrollTopButton.classList.remove("translate-x-full")
        })
    }
    if (accordionList && navLinkClick) {
        Array.apply(null, navLinkClick).forEach((link) => {
            link.addEventListener("click", () => {
                accordionList.classList.remove("max-h-screen")
                scrollTopButton.classList.remove("translate-x-full")
            })
        })
    }

    // slider for the hero section on desktop
    const openDesktopNav = document.querySelector(
        "[data-toggle='open-nav-desktop']",
    )
    const closeDesktopNav = document.querySelector(
        "[data-toggle='close-nav-desktop']",
    )

    const navSlider = document.getElementById("slider")

    if (openDesktopNav && closeDesktopNav && navSlider) {
        openDesktopNav.addEventListener("click", () => {
            navSlider.classList.add("-translate-x-1/2")
        })
        closeDesktopNav.addEventListener("click", () => {
            navSlider.classList.remove("-translate-x-1/2")
        })
    }
})
