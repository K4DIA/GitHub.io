// Calculation engine ported from Portable Antenna Planner 0.6.0 (Python).
// Classic script so the whole planner inlines into one offline HTML file.
// Everything hangs off window.AntennaEngine.
(function () {
'use strict';

const FEET_TO_METERS = 0.3048;
const SPEED_OF_LIGHT_M_S = 299792458.0;
const EARTH_RADIUS_KM = 6371.0088;

const ANTENNA_TYPES = {
  DIPOLE: 'Horizontal dipole',
  INVERTED_V: 'Inverted-V',
  EFHW: 'End-fed half-wave',
  VERTICAL: 'Quarter-wave vertical',
  VERTICAL_DIPOLE: 'Vertical half-wave dipole',
  YAGI_2: '2-element Yagi',
  YAGI_3: '3-element Yagi',
  MOXON: 'Moxon rectangle',
};

/* Free-space gain and pattern shape per type. Planning estimates for a
   well-built antenna in the clear, not modelled figures — the NEC export
   exists for that. `boom` is in wavelengths. */
const ANTENNA_SPECS = {
  'Horizontal dipole': { gain: 2.15, polarization: 'H', family: 'wire', legs: 2 },
  'Inverted-V': { gain: 1.8, polarization: 'H', family: 'wire', legs: 2 },
  'End-fed half-wave': { gain: 2.0, polarization: 'H', family: 'wire', legs: 1 },
  'Quarter-wave vertical': { gain: 0.5, polarization: 'V', family: 'vertical' },
  'Vertical half-wave dipole': { gain: 2.15, polarization: 'V', family: 'vertical' },
  '2-element Yagi': { gain: 6.0, polarization: 'H', family: 'beam', fb: 10, boom: 0.15, beamwidth: 70 },
  '3-element Yagi': { gain: 7.5, polarization: 'H', family: 'beam', fb: 20, boom: 0.30, beamwidth: 60 },
  'Moxon rectangle': { gain: 5.8, polarization: 'H', family: 'beam', fb: 25, boom: 0.14, beamwidth: 72 },
};

function specFor(antennaType) {
  return ANTENNA_SPECS[antennaType] || ANTENNA_SPECS['Horizontal dipole'];
}

function estimatedGainDbi(antennaType) {
  return specFor(antennaType).gain;
}

function isBeam(antennaType) { return specFor(antennaType).family === 'beam'; }
function isVerticalFamily(antennaType) { return specFor(antennaType).family === 'vertical'; }

/* A beam points along its boom; a wire antenna radiates broadside to itself. */
function recommendedAzimuthFor(antennaType, targetBearingDeg) {
  return isBeam(antennaType) ? normalizeBearing(targetBearingDeg) : normalizeBearing(targetBearingDeg - 90);
}

const PROPAGATION_MODELS = {
  FREE_SPACE: 'Free space',
  TERRAIN_KNIFE_EDGE: 'Terrain + knife-edge',
};

const CABLES = {
  'RG-58 (generic)': { 1: 0.4, 10: 1.4, 30: 2.5, 50: 3.3, 100: 4.9, 150: 6.2, 450: 11.2 },
  'RG-8X (generic)': { 1: 0.3, 10: 0.9, 30: 1.7, 50: 2.2, 100: 3.3, 150: 4.2, 450: 8.1 },
  'RG-213 (generic)': { 1: 0.2, 10: 0.6, 30: 1.0, 50: 1.3, 100: 2.0, 150: 2.5, 450: 5.0 },
  'LMR-240 (generic)': { 1: 0.24, 10: 0.77, 30: 1.34, 50: 1.73, 100: 2.45, 150: 3.01, 450: 5.28 },
  'LMR-400 (generic)': { 1: 0.12, 10: 0.39, 30: 0.68, 50: 0.88, 100: 1.25, 150: 1.54, 450: 2.71 },
};

const OBJECT_KINDS = {
  TREE: 'Tree',
  MAST: 'Mast',
  HAZARD: 'Hazard / exclusion zone',
  BUILDING: 'Building',
  VEHICLE: 'Vehicle',
  METAL_STRUCTURE: 'Metal structure',
};

const DEFAULT_OBJECT_ATTENUATION_DB = {
  [OBJECT_KINDS.TREE]: 2.0,
  [OBJECT_KINDS.BUILDING]: 12.0,
  [OBJECT_KINDS.VEHICLE]: 4.0,
  [OBJECT_KINDS.METAL_STRUCTURE]: 18.0,
};

const DEFAULT_OBJECT_HEIGHT_FT = {
  [OBJECT_KINDS.TREE]: 35.0,
  [OBJECT_KINDS.MAST]: 30.0,
  [OBJECT_KINDS.HAZARD]: 0.0,
  [OBJECT_KINDS.BUILDING]: 20.0,
  [OBJECT_KINDS.VEHICLE]: 6.0,
  [OBJECT_KINDS.METAL_STRUCTURE]: 12.0,
};

function objectHeightFt(item) {
  if (Number.isFinite(item.height_ft) && item.height_ft > 0) return item.height_ft;
  return DEFAULT_OBJECT_HEIGHT_FT[item.kind] || 0;
}

/* How far along the ray the object sits, 0 at the feedpoint and 1 at the far end. */
function projectionFraction(point, start, end) {
  const dx = end.x - start.x;
  const dy = end.y - start.y;
  if (dx === 0 && dy === 0) return 0;
  const t = ((point.x - start.x) * dx + (point.y - start.y) * dy) / (dx * dx + dy * dy);
  return Math.max(0, Math.min(1, t));
}

function defaultPlan() {
  return {
    frequency_mhz: 7.2,
    antenna_type: ANTENNA_TYPES.INVERTED_V,
    site: { width_ft: 120, depth_ft: 100, boundary: [] },
    feedpoint: { x: 60, y: 50 },
    feedpoint_height_ft: 30,
    endpoint_height_ft: 8,
    wire_azimuth_deg: 0,
    target_bearing_deg: 90,
    radio_position: { x: 20, y: 15 },
    service_loop_ft: 8,
    cable_name: 'LMR-400 (generic)',
    input_power_w: 100,
    swr_at_antenna: 1.5,
    connector_loss_db: 0.1,
    site_objects: [],
    radial_count: 16,
    radial_length_ft: 0,
    remote_distance_km: 50,
    remote_height_ft: 20,
    tx_antenna_gain_dbi: 2.15,
    rx_antenna_gain_dbi: 2.15,
    other_system_loss_db: 0,
    propagation_model: PROPAGATION_MODELS.FREE_SPACE,
    terrain_profile: [],
    terrain_source: '',
    imported_pattern: [],
    pattern_source: '',
    network_data: [],
    network_source: '',
    geographic_path_enabled: false,
    tx_latitude_deg: 0,
    tx_longitude_deg: 0,
    rx_latitude_deg: 0,
    rx_longitude_deg: 0,
  };
}

/* ---------- geometry ---------- */

const normalizeBearing = (d) => ((d % 360) + 360) % 360;

function angularDifference(a, b) {
  return Math.abs((((a - b + 180) % 360) + 360) % 360 - 180);
}

function dipoleLengthFt(f) {
  if (f <= 0) throw new Error('Frequency must be greater than zero');
  return 468.0 / f;
}

function quarterWaveLengthFt(f) {
  if (f <= 0) throw new Error('Frequency must be greater than zero');
  return 234.0 / f;
}

const recommendedWireAzimuth = (target) => normalizeBearing(target - 90);

function distanceToSegment(p, a, b) {
  const dx = b.x - a.x;
  const dy = b.y - a.y;
  if (dx === 0 && dy === 0) return Math.hypot(p.x - a.x, p.y - a.y);
  let t = ((p.x - a.x) * dx + (p.y - a.y) * dy) / (dx * dx + dy * dy);
  t = Math.max(0, Math.min(1, t));
  return Math.hypot(p.x - (a.x + t * dx), p.y - (a.y + t * dy));
}

function pointInsideBoundary(point, site) {
  if (!(point.x >= 0 && point.x <= site.width_ft && point.y >= 0 && point.y <= site.depth_ft)) return false;
  const poly = site.boundary || [];
  if (poly.length < 3) return true;
  let inside = false;
  let previous = poly[poly.length - 1];
  for (const current of poly) {
    if ((current.y > point.y) !== (previous.y > point.y)) {
      const crossing = ((previous.x - current.x) * (point.y - current.y)) / (previous.y - current.y) + current.x;
      if (point.x < crossing) inside = !inside;
    }
    previous = current;
  }
  return inside;
}

function calculateDeployment(data) {
  const type = data.antenna_type;
  const totalWire = type === ANTENNA_TYPES.VERTICAL
    ? quarterWaveLengthFt(data.frequency_mhz)
    : dipoleLengthFt(data.frequency_mhz);
  const spec = specFor(type);
  const beam = spec.family === 'beam';
  const verticalFamily = spec.family === 'vertical';
  const twoLegged = type === ANTENNA_TYPES.DIPOLE || type === ANTENNA_TYPES.INVERTED_V || beam;
  const leg = twoLegged ? totalWire / 2 : totalWire;
  const wavelengthFt = 983.571 / data.frequency_mhz;
  const boomFt = beam ? spec.boom * wavelengthFt : 0;
  const drop = Math.max(0, data.feedpoint_height_ft - data.endpoint_height_ft);

  let horizontalLeg = 0;
  let apex = 0;
  let unrealizable = false;
  if (type === ANTENNA_TYPES.DIPOLE) {
    horizontalLeg = leg;
    apex = 180;
  } else if (type === ANTENNA_TYPES.INVERTED_V) {
    if (drop >= leg) {
      unrealizable = true;
    } else {
      horizontalLeg = Math.sqrt(leg * leg - drop * drop);
      apex = (Math.acos((drop * drop - horizontalLeg * horizontalLeg) / (leg * leg)) * 180) / Math.PI;
    }
  } else if (type === ANTENNA_TYPES.EFHW) {
    const rise = Math.abs(data.feedpoint_height_ft - data.endpoint_height_ft);
    if (rise >= totalWire) unrealizable = true;
    horizontalLeg = Math.sqrt(Math.max(0, totalWire * totalWire - rise * rise));
  } else if (beam) {
    horizontalLeg = leg;
    apex = 180;
  }

  // A beam's elements run across the boom, so its wire axis is the boom
  // heading turned ninety degrees.
  const elementAzimuth = beam
    ? normalizeBearing(data.wire_azimuth_deg + 90)
    : normalizeBearing(data.wire_azimuth_deg);
  const azimuth = (elementAzimuth * Math.PI) / 180;
  const east = Math.sin(azimuth);
  const north = Math.cos(azimuth);
  let endA;
  let endB;
  if (verticalFamily) {
    endA = { ...data.feedpoint };
    endB = { ...data.feedpoint };
  } else if (twoLegged) {
    endA = { x: data.feedpoint.x + east * horizontalLeg, y: data.feedpoint.y + north * horizontalLeg };
    endB = { x: data.feedpoint.x - east * horizontalLeg, y: data.feedpoint.y - north * horizontalLeg };
  } else {
    endA = { ...data.feedpoint };
    endB = { x: data.feedpoint.x + east * horizontalLeg, y: data.feedpoint.y + north * horizontalLeg };
  }

  const broadside = beam
    ? [normalizeBearing(data.wire_azimuth_deg), normalizeBearing(data.wire_azimuth_deg + 180)]
    : [normalizeBearing(data.wire_azimuth_deg + 90), normalizeBearing(data.wire_azimuth_deg - 90)];
  let alignmentError = 0;
  if (beam) alignmentError = angularDifference(data.target_bearing_deg, broadside[0]);
  else if (!verticalFamily) {
    alignmentError = Math.min(
      angularDifference(data.target_bearing_deg, broadside[0]),
      angularDifference(data.target_bearing_deg, broadside[1]),
    );
  }

  const horizontalCoax = Math.hypot(data.feedpoint.x - data.radio_position.x, data.feedpoint.y - data.radio_position.y);
  const requiredCoax = horizontalCoax + data.feedpoint_height_ft + data.service_loop_ft;
  const matched = matchedLossDb(data.cable_name, data.frequency_mhz, requiredCoax);
  const adjusted = swrAdjustedLossDb(matched, data.swr_at_antenna);
  const totalLoss = adjusted + data.connector_loss_db;
  const delivered = powerAfterLoss(data.input_power_w, totalLoss);
  const efficiency = data.input_power_w === 0 ? 0 : (delivered / data.input_power_w) * 100;

  const warnings = [];
  const checkPoints = verticalFamily
    ? [['Antenna base', data.feedpoint]]
    : [['Endpoint A', endA], ['Endpoint B', endB]];
  for (const [label, point] of checkPoints) {
    if (!pointInsideBoundary(point, data.site)) warnings.push(`${label} is outside the site boundary.`);
  }
  if (type === ANTENNA_TYPES.INVERTED_V && drop >= leg) {
    warnings.push('The selected vertical drop exceeds the available wire-leg length. This geometry has no physical solution.');
  }
  if (type === ANTENNA_TYPES.EFHW && Math.abs(data.feedpoint_height_ft - data.endpoint_height_ft) >= totalWire) {
    warnings.push('The selected height difference exceeds the available end-fed wire length.');
  }
  if (type === ANTENNA_TYPES.INVERTED_V && apex > 0 && apex < 90) {
    warnings.push('The inverted-V included apex angle is below 90 degrees.');
  }
  const effectiveEnd = (type === ANTENNA_TYPES.DIPOLE || beam) ? data.feedpoint_height_ft : data.endpoint_height_ft;
  if (!verticalFamily && effectiveEnd < 7) {
    warnings.push('An antenna endpoint is below the suggested 7 ft public-clearance threshold.');
  }
  if (beam && alignmentError > 20) {
    warnings.push(`The boom is ${alignmentError.toFixed(0)}° off the target — a beam only pays for itself when it is pointed.`);
  } else if (!verticalFamily && alignmentError > 25) {
    warnings.push("The target is poorly aligned with the wire's estimated broadside direction.");
  }
  if (totalLoss >= 1.5) {
    warnings.push('Estimated feed-system loss is at least 1.5 dB; consider a lower-loss or shorter line.');
  }
  for (const item of data.site_objects || []) {
    if (item.kind === OBJECT_KINDS.HAZARD && distanceToSegment(item.position, endA, endB) <= item.radius_ft) {
      warnings.push(`${item.label || 'A hazard/exclusion zone'} overlaps the antenna wire path.`);
    }
  }

  const radialLength = type === ANTENNA_TYPES.VERTICAL
    ? (data.radial_length_ft > 0 ? data.radial_length_ft : totalWire) : 0;

  return {
    total_wire_length_ft: totalWire,
    leg_length_ft: leg,
    horizontal_leg_ft: horizontalLeg,
    physical_span_ft: horizontalLeg * (twoLegged ? 2 : 1),
    endpoint_a: endA,
    endpoint_b: endB,
    broadside_bearings_deg: broadside,
    target_alignment_error_deg: alignmentError,
    included_apex_angle_deg: apex,
    horizontal_coax_route_ft: horizontalCoax,
    required_coax_length_ft: requiredCoax,
    matched_cable_loss_db: matched,
    swr_adjusted_cable_loss_db: adjusted,
    total_system_loss_db: totalLoss,
    power_at_antenna_w: delivered,
    efficiency_percent: efficiency,
    boom_length_ft: boomFt,
    element_azimuth_deg: elementAzimuth,
    radiator_height_ft: radiatorHeightFt(data, totalWire),
    takeoff_angle_deg: takeoffAngleDeg(type, radiatorHeightFt(data, totalWire), data.frequency_mhz, data.tx_antenna_gain_dbi),
    estimated_gain_dbi: spec.gain,
    gain_dbi: Number.isFinite(data.tx_antenna_gain_dbi) ? data.tx_antenna_gain_dbi : spec.gain,
    beamwidth_deg: beamwidthFor(type, data.tx_antenna_gain_dbi),
    is_beam: beam,
    radial_count: type === ANTENNA_TYPES.VERTICAL ? Math.max(0, data.radial_count) : 0,
    radial_length_ft: radialLength,
    is_omnidirectional: verticalFamily,
    unrealizable,
    warnings,
  };
}

/* ---------- feed line ---------- */

function logInterpolate(points, frequencyMhz) {
  if (frequencyMhz <= 0) throw new Error('Frequency must be greater than zero');
  const freqs = Object.keys(points).map(Number).sort((a, b) => a - b);
  if (frequencyMhz <= freqs[0]) return points[freqs[0]];
  if (frequencyMhz >= freqs[freqs.length - 1]) return points[freqs[freqs.length - 1]];
  for (let i = 0; i < freqs.length - 1; i += 1) {
    const low = freqs[i];
    const high = freqs[i + 1];
    if (frequencyMhz >= low && frequencyMhz <= high) {
      const portion = Math.log(frequencyMhz / low) / Math.log(high / low);
      return points[low] + portion * (points[high] - points[low]);
    }
  }
  throw new Error('Interpolation interval was not found');
}

function matchedLossDb(cableName, frequencyMhz, lengthFt) {
  if (lengthFt < 0) throw new Error('Cable length cannot be negative');
  const cable = CABLES[cableName];
  if (!cable) throw new Error(`Unknown cable: ${cableName}`);
  return (logInterpolate(cable, frequencyMhz) * lengthFt) / 100;
}

function swrAdjustedLossDb(matchedDb, swr) {
  if (matchedDb < 0) throw new Error('Matched loss cannot be negative');
  if (swr < 1) throw new Error('SWR must be at least 1:1');
  if (matchedDb === 0) return 0;
  const gamma = (swr - 1) / (swr + 1);
  const oneWay = 10 ** (-matchedDb / 10);
  const delivered = (oneWay * (1 - gamma ** 2)) / (1 - gamma ** 2 * oneWay ** 2);
  return -10 * Math.log10(delivered);
}

function powerAfterLoss(inputPowerW, lossDb) {
  if (inputPowerW < 0) throw new Error('Power cannot be negative');
  return inputPowerW * 10 ** (-lossDb / 10);
}

/* ---------- patterns and path loss ---------- */

/* Gain above the type's own estimate has to come from somewhere: for a beam or
   a wire it narrows the azimuth lobe, for an omni it squashes the elevation
   lobe. Passing no gain leaves the type's stock pattern alone. */
function gainRatio(antennaType, gainDbi) {
  const spec = specFor(antennaType);
  if (!Number.isFinite(gainDbi)) return 1;
  return Math.max(0.25, Math.min(40, 10 ** ((gainDbi - spec.gain) / 10)));
}

function beamwidthFor(antennaType, gainDbi) {
  const spec = specFor(antennaType);
  if (spec.family !== 'beam') return null;
  return Math.max(12, Math.min(170, spec.beamwidth / gainRatio(antennaType, gainDbi)));
}

function azimuthRelativeGainDb(antennaType, wireAzimuthDeg, bearingDeg, gainDbi) {
  const spec = specFor(antennaType);
  if (spec.family === 'vertical') return 0;
  const offset = angularDifference(bearingDeg, wireAzimuthDeg);
  const ratio = gainRatio(antennaType, gainDbi);
  if (spec.family === 'beam') {
    // Main lobe shaped to the quoted 3 dB beamwidth, standing on a floor set
    // by the quoted front-to-back. A plain cardioid can only satisfy one of the two.
    const back = 10 ** (-spec.fb / 20);
    const beamwidth = Math.max(12, Math.min(170, spec.beamwidth / ratio));
    const exponent = Math.log(Math.SQRT1_2) / Math.log(Math.cos((beamwidth / 4) * (Math.PI / 180)));
    const lobe = Math.max(0, Math.cos((offset * Math.PI) / 360)) ** (2 * exponent);
    const field = Math.sqrt(lobe + back * back) / Math.sqrt(1 + back * back);
    return 20 * Math.log10(Math.max(field, 0.001));
  }
  const relative = (offset * Math.PI) / 180;
  let shape = Math.abs(Math.sin(relative)) ** (2 * Math.max(1, ratio));
  if (antennaType === ANTENNA_TYPES.INVERTED_V) shape = 0.15 + 0.85 * shape;
  return 10 * Math.log10(Math.max(shape, 0.001));
}

/* Elevation pattern including the ground-reflection lobe, which is what
   actually decides take-off angle. Perfect-ground image theory: horizontal
   antennas take the sine factor, verticals the cosine. */
function elevationFieldAt(antennaType, heightFt, frequencyMhz, elevationDeg, sharpness) {
  const spec = specFor(antennaType);
  const alpha = (elevationDeg * Math.PI) / 180;
  const squash = Number.isFinite(sharpness) && sharpness > 0 ? Math.cos(alpha) ** sharpness : 1;
  const wavelengthM = 299.792458 / Math.max(frequencyMhz, 0.001);
  const heightLambda = (heightFt * FEET_TO_METERS) / wavelengthM;
  const phase = 2 * Math.PI * heightLambda * Math.sin(alpha);
  if (spec.polarization === 'V') {
    const cosAlpha = Math.cos(alpha);
    const element = Math.abs(cosAlpha) < 1e-6
      ? 0
      : Math.abs(Math.cos((Math.PI / 2) * Math.sin(alpha)) / cosAlpha);
    return element * squash * 2 * Math.abs(Math.cos(phase));
  }
  return squash * 2 * Math.abs(Math.sin(phase));
}

/* Solve for the elevation squash exponent that turns the stock pattern into
   one with the requested extra directivity. Numeric, so it stays honest. */
function elevationSharpnessFor(antennaType, heightFt, frequencyMhz, gainDbi) {
  const spec = specFor(antennaType);
  if (spec.family !== 'vertical') return 0;
  const wanted = gainRatio(antennaType, gainDbi);
  if (wanted <= 1.02) return 0;
  const directivity = (sharpness) => {
    let peak = 0;
    const field = [];
    for (let deg = 0; deg <= 90; deg += 1) {
      const value = elevationFieldAt(antennaType, heightFt, frequencyMhz, deg, sharpness);
      peak = Math.max(peak, value);
      field.push(value);
    }
    if (peak <= 0) return 1;
    let integral = 0;
    for (let deg = 0; deg <= 90; deg += 1) {
      const normalized = field[deg] / peak;
      integral += normalized * normalized * Math.cos((deg * Math.PI) / 180) * (Math.PI / 180);
    }
    return integral > 0 ? 2 / integral : 1;
  };
  const reference = directivity(0);
  let low = 0;
  let high = 24;
  for (let step = 0; step < 24; step += 1) {
    const mid = (low + high) / 2;
    if (directivity(mid) / reference < wanted) low = mid; else high = mid;
  }
  return (low + high) / 2;
}

function elevationPattern(antennaType, heightFt, frequencyMhz, stepDeg = 1, gainDbi) {
  const sharpness = elevationSharpnessFor(antennaType, heightFt, frequencyMhz, gainDbi);
  const samples = [];
  let peak = 0;
  for (let elevation = 0; elevation <= 90; elevation += stepDeg) {
    const field = elevationFieldAt(antennaType, heightFt, frequencyMhz, elevation, sharpness);
    peak = Math.max(peak, field);
    samples.push({ elevation_deg: elevation, field });
  }
  const floor = 10 ** (-30 / 20);
  return samples.map((sample) => ({
    elevation_deg: sample.elevation_deg,
    relative_gain_db: 20 * Math.log10(Math.max(peak > 0 ? sample.field / peak : 0, floor)),
  }));
}

/* Over a perfect reflector a horizontal wire's elevation lobes are all the same
   height, so "the strongest sample wins" returns whichever lobe the sample grid
   happens to favour and the answer jumps around with height. Take-off angle
   conventionally means the lowest lobe, the one that works DX, so find the peak
   and then return the first lobe that reaches it. */
function takeoffAngleDeg(antennaType, heightFt, frequencyMhz, gainDbi) {
  const sharpness = elevationSharpnessFor(antennaType, heightFt, frequencyMhz, gainDbi);
  const step = 0.25;
  const field = [];
  let peak = 0;
  for (let elevation = 0; elevation <= 90 + 1e-9; elevation += step) {
    const value = elevationFieldAt(antennaType, heightFt, frequencyMhz, elevation, sharpness);
    field.push({ elevation, value });
    if (value > peak) peak = value;
  }
  if (peak <= 0) return 0;
  const threshold = peak * 10 ** (-0.25 / 20);   // within a quarter of a dB of the peak
  for (let i = 0; i < field.length; i += 1) {
    if (field[i].value < threshold) continue;
    const prev = i > 0 ? field[i - 1].value : -Infinity;
    const next = i < field.length - 1 ? field[i + 1].value : -Infinity;
    if (field[i].value >= prev && field[i].value >= next) return field[i].elevation;
  }
  return field.reduce((a, b) => (b.value > a.value ? b : a)).elevation;
}

/* Height of the radiating centre above ground, which is what the ground
   reflection is referenced to. */
function radiatorHeightFt(plan, totalWireFt) {
  if (plan.antenna_type === ANTENNA_TYPES.VERTICAL) {
    return plan.feedpoint_height_ft + (totalWireFt || 0) / 2;
  }
  if (plan.antenna_type === ANTENNA_TYPES.INVERTED_V) {
    return plan.feedpoint_height_ft * 0.7 + plan.endpoint_height_ft * 0.3;
  }
  if (plan.antenna_type === ANTENNA_TYPES.EFHW) {
    return (plan.feedpoint_height_ft + plan.endpoint_height_ft) / 2;
  }
  return plan.feedpoint_height_ft;
}

function interpolatePattern(points, bearingDeg) {
  const ordered = points
    .map((p) => [normalizeBearing(p.bearing_deg), p.relative_gain_db])
    .sort((a, b) => a[0] - b[0]);
  const bearing = normalizeBearing(bearingDeg);
  const last = ordered[ordered.length - 1];
  const extended = [[last[0] - 360, last[1]], ...ordered, [ordered[0][0] + 360, ordered[0][1]]];
  for (let i = 0; i < extended.length - 1; i += 1) {
    const [b0, g0] = extended[i];
    const [b1, g1] = extended[i + 1];
    if (b0 <= bearing && bearing <= b1) {
      const span = Math.max(b1 - b0, 1e-9);
      return g0 + ((bearing - b0) / span) * (g1 - g0);
    }
  }
  return ordered[0][1];
}

function patternRelativeGainDb(data, bearingDeg) {
  if (data.imported_pattern && data.imported_pattern.length) return interpolatePattern(data.imported_pattern, bearingDeg);
  return azimuthRelativeGainDb(data.antenna_type, data.wire_azimuth_deg, bearingDeg, data.tx_antenna_gain_dbi);
}

function patternForData(data, stepDeg = 2) {
  const out = [];
  for (let bearing = 0; bearing <= 360; bearing += stepDeg) {
    out.push({ bearing_deg: bearing, relative_gain_db: patternRelativeGainDb(data, bearing) });
  }
  return out;
}

function elevationRelativeGainDb(elevationDeg) {
  if (elevationDeg < 0 || elevationDeg > 90) throw new Error('Elevation must be between 0 and 90 degrees');
  const alpha = (elevationDeg * Math.PI) / 180;
  if (Math.abs(Math.cos(alpha)) < 1e-9) return -30;
  const field = Math.abs(Math.cos((Math.PI / 2) * Math.sin(alpha)) / Math.cos(alpha));
  return 20 * Math.log10(Math.max(field, 0.0316227766));
}

function freeSpacePathLossDb(frequencyMhz, distanceKm) {
  if (frequencyMhz <= 0 || distanceKm <= 0) throw new Error('Frequency and distance must be greater than zero');
  return 32.4478 + 20 * Math.log10(frequencyMhz) + 20 * Math.log10(distanceKm);
}

function radioHorizonKm(txHeightFt, rxHeightFt, effectiveEarth = true) {
  if (txHeightFt < 0 || rxHeightFt < 0) throw new Error('Antenna heights cannot be negative');
  const k = effectiveEarth ? 4.12 : 3.57;
  return k * (Math.sqrt(txHeightFt * FEET_TO_METERS) + Math.sqrt(rxHeightFt * FEET_TO_METERS));
}

function firstFresnelMidpointM(frequencyMhz, distanceKm) {
  if (frequencyMhz <= 0 || distanceKm <= 0) throw new Error('Frequency and distance must be greater than zero');
  const wavelength = SPEED_OF_LIGHT_M_S / (frequencyMhz * 1e6);
  return Math.sqrt((wavelength * distanceKm * 1000) / 4);
}

const EMPTY_TERRAIN = {
  diffraction_loss_db: 0,
  worst_distance_km: 0,
  worst_clearance_m: 0,
  worst_fresnel_radius_m: 0,
  obstruction_v: -Infinity,
};

function terrainPathAnalysis(data) {
  const profile = data.terrain_profile || [];
  if (profile.length < 2) return EMPTY_TERRAIN;
  const points = [...profile].sort((a, b) => a.distance_km - b.distance_km);
  const totalM = points[points.length - 1].distance_km * 1000;
  if (totalM <= 0) return EMPTY_TERRAIN;
  const wavelength = SPEED_OF_LIGHT_M_S / (data.frequency_mhz * 1e6);
  const txM = points[0].elevation_m + data.feedpoint_height_ft * FEET_TO_METERS;
  const rxM = points[points.length - 1].elevation_m + data.remote_height_ft * FEET_TO_METERS;
  const earthRadius = (4 / 3) * 6371000;
  let worstV = -Infinity;
  let worstDistance = 0;
  let worstClearance = 0;
  let worstFresnel = 0;
  for (const point of points.slice(1, -1)) {
    const d1 = point.distance_km * 1000;
    const d2 = totalM - d1;
    if (d1 <= 0 || d2 <= 0) continue;
    const lineHeight = txM + (rxM - txM) * (d1 / totalM);
    const bulge = (d1 * d2) / (2 * earthRadius);
    const effective = point.elevation_m + bulge;
    const obstruction = effective - lineHeight;
    const fresnel = Math.sqrt((wavelength * d1 * d2) / totalM);
    const v = obstruction * Math.sqrt((2 / wavelength) * (1 / d1 + 1 / d2));
    if (v > worstV) {
      worstV = v;
      worstDistance = point.distance_km;
      worstClearance = lineHeight - effective;
      worstFresnel = fresnel;
    }
  }
  const loss = worstV === -Infinity || worstV <= -0.78
    ? 0
    : 6.9 + 20 * Math.log10(Math.sqrt((worstV - 0.1) ** 2 + 1) + worstV - 0.1);
  return {
    diffraction_loss_db: loss,
    worst_distance_km: worstDistance,
    worst_clearance_m: worstClearance,
    worst_fresnel_radius_m: worstFresnel,
    obstruction_v: worstV,
  };
}

function objectRadiusFt(item) {
  if ([OBJECT_KINDS.BUILDING, OBJECT_KINDS.VEHICLE, OBJECT_KINDS.METAL_STRUCTURE].includes(item.kind)) {
    return Math.hypot(item.width_ft, item.depth_ft) / 2;
  }
  return item.radius_ft;
}

/* Height-aware shadowing. An object only obstructs if its top reaches the
   line of sight at the point where the ray passes it, with a soft edge as the
   ray grazes the top. endHeightFt is the height of the far end of the ray. */
function pathObstructionLossDb(data, pathEnd, endHeightFt) {
  const feedHeight = data.feedpoint_height_ft;
  const farHeight = Number.isFinite(endHeightFt) ? endHeightFt : 6.0;
  let loss = 0;
  for (const item of data.site_objects || []) {
    const fallback = DEFAULT_OBJECT_ATTENUATION_DB[item.kind];
    if (fallback === undefined) continue;
    if (distanceToSegment(item.position, data.feedpoint, pathEnd) > objectRadiusFt(item)) continue;
    const top = objectHeightFt(item);
    if (top <= 0) continue;
    const fraction = projectionFraction(item.position, data.feedpoint, pathEnd);
    const rayHeight = feedHeight + (farHeight - feedHeight) * fraction;
    const attenuation = item.attenuation_db > 0 ? item.attenuation_db : fallback;
    if (top >= rayHeight) { loss += attenuation; continue; }
    const clearance = rayHeight - top;
    const soft = Math.max(6.0, top * 0.25);
    if (clearance < soft) loss += attenuation * (1 - clearance / soft) * 0.5;
  }
  return loss;
}

function installationShadowLossDb(data, bearingDeg) {
  const distance = Math.hypot(data.site.width_ft, data.site.depth_ft) * 2;
  const angle = (bearingDeg * Math.PI) / 180;
  // A distant station sits near the horizon, so the ray leaves at feed height
  // and stays there across the site: only things taller than the feed shadow it.
  return pathObstructionLossDb(data, {
    x: data.feedpoint.x + Math.sin(angle) * distance,
    y: data.feedpoint.y + Math.cos(angle) * distance,
  }, data.feedpoint_height_ft);
}

function calculateLinkBudget(data, deliveredPowerW) {
  const freeSpace = freeSpacePathLossDb(data.frequency_mhz, data.remote_distance_km);
  const terrain = terrainPathAnalysis(data);
  const terrainLoss = data.propagation_model === PROPAGATION_MODELS.TERRAIN_KNIFE_EDGE ? terrain.diffraction_loss_db : 0;
  const pathLoss = freeSpace + terrainLoss;
  const direction = patternRelativeGainDb(data, data.target_bearing_deg);
  const installation = installationShadowLossDb(data, data.target_bearing_deg);
  const txDbm = 10 * Math.log10(Math.max(deliveredPowerW, 1e-12) * 1000);
  const horizon = radioHorizonKm(data.feedpoint_height_ft, data.remote_height_ft);
  return {
    free_space_loss_db: freeSpace,
    terrain_diffraction_loss_db: terrainLoss,
    total_path_loss_db: pathLoss,
    propagation_model: data.propagation_model,
    directional_adjustment_db: direction,
    installation_loss_db: installation,
    received_power_dbm: txDbm + data.tx_antenna_gain_dbi + direction + data.rx_antenna_gain_dbi
      - pathLoss - installation - data.other_system_loss_db,
    radio_horizon_km: horizon,
    within_radio_horizon: data.remote_distance_km <= horizon,
    first_fresnel_midpoint_m: firstFresnelMidpointM(data.frequency_mhz, data.remote_distance_km),
  };
}

/* ---------- geodesy ---------- */

function validateCoordinate(lat, lon) {
  if (!(lat >= -90 && lat <= 90)) throw new Error('Latitude must be between -90 and 90 degrees');
  if (!(lon >= -180 && lon <= 180)) throw new Error('Longitude must be between -180 and 180 degrees');
}

function haversineDistanceKm(txLat, txLon, rxLat, rxLon) {
  validateCoordinate(txLat, txLon);
  validateCoordinate(rxLat, rxLon);
  const toRad = Math.PI / 180;
  const lat1 = txLat * toRad;
  const lat2 = rxLat * toRad;
  const dLat = lat2 - lat1;
  const dLon = (rxLon - txLon) * toRad;
  const a = Math.sin(dLat / 2) ** 2 + Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLon / 2) ** 2;
  return EARTH_RADIUS_KM * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(Math.max(0, 1 - a)));
}

function initialBearingDeg(txLat, txLon, rxLat, rxLon) {
  validateCoordinate(txLat, txLon);
  validateCoordinate(rxLat, rxLon);
  const toRad = Math.PI / 180;
  const lat1 = txLat * toRad;
  const lat2 = rxLat * toRad;
  const dLon = (rxLon - txLon) * toRad;
  const x = Math.sin(dLon) * Math.cos(lat2);
  const y = Math.cos(lat1) * Math.sin(lat2) - Math.sin(lat1) * Math.cos(lat2) * Math.cos(dLon);
  if (Math.abs(x) < 1e-15 && Math.abs(y) < 1e-15) {
    throw new Error('Transmitter and receiver coordinates must be different');
  }
  return normalizeBearing((Math.atan2(x, y) * 180) / Math.PI);
}

const HGT_NAME = /^([NS])(\d{2})([EW])(\d{3})\.hgt$/i;

function terrainProfileFromHgt(fileName, buffer, txLat, txLon, rxLat, rxLon, sampleCount = 201) {
  const match = HGT_NAME.exec(fileName);
  if (!match) throw new Error('HGT filename must identify its tile, for example N32W081.hgt');
  const south = (match[1].toUpperCase() === 'N' ? 1 : -1) * parseInt(match[2], 10);
  const west = (match[3].toUpperCase() === 'E' ? 1 : -1) * parseInt(match[4], 10);
  for (const [lat, lon] of [[txLat, txLon], [rxLat, rxLon]]) {
    validateCoordinate(lat, lon);
    if (!(lat >= south && lat <= south + 1) || !(lon >= west && lon <= west + 1)) {
      throw new Error('Both path endpoints must be inside the selected one-degree HGT tile');
    }
  }
  if (buffer.byteLength % 2) throw new Error('Invalid HGT byte count');
  const sampleTotal = buffer.byteLength / 2;
  const dimension = Math.round(Math.sqrt(sampleTotal));
  if (dimension < 2 || dimension * dimension !== sampleTotal) {
    throw new Error('HGT file must contain a square grid of 16-bit elevation samples');
  }
  const view = new DataView(buffer);
  const distanceKm = haversineDistanceKm(txLat, txLon, rxLat, rxLon);
  if (distanceKm <= 0) throw new Error('Transmitter and receiver coordinates must be different');

  const sample = (lat, lon) => {
    const row = Math.min(dimension - 1, Math.max(0, Math.round((south + 1 - lat) * (dimension - 1))));
    const col = Math.min(dimension - 1, Math.max(0, Math.round((lon - west) * (dimension - 1))));
    const value = view.getInt16((row * dimension + col) * 2, false); // SRTM is big-endian
    if (value === -32768) throw new Error('Selected HGT path crosses a void elevation sample');
    return value;
  };

  const profile = [];
  for (let i = 0; i < sampleCount; i += 1) {
    const fraction = i / (sampleCount - 1);
    profile.push({
      distance_km: distanceKm * fraction,
      elevation_m: sample(txLat + (rxLat - txLat) * fraction, txLon + (rxLon - txLon) * fraction),
    });
  }
  return profile;
}

/* ---------- imports ---------- */

function parseCsv(text) {
  const lines = text.replace(/^\uFEFF/, '').split(/\r?\n/).filter((line) => line.trim());
  if (!lines.length) return { headers: [], rows: [] };
  const headers = lines[0].split(',').map((name) => name.trim().toLowerCase());
  const rows = lines.slice(1).map((line) => {
    const cells = line.split(',');
    const row = {};
    headers.forEach((name, index) => { row[name] = (cells[index] || '').trim(); });
    return row;
  });
  return { headers, rows };
}

function importTerrainCsv(text) {
  const { headers, rows } = parseCsv(text);
  const distanceKey = headers.includes('distance_km') ? 'distance_km' : (headers.includes('distance') ? 'distance' : null);
  const elevationKey = headers.includes('elevation_m') ? 'elevation_m' : (headers.includes('elevation') ? 'elevation' : null);
  if (!distanceKey || !elevationKey) throw new Error('Terrain CSV needs distance_km and elevation_m columns');
  let points = rows
    .filter((row) => row[distanceKey] && row[elevationKey])
    .map((row) => ({ distance_km: Number(row[distanceKey]), elevation_m: Number(row[elevationKey]) }));
  if (points.some((p) => !Number.isFinite(p.distance_km) || !Number.isFinite(p.elevation_m))) {
    throw new Error('Terrain CSV contains a value that is not a number');
  }
  if (points.length < 2) throw new Error('Terrain profile needs at least two points');
  points = points.sort((a, b) => a.distance_km - b.distance_km);
  const bad = points[0].distance_km < 0
    || points.some((point, index) => index > 0 && point.distance_km <= points[index - 1].distance_km);
  if (bad) throw new Error('Terrain distances must be unique, increasing, and non-negative');
  return points;
}

function importPatternCsv(text) {
  const { headers, rows } = parseCsv(text);
  const bearingKey = ['bearing_deg', 'azimuth_deg', 'angle_deg'].find((name) => headers.includes(name));
  const gainKey = ['relative_gain_db', 'gain_db', 'gain_dbi', 'estimated_gain_dbi'].find((name) => headers.includes(name));
  if (!bearingKey || !gainKey) throw new Error('Pattern CSV needs bearing_deg and a gain column');
  const unique = new Map();
  for (const row of rows) {
    if (!row[bearingKey] || !row[gainKey]) continue;
    const bearing = normalizeBearing(Number(row[bearingKey]));
    const gain = Number(row[gainKey]);
    if (!Number.isFinite(bearing) || !Number.isFinite(gain)) continue;
    unique.set(bearing, gain);
  }
  if (unique.size < 3) throw new Error('Radiation pattern needs at least three samples');
  const peak = Math.max(...unique.values());
  return [...unique.entries()]
    .sort((a, b) => a[0] - b[0])
    .map(([bearing, gain]) => ({ bearing_deg: bearing, relative_gain_db: Math.max(-60, gain - peak) }));
}

function importTouchstone(fileName, text) {
  const suffix = fileName.toLowerCase().slice(fileName.lastIndexOf('.'));
  if (suffix !== '.s1p' && suffix !== '.s2p') {
    throw new Error('Only one-port and two-port Touchstone files (.s1p/.s2p) are supported');
  }
  const perRecord = suffix === '.s1p' ? 3 : 9;
  let scale = 1;
  let format = 'MA';
  const tokens = [];
  const records = [];
  for (const original of text.split(/\r?\n/)) {
    const line = original.split('!')[0].trim();
    if (!line) continue;
    if (line.startsWith('#')) {
      const parts = line.slice(1).split(/\s+/).map((t) => t.toUpperCase());
      const units = { HZ: 1e-6, KHZ: 1e-3, MHZ: 1, GHZ: 1e3 };
      const unit = Object.keys(units).find((name) => parts.includes(name));
      scale = unit ? units[unit] : 1;
      format = ['RI', 'MA', 'DB'].find((name) => parts.includes(name)) || 'MA';
      if (['Y', 'Z', 'H', 'G'].some((name) => parts.includes(name))) {
        throw new Error('Touchstone import currently supports S-parameters only');
      }
      continue;
    }
    if (line.startsWith('[')) continue;
    for (const token of line.split(/\s+/)) {
      const value = Number(token.replace(/[Dd]/, 'e'));
      if (!Number.isFinite(value)) throw new Error(`Invalid Touchstone numeric data: ${original}`);
      tokens.push(value);
    }
    while (tokens.length >= perRecord) {
      const record = tokens.splice(0, perRecord);
      let magnitude;
      if (format === 'RI') magnitude = Math.hypot(record[1], record[2]);
      else if (format === 'MA') magnitude = Math.abs(record[1]);
      else magnitude = 10 ** (record[1] / 20);
      magnitude = Math.max(0, magnitude);
      records.push({
        frequency_mhz: record[0] * scale,
        s11_magnitude: magnitude,
        return_loss_db: -20 * Math.log10(Math.max(magnitude, 1e-12)),
        swr: magnitude < 1 ? (1 + magnitude) / Math.max(1e-9, 1 - magnitude) : 999,
      });
    }
  }
  if (tokens.length) throw new Error('Incomplete Touchstone data record');
  if (!records.length) throw new Error('Touchstone file contains no S-parameter records');
  return records;
}

/* ---------- plan files ---------- */

const CLASSIC_EQUIVALENT = {
  'Vertical half-wave dipole': 'Quarter-wave vertical',
  '2-element Yagi': 'Horizontal dipole',
  '3-element Yagi': 'Horizontal dipole',
  'Moxon rectangle': 'Horizontal dipole',
};

function planFromProjectFile(raw) {
  if (raw.format_version !== 1) throw new Error('Unsupported project-file version');
  const plan = { ...defaultPlan() };
  const num = (value, fallback) => (Number.isFinite(Number(value)) ? Number(value) : fallback);
  plan.frequency_mhz = num(raw.frequency_mhz, plan.frequency_mhz);
  // 0.6 desktop only knows the four classic types, so the real one travels in
  // its own key and antenna_type carries the nearest classic equivalent.
  plan.antenna_type = ANTENNA_SPECS[raw.planner_antenna_type] ? raw.planner_antenna_type : raw.antenna_type;
  plan.site = {
    width_ft: num(raw.site.width_ft, 120),
    depth_ft: num(raw.site.depth_ft, 100),
    boundary: (raw.site.boundary || []).map((p) => ({ x: Number(p.x), y: Number(p.y) })),
  };
  plan.feedpoint = { x: Number(raw.feedpoint.x), y: Number(raw.feedpoint.y) };
  plan.radio_position = { x: Number(raw.radio_position.x), y: Number(raw.radio_position.y) };
  for (const key of [
    'feedpoint_height_ft', 'endpoint_height_ft', 'wire_azimuth_deg', 'target_bearing_deg',
    'service_loop_ft', 'input_power_w', 'swr_at_antenna', 'connector_loss_db',
    'radial_count', 'radial_length_ft', 'remote_distance_km', 'remote_height_ft',
    'tx_antenna_gain_dbi', 'rx_antenna_gain_dbi', 'other_system_loss_db',
    'tx_latitude_deg', 'tx_longitude_deg', 'rx_latitude_deg', 'rx_longitude_deg',
  ]) {
    plan[key] = num(raw[key], plan[key]);
  }
  plan.cable_name = CABLES[raw.cable_name] ? raw.cable_name : plan.cable_name;
  plan.propagation_model = raw.propagation_model || plan.propagation_model;
  plan.geographic_path_enabled = Boolean(raw.geographic_path_enabled);
  plan.terrain_source = raw.terrain_source || '';
  plan.pattern_source = raw.pattern_source || '';
  plan.network_source = raw.network_source || '';
  plan.terrain_profile = (raw.terrain_profile || []).map((p) => ({
    distance_km: Number(p.distance_km), elevation_m: Number(p.elevation_m),
  })).sort((a, b) => a.distance_km - b.distance_km);
  if (plan.terrain_profile.length === 1) throw new Error('A stored terrain profile needs at least two points');
  if (plan.terrain_profile.some((p, i) => i > 0 && p.distance_km <= plan.terrain_profile[i - 1].distance_km)) {
    throw new Error('Stored terrain distances must be unique and increasing');
  }
  plan.imported_pattern = (raw.imported_pattern || []).map((p) => ({
    bearing_deg: Number(p.bearing_deg), relative_gain_db: Number(p.relative_gain_db),
  }));
  plan.network_data = (raw.network_data || []).map((p) => ({
    frequency_mhz: Number(p.frequency_mhz),
    s11_magnitude: Number(p.s11_magnitude),
    return_loss_db: Number(p.return_loss_db),
    swr: Number(p.swr),
  }));
  plan.site_objects = (raw.site_objects || []).map((item) => ({
    kind: item.kind,
    position: { x: Number(item.position.x), y: Number(item.position.y) },
    radius_ft: num(item.radius_ft, 6),
    label: item.label || '',
    width_ft: num(item.width_ft, 12),
    depth_ft: num(item.depth_ft, 12),
    orientation_deg: num(item.orientation_deg, 0),
    attenuation_db: num(item.attenuation_db, 0),
    height_ft: num(item.height_ft, DEFAULT_OBJECT_HEIGHT_FT[item.kind] || 0),
  }));
  return plan;
}

function planToProjectFile(plan) {
  return {
    format_version: 1,
    frequency_mhz: plan.frequency_mhz,
    antenna_type: CLASSIC_EQUIVALENT[plan.antenna_type] || plan.antenna_type,
    planner_antenna_type: plan.antenna_type,
    site: {
      width_ft: plan.site.width_ft,
      depth_ft: plan.site.depth_ft,
      boundary: plan.site.boundary.map((p) => ({ x: p.x, y: p.y })),
    },
    feedpoint: { x: plan.feedpoint.x, y: plan.feedpoint.y },
    feedpoint_height_ft: plan.feedpoint_height_ft,
    endpoint_height_ft: plan.endpoint_height_ft,
    wire_azimuth_deg: plan.wire_azimuth_deg,
    target_bearing_deg: plan.target_bearing_deg,
    radio_position: { x: plan.radio_position.x, y: plan.radio_position.y },
    service_loop_ft: plan.service_loop_ft,
    cable_name: plan.cable_name,
    input_power_w: plan.input_power_w,
    swr_at_antenna: plan.swr_at_antenna,
    connector_loss_db: plan.connector_loss_db,
    radial_count: plan.radial_count,
    radial_length_ft: plan.radial_length_ft,
    remote_distance_km: plan.remote_distance_km,
    remote_height_ft: plan.remote_height_ft,
    tx_antenna_gain_dbi: plan.tx_antenna_gain_dbi,
    rx_antenna_gain_dbi: plan.rx_antenna_gain_dbi,
    other_system_loss_db: plan.other_system_loss_db,
    propagation_model: plan.propagation_model,
    terrain_source: plan.terrain_source,
    terrain_profile: plan.terrain_profile.map((p) => ({ distance_km: p.distance_km, elevation_m: p.elevation_m })),
    pattern_source: plan.pattern_source,
    imported_pattern: plan.imported_pattern.map((p) => ({ bearing_deg: p.bearing_deg, relative_gain_db: p.relative_gain_db })),
    network_source: plan.network_source,
    network_data: plan.network_data.map((p) => ({
      frequency_mhz: p.frequency_mhz,
      s11_magnitude: p.s11_magnitude,
      return_loss_db: p.return_loss_db,
      swr: p.swr,
    })),
    geographic_path_enabled: plan.geographic_path_enabled,
    tx_latitude_deg: plan.tx_latitude_deg,
    tx_longitude_deg: plan.tx_longitude_deg,
    rx_latitude_deg: plan.rx_latitude_deg,
    rx_longitude_deg: plan.rx_longitude_deg,
    itm_climate: 5,
    itm_refractivity_n: 301,
    itm_ground_permittivity: 15,
    itm_ground_conductivity_s_m: 0.005,
    itm_confidence_pct: 50,
    itm_reliability_pct: 50,
    itm_polarization: 'Horizontal',
    site_objects: plan.site_objects.map((item) => ({
      kind: item.kind,
      position: { x: item.position.x, y: item.position.y },
      radius_ft: item.radius_ft,
      label: item.label,
      width_ft: item.width_ft,
      depth_ft: item.depth_ft,
      orientation_deg: item.orientation_deg,
      attenuation_db: item.attenuation_db,
      height_ft: item.height_ft,
    })),
  };
}

/* ---------- SRTM tiles: naming, stitching, caching ---------- */

function tileNameFor(lat, lon) {
  const ns = lat < 0 ? 'S' : 'N';
  const ew = lon < 0 ? 'W' : 'E';
  const la = String(Math.abs(Math.floor(lat))).padStart(2, '0');
  const lo = String(Math.abs(Math.floor(lon))).padStart(3, '0');
  return `${ns}${la}${ew}${lo}.hgt`;
}

function pathSamplePoints(txLat, txLon, rxLat, rxLon, sampleCount) {
  const points = [];
  for (let i = 0; i < sampleCount; i += 1) {
    const f = sampleCount === 1 ? 0 : i / (sampleCount - 1);
    points.push([txLat + (rxLat - txLat) * f, txLon + (rxLon - txLon) * f]);
  }
  return points;
}

// An endpoint left at exactly 0,0 is unset, not a position in the Gulf of Guinea.
function endpointIsSet(lat, lon) {
  return Number.isFinite(lat) && Number.isFinite(lon) && (Math.abs(lat) > 1e-6 || Math.abs(lon) > 1e-6);
}

function pathEndpointsReady(txLat, txLon, rxLat, rxLon) {
  return endpointIsSet(txLat, txLon)
    && endpointIsSet(rxLat, rxLon)
    && (Math.abs(txLat - rxLat) > 1e-9 || Math.abs(txLon - rxLon) > 1e-9);
}

function requiredTiles(txLat, txLon, rxLat, rxLon, sampleCount = 201) {
  if (!pathEndpointsReady(txLat, txLon, rxLat, rxLon)) return [];
  const names = new Set();
  for (const [lat, lon] of pathSamplePoints(txLat, txLon, rxLat, rxLon, sampleCount)) {
    names.add(tileNameFor(lat, lon));
  }
  return [...names].sort();
}

function parseHgtTile(fileName, buffer) {
  const match = HGT_NAME.exec(fileName);
  if (!match) throw new Error(`${fileName} is not named like N32W081.hgt`);
  if (buffer.byteLength % 2) throw new Error(`${fileName}: odd byte count`);
  const total = buffer.byteLength / 2;
  const dimension = Math.round(Math.sqrt(total));
  if (dimension < 2 || dimension * dimension !== total) {
    throw new Error(`${fileName}: not a square grid of 16-bit samples`);
  }
  return {
    name: `${match[1].toUpperCase()}${match[2]}${match[3].toUpperCase()}${match[4]}.hgt`,
    south: (match[1].toUpperCase() === 'N' ? 1 : -1) * parseInt(match[2], 10),
    west: (match[3].toUpperCase() === 'E' ? 1 : -1) * parseInt(match[4], 10),
    dimension,
    bytes: buffer.byteLength,
    arcSeconds: dimension === 3601 ? 1 : (dimension === 1201 ? 3 : Math.max(1, Math.round(3600 / (dimension - 1)))),
    view: new DataView(buffer),
  };
}

function sampleTile(tile, lat, lon) {
  const row = Math.min(tile.dimension - 1, Math.max(0, Math.round((tile.south + 1 - lat) * (tile.dimension - 1))));
  const col = Math.min(tile.dimension - 1, Math.max(0, Math.round((lon - tile.west) * (tile.dimension - 1))));
  const value = tile.view.getInt16((row * tile.dimension + col) * 2, false); // SRTM is big-endian
  return value === -32768 ? null : value;
}

function fillGaps(values, label) {
  const known = values.map((v, i) => (v === null ? -1 : i)).filter((i) => i >= 0);
  if (!known.length) throw new Error(`${label} returned no usable elevations for this path`);
  return values.map((value, index) => {
    if (value !== null) return value;
    let before = null;
    let after = null;
    for (const i of known) { if (i < index) before = i; else { after = i; break; } }
    if (before === null) return values[after];
    if (after === null) return values[before];
    const f = (index - before) / (after - before);
    return values[before] + (values[after] - values[before]) * f;
  });
}

function terrainProfileFromTiles(tiles, txLat, txLon, rxLat, rxLon, sampleCount = 201) {
  const byName = new Map(tiles.map((tile) => [tile.name.toUpperCase(), tile]));
  const distanceKm = haversineDistanceKm(txLat, txLon, rxLat, rxLon);
  if (distanceKm <= 0) throw new Error('Transmitter and receiver coordinates must be different');
  const missing = new Set();
  const raw = [];
  for (const [lat, lon] of pathSamplePoints(txLat, txLon, rxLat, rxLon, sampleCount)) {
    const name = tileNameFor(lat, lon);
    const tile = byName.get(name.toUpperCase());
    if (!tile) { missing.add(name); raw.push(null); continue; }
    raw.push(sampleTile(tile, lat, lon));
  }
  if (missing.size) {
    // Name a few; a path needing dozens means the coordinates are wrong, and a
    // wall of filenames buries that.
    const all = [...missing].sort();
    const shown = all.slice(0, 4).join(', ');
    const rest = all.length > 4 ? `, and ${all.length - 4} more` : '';
    throw new Error(`Missing ${all.length} terrain tile${all.length === 1 ? '' : 's'}: ${shown}${rest}.`);
  }
  const filled = fillGaps(raw, 'The selected tiles');
  return filled.map((elevation, index) => ({
    distance_km: (distanceKm * index) / (sampleCount - 1),
    elevation_m: elevation,
  }));
}

/* Online elevation: USGS 3DEP, which covers CONUS, Alaska, Hawaii and the
   island territories. One POST returns the whole profile. */
const USGS_3DEP_SAMPLES = 'https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/getSamples';

async function fetchProfileFrom3DEP(txLat, txLon, rxLat, rxLon, sampleCount = 201) {
  const distanceKm = haversineDistanceKm(txLat, txLon, rxLat, rxLon);
  if (distanceKm <= 0) throw new Error('Transmitter and receiver coordinates must be different');
  const points = pathSamplePoints(txLat, txLon, rxLat, rxLon, sampleCount).map(([lat, lon]) => [lon, lat]);
  const body = new URLSearchParams({
    geometry: JSON.stringify({ points, spatialReference: { wkid: 4326 } }),
    geometryType: 'esriGeometryMultipoint',
    returnFirstValueOnly: 'true',
    interpolation: 'RSP_BilinearInterpolation',
    f: 'json',
  });
  const response = await fetch(USGS_3DEP_SAMPLES, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: body.toString(),
  });
  if (!response.ok) throw new Error(`USGS 3DEP returned ${response.status}`);
  const payload = await response.json();
  if (payload.error) throw new Error(payload.error.message || 'USGS 3DEP refused the request');
  const byIndex = new Map();
  for (const sample of payload.samples || []) {
    const value = Number(sample.value);
    if (Number.isFinite(value) && value > -9000) byIndex.set(Number(sample.locationId), value);
  }
  if (byIndex.size < 2) throw new Error('USGS 3DEP has no elevation for this path — it covers the US and its territories only');
  const raw = [];
  for (let i = 0; i < sampleCount; i += 1) raw.push(byIndex.has(i) ? byIndex.get(i) : null);
  const filled = fillGaps(raw, 'USGS 3DEP');
  return filled.map((elevation, index) => ({
    distance_km: (distanceKm * index) / (sampleCount - 1),
    elevation_m: elevation,
  }));
}

/* Tile cache. IndexedDB where the browser allows it (Chrome blocks it on
   file:// URLs), otherwise an in-session map so nothing hard-fails. */
const memoryTiles = new Map();
let tileDbPromise = null;

const META_PREFIX = 'meta:';

/* The schema is never versioned up. A version bump waits on every other open
   tab before it can run, and in an offline app that wait has no end — the tile
   list simply never arrives. Metadata therefore lives in the same store under a
   "meta:" key prefix, so a listing reads only small records and never the
   tens of megabytes of elevation bytes beside them. */
function openTileDb() {
  if (tileDbPromise) return tileDbPromise;
  tileDbPromise = new Promise((resolve) => {
    let settled = false;
    const finish = (value) => { if (!settled) { settled = true; resolve(value); } };
    // Never let storage hang the interface; fall back to the session map.
    setTimeout(() => finish(null), 2500);
    try {
      if (!self.indexedDB) { finish(null); return; }
      // No version argument: open whatever exists (creating v1 if it does not),
      // so an older or newer stored schema can never error or block.
      const request = indexedDB.open('antenna-planner-tiles');
      request.onupgradeneeded = () => {
        const db = request.result;
        if (!db.objectStoreNames.contains('tiles')) db.createObjectStore('tiles', { keyPath: 'name' });
      };
      request.onsuccess = () => {
        const db = request.result;
        if (!db.objectStoreNames.contains('tiles')) { finish(null); return; }
        finish(db);
      };
      request.onerror = () => finish(null);
      request.onblocked = () => finish(null);
    } catch (error) { finish(null); }
  });
  return tileDbPromise;
}

function idbRequest(store, work) {
  return new Promise((resolve, reject) => {
    const request = work(store);
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

async function saveTile(record) {
  const meta = { name: record.name, size: record.buffer.byteLength, added: Date.now() };
  const db = await openTileDb();
  if (!db) { memoryTiles.set(meta.name, { ...meta, bytes: record.buffer }); return { persisted: false }; }
  try {
    const tx = db.transaction('tiles', 'readwrite');
    const store = tx.objectStore('tiles');
    store.put({ name: record.name, bytes: record.buffer });
    store.put({ name: META_PREFIX + record.name, size: meta.size, added: meta.added });
    await new Promise((resolve, reject) => {
      tx.oncomplete = resolve;
      tx.onerror = () => reject(tx.error);
      tx.onabort = () => reject(tx.error);
    });
    return { persisted: true };
  } catch (error) {
    memoryTiles.set(meta.name, { ...meta, bytes: record.buffer });
    return { persisted: false };
  }
}

async function listTiles() {
  const fromMemory = [...memoryTiles.values()].map(({ name, size, added }) => ({ name, size, added, persisted: false }));
  const db = await openTileDb();
  if (!db) return fromMemory;
  try {
    const tx = db.transaction('tiles', 'readonly');
    const store = tx.objectStore('tiles');
    const range = IDBKeyRange.bound(META_PREFIX, META_PREFIX + '\uffff');
    const metas = await idbRequest(store, (s) => s.getAll(range));
    let listed = metas.map((entry) => ({
      name: entry.name.slice(META_PREFIX.length), size: entry.size, added: entry.added, persisted: true,
    }));
    if (!listed.length) {
      // Tiles stored before metadata existed: recover names without the bytes.
      const keys = await idbRequest(store, (s) => s.getAllKeys());
      listed = keys
        .filter((key) => typeof key === 'string' && key.indexOf(META_PREFIX) !== 0)
        .map((name) => ({ name, size: 0, added: 0, persisted: true }));
    }
    return [...listed, ...fromMemory];
  } catch (error) {
    return fromMemory;
  }
}

async function loadTiles(names) {
  const out = [];
  const db = await openTileDb();
  if (db) {
    try {
      const tx = db.transaction('tiles', 'readonly');
      const store = tx.objectStore('tiles');
      for (const name of names) {
        // One keyed read per tile, never getAll(): the store holds tens of MB.
        const entry = await idbRequest(store, (s) => s.get(name));
        if (entry && entry.bytes) out.push(parseHgtTile(name, entry.bytes));
      }
    } catch (error) { /* fall through to the session map */ }
  }
  const have = new Set(out.map((tile) => tile.name.toUpperCase()));
  for (const name of names) {
    const entry = memoryTiles.get(name);
    if (entry && !have.has(name.toUpperCase())) out.push(parseHgtTile(entry.name, entry.bytes));
  }
  return out;
}

async function deleteTile(name) {
  memoryTiles.delete(name);
  const db = await openTileDb();
  if (!db) return;
  try {
    const tx = db.transaction('tiles', 'readwrite');
    tx.objectStore('tiles').delete(name);
    tx.objectStore('tiles').delete(META_PREFIX + name);
    await new Promise((resolve) => { tx.oncomplete = resolve; tx.onerror = resolve; tx.onabort = resolve; });
  } catch (error) { /* nothing to undo */ }
}

/* ---------- measured data ---------- */

function nearestNetworkPoint(network, frequencyMhz) {
  if (!network.length) return null;
  return network.reduce((best, point) => (
    Math.abs(point.frequency_mhz - frequencyMhz) < Math.abs(best.frequency_mhz - frequencyMhz) ? point : best
  ));
}

function resonanceOf(network) {
  if (!network.length) return null;
  return network.reduce((best, point) => (point.swr < best.swr ? point : best));
}

/* ---------- GPX / KML tracks ---------- */

function importTrackXml(fileName, text) {
  const doc = new DOMParser().parseFromString(text, 'application/xml');
  if (doc.getElementsByTagName('parsererror').length) throw new Error(`${fileName} is not valid XML`);
  const points = [];
  const nodes = [
    ...doc.getElementsByTagName('trkpt'),
    ...doc.getElementsByTagName('rtept'),
  ];
  const waypoints = nodes.length ? nodes : [...doc.getElementsByTagName('wpt')];
  for (const node of waypoints) {
    const lat = Number(node.getAttribute('lat'));
    const lon = Number(node.getAttribute('lon'));
    if (!Number.isFinite(lat) || !Number.isFinite(lon)) continue;
    const ele = node.getElementsByTagName('ele')[0];
    points.push({ lat, lon, elevation_m: ele ? Number(ele.textContent) : null });
  }
  if (!points.length) {
    for (const node of doc.getElementsByTagName('coordinates')) {
      for (const triple of node.textContent.trim().split(/\s+/)) {
        const [lon, lat, ele] = triple.split(',').map(Number);
        if (!Number.isFinite(lat) || !Number.isFinite(lon)) continue;
        points.push({ lat, lon, elevation_m: Number.isFinite(ele) ? ele : null });
      }
    }
  }
  if (points.length < 2) throw new Error(`${fileName} holds no track or route with at least two points`);
  return points;
}

/* Cumulative along-track distance, so a walked or driven track becomes a
   terrain profile. Track elevation is GPS altitude — coarser than a DEM. */
function profileFromTrack(points) {
  const withElevation = points.filter((point) => Number.isFinite(point.elevation_m));
  if (withElevation.length < 2) throw new Error('That track carries no elevation data — use it for endpoints instead');
  let distance = 0;
  const profile = [{ distance_km: 0, elevation_m: withElevation[0].elevation_m }];
  for (let i = 1; i < withElevation.length; i += 1) {
    const previous = withElevation[i - 1];
    const current = withElevation[i];
    const step = haversineDistanceKm(previous.lat, previous.lon, current.lat, current.lon);
    if (step <= 0) continue;
    distance += step;
    profile.push({ distance_km: distance, elevation_m: current.elevation_m });
  }
  if (profile.length < 2 || distance <= 0) throw new Error('That track does not move far enough to form a path');
  return profile;
}

function fillProfileGaps(profile, label) {
  const filled = fillGaps(profile.map((point) => point.elevation_m), label);
  return profile.map((point, index) => ({ distance_km: point.distance_km, elevation_m: filled[index] }));
}

window.AntennaEngine = { FEET_TO_METERS, SPEED_OF_LIGHT_M_S, EARTH_RADIUS_KM, ANTENNA_TYPES, PROPAGATION_MODELS, CABLES, OBJECT_KINDS, DEFAULT_OBJECT_ATTENUATION_DB, defaultPlan, normalizeBearing, angularDifference, dipoleLengthFt, quarterWaveLengthFt, recommendedWireAzimuth, distanceToSegment, pointInsideBoundary, calculateDeployment, matchedLossDb, swrAdjustedLossDb, powerAfterLoss, azimuthRelativeGainDb, patternRelativeGainDb, patternForData, elevationRelativeGainDb, freeSpacePathLossDb, radioHorizonKm, firstFresnelMidpointM, terrainPathAnalysis, pathObstructionLossDb, installationShadowLossDb, calculateLinkBudget, haversineDistanceKm, initialBearingDeg, terrainProfileFromHgt, importTerrainCsv, importPatternCsv, importTouchstone, planFromProjectFile, planToProjectFile,
  tileNameFor, requiredTiles, pathEndpointsReady, parseHgtTile, terrainProfileFromTiles, fetchProfileFrom3DEP,
  saveTile, listTiles, loadTiles, deleteTile, nearestNetworkPoint, resonanceOf, importTrackXml, profileFromTrack, fillProfileGaps,
  ANTENNA_SPECS, specFor, estimatedGainDbi, isBeam, isVerticalFamily, recommendedAzimuthFor,
  elevationFieldAt, elevationPattern, takeoffAngleDeg, radiatorHeightFt,
  DEFAULT_OBJECT_HEIGHT_FT, objectHeightFt, gainRatio, beamwidthFor, elevationSharpnessFor };
}());
