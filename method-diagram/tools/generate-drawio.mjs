#!/usr/bin/env node

import { readFileSync, writeFileSync } from 'node:fs';

// ── Grid constants ──────────────────────────────────────────────────────────
const GRID = {
  swimlanePadTop: 40,
  swimlanePadBottom: 25,
  swimlanePadSide: 20,
  swimlaneGap: 20,
  swimlaneStartX: 10,
  swimlaneStartY: 10,
  rowHeight: 90,
  colCenters: { '-1': 140, 0: 400, 1: 660 },
  mergeTrackX: 780,
  returnTrackX: -30,
};

const SHAPES = {
  start:    { w: 140, h: 40 },
  end:      { w: 140, h: 40 },
  process:  { w: 260, h: 50 },
  decision: { w: 240, h: 70 },
  opaque:   { w: 260, h: 50 },
  note:     { w: 200, h: 60 },
};

const COLORS = {
  green:  { fill: '#d5e8d4', stroke: '#82b366' },
  blue:   { fill: '#dae8fc', stroke: '#6c8ebf' },
  orange: { fill: '#ffe6cc', stroke: '#d79b00' },
  red:    { fill: '#f8cecc', stroke: '#b85450' },
  yellow: { fill: '#fff2cc', stroke: '#d6b656' },
};

const TYPE_DEFAULTS = {
  start:    { style: 'ellipse',           defaultColor: 'green' },
  end:      { style: 'ellipse',           defaultColor: 'green' },
  process:  { style: 'rounded=1',         defaultColor: null },
  decision: { style: 'rhombus',           defaultColor: null },
  opaque:   { style: 'rounded=1',         defaultColor: null },
  note:     { style: 'shape=note;size=15', defaultColor: 'yellow' },
};

// ── Helpers ─────────────────────────────────────────────────────────────────
function escapeXml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function nl(s) {
  return String(s).replace(/\n/g, '&#xa;');
}

function uid(swId, nodeId) {
  return swId ? `${swId}_${nodeId}` : nodeId;
}

function styleFor(type, color) {
  const td = TYPE_DEFAULTS[type] || TYPE_DEFAULTS.process;
  const c = color || td.defaultColor;
  let s = `${td.style};whiteSpace=wrap;html=1;`;
  if (c && COLORS[c]) {
    s += `fillColor=${COLORS[c].fill};strokeColor=${COLORS[c].stroke};`;
  }
  return s;
}

function nodeHeight(node) {
  const base = SHAPES[node.type] || SHAPES.process;
  const lines = (String(node.label).match(/\n/g) || []).length + 1;
  return Math.max(base.h, 30 + lines * 16);
}

// ── Layout ──────────────────────────────────────────────────────────────────
function placeNodes(nodes, swId) {
  const lookup = {};
  for (const n of nodes) {
    const shape = SHAPES[n.type] || SHAPES.process;
    const h = nodeHeight(n);
    const colCenter = GRID.colCenters[String(n.col)] ?? GRID.colCenters['0'];
    const x = colCenter - shape.w / 2;
    const y = GRID.swimlanePadTop + n.row * GRID.rowHeight;
    n._px = { x, y, w: shape.w, h };
    n._uid = uid(swId, n.id);
    lookup[n.id] = n;
  }
  return lookup;
}

function sizeSwimlane(sw) {
  let maxRow = 0;
  let maxBottom = 0;
  let maxRight = 0;
  for (const n of sw.nodes) {
    if (n.row > maxRow) maxRow = n.row;
    const bottom = n._px.y + n._px.h;
    if (bottom > maxBottom) maxBottom = bottom;
    const right = n._px.x + n._px.w;
    if (right > maxRight) maxRight = right;
  }
  const height = Math.max(
    GRID.swimlanePadTop + (maxRow + 1) * GRID.rowHeight + GRID.swimlanePadBottom,
    maxBottom + GRID.swimlanePadBottom
  );
  const width = Math.max(GRID.mergeTrackX + 60, maxRight + GRID.swimlanePadSide + 40);
  sw._size = { w: width, h: height };
}

function stackSwimlanes(swimlanes) {
  let y = GRID.swimlaneStartY;
  for (const sw of swimlanes) {
    sw._origin = { x: GRID.swimlaneStartX, y };
    y += sw._size.h + GRID.swimlaneGap;
  }
}

// ── Edge routing helpers ────────────────────────────────────────────────────
function computeEdgeAttrs(edge, lookup) {
  let styleExtra = '';
  let waypoints = [];

  const src = lookup[edge.from];
  const tgt = lookup[edge.to];
  if (!src || !tgt) return { styleExtra, waypoints };

  if (edge.direction === 'right') {
    styleExtra += 'exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;';
  } else if (edge.direction === 'left') {
    styleExtra += 'exitX=0;exitY=0.5;exitDx=0;exitDy=0;entryX=1;entryY=0.5;entryDx=0;entryDy=0;';
  }

  if (edge.merge === 'right') {
    styleExtra = 'exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=1;entryY=0.5;entryDx=0;entryDy=0;';
    // Count sibling merges to same target for staggering
    const trackX = GRID.mergeTrackX + (edge._mergeOffset || 0) * 10;
    const srcCY = src._px.y + src._px.h / 2;
    const tgtCY = tgt._px.y + tgt._px.h / 2;
    waypoints = [{ x: trackX, y: srcCY }, { x: trackX, y: tgtCY }];
  } else if (edge.merge === 'left') {
    styleExtra = 'exitX=0;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;';
    const trackX = GRID.swimlanePadSide - 20;
    const srcCY = src._px.y + src._px.h / 2;
    const tgtCY = tgt._px.y + tgt._px.h / 2;
    waypoints = [{ x: trackX, y: srcCY }, { x: trackX, y: tgtCY }];
  }

  return { styleExtra, waypoints };
}

function assignMergeOffsets(edges) {
  const groups = {};
  for (const e of edges) {
    if (e.merge) {
      const key = `${e.merge}:${e.to}`;
      if (!groups[key]) groups[key] = [];
      groups[key].push(e);
    }
  }
  for (const arr of Object.values(groups)) {
    arr.forEach((e, i) => { e._mergeOffset = i; });
  }
}

// ── XML generation ──────────────────────────────────────────────────────────
function xmlNode(node, parentId) {
  const style = styleFor(node.type, node.color);
  const label = nl(escapeXml(node.label));
  const { x, y, w, h } = node._px;
  return `    <mxCell id="${node._uid}" value="${label}" style="${style}" vertex="1" parent="${parentId}">
      <mxGeometry x="${x}" y="${y}" width="${w}" height="${h}" as="geometry"/>
    </mxCell>`;
}

function xmlEdge(edge, parentId, lookup) {
  const srcId = lookup[edge.from]?._uid;
  const tgtId = lookup[edge.to]?._uid;
  if (!srcId || !tgtId) return '';

  const edgeId = `e_${srcId}_${tgtId}`;
  const { styleExtra, waypoints } = computeEdgeAttrs(edge, lookup);
  const style = `edgeStyle=orthogonalEdgeStyle;html=1;${styleExtra}`;
  const label = edge.label ? ` value="${escapeXml(edge.label)}"` : '';

  let geoInner = '';
  if (waypoints.length > 0) {
    const pts = waypoints.map(p => `        <mxPoint x="${p.x}" y="${p.y}"/>`).join('\n');
    geoInner = `\n      <Array as="points">\n${pts}\n      </Array>\n    `;
  }

  return `    <mxCell id="${edgeId}"${label} style="${style}" edge="1" source="${srcId}" target="${tgtId}" parent="${parentId}">
      <mxGeometry relative="1" as="geometry">${geoInner}</mxGeometry>
    </mxCell>`;
}

function xmlCrossEdge(ce, swimlanes, edgeIdx) {
  const srcSw = swimlanes.find(s => s.id === ce.from.swimlane);
  const tgtSw = swimlanes.find(s => s.id === ce.to.swimlane);
  if (!srcSw || !tgtSw) return '';

  const srcNode = srcSw.nodes.find(n => n.id === ce.from.node);
  const tgtNode = tgtSw.nodes.find(n => n.id === ce.to.node);
  if (!srcNode || !tgtNode) return '';

  const srcGlobal = srcNode._uid;
  const tgtGlobal = tgtNode._uid;
  const edgeId = `e_cross_${edgeIdx}`;
  const label = ce.label ? ` value="${escapeXml(ce.label)}"` : '';

  let style = 'edgeStyle=orthogonalEdgeStyle;html=1;';
  let waypoints = [];

  if (ce.returnEdge) {
    style += 'exitX=0;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;';
    const absSrcY = srcSw._origin.y + srcNode._px.y + srcNode._px.h / 2;
    const absTgtY = tgtSw._origin.y + tgtNode._px.y + tgtNode._px.h / 2;
    waypoints = [
      { x: GRID.returnTrackX, y: absSrcY },
      { x: GRID.returnTrackX, y: absTgtY },
    ];
  }

  let geoInner = '';
  if (waypoints.length > 0) {
    const pts = waypoints.map(p => `        <mxPoint x="${p.x}" y="${p.y}"/>`).join('\n');
    geoInner = `\n      <Array as="points">\n${pts}\n      </Array>\n    `;
  }

  return `    <mxCell id="${edgeId}"${label} style="${style}" edge="1" source="${srcGlobal}" target="${tgtGlobal}" parent="1">
      <mxGeometry relative="1" as="geometry">${geoInner}</mxGeometry>
    </mxCell>`;
}

function xmlNote(note, swimlanes, noteIdx) {
  const sw = note.attachTo.swimlane
    ? swimlanes?.find(s => s.id === note.attachTo.swimlane)
    : null;
  const nodes = sw ? sw.nodes : swimlanes; // fallback for single-mode
  const targetNode = (sw ? sw.nodes : nodes).find(n => n.id === note.attachTo.node);
  if (!targetNode) return '';

  const parentId = sw ? sw.id : '1';
  const noteId = `note_${noteIdx}`;
  const noteEdgeId = `e_note_${noteIdx}`;
  const pos = note.position || 'left';
  const noteW = SHAPES.note.w;
  const noteH = SHAPES.note.h;
  const noteX = pos === 'left'
    ? targetNode._px.x - noteW - 40
    : targetNode._px.x + targetNode._px.w + 40;
  const noteY = targetNode._px.y;
  const style = styleFor('note', 'yellow');

  const nodeXml = `    <mxCell id="${noteId}" value="${nl(escapeXml(note.text))}" style="${style}" vertex="1" parent="${parentId}">
      <mxGeometry x="${noteX}" y="${noteY}" width="${noteW}" height="${noteH}" as="geometry"/>
    </mxCell>`;

  const edgeXml = `    <mxCell id="${noteEdgeId}" style="edgeStyle=orthogonalEdgeStyle;html=1;dashed=1;endArrow=none;" edge="1" source="${noteId}" target="${targetNode._uid}" parent="${parentId}">
      <mxGeometry relative="1" as="geometry"/>
    </mxCell>`;

  return nodeXml + '\n' + edgeXml;
}

// ── Main generation ─────────────────────────────────────────────────────────
function generate(ir) {
  const lines = [];
  lines.push('<mxfile>');
  lines.push(`  <diagram name="${escapeXml(ir.title)}">`);
  lines.push('    <mxGraphModel adaptiveColors="auto">');
  lines.push('      <root>');
  lines.push('        <mxCell id="0"/>');
  lines.push('        <mxCell id="1" parent="0"/>');

  const isSwimlaneMode = Array.isArray(ir.swimlanes) && ir.swimlanes.length > 0;

  if (isSwimlaneMode) {
    // Layout all swimlanes
    for (const sw of ir.swimlanes) {
      sw._lookup = placeNodes(sw.nodes, sw.id);
      sizeSwimlane(sw);
      assignMergeOffsets(sw.edges);
    }
    stackSwimlanes(ir.swimlanes);

    // Generate swimlanes
    for (const sw of ir.swimlanes) {
      const { x, y } = sw._origin;
      const { w, h } = sw._size;
      lines.push('');
      lines.push(`    <mxCell id="${sw.id}" value="${escapeXml(sw.label)}" style="swimlane;startSize=30;html=1;whiteSpace=wrap;" vertex="1" parent="1">`);
      lines.push(`      <mxGeometry x="${x}" y="${y}" width="${w}" height="${h}" as="geometry"/>`);
      lines.push('    </mxCell>');

      for (const n of sw.nodes) {
        lines.push(xmlNode(n, sw.id));
      }
      for (const e of sw.edges) {
        const xml = xmlEdge(e, sw.id, sw._lookup);
        if (xml) lines.push(xml);
      }
    }

    // Cross-swimlane edges
    if (ir.crossEdges) {
      lines.push('');
      ir.crossEdges.forEach((ce, i) => {
        const xml = xmlCrossEdge(ce, ir.swimlanes, i);
        if (xml) lines.push(xml);
      });
    }

    // Notes
    if (ir.notes) {
      ir.notes.forEach((note, i) => {
        const xml = xmlNote(note, ir.swimlanes, i);
        if (xml) lines.push(xml);
      });
    }
  } else {
    // Single-method mode
    const nodes = ir.nodes || [];
    const edges = ir.edges || [];
    const lookup = placeNodes(nodes, null);
    assignMergeOffsets(edges);

    for (const n of nodes) {
      lines.push(xmlNode(n, '1'));
    }
    lines.push('');
    for (const e of edges) {
      const xml = xmlEdge(e, '1', lookup);
      if (xml) lines.push(xml);
    }

    // Notes in single mode
    if (ir.notes) {
      ir.notes.forEach((note, i) => {
        const targetNode = nodes.find(n => n.id === note.attachTo.node);
        if (!targetNode) return;
        const noteId = `note_${i}`;
        const noteEdgeId = `e_note_${i}`;
        const pos = note.position || 'left';
        const noteW = SHAPES.note.w;
        const noteH = SHAPES.note.h;
        const noteX = pos === 'left'
          ? targetNode._px.x - noteW - 40
          : targetNode._px.x + targetNode._px.w + 40;
        const noteY = targetNode._px.y;
        lines.push(`    <mxCell id="${noteId}" value="${nl(escapeXml(note.text))}" style="${styleFor('note', 'yellow')}" vertex="1" parent="1">`);
        lines.push(`      <mxGeometry x="${noteX}" y="${noteY}" width="${noteW}" height="${noteH}" as="geometry"/>`);
        lines.push('    </mxCell>');
        lines.push(`    <mxCell id="${noteEdgeId}" style="edgeStyle=orthogonalEdgeStyle;html=1;dashed=1;endArrow=none;" edge="1" source="${noteId}" target="${targetNode._uid}" parent="1">`);
        lines.push('      <mxGeometry relative="1" as="geometry"/>');
        lines.push('    </mxCell>');
      });
    }
  }

  lines.push('');
  lines.push('      </root>');
  lines.push('    </mxGraphModel>');
  lines.push('  </diagram>');
  lines.push('</mxfile>');
  return lines.join('\n') + '\n';
}

// ── CLI ─────────────────────────────────────────────────────────────────────
function main() {
  const [inputPath, outputPath] = process.argv.slice(2);
  if (!inputPath || !outputPath) {
    console.error('Usage: node generate-drawio.mjs <input.json> <output.drawio>');
    process.exit(1);
  }

  let raw;
  try {
    raw = readFileSync(inputPath, 'utf8');
  } catch (e) {
    console.error(`Failed to read ${inputPath}: ${e.message}`);
    process.exit(1);
  }

  let ir;
  try {
    ir = JSON.parse(raw);
  } catch (e) {
    console.error(`Invalid JSON: ${e.message}`);
    process.exit(1);
  }

  if (!ir.title) {
    console.error('IR must have a "title" field');
    process.exit(1);
  }

  const xml = generate(ir);
  writeFileSync(outputPath, xml, 'utf8');
  console.log(`Generated ${outputPath}`);
}

main();
