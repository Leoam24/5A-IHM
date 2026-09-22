import math

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def heap_permute(n, order, orders): 
    if n == 1:
        orders.append(list(order)) 
    else:
        for i in range(n):
            heap_permute(n - 1, order, orders) 
            if n % 2 != 0:
                order[0], order[n - 1] = order[n - 1], order[0] 
            else:
                order[i], order[n - 1] = order[n - 1], order[i] 

def make_unistrokes(strokes): 
    orders = []
    heap_permute(len(strokes), list(range(len(strokes))), orders) 
    unistrokes = []
    for order in orders: 
        for b in range(2 ** len(strokes)): 
            unistroke = []
            for i in range(len(order)): 
                if (b >> i) & 1 == 1: 
                    unistroke.extend(reversed(strokes[order[i]])) 
                else:
                    unistroke.extend(strokes[order[i]]) 
            unistrokes.append(unistroke) 
    return unistrokes 

def combine_strokes(strokes): 
    points = []
    for stroke in strokes: 
        points.extend(stroke) 
    return points 

def resample(points, n): 
    I = path_length(points) / (n - 1) 
    D = 0.0 
    new_points = [points[0]] 
    i = 1
    while i < len(points):
        d = distance(points[i - 1], points[i]) 
        if (D + d) >= I: 
            qx = points[i - 1].x + ((I - D) / d) * (points[i].x - points[i - 1].x) 
            qy = points[i - 1].y + ((I - D) / d) * (points[i].y - points[i - 1].y) 
            q = Point(qx, qy) 
            new_points.append(q) 
            points.insert(i, q) 
            D = 0.0 
        else:
            D += d 
        i += 1
    if len(new_points) == n - 1:
        new_points.append(points[-1])
    return new_points 

def indicative_angle(points): 
    c = centroid(points) 
    return math.atan2(c.y - points[0].y, c.x - points[0].x) 

def rotate_by(points, omega): 
    c = centroid(points) 
    new_points = []
    for p in points: 
        qx = (p.x - c.x) * math.cos(omega) - (p.y - c.y) * math.sin(omega) + c.x 
        qy = (p.x - c.x) * math.sin(omega) + (p.y - c.y) * math.cos(omega) + c.y 
        new_points.append(Point(qx, qy)) 
    return new_points 

def bounding_box(points): 
    min_x, max_x = float('inf'), float('-inf')
    min_y, max_y = float('inf'), float('-inf')
    for p in points: 
        min_x, max_x = min(min_x, p.x), max(max_x, p.x)
        min_y, max_y = min(min_y, p.y), max(max_y, p.y)
    return min_x, min_y, max_x - min_x, max_y - min_y 

def scale_dim_to(points, size, threshold=0.30): 
    _, _, b_width, b_height = bounding_box(points) 
    new_points = []
    uniform = False
    if b_width > 0 and b_height > 0:
        uniform = min(b_width / b_height, b_height / b_width) <= threshold 
    
    for p in points: 
        if uniform: 
            qx = p.x * size / max(b_width, b_height) 
            qy = p.y * size / max(b_width, b_height) 
        else: 
            qx = p.x * size / b_width if b_width != 0 else p.x 
            qy = p.y * size / b_height if b_height != 0 else p.y 
        new_points.append(Point(qx, qy)) 
    return new_points 

def translate_to(points, kx, ky): 
    c = centroid(points) 
    new_points = []
    for p in points: 
        new_points.append(Point(p.x + kx - c.x, p.y + ky - c.y)) 
    return new_points 

def calc_start_unit_vector(points, index): 
    qx = points[index].x - points[0].x 
    qy = points[index].y - points[0].y 
    length = math.sqrt(qx**2 + qy**2) 
    if length == 0: return (0, 0)
    return (qx / length, qy / length) 

def angle_between_vectors(v1, v2): 
    val = v1[0]*v2[0] + v1[1]*v2[1]
    val = max(-1.0, min(1.0, val))
    return math.acos(val) 

def distance_at_angle(points, t_points, theta): 
    new_points = rotate_by(points, theta) 
    return path_distance(new_points, t_points) 

def distance_at_best_angle(points, t_points, a, b, threshold): 
    phi = 0.5 * (-1.0 + math.sqrt(5.0)) 
    x1 = phi * a + (1.0 - phi) * b 
    f1 = distance_at_angle(points, t_points, x1) 
    x2 = (1.0 - phi) * a + phi * b 
    f2 = distance_at_angle(points, t_points, x2) 
    
    while abs(b - a) > threshold: 
        if f1 < f2: 
            b, x2, f2 = x2, x1, f1 
            x1 = phi * a + (1.0 - phi) * b 
            f1 = distance_at_angle(points, t_points, x1) 
        else: 
            a, x1, f1 = x1, x2, f2 
            x2 = (1.0 - phi) * a + phi * b 
            f2 = distance_at_angle(points, t_points, x2) 
    return min(f1, f2) 

def path_distance(pts1, pts2): 
    d = 0.0 
    for i in range(min(len(pts1), len(pts2))): 
        d += distance(pts1[i], pts2[i]) 
    return d / len(pts1) 

def path_length(points): 
    d = 0.0 
    for i in range(1, len(points)): 
        d += distance(points[i - 1], points[i]) 
    return d 

def distance(p1, p2): 
    return math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2) 

def centroid(points): 
    x = sum(p.x for p in points) / len(points) 
    y = sum(p.y for p in points) / len(points) 
    return Point(x, y) 

class MultistrokeTemplate:
    def __init__(self, name, strokes, num_points=96, size=250.0):
        self.name = name
        raw_unistrokes = make_unistrokes(strokes) 
        self.processed_unistrokes = []
        for u in raw_unistrokes: 
            pts = resample(u, num_points) 
            omega = indicative_angle(pts) 
            pts = rotate_by(pts, -omega) 
            pts = scale_dim_to(pts, size, 0.30) 
            pts = rotate_by(pts, omega) 
            pts = translate_to(pts, 0, 0) 
            start_v = calc_start_unit_vector(pts, 12) 
            self.processed_unistrokes.append({"points": pts, "vector": start_v})

class NDollarRecognizer:
    def __init__(self):
        self.templates = []
        self.num_points = 96 
        self.size = 250.0 
        self.half_diagonal = 0.5 * math.sqrt(self.size**2 + self.size**2) 

    def add_template(self, name, strokes):
        self.templates.append(MultistrokeTemplate(name, strokes, self.num_points, self.size))

    def recognize(self, candidate_strokes):
        if not candidate_strokes or not self.templates:
            return "Aucun", 0.0

        pts = combine_strokes(candidate_strokes) 
        pts = resample(pts, self.num_points) 
        omega = indicative_angle(pts) 
        pts = rotate_by(pts, -omega) 
        pts = scale_dim_to(pts, self.size, 0.30) 
        pts = rotate_by(pts, omega) 
        pts = translate_to(pts, 0, 0) 
        start_v = calc_start_unit_vector(pts, 12) 

        best_distance = float("infinity")
        best_name = "Inconnu"
        phi_threshold = math.radians(30) 
        angle_range = math.radians(45) 
        angle_precision = math.radians(2) 

        for template in self.templates: 
            for u in template.processed_unistrokes: 
                if angle_between_vectors(start_v, u["vector"]) <= phi_threshold: 
                    dist = distance_at_best_angle(pts, u["points"], -angle_range, angle_range, angle_precision) 
                    if dist < best_distance: 
                        best_distance = dist 
                        best_name = template.name 

        score = 1.0 - (best_distance / self.half_diagonal) if best_distance != float("infinity") else 0.0 
        return best_name, max(0.0, score)