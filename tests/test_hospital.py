"""
Unit Tests untuk Nearby Hospital Service
"""
import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from src.services.hospital_service import NearbyHospitalService

def test_haversine_distance():
    # Koordinat Monas (-6.1754, 106.8272) ke Bundaran HI (-6.1950, 106.8230) ~2.2 km
    dist = NearbyHospitalService.haversine(-6.1754, 106.8272, -6.1950, 106.8230)
    assert 2.0 <= dist <= 2.5

def test_find_nearby_facilities_fallback_or_api():
    service = NearbyHospitalService()
    facilities = service.find_nearby_facilities(-6.9740, 107.6303, radius_km=5.0)
    assert len(facilities) > 0
    first = facilities[0]
    assert hasattr(first, "name")
    assert hasattr(first, "distance_km")
    assert hasattr(first, "maps_url")
    assert "google.com/maps" in first.maps_url

if __name__ == "__main__":
    test_haversine_distance()
    test_find_nearby_facilities_fallback_or_api()
    print("All Hospital Tests PASSED successfully!")
