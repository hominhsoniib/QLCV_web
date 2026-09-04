from PyInstaller.utils.hooks import copy_metadata, collect_submodules, collect_data_files

# Collect Streamlit metadata
datas = copy_metadata('streamlit')

# Collect all Streamlit submodules
hiddenimports = collect_submodules('streamlit')

# Collect Streamlit static data files
datas += collect_data_files('streamlit')
