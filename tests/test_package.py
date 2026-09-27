def test_import_package():
    import pronostico_demanda_electrica

    assert pronostico_demanda_electrica.__name__ == "pronostico_demanda_electrica"
    