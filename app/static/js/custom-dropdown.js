document.addEventListener("DOMContentLoaded", () => {

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
    return chartObj
  }
  const addTogglesToController = (chartControllerObject) => {
    const chartIds = Object.keys(chartControllerObject)
    chartIds.forEach((chartId) => {
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
      // returns an Object like { "chart-1-id": {"ber": chart1-ber, "de": chart1-de, "toggle": chart1-toggle} }
      Object.keys(chartControllerObject).forEach((chartId) => {
        const chartObj = chartControllerObject[chartId]
        chartObj["toggle"].addEventListener("change", (e) => {
          const activeChartLocation = e.target.value
          const locations = ["ber", "de"]
          console.log(chartObj, activeChartLocation)
          locations.forEach((location) => {
            chartObj[location].style.display = "block"
            if (location == activeChartLocation) {
              chartObj[location].firstChild.style.maxHeight = "fit-content"
            } else {
              chartObj[location].firstChild.style.maxHeight = 0
            }
        })
      })
    })

      clearInterval(getChartsInterval)
      console.log(chartControllerObject)      
    }
  },500)
})
