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
        const link = navElement.querySelector("a")
        if (link) {
            if (sectionId === inViewId) {
                link.innerHTML = `<strong>${link.textContent}</strong>`
            } else {
                link.innerHTML = link.textContent
            }
        }
    })
}

updateNavigationView(inViewId)
