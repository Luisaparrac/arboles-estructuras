const SEVERITY = { CRITICAL: "#ff3b5c", HIGH: "#ff8a1f", MEDIUM: "#ffd23f", LOW: "#3de0a3", INFO: "#5aa9ff" };
const QUESTION_COLOR = "#19e3ff";
const NS = "http://www.w3.org/2000/svg";
const $ = (id) => document.getElementById(id);
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const colorOf = (node) => SEVERITY[node.severity] ?? QUESTION_COLOR;

function svg(tag, attrs = {}, parent) {
  const el = document.createElementNS(NS, tag);
  Object.entries(attrs).forEach(([key, value]) => el.setAttribute(key, value));
  parent?.appendChild(el);
  return el;
}

class Api {
  static async get(path) {
    const response = await fetch(`/api/${path}`);
    return response.json();
  }
}

/** Draws the tree as SVG and owns every visual state of its nodes and edges. */
class TreeView {
  constructor(root, element) {
    this.svg = element;
    this.nodes = new Map();
    this.edges = new Map();
    this.items = [];
    this.layout(root);
    this.draw();
  }

  layout(root) {
    let column = 0;
    const place = (node, depth, parent, label) => {          // in-order: YES left, NO right
      if (node.yes) place(node.yes, depth + 1, node, "YES");
      this.items.push({ node, depth, parent, label, col: column++ });
      if (node.no) place(node.no, depth + 1, node, "NO");
    };
    place(root, 0, null, "");
    this.items.forEach((item, i) => Object.assign(item, { x: 60 + item.col * 72, y: 60 + item.depth * 105, i }));
    this.byId = new Map(this.items.map((item) => [item.node.id, item]));
    this.height = 120 + Math.max(...this.items.map((item) => item.depth)) * 105;
    this.width = 120 + (column - 1) * 72;
  }

  draw() {
    this.svg.setAttribute("viewBox", `0 0 ${this.width} ${this.height}`);
    const edgeLayer = svg("g", {}, this.svg);
    const nodeLayer = svg("g", {}, this.svg);
    this.items.forEach((item) => {
      if (item.parent) this.drawEdge(item, edgeLayer);
      this.drawNode(item, nodeLayer);
    });
  }

  drawEdge(item, layer) {
    const from = this.byId.get(item.parent.id);
    const mid = (from.y + item.y) / 2;
    const path = svg("path", { class: "edge", d: `M${from.x} ${from.y} C${from.x} ${mid} ${item.x} ${mid} ${item.x} ${item.y}` }, layer);
    path.style.setProperty("--len", path.getTotalLength());
    path.style.setProperty("--i", item.i);
    const label = svg("text", { class: "edge-label", x: (from.x + item.x) / 2 + (item.label === "YES" ? -14 : 14), y: mid }, layer);
    label.textContent = item.label;
    this.edges.set(item.node.id, path);
  }

  drawNode({ node, x, y, i }, layer) {
    const group = svg("g", { class: "node", transform: `translate(${x} ${y})` }, layer);
    group.style.setProperty("--c", colorOf(node));
    group.style.setProperty("--i", i);
    const body = svg("g", { class: "node-body" }, group);
    const shape = node.leaf ? { tag: "rect", attrs: { x: -22, y: -22, width: 44, height: 44, rx: 10 } } : { tag: "circle", attrs: { r: 23 } };
    svg(shape.tag, { ...shape.attrs, class: "ring" }, body);
    svg(shape.tag, { ...shape.attrs, class: "shape" }, body);
    svg("text", {}, body).textContent = node.id;
    svg("title", {}, body).textContent = node.text;
    this.nodes.set(node.id, group);
  }

  mark(id, state) { this.nodes.get(id)?.classList.add(state); }
  unmark(state) { this.nodes.forEach((n) => n.classList.remove(state)); }

  focus(id) {
    this.unmark("active");
    this.mark(id, "active");
  }

  travel(fromId, toId) {
    this.unmark("active");
    this.mark(fromId, "done");
    this.edges.get(toId)?.classList.add("on");
  }

  reset() {
    ["active", "done", "visit"].forEach((state) => this.unmark(state));
    this.edges.forEach((edge) => edge.classList.remove("on"));
  }
}

/** Connects the API, the tree view and the side panels. */
class App {
  constructor() {
    this.busy = false;
    $("yes").onclick = () => this.answer(true);
    $("no").onclick = () => this.answer(false);
    $("restart").onclick = () => this.restart();
    document.querySelectorAll("[data-mode]").forEach((btn) => (btn.onclick = () => this.traverse(btn.dataset.mode)));
  }

  async start() {
    const { tree, stats } = await Api.get("tree");
    this.root = tree;
    this.view = new TreeView(tree, $("tree"));
    this.renderStats(stats);
    this.renderLegend();
    this.restart();
  }

  renderStats(stats) {
    $("stats").innerHTML = Object.entries(stats)
      .map(([key, value], i) => `<li style="animation-delay:${i * 90}ms"><b>${value}</b>${key}</li>`).join("");
  }

  renderLegend() {
    const entries = [["Question", QUESTION_COLOR], ...Object.entries(SEVERITY)];
    $("legend").innerHTML = entries.map(([name, color]) => `<li><i style="--c:${color}"></i>${name}</li>`).join("");
  }

  restart() {
    this.view.reset();
    this.depth = 0;
    $("path").innerHTML = "";
    $("verdict").hidden = true;
    $("question").hidden = false;
    this.show(this.root);
  }

  show(node) {
    this.current = node;
    this.view.focus(node.id);
    if (node.leaf) return this.showVerdict(node);
    $("step").textContent = `STEP ${String(this.depth + 1).padStart(2, "0")} · ${node.id}`;
    $("qtext").textContent = node.text;
  }

  showVerdict(node) {
    $("question").hidden = true;
    const card = $("verdict");
    card.hidden = false;
    card.className = `card verdict ${node.severity}`;
    $("badge").textContent = node.severity;
    $("action").textContent = node.action;
    card.style.animation = "none";
    card.offsetHeight;                                        // restart the entrance animation
    card.style.animation = "";
  }

  async answer(yes) {
    if (this.busy || this.current.leaf) return;
    this.busy = true;
    const next = await Api.get(`step?id=${this.current.id}&answer=${yes ? "yes" : "no"}`);
    $("path").insertAdjacentHTML("beforeend",
      `<li><span>${this.current.id} · ${this.current.text}</span><em class="${yes ? "Y" : "N"}">${yes ? "YES" : "NO"}</em></li>`);
    this.view.travel(this.current.id, next.id);
    this.depth++;
    this.show(next);
    this.busy = false;
  }

  async traverse(mode) {
    if (this.busy) return;
    this.busy = true;
    this.view.reset();
    $("readout").innerHTML = "";
    const order = await Api.get(`traverse?mode=${mode}`);
    for (const id of order) {
      this.view.unmark("visit");
      this.view.mark(id, "visit");
      $("readout").insertAdjacentHTML("beforeend", `<b>${id}</b>`);
      await sleep(450);
    }
    await sleep(600);
    this.busy = false;
    this.restart();
  }
}

new App().start();
