document.addEventListener("DOMContentLoaded", () => {
  const allSections = document.querySelectorAll("section")
  const sectionIds = Array.from(allSections).map((section) =>
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
      const SUFFIX_LENGTH = "ber".length
      const selectedChartId = section.toggle.value
      const activeChartLocation = selectedChartId.slice(-SUFFIX_LENGTH)
      const inactiveChartLocation = locations.find(
        (location) => location !== activeChartLocation,
      )
      section.charts[activeChartLocation].classList.remove("hidden")
      section.charts[inactiveChartLocation].classList.add("hidden")
    })
  })
})
