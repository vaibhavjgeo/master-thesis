# Climate Change x Shallow Geothermal Potential - M.Sc. Thesis (KIT)

> How does a warming climate reshape Germany's shallow geothermal yield? My Master's thesis results as an interactive web atlas: 8 CMIP6 climate models x finite-line-source BHE theory at 5 km resolution.

**Live**: [vaibhavjgeo.vercel.app/thesis](https://vaibhavjgeo.vercel.app/thesis/) · Fullscreen atlas: [/thesis/map-fullscreen.html](https://vaibhavjgeo.vercel.app/thesis/map-fullscreen.html)

## What this is

The public, explorable version of my M.Sc. thesis at Karlsruhe Institute of Technology: *Impact of Climate Change on the Geothermal Potential of Closed Systems Using GIS and Python* (supervised by PD Dr. Kathrin Menberg, Engineering Geology, and Dr. Susanne Benz, IPF). A Python pipeline processes the model outputs into 24 JSON layers rendered live with Leaflet.js - real simulation output in the browser, no screenshots.

## Key findings

- Mean shallow ground warming of **1.7 ± 0.6 °C (SSP 2-4.5)** to **3.1 ± 1.1 °C (SSP 5-8.5)** by 2100
- Heat-extraction efficiency rises **~8-24% by 2100** versus baseline
- Each **1 °C of warming substitutes ~4 m of drilling depth** for equivalent heat supply
- Results computed per 5 km pixel across Germany, for 50-year, 100-year, and 100-year-sustainable operating horizons

## Methodology in one paragraph

Ground-surface temperature trends from **8 CMIP6 GCMs** (BBC, CanESM, GFDL, GISS, HadGEM, IPSL, MIROC, MPI) under SSP 2-4.5 and SSP 5-8.5 were processed in **Google Earth Engine** to a uniform 5 km grid. A Python model implements **finite-line-source / moving-FLS theory** with seasonal signals and borehole thermal resistance; the maximum sustainable extraction rate per pixel is solved with **Brent's method** under SIA 384/6 minimum-fluid-temperature constraints. Ensemble statistics (mean, P25, P50, P75) quantify climate-model uncertainty.

## How this was built - AI-pair-programming disclosure

The scientific model, parameter choices, and analysis are my thesis work. The web presentation was built with **AI-assisted development** (Anthropic Claude as pair-programmer for the Leaflet rendering, layer toggles, and page structure), with every line reviewed. The numbers on the page come exclusively from the thesis outputs.

## Architecture

```
Python pipeline (NumPy, SciPy, scipy.optimize.brentq)
   |
   +-- processes CMIP6 GeoTIFFs -> per-pixel extraction rates & power
   |
   v
24 JSON layers (data_json/: 16 individual model+scenario, 8 ensemble)
   |
   v
Static frontend (Leaflet.js + chroma-js) - renders layers live, toggleable
```

No backend, no database. The full scientific atlas is served from static hosting.

## Tech stack

| Layer | What |
|---|---|
| Modelling | Python, NumPy, SciPy (Brent's method root finding) |
| Climate data | CMIP6 (8 GCMs, SSP 2-4.5 / SSP 5-8.5) via Google Earth Engine |
| Data format | GeoTIFF in, JSON out (EPSG:4326) |
| Frontend | Vanilla JavaScript, Leaflet.js, chroma-js |
| Hosting | Vercel (auto-deploys from `main`) |
| Cost | 0 EUR/month |

## Features

- Individual-model and 8-model-ensemble views
- Scenario switching (SSP 2-4.5 vs SSP 5-8.5) and percentile selection (mean, P25, P50, P75)
- Six toggleable result layers: heat extraction and usable power for 50-yr, 100-yr, and 100-yr-sustainable horizons
- Click anywhere for the exact value at that point
- Fullscreen atlas mode

## Run locally

```bash
git clone https://github.com/vaibhavjgeo/master-thesis.git
cd master-thesis
python3 -m http.server 8000
# Open http://localhost:8000
```

## Project structure

```
.
├── index.html               # Thesis page with embedded explorer
├── map-fullscreen.html      # Fullscreen atlas
├── data_json/               # 24 JSON result layers (individual/ + ensemble/)
├── files/                   # Jupyter notebook + JSON export script
└── README.md
```

## License

MIT for the code. Thesis text and figures remain © Vaibhav Jaiswal / KIT.

## Contact

- **Email**: vaibhavjaiswal1234@gmail.com
- **Portfolio**: [vaibhavjgeo.vercel.app](https://vaibhavjgeo.vercel.app)
- **LinkedIn**: [linkedin.com/in/vaibhavgeo](https://www.linkedin.com/in/vaibhavgeo/)
