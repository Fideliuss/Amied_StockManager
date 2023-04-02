import PyInstaller.__main__
import StockM_UI

PyInstaller.__main__.run([
    'StockM_UI.py',
    '--windowed',
    '--add-data=icon/Logo_GB_2015.ico;icon/',
    '--add-data=saves/tree_save.json;saves/',
    '--add-data=theme/forest-light/*;theme/forest-light',
    '--add-data=theme/forest-light.tcl;theme/',
    '--icon=icon/logo_amiedition_resize.ico',
    f'--name=Amiedtions S_Manager {StockM_UI.StockUI.VERSION}'
])
