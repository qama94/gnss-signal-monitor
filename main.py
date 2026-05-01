import sys, os
sys.path.insert(0, "src")
from data_generator import generate
from signal_monitor import run_monitoring
from visualiser import plot_dashboard
from report_generator import generate_text_report
os.makedirs("results", exist_ok=True)
print("Running Galileo / GPS Signal Quality Monitor...")
print("Using synthetic data calibrated to Galileo E1 OS signal characteristics")
print("")
df = generate(duration_hours=6, inject_events=True)
print("Loaded " + str(len(df)) + " observations | " + str(df["sv"].nunique()) + " SVs | " + str(df["epoch"].nunique()) + " epochs")
print("")
result = run_monitoring(df)
plot_dashboard(df, result, output_dir="results")
generate_text_report(df, result, output_dir="results")
print("")
print("Done! Check the results/ folder:")
print("  monitoring_dashboard.png  - open this to see the plots")
print("  monitoring_report.txt     - structured performance report")
