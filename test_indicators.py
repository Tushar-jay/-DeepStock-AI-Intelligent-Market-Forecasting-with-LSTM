import pandas as pd
from daily_fetch import compute_indicators

def test_compute_indicators():
    # Dummy data
    dates = pd.date_range('2025-06-01', periods=10)
    df = pd.DataFrame({
        'Date': dates,
        'Close': range(100, 110),
        'Volume': [1000, 2000, 1500, 3000, 500, 800, 1200, 2200, 1700, 1800],
        'Open': range(100, 110),
        'High': range(100, 110),
        'Low': range(100, 110),
    })
    df_ind = compute_indicators(df)

    # Check columns
    assert all(col in df_ind.columns for col in ['Pct_Change','7D_MA_Close','7D_Avg_Volume','Volume_Spike'])

    # Check types
    assert pd.api.types.is_numeric_dtype(df_ind['Pct_Change'])
    assert pd.api.types.is_bool_dtype(df_ind['Volume_Spike'])

    # Test spike logic
    last_vol = df_ind.iloc[-1]['Volume']
    last_avg_vol = df_ind.iloc[-1]['7D_Avg_Volume']
    expected_spike = last_vol > 1.5 * last_avg_vol
    assert df_ind.iloc[-1]['Volume_Spike'] == expected_spike
