import math


def clamp(value, minimum, maximum):
	return max(minimum, min(maximum, value))


def distance(point_a, point_b):
	return math.hypot(point_b[0] - point_a[0], point_b[1] - point_a[1])


def normalize_distance_to_midi(value, minimum, maximum):
	if maximum <= minimum:
		return 0

	clamped = clamp(value, minimum, maximum)
	normalized = (clamped - minimum) / float(maximum - minimum)
	return int(round(normalized * 127))


def normalize_vertical_to_midi(y_position, top_limit, bottom_limit):
	if bottom_limit <= top_limit:
		return 0

	clamped = clamp(y_position, top_limit, bottom_limit)
	normalized = (bottom_limit - clamped) / float(bottom_limit - top_limit)
	return int(round(normalized * 127))


def significant_change(previous_value, current_value, threshold):
	if previous_value is None:
		return True

	return abs(current_value - previous_value) >= threshold
