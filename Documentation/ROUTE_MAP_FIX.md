# Fix: Map Showed a Straight Line Instead of a Road Route

## Summary

In the Medical Chat ambulance sidebar, the map drew a **straight line** between the
ambulance and the patient instead of a proper road-following route (like phone
navigation). This document explains the root causes and how they were fixed.

**File changed:** `frontend/default/src/pages/MedicalChat/components/GoogleMapsRoute.js`

---

## Symptoms

- A straight blue line connected the two points, cutting across buildings/water.
- The backend was healthy: `GET /maps/debug/test-route` returned
  `"api_status": "success"` with a full encoded `polyline` (~474 chars).
- `GET /maps/nearest-ambulance` also returned a valid `route.polyline`.

So the data was correct — the problem was entirely in the **frontend rendering**.

---

## Root Cause 1 — Wrong rendering method

The component built a *fake* directions object and passed it to
`<DirectionsRenderer>`:

```js
const directionsResult = {
  routes: [{
    legs: [{ /* ... */ }],
    overview_polyline: { points: routeData.polyline }
  }]
};
setDirections(directionsResult);
```

`<DirectionsRenderer>` only renders a **real `DirectionsResult`** produced by
Google's `DirectionsService`. It ignores a hand-built object with an
`overview_polyline` string, so the road route never drew and the code fell back to
the straight `<Polyline>`.

### Correct approach

Decode the encoded polyline with the **geometry library** and draw it as a real
`<Polyline>`:

```js
const decoded = window.google.maps.geometry.encoding
  .decodePath(routeData.polyline)
  .map((point) => ({ lat: point.lat(), lng: point.lng() }));
setRoutePath(decoded);
```

The `geometry` library was already loaded via `LoadScript libraries={['geometry']}`.

---

## Root Cause 2 — Race condition (the real blocker)

Even after switching to decoding, the route still didn't show because the route
data arrived **before** Google Maps finished loading. The old effect had a dead-end
branch:

```js
} else if (routeData && !window.google) {
  console.warn('Google Maps not loaded yet'); // never retried
}
```

It logged a warning and **gave up** — once Maps finished loading, nothing
re-triggered the decode.

### Fix

Introduced a `googleReady` flag set when Maps loads (in both `LoadScript.onLoad`
and the map's `onLoad`), and added it to the decode effect's dependencies so the
decode **re-runs** as soon as Maps + the geometry library are ready:

```js
const [googleReady, setGoogleReady] = useState(false);

useEffect(() => {
  if (!googleReady || !window.google?.maps?.geometry?.encoding) {
    if (routeData) console.warn('Google Maps geometry not ready yet, will retry once loaded');
    return;
  }
  if (!routeData) return;
  // ...decode routeData.polyline into routePath...
}, [googleReady, routeData, patientLat, patientLon, ambulanceLat, ambulanceLon]);
```

---

## Additional improvements

- **Auto-fit the map** to the route using `map.fitBounds()` so the whole path is
  visible (phone-navigation feel).
- **Straight line is now a clear fallback only** — rendered in **grey** (not blue)
  when no road polyline exists, so it is obvious it is an estimate.
- Removed the unused `DirectionsRenderer` import.

---

## How to verify

1. Hard refresh the page (`Ctrl+Shift+R`).
2. Create a case with a GPS location, then click **🚑 Ambulance Info**.
3. Open the browser console (F12). Expected logs:
   ```
   Google Maps loaded successfully
   Decoded road polyline with N points
   ```
4. The map shows a **blue road-following route** and auto-zooms to fit.

### If it still shows a straight/grey line

- `geometry not ready yet` repeating → the `geometry` library isn't loading
  (check the Maps JavaScript API key and enabled APIs).
- `Decoded road polyline with N points` but still straight → investigate further.
- No logs at all → the frontend didn't reload the updated file.

---

## Prerequisites (unchanged, for reference)

- **Backend** uses the Google **Directions API** (requires billing enabled).
- **Frontend** uses the **Maps JavaScript API** + `geometry` library.
- Both read the key from their respective `.env` files
  (`GOOGLE_MAPS_API_KEY` / `REACT_APP_GOOGLE_MAPS_API_KEY`).
