const AdmZip = require("adm-zip")
require("dotenv").config()
const fs = require("fs")
const request = require("request")

const fileUrl = process.env.FONTS_URL
const fontsFolder = "app/static/fonts"

function downloadAndExtractFontFiles() {
  request.get({ url: fileUrl, encoding: null }, (error, _res, body) => {
    if (error) {
      throw error
    }
    const zip = new AdmZip(body)
    const entries = zip
      .getEntries()
      .filter((entry) => !entry.isDirectory && !entry.name.startsWith("."))
      .map((entry) => {
        const targetPath = `${fontsFolder}/${entry.name}`
        fs.writeFileSync(targetPath, entry.getData())
      })
    console.log(`Downloaded and extracted ${entries.length} font files.`)
  })
}

downloadAndExtractFontFiles()
