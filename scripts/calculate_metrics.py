import json
import pandas as pd
from datetime import datetime, timedelta
import os
import matplotlib.pyplot as plt

os.makedirs("metrics", exist_ok=True)

# Cargar issues
with open("metrics/issues.json") as f:
    issues = json.load(f)

rows = []
for issue in issues:
    if "pull_request" in issue:
        continue
    created = datetime.strptime(issue["created_at"], "%Y-%m-%dT%H:%M:%SZ")
    closed = None
    if issue["closed_at"]:
        closed = datetime.strptime(issue["closed_at"], "%Y-%m-%dT%H:%M:%SZ")
    rows.append({
        "id": issue["number"],
        "title": issue["title"],
        "created": created,
        "closed": closed,
        "duration_days": (closed - created).days if closed else None
    })

df = pd.DataFrame(rows)
df.to_csv("metrics/issues_table.csv", index=False)

# Métricas básicas
velocity = df[df["closed"].notnull()].shape[0]
lead_time = df["duration_days"].mean()

with open("metrics/summary.txt", "w") as f:
    f.write("=== SCRUM METRICS ===\n")
    f.write(f"Velocidad (issues cerrados): {velocity}\n")
    f.write(f"Lead time promedio (días): {lead_time:.2f}\n")

# Gráfico de Lead Time
df_closed = df[df["closed"].notnull()]
plt.figure(figsize=(8,5))
plt.bar(df_closed["id"].astype(str), df_closed["duration_days"], color='skyblue')
plt.xlabel("ID de Issue")
plt.ylabel("Días para cerrar")
plt.title("Lead Time por Issue")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("metrics/lead_time.png")
plt.close()

# Burndown Chart histórico
if not df.empty:
    start_date = df["created"].min().date()
    end_date = df["closed"].max().date() if df["closed"].notnull().any() else datetime.utcnow().date()
    date_range = pd.date_range(start=start_date, end=end_date)

    burndown = pd.Series(0, index=date_range)

    for _, row in df.iterrows():
        created = row["created"].date()
        if pd.notnull(row["closed"]):
            closed = row["closed"].date()
            closed_effective = closed - pd.Timedelta(days=1)
        else:
            closed_effective = end_date  # sigue abierto

        burndown[created : closed_effective] += 1

    plt.figure(figsize=(10,5))
    plt.plot(burndown.index, burndown.values, marker='o', color='red')
    plt.xlabel("Fecha")
    plt.ylabel("Issues abiertos")
    plt.title("Burndown Chart Histórico")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("metrics/burndown.png")
    plt.close()

