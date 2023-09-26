const sections = document.querySelectorAll("section[id]")
const navElements = document.querySelectorAll(".nav-element")
let inViewId = ""

const handleIntersection = (entries) => {
    entries.forEach((entry) => {
        if (entry.isIntersecting) {
            const sectionId = entry.target.getAttribute("id")
            inViewId = sectionId
            console.log("inViewId", inViewId)
            updateNavigationView(inViewId)
        }
    })
}

const observerOptions = {
    root: null, // Use the viewport as the root
    rootMargin: "0px",
    threshold: 0.2,
}

const observer = new IntersectionObserver(handleIntersection, observerOptions)

sections.forEach((section) => {
    observer.observe(section)
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

document.addEventListener("DOMContentLoaded", () => {
    const accordionToggle = document.querySelector("[data-toggle='accordion']")
    const scrollTopButton = document.getElementById("scroll-top-button")
    const closeAccordionButton = document.querySelector(
        "[data-toggle='accordionCloseOnly']",
    )
    const accordionList = document.getElementById("accordion-list")

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
})
