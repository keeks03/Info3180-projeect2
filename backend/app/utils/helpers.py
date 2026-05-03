import os
import math
from flask import current_app
from werkzeug.utils import secure_filename
from PIL import Image
import uuid


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_profile_picture(file):
    """Save uploaded profile picture, resize and return filename."""
    if not allowed_file(file.filename):
        return None

    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    upload_folder = current_app.config['UPLOAD_FOLDER']
    filepath = os.path.join(upload_folder, filename)

    # Resize to max 400x400 to save space
    img = Image.open(file)
    img.thumbnail((400, 400), Image.LANCZOS)
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    img.save(filepath, optimize=True, quality=85)

    return filename


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two lat/lon points."""
    R = 6371  # Earth's radius in km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def compute_match_score(profile_a, profile_b):
    """
    Compute a compatibility score (0-100) between two profiles.
    Factors: shared interests, age compatibility, distance, gender preference.
    """
    score = 0

    # Shared interests (up to 40 points)
    interests_a = {i.name for i in profile_a.interests}
    interests_b = {i.name for i in profile_b.interests}
    shared = interests_a & interests_b
    total = interests_a | interests_b
    if total:
        score += (len(shared) / len(total)) * 40

    # Age within each other's preference range (up to 30 points)
    age_a = profile_a.age()
    age_b = profile_b.age()
    a_in_b_range = profile_b.min_age_preference <= age_a <= profile_b.max_age_preference
    b_in_a_range = profile_a.min_age_preference <= age_b <= profile_a.max_age_preference
    if a_in_b_range and b_in_a_range:
        score += 30
    elif a_in_b_range or b_in_a_range:
        score += 15

    # Distance score (up to 20 points)
    if (profile_a.latitude and profile_a.longitude and
            profile_b.latitude and profile_b.longitude):
        dist = haversine_distance(
            profile_a.latitude, profile_a.longitude,
            profile_b.latitude, profile_b.longitude
        )
        max_dist = max(profile_a.max_distance_km, profile_b.max_distance_km, 1)
        if dist <= max_dist:
            score += max(0, 20 * (1 - dist / max_dist))

    # Gender preference compatibility (up to 10 points)
    def pref_matches(pref, gender):
        return pref == 'any' or pref == gender

    if pref_matches(profile_a.looking_for, profile_b.gender) and pref_matches(profile_b.looking_for, profile_a.gender):
        score += 10

    return round(score, 1)
