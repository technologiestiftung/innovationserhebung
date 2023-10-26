const showNavObserverOptions = {
    root: null,
    rootMargin: "0px",
    threshold: 0,
}

const mobileNavElement = document.getElementById("nav-mobile")
const desktopScrollTopButton = document.getElementById("scroll-top-button-desktop")
const navVisibleAnchor = document.getElementById("nav-visible-anchor")

const handleNavVisibility = (entries) => {
    entries.forEach((entry) => {
        if (entry.isIntersecting) {
            mobileNavElement.classList.add("translate-y-full")
            desktopScrollTopButton.classList.add("translate-y-2x-full")
        } else {
            mobileNavElement.classList.remove("translate-y-full")
            desktopScrollTopButton.classList.remove("translate-y-2x-full")
        }
    })
}

const showNavObserver = new IntersectionObserver(
    handleNavVisibility,
    showNavObserverOptions,
)

showNavObserver.observe(navVisibleAnchor)

handleNavVisibility([navVisibleAnchor])
