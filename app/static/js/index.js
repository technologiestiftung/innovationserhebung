// Function to check if an element is in the viewport
let inViewId = "";

const inView = (element) => {
  const rect = element.getBoundingClientRect();
  return (
    rect.top >= 0 &&
    rect.left >= 0 &&
    rect.bottom <=
      (window.innerHeight || document.documentElement.clientHeight) &&
    rect.right <= (window.innerWidth || document.documentElement.clientWidth)
  );
};

const updateNavigationView = (inViewId) => {
  // Update the HTML content with the new value of inViewId
  const navElements = document.querySelectorAll(".nav-element");
  navElements.forEach((navElement) => {
    const sectionId = navElement.getAttribute("data-section-id");

    // Check if the sectionId matches the inViewId
    if (sectionId === inViewId) {
      console.log(sectionId);
      // Apply the <strong> tag to the navigation link
      const link = navElement.querySelector("a");
      if (link) {
        link.innerHTML = `<strong>${link.textContent}</strong>`;
      }
    } else {
      // Remove <strong> tag if it exists
      const link = navElement.querySelector("a");
      if (link) {
        link.innerHTML = link.textContent;
      }
    }
  });
};

// Function to handle scroll events
const handleScroll = () => {
  const sections = document.querySelectorAll("section[id]");

  sections.forEach((section) => {
    const sectionId = section.getAttribute("id");

    if (inView(section)) {
      // You can perform actions specific to this section here
      inViewId = sectionId.toString();
      updateNavigationView(inViewId);
    }
  });
};

// Attach the scroll event listener
window.addEventListener("scroll", handleScroll);

// Initial check to see which section is in view on page load
handleScroll();
