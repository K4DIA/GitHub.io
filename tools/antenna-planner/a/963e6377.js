// Minimal GeoTIFF DEM reader, enough for USGS 3DEP elevation rasters.
// Classic script so it inlines into the standalone file. window.GeoTiffDem.
(function () {
'use strict';

const TYPE_SIZE = { 1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 6: 1, 7: 1, 8: 2, 9: 4, 10: 8, 11: 4, 12: 8 };

const TAG = {
  width: 256, height: 257, bitsPerSample: 258, compression: 259, photometric: 262,
  stripOffsets: 273, samplesPerPixel: 277, rowsPerStrip: 278, stripByteCounts: 279,
  planarConfig: 284, predictor: 317, tileWidth: 322, tileLength: 323,
  tileOffsets: 324, tileByteCounts: 325, sampleFormat: 339,
  pixelScale: 33550, tiePoint: 33922, transform: 34264, geoKeys: 34735, nodata: 42113,
};

function readValues(view, little, type, count, offset) {
  const out = [];
  for (let i = 0; i < count; i += 1) {
    const at = offset + i * TYPE_SIZE[type];
    switch (type) {
      case 1: case 7: out.push(view.getUint8(at)); break;
      case 2: out.push(String.fromCharCode(view.getUint8(at))); break;
      case 3: out.push(view.getUint16(at, little)); break;
      case 4: out.push(view.getUint32(at, little)); break;
      case 5: out.push(view.getUint32(at, little) / view.getUint32(at + 4, little)); break;
      case 6: out.push(view.getInt8(at)); break;
      case 8: out.push(view.getInt16(at, little)); break;
      case 9: out.push(view.getInt32(at, little)); break;
      case 10: out.push(view.getInt32(at, little) / view.getInt32(at + 4, little)); break;
      case 11: out.push(view.getFloat32(at, little)); break;
      case 12: out.push(view.getFloat64(at, little)); break;
      default: out.push(0);
    }
  }
  return type === 2 ? out.join('').replace(/\0+$/, '') : out;
}

function readIfd(buffer) {
  const view = new DataView(buffer);
  const byteOrder = view.getUint16(0, false);
  let little;
  if (byteOrder === 0x4949) little = true;
  else if (byteOrder === 0x4d4d) little = false;
  else throw new Error('Not a TIFF file');
  const version = view.getUint16(2, little);
  if (version === 43) throw new Error('This is a BigTIFF. Export a standard GeoTIFF, or use an SRTM tile.');
  if (version !== 42) throw new Error('Not a TIFF file');
  const ifdOffset = view.getUint32(4, little);
  const count = view.getUint16(ifdOffset, little);
  const entries = new Map();
  for (let i = 0; i < count; i += 1) {
    const at = ifdOffset + 2 + i * 12;
    const tag = view.getUint16(at, little);
    const type = view.getUint16(at + 2, little);
    const length = view.getUint32(at + 4, little);
    const size = (TYPE_SIZE[type] || 1) * length;
    const valueAt = size > 4 ? view.getUint32(at + 8, little) : at + 8;
    entries.set(tag, readValues(view, little, type, length, valueAt));
  }
  return { view, little, entries };
}

/* ---------- decompression ---------- */

function lzwDecode(input) {
  const out = [];
  let dictionary = [];
  const reset = () => {
    dictionary = new Array(256);
    for (let i = 0; i < 256; i += 1) dictionary[i] = [i];
    dictionary.length = 258;
  };
  reset();
  let bitPosition = 0;
  let codeWidth = 9;
  let previous = null;
  const readCode = () => {
    let code = 0;
    for (let i = 0; i < codeWidth; i += 1) {
      const byte = input[bitPosition >> 3];
      if (byte === undefined) return 257;
      code = (code << 1) | ((byte >> (7 - (bitPosition & 7))) & 1);
      bitPosition += 1;
    }
    return code;
  };
  for (;;) {
    const code = readCode();
    if (code === 257) break;
    if (code === 256) { reset(); codeWidth = 9; previous = null; continue; }
    let entry;
    if (code < dictionary.length && dictionary[code]) entry = dictionary[code];
    else if (previous) entry = previous.concat(previous[0]);
    else throw new Error('Corrupt LZW stream');
    for (const byte of entry) out.push(byte);
    if (previous) dictionary.push(previous.concat(entry[0]));
    previous = entry;
    // TIFF uses early change: widen one code before the boundary.
    if (dictionary.length + 1 >= 1 << codeWidth && codeWidth < 12) codeWidth += 1;
  }
  return new Uint8Array(out);
}

async function inflate(bytes, raw) {
  if (typeof DecompressionStream !== 'function') {
    throw new Error('This browser cannot inflate Deflate-compressed GeoTIFFs');
  }
  const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream(raw ? 'deflate-raw' : 'deflate'));
  return new Uint8Array(await new Response(stream).arrayBuffer());
}

async function decompress(bytes, compression) {
  if (compression === 1) return bytes;
  if (compression === 5) return lzwDecode(bytes);
  if (compression === 8 || compression === 32946) {
    try { return await inflate(bytes, false); } catch (error) { return inflate(bytes, true); }
  }
  throw new Error(`Compression ${compression} is not supported — re-export as uncompressed, LZW or Deflate`);
}

function undoPredictor(bytes, predictor, width, samples, bitsPerSample) {
  if (predictor === 1) return bytes;
  const bytesPerSample = bitsPerSample / 8;
  const rowBytes = width * samples * bytesPerSample;
  const rows = Math.floor(bytes.length / rowBytes);
  if (predictor === 2) {
    if (bitsPerSample !== 8 && bitsPerSample !== 16 && bitsPerSample !== 32) return bytes;
    const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
    for (let row = 0; row < rows; row += 1) {
      const base = row * rowBytes;
      for (let i = samples; i < width * samples; i += 1) {
        const at = base + i * bytesPerSample;
        const back = at - samples * bytesPerSample;
        if (bitsPerSample === 8) view.setUint8(at, (view.getUint8(at) + view.getUint8(back)) & 0xff);
        else if (bitsPerSample === 16) view.setUint16(at, (view.getUint16(at, true) + view.getUint16(back, true)) & 0xffff, true);
        else view.setUint32(at, (view.getUint32(at, true) + view.getUint32(back, true)) >>> 0, true);
      }
    }
    return bytes;
  }
  if (predictor === 3) {
    // Floating-point predictor: bytes are stored plane by plane, differenced.
    const out = new Uint8Array(bytes.length);
    for (let row = 0; row < rows; row += 1) {
      const base = row * rowBytes;
      for (let i = samples; i < rowBytes; i += 1) {
        bytes[base + i] = (bytes[base + i] + bytes[base + i - samples]) & 0xff;
      }
      const count = width * samples;
      for (let i = 0; i < count; i += 1) {
        for (let b = 0; b < bytesPerSample; b += 1) {
          out[base + i * bytesPerSample + b] = bytes[base + b * count + i];
        }
      }
    }
    return out;
  }
  throw new Error(`Predictor ${predictor} is not supported`);
}

/* ---------- the DEM ---------- */

async function readDem(buffer, fileName) {
  const { view, little, entries } = readIfd(buffer);
  const get = (tag, fallback) => (entries.has(tag) ? entries.get(tag)[0] : fallback);
  const width = get(TAG.width);
  const height = get(TAG.height);
  if (!width || !height) throw new Error(`${fileName}: no raster dimensions`);
  const samples = get(TAG.samplesPerPixel, 1);
  const bits = get(TAG.bitsPerSample, 32);
  const format = get(TAG.sampleFormat, 1);
  const compression = get(TAG.compression, 1);
  const predictor = get(TAG.predictor, 1);
  if (get(TAG.planarConfig, 1) !== 1) throw new Error(`${fileName}: planar-separate rasters are not supported`);

  const scale = entries.get(TAG.pixelScale);
  const tie = entries.get(TAG.tiePoint);
  if (!scale || !tie) throw new Error(`${fileName}: no GeoTIFF georeferencing — is this a plain TIFF?`);
  const originLon = tie[3] - tie[0] * scale[0];
  const originLat = tie[4] + tie[1] * scale[1];
  if (Math.abs(originLon) > 180 || Math.abs(originLat) > 90 || scale[0] > 1) {
    throw new Error(`${fileName} is in a projected coordinate system. Download the geographic (NAD83 / WGS84 degrees) version.`);
  }

  const nodataRaw = entries.has(TAG.nodata) ? Number(entries.get(TAG.nodata)) : null;
  const nodata = Number.isFinite(nodataRaw) ? nodataRaw : null;

  const tiled = entries.has(TAG.tileWidth);
  const blockWidth = tiled ? get(TAG.tileWidth) : width;
  const blockHeight = tiled ? get(TAG.tileLength) : get(TAG.rowsPerStrip, height);
  const offsets = entries.get(tiled ? TAG.tileOffsets : TAG.stripOffsets);
  const byteCounts = entries.get(tiled ? TAG.tileByteCounts : TAG.stripByteCounts);
  const across = tiled ? Math.ceil(width / blockWidth) : 1;
  const cache = new Map();

  const readBlock = async (index) => {
    if (cache.has(index)) return cache.get(index);
    const start = offsets[index];
    const length = byteCounts[index];
    if (start === undefined) throw new Error(`${fileName}: missing raster block`);
    const raw = new Uint8Array(buffer.slice(start, start + length));
    const inflated = await decompress(raw, compression);
    const planar = undoPredictor(inflated, predictor, blockWidth, samples, bits);
    const block = new DataView(planar.buffer, planar.byteOffset, planar.byteLength);
    if (cache.size > 24) cache.clear();
    cache.set(index, block);
    return block;
  };

  const valueAt = (block, x, y) => {
    const index = (y * blockWidth + x) * samples;
    const at = index * (bits / 8);
    if (at + bits / 8 > block.byteLength) return null;
    if (format === 3) return bits === 64 ? block.getFloat64(at, little) : block.getFloat32(at, little);
    if (format === 2) return bits === 16 ? block.getInt16(at, little) : block.getInt32(at, little);
    return bits === 16 ? block.getUint16(at, little) : block.getUint32(at, little);
  };

  const sample = async (lat, lon) => {
    const px = Math.floor((lon - originLon) / scale[0]);
    const py = Math.floor((originLat - lat) / scale[1]);
    if (px < 0 || py < 0 || px >= width || py >= height) return null;
    const blockIndex = tiled
      ? Math.floor(py / blockHeight) * across + Math.floor(px / blockWidth)
      : Math.floor(py / blockHeight);
    const block = await readBlock(blockIndex);
    const value = valueAt(block, px % blockWidth, py % blockHeight);
    if (value === null || !Number.isFinite(value)) return null;
    if (nodata !== null && Math.abs(value - nodata) < 1e-6) return null;
    if (value < -1000 || value > 9000) return null;
    return value;
  };

  return {
    name: fileName,
    width,
    height,
    originLat,
    originLon,
    south: originLat - height * scale[1],
    north: originLat,
    west: originLon,
    east: originLon + width * scale[0],
    metres: Math.round(scale[0] * 111320),
    sample,
  };
}

async function profileFromDem(dem, txLat, txLon, rxLat, rxLon, distanceKm, sampleCount = 201) {
  const raw = [];
  for (let i = 0; i < sampleCount; i += 1) {
    const f = i / (sampleCount - 1);
    raw.push(await dem.sample(txLat + (rxLat - txLat) * f, txLon + (rxLon - txLon) * f));
  }
  if (raw.every((value) => value === null)) {
    throw new Error(`${dem.name} does not cover this path (${dem.south.toFixed(3)}–${dem.north.toFixed(3)}° N, ${dem.west.toFixed(3)}–${dem.east.toFixed(3)}° E)`);
  }
  return raw.map((elevation, index) => ({
    distance_km: (distanceKm * index) / (sampleCount - 1),
    elevation_m: elevation,
  }));
}

window.GeoTiffDem = { readDem, profileFromDem };
}());
