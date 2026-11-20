import math


def find_bus_path(lat, lon, heading, route, max_dist_m=500.0, tie_margin_m=10.0,
                  eps_m=3.0, loop=True, perpendicular_tol_deg=0.0,
                  nyc_bbox=(40.45, 40.95, -74.30, -73.65), return_info=False):
    """
    Given a bus position (lat, lon) and the route list built by
    kmz_route_points(), return the critical points from the bus to the next
    station. `heading` is accepted for caller compatibility but is ignored:
    buses always travel forward, toward the end of the route list.

    Returns a list in the same style as the route list:
        [bus_point, bend, bend, ..., station_point]
    The list contains only (x, y) = (lon, lat) coordinates, never strings. The
    last point is the next station (or the end of the route if none is ahead).
    bus_point is the bus snapped onto the line.

    How it works
    1. The route list is turned into nodes (a point plus any stop names that
       followed it). Consecutive nodes are the polyline segments.
    0. Buses are IGNORED (an empty list [] is returned, no error) if the inputs
       are missing/non-numeric, the position is outside `nyc_bbox`
       (south, north, west, east; pass None to disable the check), or the bus is
       more than `max_dist_m` from every segment. An empty list is falsy, so
       `if path:` tells you whether the bus was usable.
    2. The bus is matched to the closest route segment.
    3. Direction is always "forward" (towards the END of the list).
    4. Walking from the bus in that direction, every node is added until one
       with a stop name is reached; that point ends the list (the name itself is
       not included, but is available as info["station"]).
       A node within `eps_m` of the bus at the very start is skipped (the bus
       is already there). The route is treated as a LOOP (loop=True, the
       default): past the last point it continues from the first point until a
       stop is reached. It walks at most one full lap, so a route with no stops
       at all returns a full lap instead of looping forever. With loop=False the
       list instead just ends at the end of the route if no stop is ahead.

    return_info=True returns (path, info). For an ignored bus that is
    ([], {"skipped": "bad_input" | "outside_nyc" | "too_far_from_route"}).
    Otherwise info is a dict with the matched
    segment's node indexes, direction, distance to the line and the station name
    (None if none was found). heading_diff_deg is retained as None for caller
    compatibility.
    """
    def skip(reason):
        return ([], {"skipped": reason}) if return_info else []

    try:
        lat, lon = float(lat), float(lon)
    except (TypeError, ValueError):
        return skip("bad_input")
    if not all(map(math.isfinite, (lat, lon))):
        return skip("bad_input")
    if nyc_bbox is not None:
        south, north, west, east = nyc_bbox
        if not (south <= lat <= north and west <= lon <= east):
            return skip("outside_nyc")

    # --- nodes: (point, [names]) ---------------------------------------------
    nodes = []
    for item in route:
        if isinstance(item, str):
            if nodes:
                nodes[-1][1].append(item)
        else:
            nodes.append((tuple(item), []))
    n = len(nodes)
    if n < 2:
        raise ValueError("route needs at least 2 points")

    # --- local flat-earth meters around the bus ------------------------------
    kx, ky = 111_320 * math.cos(math.radians(lat)), 110_540
    m = lambda p: (p[0] * kx, p[1] * ky)
    bus = (lon, lat)

    def project(p, a, b):
        px, py = m(p); ax, ay = m(a); bx, by = m(b)
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy
        t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
        d = math.hypot(px - (ax + t * dx), py - (ay + t * dy))
        snapped = (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))
        return d, snapped

    # --- 1. candidate segments -----------------------------------------------
    cands = []
    for i in range(n - 1):
        a, b = nodes[i][0], nodes[i + 1][0]
        ax, ay = m(a); bx, by = m(b)
        if math.hypot(bx - ax, by - ay) < 0.01:      # zero-length segment
            continue
        d, snapped = project(bus, a, b)
        cands.append((d, i, snapped))
    if not cands:
        raise ValueError("route has no usable segments")
    dmin = min(c[0] for c in cands)
    if dmin > max_dist_m:
        return skip("too_far_from_route")

    # --- 2. pick the closest segment -----------------------------------------
    d, i, snap = min(cands, key=lambda candidate: (candidate[0], candidate[1]))

    # --- 3. always move forward along the list -------------------------------
    step, idx = 1, i + 1



    # --- 4. walk to the next station -----------------------------------------
    path = [snap]
    station = None
    sx, sy = m(snap)

    for k in range(n + 1):   # n + 1 so a full lap can return to the bus's own stop
        if loop:
            if idx >= n:
                path.append("LOOP")
                idx %= n
        elif not 0 <= idx < n:
            break

        pt, names = nodes[idx]
        px, py = m(pt)

        if not (k == 0 and math.hypot(px - sx, py - sy) < eps_m):
            if pt != path[-1]:
                path.append(pt)

            if names:
                path.append("STOP")
                station = names[0]
                break

        idx += step

    if return_info:
        return path, {
            "segment": (i, i + 1),
            "direction": "forward",
            "heading_diff_deg": None,
            "dist_to_line_m": d,
            "station": station,
        }

    return path