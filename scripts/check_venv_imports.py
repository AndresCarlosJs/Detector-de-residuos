import importlib, sys
mods = ['cv2','torch','flask','PIL','ultralytics','fpdf']
failed = []
for m in mods:
    try:
        importlib.import_module(m)
        print(f'{m} OK')
    except Exception as e:
        print(f'{m} FAIL: {e}')
        failed.append(m)
print(f"Summary: {len(failed)} modules failed: {failed}")
# exit non-zero if any failed
sys.exit(0 if not failed else 1)
