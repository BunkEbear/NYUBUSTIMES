import math
import zipfile
import xml.etree.ElementTree as ET


def kmz_route_points(path, stop_names=None, max_dist_m=40.0, eps_m=0.5):
    """
    Open a KMZ (or plain KML) route file and return ONE ordered list of every
    critical point along the route, start to end, with stop names interspersed.

    Items in the list are either:
        (x, y)       a point on the route (x = longitude, y = latitude)
        "STOP NAME"  a string; it always directly follows the point of that stop

    Example shape:
        [(x,y), (x,y), (sx,sy), "Stop A", (x,y), (sx,sy), "Stop B", ...]

    So any two consecutive tuples (skipping the strings) are one polyline
    segment, and the string after a tuple tells you "this point is stop N".

    Rules
    - `stop_names` is an optional list of stop names to include. Only stops whose
      name is in the list are placed in the output; all others are ignored (their
      points are still used for the polyline, they just aren't inserted as stops).
      Names are compared ignoring case and surrounding whitespace. If None
      (default), every stop in the file is included. An empty list includes none.
    - Lines are joined in file order. If a line starts exactly where the previous
      one ended, the duplicate point is dropped. If there is a gap, the list
      simply continues with the next line's first point.
    - Each stop is SNAPPED onto the polyline (its closest point on the line), so
      the stop point is guaranteed to lie on the route.
    - A stop is attached to a line only if it is within `max_dist_m` meters of
      it, and only at its single nearest spot on that line. A stop on two lines
      (e.g. a terminal at both start and end) appears once per line.
    - If a stop snaps onto an existing vertex (within `eps_m`), no duplicate
      point is added; the name just follows that vertex.
    """
    # --- read KML -------------------------------------------------------------
    if path.lower().endswith(".kmz"):
        with zipfile.ZipFile(path) as z:
            kml = next(n for n in z.namelist() if n.lower().endswith(".kml"))
            root = ET.fromstring(z.read(kml))
    else:
        root = ET.parse(path).getroot()
    ns = {"k": root.tag.split("}")[0][1:]}

    stops, lines = [], []
    for pm in root.iterfind(".//k:Placemark", ns):
        el = pm.find("k:name", ns)
        name = el.text.strip() if el is not None and el.text else ""
        pt = pm.find(".//k:Point/k:coordinates", ns)
        ls = pm.find(".//k:LineString/k:coordinates", ns)
        if pt is not None:
            x, y = map(float, pt.text.strip().split(",")[:2])
            stops.append((name, (x, y)))
        elif ls is not None:
            lines.append([tuple(map(float, c.split(",")[:2])) for c in ls.text.split()])

    if stop_names is not None:
        wanted = {n.strip().casefold() for n in stop_names}
        stops = [s for s in stops if s[0].casefold() in wanted]

    # --- geometry (local flat-earth meters; fine at city scale) --------------
    pts = [c for line in lines for c in line]
    lat0 = math.radians(sum(p[1] for p in pts) / len(pts)) if pts else 0.0
    kx, ky = 111_320 * math.cos(lat0), 110_540
    m = lambda p: (p[0] * kx, p[1] * ky)

    def project(p, a, b):
        """Return (distance_m, t, snapped_point) of p onto segment a-b."""
        px, py = m(p); ax, ay = m(a); bx, by = m(b)
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy
        t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
        d = math.hypot(px - (ax + t * dx), py - (ay + t * dy))
        snapped = (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))
        return d, t, snapped

    # --- build the flat list --------------------------------------------------
    out = []

    def _last_point_equals(lst, p):
        for item in reversed(lst):
            if isinstance(item, tuple):
                return item == p
        return False

    for coords in lines:
        n = len(coords)
        at_vertex = [[] for _ in range(n)]       # names that sit exactly on a vertex
        in_segment = [[] for _ in range(n - 1)]  # (t, snapped, name) inside a segment

        for name, sp in stops:
            best = None
            for i in range(n - 1):
                d, t, snapped = project(sp, coords[i], coords[i + 1])
                if best is None or d < best[0]:
                    best = (d, i, t, snapped)
            if best is None or best[0] > max_dist_m:
                continue
            d, i, t, snapped = best
            seg_len = math.hypot(*(a - b for a, b in zip(m(coords[i + 1]), m(coords[i]))))
            if t * seg_len <= eps_m:
                at_vertex[i].append(name)
            elif (1 - t) * seg_len <= eps_m:
                at_vertex[i + 1].append(name)
            else:
                in_segment[i].append((t, snapped, name))

        for j in range(n):
            # skip the duplicate point where one line ends and the next begins
            if j == 0 and _last_point_equals(out, coords[0]):
                pass
            else:
                out.append(coords[j])
            out.extend(at_vertex[j])
            if j < n - 1:
                for t, snapped, name in sorted(in_segment[j]):
                    out.append(snapped)
                    out.append(name)
    return out


if __name__ == "__main__":
    import sys
    for item in kmz_route_points(sys.argv[1]):
        print(repr(item))