// Build projected SVG map regions for reel templates.
//
//   node tools/geo/build-regions.mjs <out-dir> [region | name=lon0,lat0,lon1,lat1 | name=ISO3 ...]
//
// Each region is written to <out-dir>/<region>.json:
//   { W, H, proj: {scale, tx, ty}, countries: {ISO3: d}, states: {"IN-KL": d}, labels }
// Projection is plain Mercator (d3 geoMercator, no rotation), so a pin at
// (lon, lat) maps to x = tx + scale*lon_rad, y = ty - scale*ln(tan(pi/4 + lat_rad/2)).
// Paths are rounded to whole pixels with repeated points and sub-pixel rings dropped,
// which simplifies the 10m data to what is visible on a 1080px stage.
import fs from "fs";
import path from "path";
import { geoMercator, geoBounds } from "d3-geo";

const here = path.dirname(new URL(import.meta.url).pathname);
const countries = JSON.parse(fs.readFileSync(path.join(here, "data/countries-ind-10m.geojson"), "utf8"));
const states = JSON.parse(fs.readFileSync(path.join(here, "data/states-50m.geojson"), "utf8"));
const W = 1080, H = 1000;   // map stage size in the reel template

const iso = f => f.properties.ADM0_A3_IN || f.properties.ADM0_A3;
const indStates = states.features.filter(f => f.properties.adm0_a3 === "IND");
const stateId = f => "IN-" + (f.properties.postal || f.properties.iso_3166_2 || f.properties.name).replace(/^IN-/, "");
const byState = name => indStates.find(f => f.properties.name === name);
const bboxFeature = ([[x0, y0], [x1, y1]]) => ({ type: "Feature", geometry: { type: "Polygon",
  coordinates: [[[x0, y0], [x0, y1], [x1, y1], [x1, y0], [x0, y0]]] } });

// focus: what the projection fits; pad: px margin; minRing: drop rings smaller than this (px)
const REGIONS = {
  kerala:  { focus: () => byState("Kerala"), pad: 140, states: true, minRing: 1 },
  "south-india": { focus: () => bboxFeature([[72.5, 7.5], [84.5, 19.5]]), pad: 30, states: true, minRing: 1 },
  india:   { focus: () => countries.features.find(f => iso(f) === "IND"), pad: 40, states: true, minRing: 2 },
  "india-wide": { focus: () => bboxFeature([[56, 0], [99, 36]]), pad: 10, states: true, minRing: 2 },   // India + Arabian Sea + Bay of Bengal
  gulf:    { focus: () => bboxFeature([[34, 8], [80, 32]]), pad: 20, states: true, minRing: 2 },
  world:   { focus: () => bboxFeature([[-170, -58], [180, 78]]), pad: 10, states: false, minRing: 3 },
  europe:  { focus: () => bboxFeature([[-12, 35], [42, 66]]), pad: 10, states: false, minRing: 2 },
  "middle-east": { focus: () => bboxFeature([[24, 10], [64, 42]]), pad: 10, states: false, minRing: 2 },
  africa:  { focus: () => bboxFeature([[-20, -36], [54, 38]]), pad: 10, states: false, minRing: 2 },
  "east-asia": { focus: () => bboxFeature([[95, 18], [146, 50]]), pad: 10, states: false, minRing: 2 },
  "southeast-asia": { focus: () => bboxFeature([[92, -11], [142, 24]]), pad: 10, states: false, minRing: 2 },
  "north-america": { focus: () => bboxFeature([[-130, 12], [-60, 56]]), pad: 10, states: false, minRing: 2 },
  "south-america": { focus: () => bboxFeature([[-82, -56], [-34, 13]]), pad: 10, states: false, minRing: 2 },
  oceania: { focus: () => bboxFeature([[110, -48], [180, -8]]), pad: 10, states: false, minRing: 2 },
};
// Ad-hoc region from the command line: name=lon0,lat0,lon1,lat1 (e.g. panama=-84,6,-76,11),
// or name=ISO3 to fit one country (e.g. indonesia=IDN).
for (const arg of process.argv.slice(3)) {
  const [name, spec] = arg.split("=");
  if (!spec) continue;
  const nums = spec.split(",").map(Number);
  REGIONS[name] = nums.length === 4
    ? { focus: () => bboxFeature([[nums[0], nums[1]], [nums[2], nums[3]]]), pad: 20, states: false, minRing: 1 }
    : { focus: () => countries.features.find(f => iso(f) === spec), pad: 60, states: false, minRing: 1 };
}

function pathOf(feature, proj, minRing) {
  const g = feature.geometry;
  const polys = g.type === "Polygon" ? [g.coordinates] : g.type === "MultiPolygon" ? g.coordinates : [];
  let d = "";
  for (const poly of polys) for (const ring of poly) {
    const pts = [];
    for (const c of ring) {
      const p = proj([c[0], Math.max(-85, Math.min(85, c[1]))]);   // Mercator: the poles go to Infinity
      if (!p || !isFinite(p[0]) || !isFinite(p[1])) continue;
      const q = [Math.round(p[0]), Math.round(p[1])];
      const last = pts[pts.length - 1];
      if (!last || last[0] !== q[0] || last[1] !== q[1]) pts.push(q);
    }
    if (pts.length < 3) continue;
    const xs = pts.map(p => p[0]), ys = pts.map(p => p[1]);
    if (Math.max(...xs) - Math.min(...xs) < minRing && Math.max(...ys) - Math.min(...ys) < minRing) continue;
    // skip rings entirely off-stage
    if (Math.max(...xs) < -50 || Math.min(...xs) > W + 50 || Math.max(...ys) < -50 || Math.min(...ys) > H + 50) continue;
    d += "M" + pts.map(p => p.join(",")).join("L") + "Z";
  }
  return d;
}

function build(name) {
  const r = REGIONS[name];
  const proj = geoMercator().fitExtent([[r.pad, r.pad], [W - r.pad, H - r.pad]], r.focus());
  const [tx, ty] = proj.translate();
  const out = { region: name, W, H, proj: { scale: proj.scale(), tx, ty }, countries: {}, states: {} };
  for (const f of countries.features) {
    const d = pathOf(f, proj, r.minRing);
    if (d) out.countries[iso(f)] = d;
  }
  if (r.states) for (const f of indStates) {
    const d = pathOf(f, proj, 1);
    if (d) out.states[stateId(f)] = d;
  }
  out.names = Object.fromEntries(countries.features.map(f => [iso(f), f.properties.NAME]));
  out.stateNames = Object.fromEntries(indStates.map(f => [stateId(f), f.properties.name]));
  return out;
}

const [outDir, ...names] = process.argv.slice(2);
if (!outDir) { console.error("usage: node build-regions.mjs <out-dir> [region ...]"); process.exit(1); }
fs.mkdirSync(outDir, { recursive: true });
for (const name of names.length ? names.map(n => n.split("=")[0]) : Object.keys(REGIONS)) {
  const o = build(name);
  const file = path.join(outDir, `${name}.json`);
  fs.writeFileSync(file, JSON.stringify(o));
  console.log(`${name}: ${Object.keys(o.countries).length} countries, ${Object.keys(o.states).length} states, ${(fs.statSync(file).size / 1024).toFixed(0)} KB`);
}
