"""Tests for the pH sensor module."""

import pytest
from datetime import datetime

from homeph.ph_sensor import PHSensor, PHReading


class TestPHReading:
    """Tests for the PHReading dataclass."""
    
    def test_is_acidic_returns_true_for_low_ph(self):
        reading = PHReading(value=3.5, timestamp=datetime.now(), sensor_id="test")
        assert reading.is_acidic() is True
    
    def test_is_acidic_returns_false_for_high_ph(self):
        reading = PHReading(value=8.0, timestamp=datetime.now(), sensor_id="test")
        assert reading.is_acidic() is False
    
    def test_is_acidic_returns_false_for_neutral_ph(self):
        reading = PHReading(value=7.0, timestamp=datetime.now(), sensor_id="test")
        assert reading.is_acidic() is False
    
    def test_is_alkaline_returns_true_for_high_ph(self):
        reading = PHReading(value=9.0, timestamp=datetime.now(), sensor_id="test")
        assert reading.is_alkaline() is True
    
    def test_is_alkaline_returns_false_for_low_ph(self):
        reading = PHReading(value=5.0, timestamp=datetime.now(), sensor_id="test")
        assert reading.is_alkaline() is False
    
    def test_is_alkaline_returns_false_for_neutral_ph(self):
        reading = PHReading(value=7.0, timestamp=datetime.now(), sensor_id="test")
        assert reading.is_alkaline() is False
    
    def test_is_neutral_returns_true_for_ph_7(self):
        reading = PHReading(value=7.0, timestamp=datetime.now(), sensor_id="test")
        assert reading.is_neutral() is True
    
    def test_is_neutral_returns_false_for_non_7_ph(self):
        reading = PHReading(value=6.9, timestamp=datetime.now(), sensor_id="test")
        assert reading.is_neutral() is False
    
    def test_get_category_strongly_acidic(self):
        reading = PHReading(value=1.5, timestamp=datetime.now(), sensor_id="test")
        assert reading.get_category() == "strongly acidic"
    
    def test_get_category_acidic(self):
        reading = PHReading(value=4.0, timestamp=datetime.now(), sensor_id="test")
        assert reading.get_category() == "acidic"
    
    def test_get_category_slightly_acidic(self):
        reading = PHReading(value=6.5, timestamp=datetime.now(), sensor_id="test")
        assert reading.get_category() == "slightly acidic"
    
    def test_get_category_neutral(self):
        reading = PHReading(value=7.0, timestamp=datetime.now(), sensor_id="test")
        assert reading.get_category() == "neutral"
    
    def test_get_category_slightly_alkaline(self):
        reading = PHReading(value=7.5, timestamp=datetime.now(), sensor_id="test")
        assert reading.get_category() == "slightly alkaline"
    
    def test_get_category_alkaline(self):
        reading = PHReading(value=10.0, timestamp=datetime.now(), sensor_id="test")
        assert reading.get_category() == "alkaline"
    
    def test_get_category_strongly_alkaline(self):
        reading = PHReading(value=13.0, timestamp=datetime.now(), sensor_id="test")
        assert reading.get_category() == "strongly alkaline"
    
    def test_get_category_invalid_negative(self):
        reading = PHReading(value=-1.0, timestamp=datetime.now(), sensor_id="test")
        assert reading.get_category() == "invalid"
    
    def test_get_category_invalid_above_14(self):
        reading = PHReading(value=15.0, timestamp=datetime.now(), sensor_id="test")
        assert reading.get_category() == "invalid"
    
    def test_reading_with_temperature(self):
        reading = PHReading(value=7.0, timestamp=datetime.now(), sensor_id="test", temperature=25.0)
        assert reading.temperature == 25.0


class TestPHSensor:
    """Tests for the PHSensor class."""
    
    def test_sensor_initialization(self):
        sensor = PHSensor(sensor_id="sensor-001")
        assert sensor.sensor_id == "sensor-001"
        assert sensor.calibration_offset == 0.0
    
    def test_sensor_initialization_with_calibration(self):
        sensor = PHSensor(sensor_id="sensor-001", calibration_offset=0.5)
        assert sensor.calibration_offset == 0.5
    
    def test_validate_ph_valid_values(self):
        assert PHSensor.validate_ph(0.0) is True
        assert PHSensor.validate_ph(7.0) is True
        assert PHSensor.validate_ph(14.0) is True
        assert PHSensor.validate_ph(3.5) is True
    
    def test_validate_ph_invalid_values(self):
        assert PHSensor.validate_ph(-0.1) is False
        assert PHSensor.validate_ph(14.1) is False
        assert PHSensor.validate_ph(-5.0) is False
        assert PHSensor.validate_ph(20.0) is False
    
    def test_apply_calibration_no_offset(self):
        sensor = PHSensor(sensor_id="test", calibration_offset=0.0)
        assert sensor.apply_calibration(7.0) == 7.0
    
    def test_apply_calibration_positive_offset(self):
        sensor = PHSensor(sensor_id="test", calibration_offset=0.5)
        assert sensor.apply_calibration(7.0) == 7.5
    
    def test_apply_calibration_negative_offset(self):
        sensor = PHSensor(sensor_id="test", calibration_offset=-0.3)
        assert sensor.apply_calibration(7.0) == 6.7
    
    def test_apply_calibration_clamps_to_max(self):
        sensor = PHSensor(sensor_id="test", calibration_offset=2.0)
        assert sensor.apply_calibration(13.5) == 14.0
    
    def test_apply_calibration_clamps_to_min(self):
        sensor = PHSensor(sensor_id="test", calibration_offset=-2.0)
        assert sensor.apply_calibration(1.0) == 0.0
    
    def test_record_reading_valid(self):
        sensor = PHSensor(sensor_id="test")
        reading = sensor.record_reading(7.0)
        assert reading.value == 7.0
        assert reading.sensor_id == "test"
        assert sensor.get_reading_count() == 1
    
    def test_record_reading_with_temperature(self):
        sensor = PHSensor(sensor_id="test")
        reading = sensor.record_reading(7.0, temperature=25.0)
        assert reading.temperature == 25.0
    
    def test_record_reading_invalid_raises_error(self):
        sensor = PHSensor(sensor_id="test")
        with pytest.raises(ValueError, match="Invalid pH value"):
            sensor.record_reading(-1.0)
    
    def test_record_reading_invalid_high_raises_error(self):
        sensor = PHSensor(sensor_id="test")
        with pytest.raises(ValueError, match="Invalid pH value"):
            sensor.record_reading(15.0)
    
    def test_get_average_ph_no_readings(self):
        sensor = PHSensor(sensor_id="test")
        assert sensor.get_average_ph() is None
    
    def test_get_average_ph_single_reading(self):
        sensor = PHSensor(sensor_id="test")
        sensor.record_reading(7.0)
        assert sensor.get_average_ph() == 7.0
    
    def test_get_average_ph_multiple_readings(self):
        sensor = PHSensor(sensor_id="test")
        sensor.record_reading(6.0)
        sensor.record_reading(7.0)
        sensor.record_reading(8.0)
        assert sensor.get_average_ph() == 7.0
    
    def test_get_average_ph_last_n(self):
        sensor = PHSensor(sensor_id="test")
        sensor.record_reading(5.0)
        sensor.record_reading(6.0)
        sensor.record_reading(7.0)
        sensor.record_reading(8.0)
        assert sensor.get_average_ph(last_n=2) == 7.5
    
    def test_clear_readings(self):
        sensor = PHSensor(sensor_id="test")
        sensor.record_reading(7.0)
        sensor.record_reading(7.5)
        assert sensor.get_reading_count() == 2
        sensor.clear_readings()
        assert sensor.get_reading_count() == 0
