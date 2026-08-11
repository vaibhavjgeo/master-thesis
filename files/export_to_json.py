"""
========================================================================
EXPORT BHE MODEL RESULTS TO JSON FOR THE WEBSITE'S LIVE EXPLORER
========================================================================

This is a ONE-TIME script. Run it after running the notebook to export
all model outputs as compact JSON files for the website.

USAGE:
    1. Place this script in the same folder as your notebook & TIFFs
    2. Open Jupyter (or just python), run all notebook cells first
       so all variables (BBC_ssp245, CanESM_ssp245, etc.) are loaded
    3. Then in the same kernel, run this script:
         exec(open('export_to_json.py').read())
       OR copy-paste the code into a new notebook cell at the end

OUTPUT:
    Creates a 'data_json/' folder with:
        individual/
            BBC_ssp245.json   (~70 KB each)
            BBC_ssp585.json
            ... 16 total
        ensemble/
            ssp245_mean.json  (~70 KB each)
            ssp245_p25.json
            ... 8 total
        meta.json             (extent, dimensions, fixed value ranges)

Total output: ~1.7 MB
Runtime: ~30 seconds (just data export, no modeling)
========================================================================
"""

import os
import json
import numpy as np

# Make output folders
os.makedirs('data_json/individual', exist_ok=True)
os.makedirs('data_json/ensemble', exist_ok=True)


def array_to_compact_list(arr):
    """Convert a 2D numpy array to a list with NaN as null, rounded to 2 decimals."""
    # Round to 2 decimals to keep file size small
    arr_rounded = np.round(arr, 2)
    # Convert to nested list, replace NaN with None for JSON
    result = []
    for row in arr_rounded:
        row_list = []
        for v in row:
            if np.isnan(v):
                row_list.append(None)
            else:
                row_list.append(float(v))
        result.append(row_list)
    return result


def export_individual(name, results_dict):
    """Export one model+scenario as compact JSON with all 6 layers."""
    
    # The 6 layers (matching notebook's panels exactly):
    layers = {
        'ql_Urban_50yr':            results_dict['ql_Urban_map'][:, :, 0],
        'EnerUrb_50yr':             results_dict['EnerUrb_map'][:, :, 0],
        'ql_UrbanRenew_50yr':       results_dict['ql_UrbanRenew_map'][:, :, 0],
        'EnerUrbRenew_50yr':        results_dict['EnerUrbRenew_map'][:, :, 0],
        'ql_UrbanRenew_max_100yr':  results_dict['ql_UrbanRenew_max_map'][:, :, 1],
        'EnerUrbRenew_100yr':       results_dict['EnerUrbRenew_map'][:, :, 1],
    }
    
    # Get extent for georeferencing in browser
    extent = results_dict['extent']  # [xmin, xmax, ymin, ymax]
    
    out = {
        'name': name,
        'extent': {
            'xmin': float(extent[0]),
            'xmax': float(extent[1]),
            'ymin': float(extent[2]),
            'ymax': float(extent[3])
        },
        'shape': {
            'rows': int(layers['ql_Urban_50yr'].shape[0]),
            'cols': int(layers['ql_Urban_50yr'].shape[1])
        },
        'layers': {k: array_to_compact_list(v) for k, v in layers.items()}
    }
    
    out_path = f'data_json/individual/{name}.json'
    with open(out_path, 'w') as f:
        json.dump(out, f, separators=(',', ':'))  # compact, no spaces
    
    file_size_kb = os.path.getsize(out_path) / 1024
    print(f"  OK  {name:20s} -> {out_path}  ({file_size_kb:.1f} KB)")


def export_ensemble(scenario_name, models_list):
    """Export ensemble stats (Mean, P25, P50, P75) for one scenario."""
    
    panels = [
        ('ql_Urban_map', 0, 'ql_Urban_50yr'),
        ('EnerUrb_map', 0, 'EnerUrb_50yr'),
        ('ql_UrbanRenew_map', 0, 'ql_UrbanRenew_50yr'),
        ('EnerUrbRenew_map', 0, 'EnerUrbRenew_50yr'),
        ('ql_UrbanRenew_max_map', 1, 'ql_UrbanRenew_max_100yr'),
        ('EnerUrbRenew_map', 1, 'EnerUrbRenew_100yr'),
    ]
    
    extent = models_list[0]['extent']
    shape = models_list[0]['ql_Urban_map'][:, :, 0].shape
    
    # Compute Mean / P25 / P50 / P75 across the 8 model stack per pixel
    stats = {'mean': {}, 'p25': {}, 'p50': {}, 'p75': {}}
    
    for key, idx, layer_name in panels:
        arrs = [m[key][:, :, idx] for m in models_list]
        stack = np.stack(arrs, axis=0)
        stats['mean'][layer_name] = np.nanmean(stack, axis=0)
        p25, p50, p75 = np.nanpercentile(stack, [25, 50, 75], axis=0)
        stats['p25'][layer_name] = p25
        stats['p50'][layer_name] = p50
        stats['p75'][layer_name] = p75
    
    # Save one file per stat
    for stat_name, layer_dict in stats.items():
        out = {
            'name': f'{scenario_name}_{stat_name}',
            'extent': {
                'xmin': float(extent[0]),
                'xmax': float(extent[1]),
                'ymin': float(extent[2]),
                'ymax': float(extent[3])
            },
            'shape': {'rows': int(shape[0]), 'cols': int(shape[1])},
            'layers': {k: array_to_compact_list(v) for k, v in layer_dict.items()}
        }
        out_path = f'data_json/ensemble/{scenario_name}_{stat_name}.json'
        with open(out_path, 'w') as f:
            json.dump(out, f, separators=(',', ':'))
        
        file_size_kb = os.path.getsize(out_path) / 1024
        print(f"  OK  {scenario_name}_{stat_name:5s}     -> {out_path}  ({file_size_kb:.1f} KB)")


# Save metadata file with fixed color scale ranges
meta = {
    'value_ranges': {
        'ql_min': 2,    'ql_max': 55,    # W/m
        'pwr_min': 100, 'pwr_max': 6000  # W
    },
    'layer_info': {
        'ql_Urban_50yr':           {'unit': 'W/m', 'type': 'heat',  'label': 'Max Heat Extraction Rate (50yr, no sustainable)'},
        'EnerUrb_50yr':            {'unit': 'W',   'type': 'power', 'label': 'Usable Power (50yr)'},
        'ql_UrbanRenew_50yr':      {'unit': 'W/m', 'type': 'heat',  'label': 'Sustainable Heat Extraction Rate (50yr)'},
        'EnerUrbRenew_50yr':       {'unit': 'W',   'type': 'power', 'label': 'Usable Power non-renewable rates'},
        'ql_UrbanRenew_max_100yr': {'unit': 'W/m', 'type': 'heat',  'label': 'Max Sustainable Heat Extraction Rate (100yr)'},
        'EnerUrbRenew_100yr':      {'unit': 'W',   'type': 'power', 'label': 'Usable Power renewable rates (100yr)'},
    }
}
with open('data_json/meta.json', 'w') as f:
    json.dump(meta, f, indent=2)


# Map of variable names (must match what's loaded in the notebook)
all_individual = {
    'BBC_ssp245': 'BBC_ssp245',
    'BBC_ssp585': 'BBC_ssp585',
    'CanESM_ssp245': 'CanESM_ssp245',
    'CanESM_ssp585': 'CanESM_ssp585',
    'GFDL_ssp245': 'GFDL_ssp245',
    'GFDL_ssp585': 'GFDL_ssp585',
    'GISS_ssp245': 'GISS_ssp245',
    'GISS_ssp585': 'GISS_ssp585',
    'HadGEM_ssp245': 'HadGEM_ssp245',
    'HadGEM_ssp585': 'HadGEM_ssp585',
    'IPSL_ssp245': 'IPSL_ssp245',
    'IPSL_ssp585': 'IPSL_ssp585',
    'MIROC_ssp245': 'MIROC_ssp245',
    'MIROC_ssp585': 'MIROC_ssp585',
    'MPI_ssp245': 'MPI_ssp245',
    'MPI_ssp585': 'MPI_ssp585',
}

print("=" * 60)
print("EXPORTING INDIVIDUAL MODEL+SCENARIO RESULTS")
print("=" * 60)

skipped = []
for name, var_name in all_individual.items():
    try:
        results = eval(var_name)  # get the variable from current namespace
        export_individual(name, results)
    except NameError:
        print(f"  SKIP {name:20s} (variable not loaded - run notebook cell first)")
        skipped.append(name)

print()
print("=" * 60)
print("EXPORTING ENSEMBLE STATISTICS")
print("=" * 60)

# Try ssp245 ensemble
try:
    models_245 = [BBC_ssp245, CanESM_ssp245, GFDL_ssp245, GISS_ssp245,
                  HadGEM_ssp245, IPSL_ssp245, MIROC_ssp245, MPI_ssp245]
    export_ensemble('ssp245', models_245)
except NameError as e:
    print(f"  SKIP ssp245 ensemble - missing variable: {e}")

try:
    models_585 = [BBC_ssp585, CanESM_ssp585, GFDL_ssp585, GISS_ssp585,
                  HadGEM_ssp585, IPSL_ssp585, MIROC_ssp585, MPI_ssp585]
    export_ensemble('ssp585', models_585)
except NameError as e:
    print(f"  SKIP ssp585 ensemble - missing variable: {e}")


print()
print("=" * 60)
print("DONE")
print("=" * 60)
print()
total_size = 0
for root, dirs, files in os.walk('data_json'):
    for f in files:
        total_size += os.path.getsize(os.path.join(root, f))
print(f"Total exported: {total_size / 1024:.1f} KB ({total_size / 1024 / 1024:.2f} MB)")
print(f"Folder: data_json/")
print()
if skipped:
    print(f"Skipped {len(skipped)} models (variables not loaded):")
    for s in skipped:
        print(f"  - {s}")
print()
print("NEXT STEPS:")
print("1. Upload the entire 'data_json/' folder to your GitHub repo")
print("   at: thesis/data_json/")
print("2. Refresh the website - live color switching now works!")
