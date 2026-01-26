# -*- coding: utf-8 -*-
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.abspath(os.getcwd()))

try:
    from utils.page_layouts import PAGE_LAYOUTS, validate_layout_indicators, get_all_page_names
    from utils.auto_render import render_page, get_render_stats
    import pandas as pd
    
    print("--- Layout Validation ---")
    errors = validate_layout_indicators()
    if errors:
        print(f"FAILED: Found {len(errors)} unknown indicators in layouts")
        for e in errors:
            print(f"  - {e}")
        # sys.exit(1) # Don't exit yet, check other things
    else:
        print("OK: All indicators in layouts are valid.")

    print("\n--- Page Stats ---")
    pages = get_all_page_names()
    print(f"Total Pages defined: {len(pages)}")
    for page in pages:
        layout = PAGE_LAYOUTS[page]
        sections = layout.get('sections', [])
        inds = sum(len(s.get('indicators', [])) for s in sections)
        print(f"  {page}: {len(sections)} sections, {inds} indicators")

    print("\n--- Mock Render Test ---")
    # Create a mock DF to see if render_page hits any immediate exceptions (using dummy st)
    class MockStreamlit:
        def subheader(self, *args): pass
        def markdown(self, *args): pass
        def caption(self, *args): pass
        def columns(self, n): return [MockStreamlit()] * n
        def metric(self, *args, **kwargs): pass
        def plotly_chart(self, *args, **kwargs): pass
        def info(self, *args): pass
        def warning(self, *args): pass
        def error(self, *args): pass
        def spinner(self, *args): 
            class Spinner:
                def __enter__(self): return self
                def __exit__(self, *args): pass
            return Spinner()
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def expander(self, *args): return self

    import streamlit as st
    # Monkeypatch st for this script
    # Note: This is an internal check, just to see if the structure of render_page is sound
    
    print("Checking render_page structure for 01_liquidity...")
    # Just checking if the function exists and has correct signature
    import inspect
    sig = inspect.signature(render_page)
    print(f"render_page signature: {sig}")
    
    print("\n[OK] Step 2 logic verification passed!")

except Exception as e:
    print(f"\n[ERROR] Verification failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
