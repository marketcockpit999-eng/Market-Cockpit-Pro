# -*- coding: utf-8 -*-
"""
Phase 3.5 Unit Tests - Element Composition Detection
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.display_checker import (
    parse_function_call,
    _parse_args_string,
    _smart_split,
    check_element_warnings,
    ELEMENT_WARNINGS,
)


def test_smart_split():
    """Test comma splitting with nested structures"""
    print("\n=== test_smart_split ===")
    
    # Simple case
    result = _smart_split("a, b, c")
    assert result == ['a', ' b', ' c'], f"Failed: {result}"
    print("[OK] Simple split")
    
    # With strings
    result = _smart_split("label, 'KEY', value")
    assert len(result) == 3, f"Failed: {result}"
    print("[OK] String split")
    
    # With nested parentheses
    result = _smart_split("func(a, b), c")
    assert len(result) == 2, f"Failed: {result}"
    print("[OK] Nested parentheses")
    
    # With keyword args
    result = _smart_split("a, b, key='value'")
    assert len(result) == 3, f"Failed: {result}"
    print("[OK] Keyword args")


def test_parse_args_string():
    """Test argument parsing"""
    print("\n=== test_parse_args_string ===")
    
    # Positional only
    result = _parse_args_string("label, series, 'EFFR'")
    assert result['pos_0'] == 'label', f"Failed: {result}"
    assert result['pos_2'] == "'EFFR'", f"Failed: {result}"
    print("[OK] Positional args")
    
    # With keyword args
    result = _parse_args_string("label, series, 'KEY', explanation_key=''")
    assert result['explanation_key'] == "''", f"Failed: {result}"
    print("[OK] Keyword args")
    
    # Mixed
    result = _parse_args_string("label, series, 'KEY', notes='test', decimal_places=2")
    assert result['notes'] == "'test'", f"Failed: {result}"
    assert result['decimal_places'] == '2', f"Failed: {result}"
    print("[OK] Mixed args")


def test_parse_function_call():
    """Test full function parsing"""
    print("\n=== test_parse_function_call ===")
    
    # Standard call
    content = """
    show_metric_with_sparkline(t('ind_EFFR'), df.get('EFFR'), 'EFFR')
    """
    result = parse_function_call(content, 'show_metric_with_sparkline')
    assert len(result) == 1, f"Failed: {result}"
    assert result[0]['key'] == 'EFFR', f"Failed: {result}"
    print("[OK] Standard call")
    
    # Call with keyword args
    content = """
    show_metric_with_sparkline(
        t('ind_EFFR'),
        df.get('EFFR'),
        'EFFR',
        explanation_key='',
        notes='test'
    )
    """
    result = parse_function_call(content, 'show_metric_with_sparkline')
    assert len(result) == 1, f"Failed: {result}"
    assert result[0]['kwargs'].get('explanation_key') == "''", f"Failed: {result}"
    print("[OK] Call with kwargs")
    
    # Multiple calls
    content = """
    show_metric_with_sparkline(t('a'), df.get('A'), 'A')
    show_metric_with_sparkline(t('b'), df.get('B'), 'B', notes='')
    """
    result = parse_function_call(content, 'show_metric_with_sparkline')
    assert len(result) == 2, f"Failed: {result}"
    print("[OK] Multiple calls")


def test_check_element_warnings():
    """Test warning detection"""
    print("\n=== test_check_element_warnings ===")
    
    # Empty explanation_key
    kwargs = {'explanation_key': "''"}
    warnings = check_element_warnings('show_metric_with_sparkline', kwargs)
    assert len(warnings) == 1, f"Failed: {warnings}"
    assert warnings[0]['severity'] == 'WARN', f"Failed: {warnings}"
    print("[OK] Empty explanation_key detected")
    
    # Empty notes (INFO level)
    kwargs = {'notes': "''"}
    warnings = check_element_warnings('show_metric_with_sparkline', kwargs)
    assert len(warnings) == 1, f"Failed: {warnings}"
    assert warnings[0]['severity'] == 'INFO', f"Failed: {warnings}"
    print("[OK] Empty notes detected")
    
    # show_level=False
    kwargs = {'show_level': 'False'}
    warnings = check_element_warnings('display_macro_card', kwargs)
    assert len(warnings) == 1, f"Failed: {warnings}"
    assert warnings[0]['severity'] == 'WARN', f"Failed: {warnings}"
    print("[OK] show_level=False detected")
    
    # No warnings
    kwargs = {'notes': "'Some notes'", 'explanation_key': "'EFFR'"}
    warnings = check_element_warnings('show_metric_with_sparkline', kwargs)
    assert len(warnings) == 0, f"Failed: {warnings}"
    print("[OK] No false positives")


def test_integration():
    """Integration test with real-like content"""
    print("\n=== test_integration ===")
    
    content = """
    # Good call
    show_metric_with_sparkline(t('ind_EFFR'), df.get('EFFR'), 'EFFR', notes='test')
    
    # Bad call - empty explanation_key
    show_metric_with_sparkline(t('ind_IORB'), df.get('IORB'), 'IORB', explanation_key='')
    
    # macro_card with show_level=False
    display_macro_card(t('ind_CPI'), df.get('CPI'), 'CPI', show_level=False)
    """
    
    # Parse sparkline calls
    spark_calls = parse_function_call(content, 'show_metric_with_sparkline')
    assert len(spark_calls) == 2, f"Failed: {spark_calls}"
    
    # Check warnings for IORB
    iorb_call = [c for c in spark_calls if c['key'] == 'IORB'][0]
    warnings = check_element_warnings('show_metric_with_sparkline', iorb_call['kwargs'])
    assert len(warnings) == 1, f"Failed: {warnings}"
    print("[OK] IORB warning detected")
    
    # Parse macro_card calls
    macro_calls = parse_function_call(content, 'display_macro_card')
    assert len(macro_calls) == 1, f"Failed: {macro_calls}"
    
    # Check warnings for CPI
    cpi_call = macro_calls[0]
    warnings = check_element_warnings('display_macro_card', cpi_call['kwargs'])
    assert len(warnings) == 1, f"Failed: {warnings}"
    assert 'show_level' in warnings[0]['message'], f"Failed: {warnings}"
    print("[OK] CPI show_level=False warning detected")


if __name__ == '__main__':
    print("=" * 60)
    print("Phase 3.5 Unit Tests - Element Composition Detection")
    print("=" * 60)
    
    test_smart_split()
    test_parse_args_string()
    test_parse_function_call()
    test_check_element_warnings()
    test_integration()
    
    print("\n" + "=" * 60)
    print("[ALL TESTS PASSED]")
    print("=" * 60)
