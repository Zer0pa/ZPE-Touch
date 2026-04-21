use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

const MODE_EXTENSION: u32 = 0b10;
const DATA_VERSION: u32 = 0;
const HEADER_VERSION: u32 = 1;
const FIBER_VERSION: u32 = 2;
const VIBRO_VERSION: u32 = 3;

const TOUCH_TYPE_BIT: u32 = 0x0800;
const LEGACY_HEADER_RECEPTOR_SHIFT: u32 = 9;
const HEADER_RECEPTOR_LOW_SHIFT: u32 = 9;
const HEADER_RECEPTOR_HIGH_SHIFT: u32 = 4;
const HEADER_REGION_SHIFT: u32 = 5;
const LEGACY_HEADER_TAG: u32 = 0x001F;
const HEADER_TAG: u32 = 0x0007;
const DIRECTION_SHIFT: u32 = 3;

const FIBER_TAG_SHIFT: u32 = 8;
const FIBER_TAG_MASK: u32 = 0x7;
const FIBER_DATA_MASK: u32 = 0xFF;

const THERMAL_FRAME_TAG: u32 = 1;
const THERMAL_SAMPLE_TAG: u32 = 2;
const PROPRIO_FRAME_TAG: u32 = 3;
const PROPRIO_JOINT_TAG: u32 = 4;
const PROPRIO_ANGLE_TAG: u32 = 5;
const PROPRIO_TENSION_TAG: u32 = 6;

const VIBRO_FRAME_TAG: u32 = 1;
const VIBRO_SAMPLE_A_TAG: u32 = 2;
const VIBRO_SAMPLE_B_TAG: u32 = 3;

#[derive(Clone, Debug, PartialEq, Eq)]
struct TouchStrokePayload {
    receptor: u8,
    region: u8,
    directions: Vec<u8>,
    pressure_profile: Vec<u8>,
}

#[derive(Clone, Debug, PartialEq, Eq)]
struct ThermalSamplePayload {
    delta: i8,
    adaptation: u8,
}

#[derive(Clone, Debug, PartialEq, Eq)]
struct ThermalBranchPayload {
    contact: TouchStrokePayload,
    thermal_profile: Vec<ThermalSamplePayload>,
}

#[derive(Clone, Debug, PartialEq, Eq)]
struct VibrotactileSamplePayload {
    band: u8,
    amplitude: u8,
    envelope: u8,
    adaptation: u8,
}

#[derive(Clone, Debug, PartialEq, Eq)]
struct VibrotactileBranchPayload {
    contact: TouchStrokePayload,
    vibrotactile_profile: Vec<VibrotactileSamplePayload>,
}

#[derive(Clone, Debug, PartialEq, Eq)]
struct ProprioceptiveSamplePayload {
    joint_id: u8,
    angle_q: u8,
    tension: u8,
}

#[derive(Clone, Debug, PartialEq, Eq)]
struct ProprioceptiveBranchPayload {
    contact: TouchStrokePayload,
    proprioceptive_profile: Vec<ProprioceptiveSamplePayload>,
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
        return Err(py_value_error(format!(
            "direction out of range: {direction}"
        )));
    }
    if pressure > 7 {
        return Err(py_value_error(format!("pressure out of range: {pressure}")));
    }
    let mut payload = TOUCH_TYPE_BIT;
    payload |= ((direction as u32) & 0x7) << DIRECTION_SHIFT;
    payload |= (pressure as u32) & 0x7;
    Ok(pack_extension_word(DATA_VERSION, payload))
}

fn build_tagged_word(version: u32, tag: u32, data: u8) -> u32 {
    let mut payload = TOUCH_TYPE_BIT;
    payload |= (tag & FIBER_TAG_MASK) << FIBER_TAG_SHIFT;
    payload |= u32::from(data);
    pack_extension_word(version, payload)
}

fn build_count_word(version: u32, tag: u32, sample_count: usize, label: &str) -> PyResult<u32> {
    if sample_count == 0 {
        return Err(py_value_error(format!(
            "{label} sample_count must be positive"
        )));
    }
    if sample_count > u8::MAX as usize {
        return Err(py_value_error(format!(
            "{label} sample_count exceeds 255: {sample_count}"
        )));
    }
    Ok(build_tagged_word(version, tag, sample_count as u8))
}

fn word_mode(word: u32) -> u32 {
    (word >> 18) & 0x3
}

fn word_version(word: u32) -> u32 {
    (word >> 16) & 0x3
}

fn tagged_word_tag(word: u32) -> u32 {
    (word >> FIBER_TAG_SHIFT) & FIBER_TAG_MASK
}

fn tagged_word_data(word: u32) -> u8 {
    (word & FIBER_DATA_MASK) as u8
}

fn is_touch_extension_word(word: u32) -> bool {
    word_mode(word) == MODE_EXTENSION && (word & TOUCH_TYPE_BIT) != 0
}

fn is_tagged_word(word: u32, version: u32, tag: u32) -> bool {
    is_touch_extension_word(word) && word_version(word) == version && tagged_word_tag(word) == tag
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

fn dict_item<'py>(item: &Bound<'py, PyAny>, key: &str) -> PyResult<Bound<'py, PyAny>> {
    item.downcast::<PyDict>()?
        .get_item(key)?
        .ok_or_else(|| py_value_error(format!("missing key: {key}")))
}

fn parse_u8_vec(item: &Bound<'_, PyAny>, key: &str) -> PyResult<Vec<u8>> {
    let list_any = dict_item(item, key)?;
    let values: Vec<u8> = list_any.extract()?;
    Ok(values)
}

fn parse_u8(item: &Bound<'_, PyAny>, key: &str) -> PyResult<u8> {
    dict_item(item, key)?.extract()
}

fn parse_i8(item: &Bound<'_, PyAny>, key: &str) -> PyResult<i8> {
    dict_item(item, key)?.extract()
}

fn parse_list<'py>(item: &Bound<'py, PyAny>, key: &str) -> PyResult<Bound<'py, PyList>> {
    dict_item(item, key)?
        .downcast::<PyList>()
        .map(|list| list.clone())
        .map_err(Into::into)
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

fn parse_thermal_sample(item: &Bound<'_, PyAny>) -> PyResult<ThermalSamplePayload> {
    let delta = parse_i8(item, "delta")?;
    if !(-7..=7).contains(&delta) {
        return Err(py_value_error(format!(
            "thermal delta must be in [-7, 7], got {delta}"
        )));
    }
    let adaptation = parse_u8(item, "adaptation")?;
    if adaptation > 15 {
        return Err(py_value_error(format!(
            "thermal adaptation must be in [0, 15], got {adaptation}"
        )));
    }
    Ok(ThermalSamplePayload { delta, adaptation })
}

fn parse_vibrotactile_sample(item: &Bound<'_, PyAny>) -> PyResult<VibrotactileSamplePayload> {
    let band = parse_u8(item, "band")?;
    let amplitude = parse_u8(item, "amplitude")?;
    let envelope = parse_u8(item, "envelope")?;
    let adaptation = parse_u8(item, "adaptation")?;
    for (label, value) in [
        ("band", band),
        ("amplitude", amplitude),
        ("envelope", envelope),
        ("adaptation", adaptation),
    ] {
        if value > 15 {
            return Err(py_value_error(format!(
                "vibrotactile {label} must be in [0, 15], got {value}"
            )));
        }
    }
    Ok(VibrotactileSamplePayload {
        band,
        amplitude,
        envelope,
        adaptation,
    })
}

fn parse_proprioceptive_sample(item: &Bound<'_, PyAny>) -> PyResult<ProprioceptiveSamplePayload> {
    let joint_id = parse_u8(item, "joint_id")?;
    if joint_id > 13 {
        return Err(py_value_error(format!(
            "proprioceptive joint_id must be in [0, 13], got {joint_id}"
        )));
    }
    let angle_q = parse_u8(item, "angle_q")?;
    let tension = parse_u8(item, "tension")?;
    if tension > 15 {
        return Err(py_value_error(format!(
            "proprioceptive tension must be in [0, 15], got {tension}"
        )));
    }
    Ok(ProprioceptiveSamplePayload {
        joint_id,
        angle_q,
        tension,
    })
}

fn parse_thermal_branch(item: &Bound<'_, PyAny>) -> PyResult<ThermalBranchPayload> {
    let contact = parse_touch_payload(item)?;
    let profile_list = parse_list(item, "thermal_profile")?;
    let mut thermal_profile = Vec::with_capacity(profile_list.len());
    for sample in profile_list.iter() {
        thermal_profile.push(parse_thermal_sample(&sample)?);
    }
    if thermal_profile.len() != contact.directions.len() {
        return Err(py_value_error(
            "thermal_profile length must match the number of contact directions",
        ));
    }
    Ok(ThermalBranchPayload {
        contact,
        thermal_profile,
    })
}

fn parse_vibrotactile_branch(item: &Bound<'_, PyAny>) -> PyResult<VibrotactileBranchPayload> {
    let contact = parse_touch_payload(item)?;
    if contact.receptor != 2 {
        return Err(py_value_error(
            "vibrotactile branch contact must use RA_II receptor (2)",
        ));
    }
    let profile_list = parse_list(item, "vibrotactile_profile")?;
    let mut vibrotactile_profile = Vec::with_capacity(profile_list.len());
    for sample in profile_list.iter() {
        vibrotactile_profile.push(parse_vibrotactile_sample(&sample)?);
    }
    if vibrotactile_profile.len() != contact.directions.len() {
        return Err(py_value_error(
            "vibrotactile_profile length must match the number of contact directions",
        ));
    }
    Ok(VibrotactileBranchPayload {
        contact,
        vibrotactile_profile,
    })
}

fn parse_proprioceptive_branch(item: &Bound<'_, PyAny>) -> PyResult<ProprioceptiveBranchPayload> {
    let contact = parse_touch_payload(item)?;
    let profile_list = parse_list(item, "proprioceptive_profile")?;
    let mut proprioceptive_profile = Vec::with_capacity(profile_list.len());
    for sample in profile_list.iter() {
        proprioceptive_profile.push(parse_proprioceptive_sample(&sample)?);
    }
    if proprioceptive_profile.is_empty() {
        return Err(py_value_error(
            "proprioceptive_profile must contain at least one sample",
        ));
    }
    Ok(ProprioceptiveBranchPayload {
        contact,
        proprioceptive_profile,
    })
}

fn py_u8_list(py: Python<'_>, values: &[u8]) -> PyResult<Py<PyList>> {
    let list = PyList::empty(py);
    for value in values {
        list.append(*value)?;
    }
    Ok(list.unbind())
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
            stroke
                .directions
                .push(((word >> DIRECTION_SHIFT) & 0x7) as u8);
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

fn consume_touch_payload(words: &[u32], start: usize) -> PyResult<(usize, TouchStrokePayload)> {
    if start >= words.len() || !is_header_word(words[start]) {
        return Err(py_value_error("expected touch header word"));
    }
    let (receptor, region) = decode_header_word(words[start]);
    let mut directions = Vec::new();
    let mut pressure_profile = Vec::new();
    let mut index = start + 1;
    while index < words.len() {
        let word = words[index];
        if !is_touch_extension_word(word)
            || is_header_word(word)
            || word_version(word) != DATA_VERSION
        {
            break;
        }
        directions.push(((word >> DIRECTION_SHIFT) & 0x7) as u8);
        pressure_profile.push((word & 0x7) as u8);
        index += 1;
    }
    if directions.is_empty() {
        return Err(py_value_error(
            "touch branch contact must contain at least one direction",
        ));
    }
    Ok((
        index,
        TouchStrokePayload {
            receptor,
            region,
            directions,
            pressure_profile,
        },
    ))
}

fn encode_thermal_sample(sample: &ThermalSamplePayload) -> u32 {
    let delta_code = (sample.delta + 7) as u8;
    let data = (delta_code << 4) | (sample.adaptation & 0x0F);
    build_tagged_word(FIBER_VERSION, THERMAL_SAMPLE_TAG, data)
}

fn decode_thermal_sample(word: u32) -> PyResult<ThermalSamplePayload> {
    if !is_tagged_word(word, FIBER_VERSION, THERMAL_SAMPLE_TAG) {
        return Err(py_value_error("word is not a thermal sample"));
    }
    let data = tagged_word_data(word);
    Ok(ThermalSamplePayload {
        delta: ((data >> 4) & 0x0F) as i8 - 7,
        adaptation: data & 0x0F,
    })
}

fn encode_vibrotactile_sample_a(sample: &VibrotactileSamplePayload) -> u32 {
    let data = ((sample.band & 0x0F) << 4) | (sample.amplitude & 0x0F);
    build_tagged_word(VIBRO_VERSION, VIBRO_SAMPLE_A_TAG, data)
}

fn encode_vibrotactile_sample_b(sample: &VibrotactileSamplePayload) -> u32 {
    let data = ((sample.envelope & 0x0F) << 4) | (sample.adaptation & 0x0F);
    build_tagged_word(VIBRO_VERSION, VIBRO_SAMPLE_B_TAG, data)
}

fn decode_vibrotactile_sample(word_a: u32, word_b: u32) -> PyResult<VibrotactileSamplePayload> {
    if !is_tagged_word(word_a, VIBRO_VERSION, VIBRO_SAMPLE_A_TAG) {
        return Err(py_value_error(
            "word is not a vibrotactile sample-a payload",
        ));
    }
    if !is_tagged_word(word_b, VIBRO_VERSION, VIBRO_SAMPLE_B_TAG) {
        return Err(py_value_error(
            "word is not a vibrotactile sample-b payload",
        ));
    }
    let data_a = tagged_word_data(word_a);
    let data_b = tagged_word_data(word_b);
    Ok(VibrotactileSamplePayload {
        band: (data_a >> 4) & 0x0F,
        amplitude: data_a & 0x0F,
        envelope: (data_b >> 4) & 0x0F,
        adaptation: data_b & 0x0F,
    })
}

fn encode_proprio_joint(sample: &ProprioceptiveSamplePayload) -> u32 {
    build_tagged_word(FIBER_VERSION, PROPRIO_JOINT_TAG, sample.joint_id)
}

fn encode_proprio_angle(sample: &ProprioceptiveSamplePayload) -> u32 {
    build_tagged_word(FIBER_VERSION, PROPRIO_ANGLE_TAG, sample.angle_q)
}

fn encode_proprio_tension(sample: &ProprioceptiveSamplePayload) -> u32 {
    build_tagged_word(FIBER_VERSION, PROPRIO_TENSION_TAG, sample.tension)
}

fn decode_proprioceptive_sample(
    joint_word: u32,
    angle_word: u32,
    tension_word: u32,
) -> PyResult<ProprioceptiveSamplePayload> {
    if !is_tagged_word(joint_word, FIBER_VERSION, PROPRIO_JOINT_TAG) {
        return Err(py_value_error("word is not a proprioceptive joint payload"));
    }
    if !is_tagged_word(angle_word, FIBER_VERSION, PROPRIO_ANGLE_TAG) {
        return Err(py_value_error("word is not a proprioceptive angle payload"));
    }
    if !is_tagged_word(tension_word, FIBER_VERSION, PROPRIO_TENSION_TAG) {
        return Err(py_value_error(
            "word is not a proprioceptive tension payload",
        ));
    }
    Ok(ProprioceptiveSamplePayload {
        joint_id: tagged_word_data(joint_word),
        angle_q: tagged_word_data(angle_word),
        tension: tagged_word_data(tension_word),
    })
}

fn pack_thermal_branch_stream(branches: &[ThermalBranchPayload]) -> PyResult<Vec<u32>> {
    let mut words = Vec::new();
    for branch in branches {
        words.push(build_count_word(
            FIBER_VERSION,
            THERMAL_FRAME_TAG,
            branch.thermal_profile.len(),
            "thermal",
        )?);
        words.extend(pack_touch_payloads(std::slice::from_ref(&branch.contact))?);
        for sample in &branch.thermal_profile {
            words.push(encode_thermal_sample(sample));
        }
    }
    Ok(words)
}

fn unpack_thermal_branch_stream(words: &[u32]) -> (u32, u32, u32, Vec<ThermalBranchPayload>) {
    let mut consumed = 0u32;
    let mut frames = 0u32;
    let mut ignored = 0u32;
    let mut decoded = Vec::new();
    let mut index = 0usize;

    while index < words.len() {
        if !is_tagged_word(words[index], FIBER_VERSION, THERMAL_FRAME_TAG) {
            ignored += 1;
            index += 1;
            continue;
        }
        let frame_start = index;
        let sample_count = tagged_word_data(words[index]) as usize;
        index += 1;
        let (next_index, contact) = match consume_touch_payload(words, index) {
            Ok(result) => result,
            Err(_) => {
                ignored += (words.len() - frame_start) as u32;
                break;
            }
        };
        index = next_index;

        let mut thermal_profile = Vec::with_capacity(sample_count);
        let mut malformed = false;
        for _ in 0..sample_count {
            if index >= words.len() {
                malformed = true;
                break;
            }
            match decode_thermal_sample(words[index]) {
                Ok(sample) => {
                    thermal_profile.push(sample);
                    index += 1;
                }
                Err(_) => {
                    malformed = true;
                    break;
                }
            }
        }
        if malformed {
            ignored += (words.len() - frame_start) as u32;
            break;
        }
        consumed += (index - frame_start) as u32;
        frames += 1;
        decoded.push(ThermalBranchPayload {
            contact,
            thermal_profile,
        });
    }

    (consumed, frames, ignored, decoded)
}

fn pack_vibrotactile_branch_stream(branches: &[VibrotactileBranchPayload]) -> PyResult<Vec<u32>> {
    let mut words = Vec::new();
    for branch in branches {
        words.push(build_count_word(
            VIBRO_VERSION,
            VIBRO_FRAME_TAG,
            branch.vibrotactile_profile.len(),
            "vibrotactile",
        )?);
        words.extend(pack_touch_payloads(std::slice::from_ref(&branch.contact))?);
        for sample in &branch.vibrotactile_profile {
            words.push(encode_vibrotactile_sample_a(sample));
            words.push(encode_vibrotactile_sample_b(sample));
        }
    }
    Ok(words)
}

fn unpack_vibrotactile_branch_stream(
    words: &[u32],
) -> (u32, u32, u32, Vec<VibrotactileBranchPayload>) {
    let mut consumed = 0u32;
    let mut frames = 0u32;
    let mut ignored = 0u32;
    let mut decoded = Vec::new();
    let mut index = 0usize;

    while index < words.len() {
        if !is_tagged_word(words[index], VIBRO_VERSION, VIBRO_FRAME_TAG) {
            ignored += 1;
            index += 1;
            continue;
        }
        let frame_start = index;
        let sample_count = tagged_word_data(words[index]) as usize;
        index += 1;
        let (next_index, contact) = match consume_touch_payload(words, index) {
            Ok(result) => result,
            Err(_) => {
                ignored += (words.len() - frame_start) as u32;
                break;
            }
        };
        index = next_index;

        let mut vibrotactile_profile = Vec::with_capacity(sample_count);
        let mut malformed = false;
        for _ in 0..sample_count {
            if index + 1 >= words.len() {
                malformed = true;
                break;
            }
            match decode_vibrotactile_sample(words[index], words[index + 1]) {
                Ok(sample) => {
                    vibrotactile_profile.push(sample);
                    index += 2;
                }
                Err(_) => {
                    malformed = true;
                    break;
                }
            }
        }
        if malformed {
            ignored += (words.len() - frame_start) as u32;
            break;
        }
        consumed += (index - frame_start) as u32;
        frames += 1;
        decoded.push(VibrotactileBranchPayload {
            contact,
            vibrotactile_profile,
        });
    }

    (consumed, frames, ignored, decoded)
}

fn pack_proprioceptive_branch_stream(
    branches: &[ProprioceptiveBranchPayload],
) -> PyResult<Vec<u32>> {
    let mut words = Vec::new();
    for branch in branches {
        words.push(build_count_word(
            FIBER_VERSION,
            PROPRIO_FRAME_TAG,
            branch.proprioceptive_profile.len(),
            "proprioceptive",
        )?);
        words.extend(pack_touch_payloads(std::slice::from_ref(&branch.contact))?);
        for sample in &branch.proprioceptive_profile {
            words.push(encode_proprio_joint(sample));
            words.push(encode_proprio_angle(sample));
            words.push(encode_proprio_tension(sample));
        }
    }
    Ok(words)
}

fn unpack_proprioceptive_branch_stream(
    words: &[u32],
) -> (u32, u32, u32, Vec<ProprioceptiveBranchPayload>) {
    let mut consumed = 0u32;
    let mut frames = 0u32;
    let mut ignored = 0u32;
    let mut decoded = Vec::new();
    let mut index = 0usize;

    while index < words.len() {
        if !is_tagged_word(words[index], FIBER_VERSION, PROPRIO_FRAME_TAG) {
            ignored += 1;
            index += 1;
            continue;
        }
        let frame_start = index;
        let sample_count = tagged_word_data(words[index]) as usize;
        index += 1;
        let (next_index, contact) = match consume_touch_payload(words, index) {
            Ok(result) => result,
            Err(_) => {
                ignored += (words.len() - frame_start) as u32;
                break;
            }
        };
        index = next_index;

        let mut proprioceptive_profile = Vec::with_capacity(sample_count);
        let mut malformed = false;
        for _ in 0..sample_count {
            if index + 2 >= words.len() {
                malformed = true;
                break;
            }
            match decode_proprioceptive_sample(words[index], words[index + 1], words[index + 2]) {
                Ok(sample) => {
                    proprioceptive_profile.push(sample);
                    index += 3;
                }
                Err(_) => {
                    malformed = true;
                    break;
                }
            }
        }
        if malformed {
            ignored += (words.len() - frame_start) as u32;
            break;
        }
        consumed += (index - frame_start) as u32;
        frames += 1;
        decoded.push(ProprioceptiveBranchPayload {
            contact,
            proprioceptive_profile,
        });
    }

    (consumed, frames, ignored, decoded)
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
        item.set_item("directions", py_u8_list(py, &stroke.directions)?)?;
        item.set_item(
            "pressure_profile",
            py_u8_list(py, &stroke.pressure_profile)?,
        )?;
        payloads.append(item)?;
    }
    Ok((metadata.unbind(), payloads.unbind()))
}

#[pyfunction(name = "pack_thermal_branch_payloads")]
fn py_pack_thermal_branch_payloads(branches: &Bound<'_, PyList>) -> PyResult<Vec<u32>> {
    let mut payloads = Vec::with_capacity(branches.len());
    for item in branches.iter() {
        payloads.push(parse_thermal_branch(&item)?);
    }
    pack_thermal_branch_stream(&payloads)
}

#[pyfunction(name = "unpack_thermal_branch_words_payload")]
fn py_unpack_thermal_branch_words_payload(
    py: Python<'_>,
    words: Vec<u32>,
) -> PyResult<(Py<PyDict>, Py<PyList>)> {
    let (consumed, frames, ignored, branches) = unpack_thermal_branch_stream(&words);
    let metadata = PyDict::new(py);
    metadata.set_item("consumed_branch_words", consumed)?;
    metadata.set_item("decoded_branches", frames)?;
    metadata.set_item("ignored_words", ignored)?;

    let payloads = PyList::empty(py);
    for branch in branches {
        let item = PyDict::new(py);
        item.set_item("receptor", branch.contact.receptor)?;
        item.set_item("region", branch.contact.region)?;
        item.set_item("directions", py_u8_list(py, &branch.contact.directions)?)?;
        item.set_item(
            "pressure_profile",
            py_u8_list(py, &branch.contact.pressure_profile)?,
        )?;
        let profile = PyList::empty(py);
        for sample in branch.thermal_profile {
            let sample_item = PyDict::new(py);
            sample_item.set_item("delta", sample.delta)?;
            sample_item.set_item("adaptation", sample.adaptation)?;
            profile.append(sample_item)?;
        }
        item.set_item("thermal_profile", profile)?;
        payloads.append(item)?;
    }
    Ok((metadata.unbind(), payloads.unbind()))
}

#[pyfunction(name = "pack_vibrotactile_branch_payloads")]
fn py_pack_vibrotactile_branch_payloads(branches: &Bound<'_, PyList>) -> PyResult<Vec<u32>> {
    let mut payloads = Vec::with_capacity(branches.len());
    for item in branches.iter() {
        payloads.push(parse_vibrotactile_branch(&item)?);
    }
    pack_vibrotactile_branch_stream(&payloads)
}

#[pyfunction(name = "unpack_vibrotactile_branch_words_payload")]
fn py_unpack_vibrotactile_branch_words_payload(
    py: Python<'_>,
    words: Vec<u32>,
) -> PyResult<(Py<PyDict>, Py<PyList>)> {
    let (consumed, frames, ignored, branches) = unpack_vibrotactile_branch_stream(&words);
    let metadata = PyDict::new(py);
    metadata.set_item("consumed_branch_words", consumed)?;
    metadata.set_item("decoded_branches", frames)?;
    metadata.set_item("ignored_words", ignored)?;

    let payloads = PyList::empty(py);
    for branch in branches {
        let item = PyDict::new(py);
        item.set_item("receptor", branch.contact.receptor)?;
        item.set_item("region", branch.contact.region)?;
        item.set_item("directions", py_u8_list(py, &branch.contact.directions)?)?;
        item.set_item(
            "pressure_profile",
            py_u8_list(py, &branch.contact.pressure_profile)?,
        )?;
        let profile = PyList::empty(py);
        for sample in branch.vibrotactile_profile {
            let sample_item = PyDict::new(py);
            sample_item.set_item("band", sample.band)?;
            sample_item.set_item("amplitude", sample.amplitude)?;
            sample_item.set_item("envelope", sample.envelope)?;
            sample_item.set_item("adaptation", sample.adaptation)?;
            profile.append(sample_item)?;
        }
        item.set_item("vibrotactile_profile", profile)?;
        payloads.append(item)?;
    }
    Ok((metadata.unbind(), payloads.unbind()))
}

#[pyfunction(name = "pack_proprioceptive_branch_payloads")]
fn py_pack_proprioceptive_branch_payloads(branches: &Bound<'_, PyList>) -> PyResult<Vec<u32>> {
    let mut payloads = Vec::with_capacity(branches.len());
    for item in branches.iter() {
        payloads.push(parse_proprioceptive_branch(&item)?);
    }
    pack_proprioceptive_branch_stream(&payloads)
}

#[pyfunction(name = "unpack_proprioceptive_branch_words_payload")]
fn py_unpack_proprioceptive_branch_words_payload(
    py: Python<'_>,
    words: Vec<u32>,
) -> PyResult<(Py<PyDict>, Py<PyList>)> {
    let (consumed, frames, ignored, branches) = unpack_proprioceptive_branch_stream(&words);
    let metadata = PyDict::new(py);
    metadata.set_item("consumed_branch_words", consumed)?;
    metadata.set_item("decoded_branches", frames)?;
    metadata.set_item("ignored_words", ignored)?;

    let payloads = PyList::empty(py);
    for branch in branches {
        let item = PyDict::new(py);
        item.set_item("receptor", branch.contact.receptor)?;
        item.set_item("region", branch.contact.region)?;
        item.set_item("directions", py_u8_list(py, &branch.contact.directions)?)?;
        item.set_item(
            "pressure_profile",
            py_u8_list(py, &branch.contact.pressure_profile)?,
        )?;
        let profile = PyList::empty(py);
        for sample in branch.proprioceptive_profile {
            let sample_item = PyDict::new(py);
            sample_item.set_item("joint_id", sample.joint_id)?;
            sample_item.set_item("angle_q", sample.angle_q)?;
            sample_item.set_item("tension", sample.tension)?;
            profile.append(sample_item)?;
        }
        item.set_item("proprioceptive_profile", profile)?;
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
    info.set_item("module_name", "zpe_touch._native")?;
    info.set_item("crate_name", env!("CARGO_PKG_NAME"))?;
    info.set_item("version", env!("CARGO_PKG_VERSION"))?;
    Ok(info.unbind())
}

#[pymodule]
fn _native(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(pack_touch_strokes_payload, m)?)?;
    m.add_function(wrap_pyfunction!(unpack_touch_words_payload, m)?)?;
    m.add_function(wrap_pyfunction!(py_pack_thermal_branch_payloads, m)?)?;
    m.add_function(wrap_pyfunction!(py_unpack_thermal_branch_words_payload, m)?)?;
    m.add_function(wrap_pyfunction!(py_pack_vibrotactile_branch_payloads, m)?)?;
    m.add_function(wrap_pyfunction!(
        py_unpack_vibrotactile_branch_words_payload,
        m
    )?)?;
    m.add_function(wrap_pyfunction!(py_pack_proprioceptive_branch_payloads, m)?)?;
    m.add_function(wrap_pyfunction!(
        py_unpack_proprioceptive_branch_words_payload,
        m
    )?)?;
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

    #[test]
    fn thermal_branch_roundtrip_preserves_contact_and_history() {
        let words = pack_thermal_branch_stream(&[ThermalBranchPayload {
            contact: sample_strokes()[0].clone(),
            thermal_profile: vec![
                ThermalSamplePayload {
                    delta: -3,
                    adaptation: 1,
                },
                ThermalSamplePayload {
                    delta: 0,
                    adaptation: 4,
                },
                ThermalSamplePayload {
                    delta: 3,
                    adaptation: 7,
                },
            ],
        }])
        .unwrap();
        let (_consumed, frames, ignored, branches) = unpack_thermal_branch_stream(&words);
        assert_eq!(frames, 1);
        assert_eq!(ignored, 0);
        assert_eq!(branches[0].thermal_profile[2].delta, 3);
        let (_base_consumed, _headers, base_ignored, base) = unpack_touch_payloads(&words);
        assert_eq!(base_ignored, 4);
        assert_eq!(base.len(), 1);
    }

    #[test]
    fn vibrotactile_branch_roundtrip_preserves_raii_payloads() {
        let words = pack_vibrotactile_branch_stream(&[VibrotactileBranchPayload {
            contact: sample_strokes()[1].clone(),
            vibrotactile_profile: vec![
                VibrotactileSamplePayload {
                    band: 3,
                    amplitude: 9,
                    envelope: 2,
                    adaptation: 4,
                },
                VibrotactileSamplePayload {
                    band: 11,
                    amplitude: 7,
                    envelope: 1,
                    adaptation: 8,
                },
                VibrotactileSamplePayload {
                    band: 15,
                    amplitude: 5,
                    envelope: 3,
                    adaptation: 10,
                },
            ],
        }])
        .unwrap();
        let (_consumed, frames, ignored, branches) = unpack_vibrotactile_branch_stream(&words);
        assert_eq!(frames, 1);
        assert_eq!(ignored, 0);
        assert_eq!(branches[0].vibrotactile_profile[0].band, 3);
        let (_base_consumed, _headers, base_ignored, base) = unpack_touch_payloads(&words);
        assert_eq!(base_ignored, 7);
        assert_eq!(base.len(), 1);
    }

    #[test]
    fn proprioceptive_branch_roundtrip_preserves_joint_trajectory() {
        let words = pack_proprioceptive_branch_stream(&[ProprioceptiveBranchPayload {
            contact: sample_strokes()[0].clone(),
            proprioceptive_profile: vec![
                ProprioceptiveSamplePayload {
                    joint_id: 5,
                    angle_q: 64,
                    tension: 3,
                },
                ProprioceptiveSamplePayload {
                    joint_id: 5,
                    angle_q: 96,
                    tension: 7,
                },
            ],
        }])
        .unwrap();
        let (_consumed, frames, ignored, branches) = unpack_proprioceptive_branch_stream(&words);
        assert_eq!(frames, 1);
        assert_eq!(ignored, 0);
        assert_eq!(branches[0].proprioceptive_profile[1].angle_q, 96);
        let (_base_consumed, _headers, base_ignored, base) = unpack_touch_payloads(&words);
        assert_eq!(base_ignored, 7);
        assert_eq!(base.len(), 1);
    }
}
