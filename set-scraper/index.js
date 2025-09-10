const express = require("express");
const got = require("got");
const cheerio = require("cheerio");

const app = express();
const PORT = 5000;

const URL = "https://www.set.or.th/th/market/index/set/overview";

app.get("/api/set-data", async (req, res) => {
  try {
    const response = await got(URL, {
      timeout: { request: 10000 },
      headers: {
        "User-Agent":
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
      },
    });

    const $ = cheerio.load(response.body);

    // Scrape SET Index
    let setValue = $("div.value.text-white.mb-0.me-2.lh-1.stock-info")
      .first()
      .text()
      .trim();

    // Scrape Value (M.Baht)
    let marketValue = $("div.d-block.quote-market-cost.ps-2.ps-xl-3")
      .first()
      .text()
      .trim();

    res.json({
      set: setValue || "N/A",
      value: marketValue || "N/A",
      live_result: "52", // placeholder
      set_result: "123", // placeholder
    });
  } catch (err) {
    console.error("Error fetching data:", err.message);
    res.status(500).json({ error: err.message });
  }
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
