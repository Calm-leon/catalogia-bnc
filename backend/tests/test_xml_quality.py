from app.xml_quality import evaluate_xml_quality


def test_xml_quality_passes_for_minimum_inferable_fields():
    xml = """<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:dc="http://purl.org/dc/elements/1.1/">
  <rdf:Description>
    <dc:title>Titulo</dc:title>
    <dc:type>Image</dc:type>
    <dc:format>image/jpeg</dc:format>
    <dc:description>Descripcion de prueba</dc:description>
  </rdf:Description>
</rdf:RDF>
"""
    result = evaluate_xml_quality(xml)
    assert result.passed is True
    assert result.score == 100
    assert all(check.passed for check in result.checks)


def test_xml_quality_fails_for_missing_required_fields():
    xml = """<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:dc="http://purl.org/dc/elements/1.1/">
  <rdf:Description>
    <dc:title></dc:title>
    <dc:format>image/jpeg</dc:format>
  </rdf:Description>
</rdf:RDF>
"""
    result = evaluate_xml_quality(xml)
    assert result.passed is False
    missing = {check.key for check in result.checks if not check.passed}
    assert "required_title" in missing
    assert "required_description" in missing
    assert "required_type" in missing
