import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

# Generate messy synthetic data
data = {
    "event_ts": ["2026-05-01T10:00:00Z", "05/01/2026 10:05", "2026-05-01 10:10:00", np.nan, "2026-05-01T10:15:00Z"],
    "user_id": ["u101", "u102", "u101", "u103", "u104"],
    "session_id": ["s1", "s2", "s1", "s3", "s4"],
    "url_path": ["/home", "/products?id=123", "/checkout", "/home", "/about"],
    "http_status": ["200", "404", "invalid", "500", np.nan],
    "response_ms": [150, 45, -500, 75000, 1200],
    "country": ["  US ", "uk", "Us", "CaNAdA", "FR "],
    "device_type": [" MOBILE ", "desktop", "TaBlet", "mobile", "  "],
    "extra_param1": ["dropme"] * 5,
    "extra_param2": ["ignore"] * 5
}
df = pd.DataFrame(data)

# Add 1000 more random rows for scale
np.random.seed(42)
extra_rows = 1000
dates = [datetime(2026, 5, 2) + timedelta(minutes=int(x)) for x in np.random.randint(0, 1440, extra_rows)]
extra_df = pd.DataFrame({
    "event_ts": [d.strftime("%Y-%m-%dT%H:%M:%SZ") for d in dates],
    "user_id": [f"u{x}" for x in np.random.randint(100, 500, extra_rows)],
    "session_id": [f"s{x}" for x in np.random.randint(1, 1000, extra_rows)],
    "url_path": np.random.choice(["/home", "/login", "/checkout", "/products", "/contact"], extra_rows),
    "http_status": np.random.choice(["200", "201", "301", "400", "404", "500"], extra_rows, p=[0.7, 0.05, 0.05, 0.05, 0.1, 0.05]),
    "response_ms": np.random.randint(50, 3000, extra_rows),
    "country": np.random.choice(["US", "UK", "CA", "FR", "IN"], extra_rows),
    "device_type": np.random.choice(["mobile", "desktop", "tablet"], extra_rows),
    "extra_param1": ["x"] * extra_rows,
    "extra_param2": ["y"] * extra_rows
})

df = pd.concat([df, extra_df], ignore_index=True)
output_path = Path("messy_logs_batch1.csv")
df.to_csv(output_path, index=False)
print(f"File generated: {output_path}")