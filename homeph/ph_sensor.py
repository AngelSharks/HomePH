"""pH Sensor module for reading and validating pH values."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class PHReading:
    """Represents a pH reading from a sensor."""
    
    value: float
    timestamp: datetime
    sensor_id: str
    temperature: Optional[float] = None  # Temperature in Celsius for compensation
    
    def is_acidic(self) -> bool:
        """Check if the pH reading indicates acidic conditions (pH < 7)."""
        return self.value < 7.0
    
    def is_alkaline(self) -> bool:
        """Check if the pH reading indicates alkaline/basic conditions (pH > 7)."""
        return self.value > 7.0
    
    def is_neutral(self) -> bool:
        """Check if the pH reading indicates neutral conditions (pH == 7)."""
        return self.value == 7.0
    
    def get_category(self) -> str:
        """Return a human-readable category for the pH value."""
        if self.value < 0 or self.value > 14:
            return "invalid"
        elif self.value < 3:
            return "strongly acidic"
        elif self.value < 6:
            return "acidic"
        elif self.value < 7:
            return "slightly acidic"
        elif self.value == 7:
            return "neutral"
        elif self.value <= 8:
            return "slightly alkaline"
        elif self.value <= 11:
            return "alkaline"
        else:
            return "strongly alkaline"


class PHSensor:
    """Represents a pH sensor device."""
    
    MIN_PH = 0.0
    MAX_PH = 14.0
    
    def __init__(self, sensor_id: str, calibration_offset: float = 0.0):
        """
        Initialize a pH sensor.
        
        Args:
            sensor_id: Unique identifier for the sensor
            calibration_offset: Offset to apply to raw readings for calibration
        """
        self.sensor_id = sensor_id
        self.calibration_offset = calibration_offset
        self._readings: list[PHReading] = []
    
    @staticmethod
    def validate_ph(value: float) -> bool:
        """
        Validate if a pH value is within the valid range (0-14).
        
        Args:
            value: The pH value to validate
            
        Returns:
            True if valid, False otherwise
        """
        return PHSensor.MIN_PH <= value <= PHSensor.MAX_PH
    
    def apply_calibration(self, raw_value: float) -> float:
        """
        Apply calibration offset to a raw pH reading.
        
        Args:
            raw_value: The raw pH value from the sensor
            
        Returns:
            Calibrated pH value, clamped to valid range
        """
        calibrated = raw_value + self.calibration_offset
        return max(self.MIN_PH, min(self.MAX_PH, calibrated))
    
    def record_reading(self, raw_value: float, temperature: Optional[float] = None) -> PHReading:
        """
        Record a new pH reading from the sensor.
        
        Args:
            raw_value: The raw pH value from the sensor
            temperature: Optional temperature for compensation
            
        Returns:
            The recorded PHReading object
            
        Raises:
            ValueError: If the raw value is outside valid pH range
        """
        if not self.validate_ph(raw_value):
            raise ValueError(f"Invalid pH value: {raw_value}. Must be between {self.MIN_PH} and {self.MAX_PH}")
        
        calibrated_value = self.apply_calibration(raw_value)
        reading = PHReading(
            value=calibrated_value,
            timestamp=datetime.now(),
            sensor_id=self.sensor_id,
            temperature=temperature
        )
        self._readings.append(reading)
        return reading
    
    def get_average_ph(self, last_n: Optional[int] = None) -> Optional[float]:
        """
        Calculate the average pH from recorded readings.
        
        Args:
            last_n: If provided, only consider the last n readings
            
        Returns:
            Average pH value, or None if no readings exist
        """
        if not self._readings:
            return None
        
        readings = self._readings[-last_n:] if last_n else self._readings
        return sum(r.value for r in readings) / len(readings)
    
    def get_reading_count(self) -> int:
        """Return the number of recorded readings."""
        return len(self._readings)
    
    def clear_readings(self) -> None:
        """Clear all recorded readings."""
        self._readings.clear()
