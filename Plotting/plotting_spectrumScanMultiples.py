import os
import glob
import matplotlib.pyplot as plt
import pandas as pd

# Define the directories
data_folder = 'Z:\\Projects\\Defects for QTM\\Raw data\\2025-03-10\\Spectrum Scan\\'
plot_save_path = 'Z:\\Projects\\Defects for QTM\\Processed data\\2025-03-10\\Spectrum Scan\\'
os.makedirs(plot_save_path, exist_ok=True)

# Define the pattern to match Loc files (all datasets are in the same folder)
loc_pattern = os.path.join(data_folder, "Loc_hBNSpectrumScan T=4 K Power=230 uW Exposuretime=*.csv")
loc_files = glob.glob(loc_pattern)

if not loc_files:
    raise FileNotFoundError("No Loc files found in the specified folder.")

# Process each dataset
for loc_file in loc_files:
    # Construct corresponding file names for Spec and Wav files
    spec_file = loc_file.replace("Loc_", "Spec_")
    wav_file = loc_file.replace("Loc_", "Wav_")

    # Check that both corresponding files exist; if not, abort
    if not os.path.exists(spec_file):
        raise FileNotFoundError(f"Spec file corresponding to {loc_file} not found.")
    if not os.path.exists(wav_file):
        raise FileNotFoundError(f"Wav file corresponding to {loc_file} not found.")

    # Load the data from CSV files
    loc_data = pd.read_csv(loc_file)
    spec_data = pd.read_csv(spec_file)
    wav_data = pd.read_csv(wav_file)

    # Convert data to numpy arrays for easier handling
    loc_array = loc_data.values
    spec_array = spec_data.values
    wav_array = wav_data.values

    # Extract the timestamp from the filename (assumes the timestamp comes after 'Exposuretime=')
    base = os.path.basename(loc_file)
    timestamp = base.replace("Loc_hBNSpectrumScan T=4 K Power=65 uW Exposuretime=", "").replace(".csv", "")

    # Iterate through each spectrum and generate/save the plot
    for idx, (x, y) in enumerate(loc_array):
        plt.figure()
        plt.plot(wav_array[idx, :], spec_array[idx, :], label=f"Spectrum at ({x:.2f}, {y:.2f})")
        plt.xlabel("Wavelength (nm)")
        plt.ylabel("Intensity")
        plt.title(f"Spectrum at ({x:.2f}, {y:.2f})")
        plt.legend()
        plt.grid()

        # Create a unique plot filename including the timestamp and coordinates
        plot_filename = f"Spectrum_{timestamp}_{x:.2f}_{y:.2f}.png"
        plt.savefig(os.path.join(plot_save_path, plot_filename))
        plt.close()

    print(f"Plots for dataset with timestamp {timestamp} saved.")

print(f"All spectra plots have been saved in {plot_save_path}")