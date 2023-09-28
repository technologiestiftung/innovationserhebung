document.addEventListener("DOMContentLoaded", () => {
  const allSections = document.querySelectorAll("section")
  const sectionIds = Array.apply(null, allSections).map((section) =>
    section.getAttribute("id"),
  )
  const sectionMeta = sectionIds
    .map((id) => {
      return { id, toggle: document.getElementById(id + "_toggle") }
    })
    .filter((meta) => meta.toggle)
    .map((meta) => {
      return {
        id: meta.id,
        toggle: meta.toggle,
        charts: {
          ber: document.getElementById(meta.id + "_ber"),
          ger: document.getElementById(meta.id + "_ger"),
        },
      }
    })

  sectionMeta.forEach((section) => {
    section.toggle.addEventListener("change", () => {
      const locations = ["ber", "ger"]
      const selectedChartId = section.toggle.value
      const activeChartLocation = selectedChartId.slice(
        -3,
        selectedChartId.length,
      )
      const inactiveChartLocation = locations.filter(
        (location) => location !== activeChartLocation,
      )[0]
      section.charts[activeChartLocation].classList.remove("hidden")
      section.charts[inactiveChartLocation].classList.add("hidden")
    })
  })
})
