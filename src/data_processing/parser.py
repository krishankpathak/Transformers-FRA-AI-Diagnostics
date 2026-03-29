import pandas as pd
import numpy as np
import os
import json
from typing import Optional, Tuple, List
from pathlib import Path

# =========================
# CONFIG
# =========================
FREQ_START = 20
FREQ_END = 2_000_000
NUM_POINTS = 500

class UniversalFRAParser:
    def __init__(self):
        self.freq_grid = np.logspace(np.log10(FREQ_START), np.log10(FREQ_END), NUM_POINTS)

    def interpolate_data(self, freq: np.ndarray, mag: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Interpolates raw sweep data to a standard 500-point log grid.
        """
        # Ensure data is sorted by frequency
        idx = np.argsort(freq)
        freq_sorted = freq[idx]
        mag_sorted = mag[idx]
        
        # Log-linear interpolation
        mag_interp = np.interp(self.freq_grid, freq_sorted, mag_sorted)
        return self.freq_grid, mag_interp

    def parse_csv(self, file_path: str) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """
        Robust CSV parser that handles various delimiters, encodings, and headers.
        """
        try:
            strategies = [
                {'sep': ',', 'encoding': 'utf-8', 'skiprows': 0},
                {'sep': ';', 'encoding': 'latin1', 'skiprows': 0},
                {'sep': ',', 'encoding': 'utf-8', 'skiprows': 1},
                {'sep': ';', 'encoding': 'latin1', 'skiprows': 1},
                {'sep': '\t', 'encoding': 'utf-16', 'skiprows': 0},
            ]
            
            df = None
            for strategy in strategies:
                try:
                    df = pd.read_csv(file_path, **strategy)
                    if df.shape[1] >= 2 and df.shape[0] > 5:
                        f_col = None
                        m_col = None
                        
                        for col in df.columns:
                            col_lower = str(col).lower()
                            if any(x in col_lower for x in ['freq', 'hz']): f_col = col
                            if any(x in col_lower for x in ['mag', 'db', 'gain']): m_col = col
                        
                        if f_col is not None and m_col is not None:
                            df[f_col] = pd.to_numeric(df[f_col], errors='coerce')
                            df[m_col] = pd.to_numeric(df[m_col], errors='coerce')
                            df = df.dropna(subset=[f_col, m_col])
                            if not df.empty:
                                return self.interpolate_data(df[f_col].to_numpy(), df[m_col].to_numpy())
                except:
                    continue

            if df is not None:
                numeric_df = df.select_dtypes(include=[np.number])
                if numeric_df.shape[1] >= 2:
                    return self.interpolate_data(numeric_df.iloc[:, 0].to_numpy(), numeric_df.iloc[:, 1].to_numpy())
            
            return None
        except Exception as e:
            print(f"[ERROR] CSV parse error: {e}")
            return None

    def parse_excel(self, file_path: str) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        try:
            df = pd.read_excel(file_path)
            f_col = None
            m_col = None
            for col in df.columns:
                col_lower = str(col).lower()
                if any(x in col_lower for x in ['freq', 'hz']): f_col = col
                if any(x in col_lower for x in ['mag', 'db', 'gain']): m_col = col
            
            if f_col is not None and m_col is not None:
                df[f_col] = pd.to_numeric(df[f_col], errors='coerce')
                df[m_col] = pd.to_numeric(df[m_col], errors='coerce')
                df = df.dropna(subset=[f_col, m_col])
                if not df.empty:
                    return self.interpolate_data(df[f_col].to_numpy(), df[m_col].to_numpy())
            return None
        except Exception as e:
            print(f"[ERROR] Excel parse error: {e}")
            return None

    def parse_json(self, file_path: str) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            if isinstance(data, dict):
                if 'frequency' in data and 'magnitude' in data:
                    return self.interpolate_data(np.array(data['frequency']), np.array(data['magnitude']))
            return None
        except Exception as e:
            print(f"[ERROR] JSON parse error: {e}")
            return None

    def parse_file(self, file_path: str) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.csv': return self.parse_csv(file_path)
        elif ext in ['.xlsx', '.xls']: return self.parse_excel(file_path)
        elif ext == '.json': return self.parse_json(file_path)
        return None

def get_universal_parser():
    return UniversalFRAParser()
