from pydantic import BaseModel


class FRAFeatures(BaseModel):
    mean_mag: float
    std_mag: float
    min_mag: float
    max_mag: float
    low_mean: float
    mid_mean: float
    high_mean: float
    peak_freq: float
    peak_mag: float
    slope: float


class GasData(BaseModel):
    H2: float
    CO: float
    C2H4: float
    C2H2: float
    rul: float


class PredictionRequest(BaseModel):
    fra_features: FRAFeatures
    gas_data: GasData