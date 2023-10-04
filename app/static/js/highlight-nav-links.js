const sections = document.querySelectorAll("section[id]")
const navElements = document.querySelectorAll(".nav-element")

const handleIntersection = (entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      const sectionId = entry.target.getAttribute("id")
      let inViewId = sectionId
      updateNavigationView(inViewId)
    }
  })
}

const navPositionObserverOptions = {
  root: null,
  rootMargin: "0px",
  threshold: 0,
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
