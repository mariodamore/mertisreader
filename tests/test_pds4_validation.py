"""Tests for mertisreader.pds4_validation.

These tests use a fake pds4_tools implementation so the module can be covered
without depending on the optional runtime package or real label files.
"""

import builtins
import importlib.util
import sys
from types import SimpleNamespace

import pandas as pd
import pytest

import mertisreader.pds4_validation as pv


class FakeLabel:
    def __init__(self, data):
        self._data = data

    def to_dict(self, cast_values=True):
        return self._data


class FakeFieldData:
    def __init__(self, meta_data):
        self.meta_data = meta_data


class FakeStructure:
    def __init__(self, struct_type="Table_Delimited", data_loaded=True, fields=None, meta_data=None):
        self.type = struct_type
        self.data_loaded = data_loaded
        self.fields = fields or []
        self.meta_data = meta_data


class FakeStructures(list):
    def __init__(self, structures, label_data):
        super().__init__(structures)
        self.label = FakeLabel(label_data)


def install_fake_pds4_tools(monkeypatch, structures):
    fake = SimpleNamespace(read=lambda *args, **kwargs: structures)
    monkeypatch.setattr(pv, "PDS4_TOOLS_AVAILABLE", True)
    monkeypatch.setattr(pv, "pds4_tools", fake)


def install_raising_pds4_tools(monkeypatch, exc):
    def _raise(*args, **kwargs):
        raise exc

    fake = SimpleNamespace(read=_raise)
    monkeypatch.setattr(pv, "PDS4_TOOLS_AVAILABLE", True)
    monkeypatch.setattr(pv, "pds4_tools", fake)


def install_pds4_tools_unavailable(monkeypatch):
    monkeypatch.setattr(pv, "PDS4_TOOLS_AVAILABLE", False)
    monkeypatch.setattr(pv, "pds4_tools", None)


def test_module_import_falls_back_when_pds4_tools_missing(monkeypatch):
    original_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "pds4_tools":
            raise ImportError("pds4_tools missing")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.delitem(sys.modules, "pds4_tools", raising=False)
    monkeypatch.setattr(builtins, "__import__", fake_import)

    spec = importlib.util.spec_from_file_location("pds4_validation_no_pds4_tools", pv.__file__)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    assert module.PDS4_TOOLS_AVAILABLE is False
    assert module.pds4_tools is None


def test_validate_pds4_label_success(tmp_path, monkeypatch):
    label_path = tmp_path / "sample.lbl"
    label_path.write_text("<xml/>", encoding="utf-8")

    label_data = {
        "Product_Observational": {
            "Identification_Area": {
                "version_id": "1.2",
                "product_class": "Product_Observational",
                "logical_identifier": "urn:test:label",
            }
        }
    }
    structures = FakeStructures(
        [FakeStructure(fields=[1, 2]), FakeStructure(struct_type="Array_2D", data_loaded=False)],
        label_data,
    )
    install_fake_pds4_tools(monkeypatch, structures)

    result = pv.validate_pds4_label(label_path)

    assert result["valid"] is True
    assert result["warnings"] == []
    assert result["structure"]["label_version"] == "1.2"
    assert result["structure"]["product_class"] == "Product_Observational"
    assert result["structure"]["logical_identifier"] == "urn:test:label"
    assert result["structure"]["structure_0"]["type"] == "Table_Delimited"
    assert result["structure"]["structure_0"]["data_loaded"] is True


def test_validate_pds4_label_missing_file_raises(tmp_path, monkeypatch):
    install_fake_pds4_tools(monkeypatch, FakeStructures([], {}))

    with pytest.raises(FileNotFoundError):
        pv.validate_pds4_label(tmp_path / "missing.lbl")


def test_validate_pds4_label_importerror_when_unavailable(tmp_path, monkeypatch):
    install_pds4_tools_unavailable(monkeypatch)

    with pytest.raises(ImportError, match="pds4_tools is required for label validation"):
        pv.validate_pds4_label(tmp_path / "missing.lbl")


def test_validate_pds4_label_marks_invalid_on_error(tmp_path, monkeypatch):
    label_path = tmp_path / "sample.lbl"
    label_path.write_text("<xml/>", encoding="utf-8")
    install_raising_pds4_tools(monkeypatch, RuntimeError("boom"))

    result = pv.validate_pds4_label(label_path)

    assert result["valid"] is False
    assert result["warnings"]
    assert "Validation error: boom" in result["warnings"][0]


def test_extract_label_metadata_success(tmp_path, monkeypatch):
    label_path = tmp_path / "sample.xml"
    label_path.write_text("<xml/>", encoding="utf-8")

    label_data = {
        "Product_Observational": {
            "Identification_Area": {
                "product_line": "MERTIS",
                "version_id": "2.0",
            },
            "Observation_Area": {
                "Primary_Result_Summary": {"processing_level": "cal"},
                "Time_Coordinates": {
                    "start_date_time": "2024-01-01T00:00:00Z",
                    "stop_date_time": "2024-01-01T00:01:00Z",
                },
                "Target_Identification": {"name": "Mars"},
                "Mission_Area": {
                    "psa:Mission_Information": {
                        "psa:Mission_Phase": {"psa:name": "Cruise"}
                    }
                },
                "Observing_System": {
                    "name": "MERTIS",
                    "Observing_System_Component": [{"name": "TIS"}, {"name": "HK"}],
                },
            },
        }
    }
    structures = FakeStructures([FakeStructure()], label_data)
    install_fake_pds4_tools(monkeypatch, structures)

    result = pv.extract_label_metadata(label_path)

    assert result["product_line"] == "MERTIS"
    assert result["label_version"] == "2.0"
    assert result["processing_level"] == "CAL"
    assert result["acquisition"]["target"] == "Mars"
    assert result["instrument"]["name"] == "MERTIS"
    assert result["instrument"]["components"] == ["TIS", "HK"]


def test_extract_label_metadata_records_error(tmp_path, monkeypatch):
    label_path = tmp_path / "sample.xml"
    label_path.write_text("<xml/>", encoding="utf-8")
    install_raising_pds4_tools(monkeypatch, RuntimeError("bad metadata"))

    result = pv.extract_label_metadata(label_path)

    assert result["error"] == "bad metadata"


def test_extract_label_metadata_missing_file_raises(tmp_path, monkeypatch):
    install_fake_pds4_tools(monkeypatch, FakeStructures([], {}))

    with pytest.raises(FileNotFoundError):
        pv.extract_label_metadata(tmp_path / "missing.xml")


def test_extract_label_metadata_importerror_when_unavailable(tmp_path, monkeypatch):
    install_pds4_tools_unavailable(monkeypatch)

    with pytest.raises(ImportError, match="pds4_tools is required for metadata extraction"):
        pv.extract_label_metadata(tmp_path / "missing.xml")


def test_get_csv_field_metadata_success(tmp_path, monkeypatch):
    label_path = tmp_path / "sample.xml"
    label_path.write_text("<xml/>", encoding="utf-8")

    field_a = FakeFieldData([("name", "col_a"), ("unit", "m"), ("description", "A"), ("data_type", "ASCII_Real")])
    field_b = FakeFieldData([("name", "col_b"), ("unit", "s"), ("description", "B"), ("data_type", "ASCII_Integer")])
    structures = FakeStructures([FakeStructure(fields=[field_a, field_b])], {"Product_Observational": {}})
    install_fake_pds4_tools(monkeypatch, structures)

    result = pv.get_csv_field_metadata(tmp_path / "sample.dat")

    assert isinstance(result, pd.DataFrame)
    assert list(result["name"]) == ["col_a", "col_b"]
    assert list(result["unit"]) == ["m", "s"]


def test_get_csv_field_metadata_importerror_when_unavailable(tmp_path, monkeypatch):
    install_pds4_tools_unavailable(monkeypatch)

    with pytest.raises(ImportError, match="pds4_tools is required for field metadata extraction"):
        pv.get_csv_field_metadata(tmp_path / "sample.dat")


def test_get_csv_field_metadata_wraps_runtime_error(tmp_path, monkeypatch):
    label_path = tmp_path / "sample.xml"
    data_path = tmp_path / "sample.dat"
    data_path.write_text("1,2,3\n", encoding="utf-8")
    label_path.write_text("<xml/>", encoding="utf-8")

    install_raising_pds4_tools(monkeypatch, RuntimeError("bad fields"))

    with pytest.raises(RuntimeError, match="Failed to extract field metadata: bad fields"):
        pv.get_csv_field_metadata(data_path)


def test_get_csv_field_metadata_missing_label_raises(tmp_path, monkeypatch):
    install_fake_pds4_tools(monkeypatch, FakeStructures([], {}))

    with pytest.raises(FileNotFoundError):
        pv.get_csv_field_metadata(tmp_path / "missing.dat")


def test_extract_mertis_hk_columns_prefers_pds4_tools(tmp_path, monkeypatch):
    data_path = tmp_path / "sample.dat"
    label_path = tmp_path / "sample.xml"
    data_path.write_text("1,2,3\n", encoding="utf-8")
    label_path.write_text("<xml/>", encoding="utf-8")

    structures = FakeStructures(
        [FakeStructure(meta_data=[SimpleNamespace(name="a"), SimpleNamespace(name="b")])],
        {"Product_Observational": {}},
    )
    install_fake_pds4_tools(monkeypatch, structures)

    result = pv.extract_mertis_hk_columns(data_path)

    assert result == ["a", "b"]


def test_extract_mertis_hk_columns_falls_back_to_xml(tmp_path, monkeypatch):
    data_path = tmp_path / "sample.dat"
    label_path = tmp_path / "sample.xml"
    data_path.write_text("1,2,3\n", encoding="utf-8")
    label_path.write_text(
        """
        <Product_Observational>
          <File_Area_Observational>
            <Table_Delimited>
              <Record_Delimited>
                <Field_Delimited><name>col_a</name></Field_Delimited>
                <Field_Delimited><name>col_b</name></Field_Delimited>
              </Record_Delimited>
            </Table_Delimited>
          </File_Area_Observational>
        </Product_Observational>
        """,
        encoding="utf-8",
    )

    monkeypatch.setattr(pv, "PDS4_TOOLS_AVAILABLE", False)

    result = pv.extract_mertis_hk_columns(data_path, use_pds4_tools=False)

    assert result == ["col_a", "col_b"]


def test_extract_mertis_hk_columns_uses_alternate_xml_path(tmp_path, monkeypatch):
        data_path = tmp_path / "sample.dat"
        label_path = tmp_path / "sample.xml"
        data_path.write_text("1,2,3\n", encoding="utf-8")
        label_path.write_text(
                """
                <Product>
                    <File_Area>
                        <Table>
                            <Record>
                                <Field><name>alt_a</name></Field>
                                <Field><name>alt_b</name></Field>
                            </Record>
                        </Table>
                    </File_Area>
                </Product>
                """,
                encoding="utf-8",
        )

        monkeypatch.setattr(pv, "PDS4_TOOLS_AVAILABLE", False)

        result = pv.extract_mertis_hk_columns(data_path, use_pds4_tools=False)

        assert result == ["alt_a", "alt_b"]


def test_extract_mertis_hk_columns_unparseable_raises(tmp_path, monkeypatch):
        data_path = tmp_path / "sample.dat"
        label_path = tmp_path / "sample.xml"
        data_path.write_text("1,2,3\n", encoding="utf-8")
        label_path.write_text("<root />", encoding="utf-8")

        monkeypatch.setattr(pv, "PDS4_TOOLS_AVAILABLE", False)

        with pytest.raises(ValueError, match="Could not parse table definition"):
                pv.extract_mertis_hk_columns(data_path, use_pds4_tools=False)
