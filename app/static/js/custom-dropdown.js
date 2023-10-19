document.addEventListener("DOMContentLoaded", () => {
  // TODO: find all sections with charts // create a connection between defined chart classes
  // TODO: get parent elements to disable on click


  const allSections = document.querySelectorAll("section")
  // const allFigures = document.querySelectorAll(".bk-panel-models-reactive_html-ReactiveHTML")
  
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

  const createChartControllerObj = () => {
    const allChartWrappers = document.querySelectorAll(".chart-wrapper")
    let chartObj = {}
    allChartWrappers.forEach(chartWrapper => { 
      const allChartsInWrapper = chartWrapper.querySelectorAll(".bk-panel-models-reactive_html-ReactiveHTML")
      Array.from(allChartsInWrapper).forEach(figure => {
        const chartElements = figure.shadowRoot.lastChild.firstChild.children
        Array.from(chartElements).forEach(chart => {
          const className = chart.firstChild.getAttribute("class")
          if (className.includes("chart_")){
            const cleanedName = className.replace('bk-Figure chart_', "")
            const [chartName, chartLocale] = cleanedName.split("_")
            chartObj[chartName] = chartObj[chartName] || {}
            chartObj[chartName][chartLocale] = chart
          }
        })
      })
    })
    // returns an Object like { "chart-1-id": {"ber": chart1-ber, "de": chart1-de} }
    return chartObj
  }
  const addTogglesToController = (chartControllerObject) => {
    const chartIds = Object.keys(chartControllerObject)
    chartIds.forEach((chartId) => {
      console.log(chartControllerObject[chartId])
      chartControllerObject[chartId]["toggle"] = document.getElementById(chartId + "_toggle")
      })
    }

  let allFigures = []
  const getChartsInterval = setInterval(() => {
    const formerFiguresLength = allFigures.length
    allFigures = document.querySelectorAll(".bk-panel-models-reactive_html-ReactiveHTML")
    
    if (allFigures.length > 0 && allFigures.length == formerFiguresLength) {
      // This condition is true, when all charts are rendered
      const chartControllerObject = createChartControllerObj()

      addTogglesToController(chartControllerObject)
      Object.keys(chartControllerObject).forEach((chartId) => {
        const chartObj = chartControllerObject[chartId]
        chartObj["toggle"].addEventListener("change", () => {
          console.log("change it")
          //TODO: insert logig for toggles
        })
      })

      clearInterval(getChartsInterval)
      console.log(chartControllerObject)      
    }
  },500)
})
