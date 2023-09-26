const sections = document.querySelectorAll("section[id]")
const navElements = document.querySelectorAll(".nav-element")
let inViewId = ""

const handleIntersection = (entries) => {
    entries.forEach((entry) => {
        if (entry.isIntersecting) {
            const sectionId = entry.target.getAttribute("id")
            inViewId = sectionId
            updateNavigationView(inViewId)
        }
    })
}

const navPositionObserverOptions = {
    root: null, // Use the viewport as the root
    rootMargin: "0px",
    threshold: 0.2,
}

const navPositionObserver = new IntersectionObserver(
    handleIntersection,
    navPositionObserverOptions,
)

sections.forEach((section) => {
    navPositionObserver.observe(section)
})

const updateNavigationView = (inViewId) => {
    navElements.forEach((navElement) => {
        const sectionId = navElement.getAttribute("data-section-id")
        const linkText = navElement.querySelector("span")
        if (linkText) {
            if (sectionId === inViewId) {
                linkText.innerHTML = `<strong>${linkText.textContent}</strong>`
            } else {
                linkText.innerHTML = linkText.textContent
            }
        }
    })
}

updateNavigationView(inViewId)

const showNavObserverOptions = {
    root: null, // Use the viewport as the root
    rootMargin: "0px",
    threshold: 0,
}

const mobileNavElement = document.getElementById("mobile-nav")
const navVisibleAnchor = document.getElementById("nav-visible-anchor")

const handleNavVisibility = (entries) => {
    entries.forEach((entry) => {
        if (entry.isIntersecting) {
            mobileNavElement.classList.add("translate-y-full")
        } else {
            mobileNavElement.classList.remove("translate-y-full")
        }
    })
}

const showNavObserver = new IntersectionObserver(
    handleNavVisibility,
    showNavObserverOptions,
)

showNavObserver.observe(navVisibleAnchor)

handleNavVisibility([navVisibleAnchor])

document.addEventListener("DOMContentLoaded", () => {
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
        accordionToggle.addEventListener("click", function () {
            accordionList.classList.toggle("max-h-screen")
            scrollTopButton.classList.toggle("translate-x-full")
        })
    }

    if (closeAccordionButton && accordionList) {
        closeAccordionButton.addEventListener("click", function () {
            accordionList.classList.remove("max-h-screen")
            scrollTopButton.classList.remove("translate-x-full")
        })
    }
    if (accordionList && navLinkClick) {
        Array.apply(null, navLinkClick).forEach((link) => {
            link.addEventListener("click", function () {
                accordionList.classList.remove("max-h-screen")
                scrollTopButton.classList.remove("translate-x-full")
            })
        })
    }

    const openDesktopNav = document.querySelector(
        "[data-toggle='open-desktop-nav']",
    )
    const closeDesktopNav = document.querySelector(
        "[data-toggle='close-desktop-nav']",
    )

    const navSlider = document.getElementById("slider")

    if (openDesktopNav && closeDesktopNav && navSlider) {
        openDesktopNav.addEventListener("click", function () {
            navSlider.classList.add("-translate-x-1/2")
        })
        closeDesktopNav.addEventListener("click", function () {
            navSlider.classList.remove("-translate-x-1/2")
        })
    }
})
