const showNavObserverOptions = {
    root: null,
    rootMargin: "0px",
    threshold: 0,
}

const mobileNavElement = document.getElementById("nav-mobile")
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
