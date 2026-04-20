use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

const MODE_EXTENSION: u32 = 0b10;
const DATA_VERSION: u32 = 0;
const HEADER_VERSION: u32 = 1;

const TOUCH_TYPE_BIT: u32 = 0x0800;
const LEGACY_HEADER_RECEPTOR_SHIFT: u32 = 9;
const HEADER_RECEPTOR_LOW_SHIFT: u32 = 9;
const HEADER_RECEPTOR_HIGH_SHIFT: u32 = 4;
const HEADER_REGION_SHIFT: u32 = 5;
const LEGACY_HEADER_TAG: u32 = 0x001F;
const HEADER_TAG: u32 = 0x0007;
const DIRECTION_SHIFT: u32 = 3;

#[derive(Clone, Debug, PartialEq, Eq)]
struct TouchStrokePayload {
    receptor: u8,
    region: u8,
    directions: Vec<u8>,
    pressure_profile: Vec<u8>,
}

fn py_value_error(message: impl Into<String>) -> PyErr {
    PyValueError::new_err(message.into())
}

fn pack_extension_word(version: u32, payload: u32) -> u32 {
    (MODE_EXTENSION << 18) | ((version & 0x3) << 16) | (payload & 0xFFFF)
}

fn build_header_word(receptor: u8, region: u8) -> PyResult<u32> {
    if receptor > 3 {
        return Err(py_value_error(format!("receptor out of range: {receptor}")));
    }
    if region > 15 {
        return Err(py_value_error(format!("region out of range: {region}")));
    }
    let mut payload = TOUCH_TYPE_BIT;
    payload |= ((receptor as u32) & 0x1) << HEADER_RECEPTOR_LOW_SHIFT;
    payload |= ((region as u32) & 0xF) << HEADER_REGION_SHIFT;
    payload |= (((receptor as u32) >> 1) & 0x1) << HEADER_RECEPTOR_HIGH_SHIFT;
    payload |= HEADER_TAG;
    Ok(pack_extension_word(HEADER_VERSION, payload))
}

fn build_step_word(direction: u8, pressure: u8) -> PyResult<u32> {
    if direction > 7 {
        return Err(py_value_error(format!("direction out of range: {direction}")));
    }
    if pressure > 7 {
        return Err(py_value_error(format!("pressure out of range: {pressure}")));
    }
    let mut payload = TOUCH_TYPE_BIT;
    payload |= ((direction as u32) & 0x7) << DIRECTION_SHIFT;
    payload |= (pressure as u32) & 0x7;
    Ok(pack_extension_word(DATA_VERSION, payload))
}

fn word_mode(word: u32) -> u32 {
    (word >> 18) & 0x3
}

fn word_version(word: u32) -> u32 {
    (word >> 16) & 0x3
}

fn is_touch_extension_word(word: u32) -> bool {
    word_mode(word) == MODE_EXTENSION && (word & TOUCH_TYPE_BIT) != 0
}

fn is_header_word(word: u32) -> bool {
    if !is_touch_extension_word(word) || word_version(word) != HEADER_VERSION {
        return false;
    }
    let payload = word & 0xFFFF;
    (payload & LEGACY_HEADER_TAG) == LEGACY_HEADER_TAG || (payload & 0xF) == HEADER_TAG
}

fn decode_header_word(word: u32) -> (u8, u8) {
    let payload = word & 0xFFFF;
    let region = ((payload >> HEADER_REGION_SHIFT) & 0xF) as u8;
    if (payload & LEGACY_HEADER_TAG) == LEGACY_HEADER_TAG {
        let receptor = ((payload >> LEGACY_HEADER_RECEPTOR_SHIFT) & 0x3) as u8;
        return (receptor, region);
    }
    let receptor_low = ((payload >> HEADER_RECEPTOR_LOW_SHIFT) & 0x1) as u8;
    let receptor_high = ((payload >> HEADER_RECEPTOR_HIGH_SHIFT) & 0x1) as u8;
    (receptor_low | (receptor_high << 1), region)
}

fn parse_u8_vec(item: &Bound<'_, PyAny>, key: &str) -> PyResult<Vec<u8>> {
    let list_any = item
        .downcast::<PyDict>()?
        .get_item(key)?
        .ok_or_else(|| py_value_error(format!("missing key: {key}")))?;
    let values: Vec<u8> = list_any.extract()?;
    Ok(values)
}

fn parse_u8(item: &Bound<'_, PyAny>, key: &str) -> PyResult<u8> {
    let value = item
        .downcast::<PyDict>()?
        .get_item(key)?
        .ok_or_else(|| py_value_error(format!("missing key: {key}")))?;
    value.extract()
}

fn parse_touch_payload(item: &Bound<'_, PyAny>) -> PyResult<TouchStrokePayload> {
    let directions = parse_u8_vec(item, "directions")?;
    let pressure_profile = parse_u8_vec(item, "pressure_profile")?;
    if pressure_profile.len() > directions.len() {
        return Err(py_value_error(
            "pressure_profile length cannot exceed directions length",
        ));
    }
    Ok(TouchStrokePayload {
        receptor: parse_u8(item, "receptor")?,
        region: parse_u8(item, "region")?,
        directions,
        pressure_profile,
    })
}

fn pack_touch_payloads(strokes: &[TouchStrokePayload]) -> PyResult<Vec<u32>> {
    let mut words = Vec::new();
    for stroke in strokes {
        if stroke.directions.is_empty() {
            continue;
        }
        words.push(build_header_word(stroke.receptor, stroke.region)?);
        for (index, direction) in stroke.directions.iter().enumerate() {
            let pressure = stroke.pressure_profile.get(index).copied().unwrap_or(0);
            words.push(build_step_word(*direction, pressure)?);
        }
    }
    Ok(words)
}

fn unpack_touch_payloads(words: &[u32]) -> (u32, u32, u32, Vec<TouchStrokePayload>) {
    let mut decoded = Vec::new();
    let mut current: Option<TouchStrokePayload> = None;
    let mut consumed = 0u32;
    let mut headers = 0u32;
    let mut ignored = 0u32;

    for &word in words {
        if !is_touch_extension_word(word) {
            ignored += 1;
            continue;
        }

        if is_header_word(word) {
            let (receptor, region) = decode_header_word(word);
            if let Some(stroke) = current.take() {
                if !stroke.directions.is_empty() {
                    decoded.push(stroke);
                }
            }
            current = Some(TouchStrokePayload {
                receptor,
                region,
                directions: Vec::new(),
                pressure_profile: Vec::new(),
            });
            headers += 1;
            consumed += 1;
            continue;
        }

        if word_version(word) != DATA_VERSION {
            ignored += 1;
            continue;
        }

        if let Some(stroke) = current.as_mut() {
            stroke.directions.push(((word >> DIRECTION_SHIFT) & 0x7) as u8);
            stroke.pressure_profile.push((word & 0x7) as u8);
            consumed += 1;
        } else {
            ignored += 1;
        }
    }

    if let Some(stroke) = current {
        if !stroke.directions.is_empty() {
            decoded.push(stroke);
        }
    }

    (consumed, headers, ignored, decoded)
}

#[pyfunction]
fn pack_touch_strokes_payload(strokes: &Bound<'_, PyList>) -> PyResult<Vec<u32>> {
    let mut payloads = Vec::with_capacity(strokes.len());
    for item in strokes.iter() {
        payloads.push(parse_touch_payload(&item)?);
    }
    pack_touch_payloads(&payloads)
}

#[pyfunction]
fn unpack_touch_words_payload(
    py: Python<'_>,
    words: Vec<u32>,
) -> PyResult<(Py<PyDict>, Py<PyList>)> {
    let (consumed, headers, ignored, strokes) = unpack_touch_payloads(&words);
    let metadata = PyDict::new(py);
    metadata.set_item("consumed_touch_words", consumed)?;
    metadata.set_item("header_words", headers)?;
    metadata.set_item("ignored_words", ignored)?;

    let payloads = PyList::empty(py);
    for stroke in strokes {
        let item = PyDict::new(py);
        item.set_item("receptor", stroke.receptor)?;
        item.set_item("region", stroke.region)?;
        item.set_item("directions", stroke.directions)?;
        item.set_item("pressure_profile", stroke.pressure_profile)?;
        payloads.append(item)?;
    }
    Ok((metadata.unbind(), payloads.unbind()))
}

#[pyfunction]
fn backend_info(py: Python<'_>) -> PyResult<Py<PyDict>> {
    let info = PyDict::new(py);
    info.set_item("backend", "rust")?;
    info.set_item("native", true)?;
    info.set_item("fallback_used", false)?;
    info.set_item("module_name", "zpe_touch_codec")?;
    info.set_item("crate_name", env!("CARGO_PKG_NAME"))?;
    info.set_item("version", env!("CARGO_PKG_VERSION"))?;
    Ok(info.unbind())
}

#[pymodule]
fn zpe_touch_codec(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(pack_touch_strokes_payload, m)?)?;
    m.add_function(wrap_pyfunction!(unpack_touch_words_payload, m)?)?;
    m.add_function(wrap_pyfunction!(backend_info, m)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn sample_strokes() -> Vec<TouchStrokePayload> {
        vec![
            TouchStrokePayload {
                receptor: 0,
                region: 1,
                directions: vec![0, 1, 2],
                pressure_profile: vec![2, 3, 4],
            },
            TouchStrokePayload {
                receptor: 2,
                region: 7,
                directions: vec![7, 6, 5],
                pressure_profile: vec![3, 2, 1],
            },
        ]
    }

    #[test]
    fn roundtrip_preserves_contact_payload() {
        let strokes = sample_strokes();
        let words = pack_touch_payloads(&strokes).unwrap();
        let (consumed, headers, ignored, decoded) = unpack_touch_payloads(&words);
        assert_eq!(consumed, words.len() as u32);
        assert_eq!(headers, 2);
        assert_eq!(ignored, 0);
        assert_eq!(decoded, strokes);
    }

    #[test]
    fn ignores_non_touch_words() {
        let mut words = pack_touch_payloads(&sample_strokes()).unwrap();
        words.insert(1, 7);
        let (_consumed, _headers, ignored, decoded) = unpack_touch_payloads(&words);
        assert_eq!(ignored, 1);
        assert_eq!(decoded.len(), 2);
    }
}
