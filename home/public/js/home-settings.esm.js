import { defineComponent as vt, computed as ne, openBlock as T, createElementBlock as R, normalizeClass as pt, toDisplayString as v, ref as P, onMounted as sn, unref as w, Fragment as me, createElementVNode as h, withDirectives as j, vModelText as J, createCommentVNode as N, renderList as gt, vModelSelect as rn, resolveComponent as Rn, withKeys as $t, createVNode as ct, withCtx as Lt, createTextVNode as Pt, normalizeStyle as In, createBlock as Mn } from "/assets/dock/js/vendor/vue.esm.js";
function $n(t) {
  let e = Object.assign({}, t);
  if (!e.url)
    throw new Error("[request] options.url is required");
  e.transformRequest && (e = e.transformRequest(t)), e.responseType || (e.responseType = "json"), e.method || (e.method = "GET");
  let n = e.url, o;
  if (e.params)
    if (e.method === "GET") {
      let s = new URLSearchParams();
      for (let r in e.params)
        s.append(r, e.params[r]);
      n = e.url + "?" + s.toString();
    } else
      o = JSON.stringify(e.params);
  return fetch(n, {
    method: e.method || "GET",
    headers: e.headers,
    body: o
  }).then((s) => {
    if (e.transformResponse)
      return e.transformResponse(s, e);
    if (s.status >= 200 && s.status < 300)
      return e.responseType === "json" ? s.json() : s;
    {
      let r = new Error(s.statusText);
      throw r.response = s, r;
    }
  }).catch((s) => {
    if (e.transformError)
      return e.transformError(s);
    throw s;
  });
}
let Ln = {};
function Pn(t) {
  return Ln[t] ?? null;
}
function V(t) {
  return $n({
    ...t,
    transformRequest: (e = {}) => {
      if (!e.url)
        throw new Error("[frappeRequest] options.url is required");
      let n = Object.assign(
        {
          Accept: "application/json",
          "Content-Type": "application/json; charset=utf-8",
          "X-Frappe-Site-Name": window.location.hostname
        },
        e.headers || {}
      );
      return window.csrf_token && window.csrf_token !== "{{ csrf_token }}" && (n["X-Frappe-CSRF-Token"] = window.csrf_token), !e.url.startsWith("/") && !e.url.startsWith("http") && (e.url = "/api/method/" + e.url), {
        ...e,
        method: e.method || "POST",
        headers: n
      };
    },
    transformResponse: async (e, n) => {
      let o = n.url;
      if (e.ok) {
        const s = await e.json();
        if (s.docs || o === "/api/method/login")
          return s;
        if (s.exc)
          try {
            console.groupCollapsed(o), console.log(n);
            let r = JSON.parse(s.exc);
            for (let i of r)
              console.log(i);
            console.groupEnd();
          } catch (r) {
            console.warn("Error printing debug messages", r);
          }
        if (s._server_messages) {
          let r = Pn("serverMessagesHandler") || n.onServerMessages || null;
          r && r(JSON.parse(s?._server_messages) || []);
        }
        return s.message;
      } else {
        let s = await e.text(), r, i;
        try {
          r = JSON.parse(s);
        } catch {
        }
        let a = [
          [n.url, r?.exc_type, r?._error_message].filter(Boolean).join(" ")
        ];
        if (r.exc) {
          i = r.exc;
          try {
            i = JSON.parse(i)[0], console.log(i);
          } catch {
          }
        }
        let l = new Error(a.join(`
`));
        throw l.exc_type = r.exc_type, l.exc = i, l.response = e, l.status = s.status, l.messages = r._server_messages ? JSON.parse(r._server_messages) : [], l.messages = l.messages.concat(r.message), l.messages = l.messages.map((c) => {
          try {
            return JSON.parse(c).message;
          } catch {
            return c;
          }
        }), l.messages = l.messages.filter(Boolean), l.messages.length || (l.messages = r._error_message ? [r._error_message] : ["Internal Server Error"]), n.onError && n.onError(l), l;
      }
    },
    transformError: (e) => {
      throw t.onError && t.onError(e), e;
    }
  });
}
const Fn = ["src", "alt"], Dn = ["title"], Nn = /* @__PURE__ */ vt({
  __name: "HouseholdMemberAvatar",
  props: {
    displayName: {},
    avatar: {},
    size: {}
  },
  setup(t) {
    const e = t, n = ne(() => {
      switch (e.size) {
        case "sm":
          return "w-8 h-8 text-xs";
        case "lg":
          return "w-12 h-12 text-base";
        default:
          return "w-10 h-10 text-sm";
      }
    }), o = ne(() => {
      const r = e.displayName.trim().split(/\s+/);
      return r.length >= 2 ? (r[0][0] + r[r.length - 1][0]).toUpperCase() : e.displayName.slice(0, 2).toUpperCase();
    }), s = ne(() => {
      const r = [
        "bg-amber-500",
        "bg-blue-500",
        "bg-emerald-500",
        "bg-purple-500",
        "bg-rose-500",
        "bg-cyan-500",
        "bg-orange-500",
        "bg-indigo-500"
      ];
      let i = 0;
      for (const a of e.displayName)
        i = a.charCodeAt(0) + ((i << 5) - i);
      return r[Math.abs(i) % r.length];
    });
    return (r, i) => t.avatar ? (T(), R("img", {
      key: 0,
      src: t.avatar,
      alt: t.displayName,
      class: pt([n.value, "rounded-full object-cover"])
    }, null, 10, Fn)) : (T(), R("div", {
      key: 1,
      class: pt([n.value, s.value, "rounded-full flex items-center justify-center text-white font-medium select-none"]),
      title: t.displayName
    }, v(o.value), 11, Dn));
  }
});
function u(t, e) {
  let o = (window.__messages || {})[t] || t;
  if (e)
    if (Array.isArray(e))
      for (let s = 0; s < e.length; s++)
        o = o.replace(new RegExp(`\\{${s}\\}`, "g"), String(e[s]));
    else
      for (const [s, r] of Object.entries(e))
        o = o.replace(new RegExp(`\\{${s}\\}`, "g"), String(r));
  return o;
}
function Hn(t) {
  return t instanceof Element;
}
function Ke(t) {
  return t instanceof HTMLElement;
}
function ue(t) {
  return typeof t == "function";
}
function We(t) {
  return typeof t == "string";
}
function H(t) {
  return t === void 0;
}
class wt {
  /**
   * Adds an event listener for the given event string.
   *
   * @param {string} event
   * @param {Function} handler
   * @param ctx
   * @param {boolean} once
   * @returns
   */
  on(e, n, o, s = !1) {
    var r;
    return H(this.bindings) && (this.bindings = {}), H(this.bindings[e]) && (this.bindings[e] = []), (r = this.bindings[e]) == null || r.push({
      handler: n,
      ctx: o,
      once: s
    }), this;
  }
  /**
   * Adds an event listener that only fires once for the given event string.
   *
   * @param {string} event
   * @param {Function} handler
   * @param ctx
   * @returns
   */
  once(e, n, o) {
    return this.on(e, n, o, !0);
  }
  /**
   * Removes an event listener for the given event string.
   *
   * @param {string} event
   * @param {Function} handler
   * @returns
   */
  off(e, n) {
    if (H(this.bindings) || H(this.bindings[e]))
      return this;
    if (H(n))
      delete this.bindings[e];
    else {
      var o;
      (o = this.bindings[e]) == null || o.forEach((s, r) => {
        if (s.handler === n) {
          var i;
          (i = this.bindings[e]) == null || i.splice(r, 1);
        }
      });
    }
    return this;
  }
  /**
   * Triggers an event listener for the given event string.
   *
   * @param {string} event
   * @returns
   */
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  trigger(e, ...n) {
    if (!H(this.bindings) && this.bindings[e]) {
      var o;
      (o = this.bindings[e]) == null || o.forEach((s, r) => {
        const {
          ctx: i,
          handler: a,
          once: l
        } = s, c = i || this;
        if (a.apply(c, n), l) {
          var f;
          (f = this.bindings[e]) == null || f.splice(r, 1);
        }
      });
    }
    return this;
  }
}
function B() {
  return B = Object.assign ? Object.assign.bind() : function(t) {
    for (var e = 1; e < arguments.length; e++) {
      var n = arguments[e];
      for (var o in n) ({}).hasOwnProperty.call(n, o) && (t[o] = n[o]);
    }
    return t;
  }, B.apply(null, arguments);
}
function an(t, e) {
  if (t == null) return {};
  var n = {};
  for (var o in t) if ({}.hasOwnProperty.call(t, o)) {
    if (e.includes(o)) continue;
    n[o] = t[o];
  }
  return n;
}
const he = {
  defaultMerge: /* @__PURE__ */ Symbol("deepmerge-ts: default merge"),
  skip: /* @__PURE__ */ Symbol("deepmerge-ts: skip")
};
he.defaultMerge;
function Bn(t, e) {
  return e;
}
function Ft(t) {
  return typeof t != "object" || t === null ? 0 : Array.isArray(t) ? 2 : Un(t) ? 1 : t instanceof Set ? 3 : t instanceof Map ? 4 : 5;
}
function jn(t) {
  const e = /* @__PURE__ */ new Set();
  for (const n of t)
    for (const o of [...Object.keys(n), ...Object.getOwnPropertySymbols(n)])
      e.add(o);
  return e;
}
function Vn(t, e) {
  return typeof t == "object" && Object.prototype.propertyIsEnumerable.call(t, e);
}
function ln(t) {
  return {
    // eslint-disable-next-line functional/functional-parameters
    *[Symbol.iterator]() {
      for (const e of t)
        for (const n of e)
          yield n;
    }
  };
}
const Dt = /* @__PURE__ */ new Set(["[object Object]", "[object Module]"]);
function Un(t) {
  if (!Dt.has(Object.prototype.toString.call(t)))
    return !1;
  const {
    constructor: e
  } = t;
  if (e === void 0)
    return !0;
  const n = e.prototype;
  return !(n === null || typeof n != "object" || !Dt.has(Object.prototype.toString.call(n)) || !n.hasOwnProperty("isPrototypeOf"));
}
function zn(t, e, n) {
  const o = {};
  for (const s of jn(t)) {
    const r = [];
    for (const l of t)
      Vn(l, s) && r.push(l[s]);
    if (r.length === 0)
      continue;
    const i = e.metaDataUpdater(n, {
      key: s,
      parents: t
    }), a = un(r, e, i);
    a !== he.skip && (s === "__proto__" ? Object.defineProperty(o, s, {
      value: a,
      configurable: !0,
      enumerable: !0,
      writable: !0
    }) : o[s] = a);
  }
  return o;
}
function Wn(t) {
  return t.flat();
}
function qn(t) {
  return new Set(ln(t));
}
function Yn(t) {
  return new Map(ln(t));
}
function cn(t) {
  return t.at(-1);
}
var ut = /* @__PURE__ */ Object.freeze({
  __proto__: null,
  mergeArrays: Wn,
  mergeMaps: Yn,
  mergeOthers: cn,
  mergeRecords: zn,
  mergeSets: qn
});
function kt(...t) {
  return Kn({})(...t);
}
function Kn(t, e) {
  const n = Xn(t, o);
  function o(...s) {
    return un(s, n, e);
  }
  return o;
}
function Xn(t, e) {
  var n, o;
  return {
    defaultMergeFunctions: ut,
    mergeFunctions: B({}, ut, Object.fromEntries(Object.entries(t).filter(([s, r]) => Object.hasOwn(ut, s)).map(([s, r]) => r === !1 ? [s, cn] : [s, r]))),
    metaDataUpdater: (n = t.metaDataUpdater) != null ? n : Bn,
    deepmerge: e,
    useImplicitDefaultMerging: (o = t.enableImplicitDefaultMerging) != null ? o : !1,
    actions: he
  };
}
function un(t, e, n) {
  if (t.length === 0)
    return;
  if (t.length === 1)
    return dt(t, e, n);
  const o = Ft(t[0]);
  if (o !== 0 && o !== 5) {
    for (let s = 1; s < t.length; s++)
      if (Ft(t[s]) !== o)
        return dt(t, e, n);
  }
  switch (o) {
    case 1:
      return Jn(t, e, n);
    case 2:
      return Gn(t, e, n);
    case 3:
      return Zn(t, e, n);
    case 4:
      return Qn(t, e, n);
    default:
      return dt(t, e, n);
  }
}
function Jn(t, e, n) {
  const o = e.mergeFunctions.mergeRecords(t, e, n);
  return o === he.defaultMerge || e.useImplicitDefaultMerging && o === void 0 && e.mergeFunctions.mergeRecords !== e.defaultMergeFunctions.mergeRecords ? e.defaultMergeFunctions.mergeRecords(t, e, n) : o;
}
function Gn(t, e, n) {
  const o = e.mergeFunctions.mergeArrays(t, e, n);
  return o === he.defaultMerge || e.useImplicitDefaultMerging && o === void 0 && e.mergeFunctions.mergeArrays !== e.defaultMergeFunctions.mergeArrays ? e.defaultMergeFunctions.mergeArrays(t) : o;
}
function Zn(t, e, n) {
  const o = e.mergeFunctions.mergeSets(t, e, n);
  return o === he.defaultMerge || e.useImplicitDefaultMerging && o === void 0 && e.mergeFunctions.mergeSets !== e.defaultMergeFunctions.mergeSets ? e.defaultMergeFunctions.mergeSets(t) : o;
}
function Qn(t, e, n) {
  const o = e.mergeFunctions.mergeMaps(t, e, n);
  return o === he.defaultMerge || e.useImplicitDefaultMerging && o === void 0 && e.mergeFunctions.mergeMaps !== e.defaultMergeFunctions.mergeMaps ? e.defaultMergeFunctions.mergeMaps(t) : o;
}
function dt(t, e, n) {
  const o = e.mergeFunctions.mergeOthers(t, e, n);
  return o === he.defaultMerge || e.useImplicitDefaultMerging && o === void 0 && e.mergeFunctions.mergeOthers !== e.defaultMergeFunctions.mergeOthers ? e.defaultMergeFunctions.mergeOthers(t) : o;
}
function St(t) {
  const e = Object.getOwnPropertyNames(t.constructor.prototype);
  for (let n = 0; n < e.length; n++) {
    const o = e[n], s = t[o];
    o !== "constructor" && typeof s == "function" && (t[o] = s.bind(t));
  }
  return t;
}
function eo(t, e) {
  return (n) => {
    if (t.isOpen()) {
      const o = t.el && n.currentTarget === t.el;
      (!H(e) && n.currentTarget.matches(e) || o) && t.tour.next();
    }
  };
}
function to(t) {
  const {
    event: e,
    selector: n
  } = t.options.advanceOn || {};
  if (e) {
    const o = eo(t, n);
    let s = null;
    if (!H(n) && (s = document.querySelector(n), !s))
      return console.error(`No element was found for the selector supplied to advanceOn: ${n}`);
    s ? (s.addEventListener(e, o), t.on("destroy", () => s.removeEventListener(e, o))) : (document.body.addEventListener(e, o, !0), t.on("destroy", () => document.body.removeEventListener(e, o, !0)));
  } else
    return console.error("advanceOn was defined, but no event name was passed.");
}
class no {
  constructor(e) {
  }
}
class oo {
  constructor(e, n) {
  }
}
function dn(t) {
  return !We(t) || t === "" ? "" : t.charAt(t.length - 1) !== "-" ? `${t}-` : t;
}
function so(t) {
  const e = t.options.attachTo || {}, n = Object.assign({}, e);
  if (ue(n.element) && (n.element = n.element.call(t)), We(n.element)) {
    try {
      n.element = document.querySelector(n.element);
    } catch {
    }
    n.element || console.error(`The element for this Shepherd step was not found ${e.element}`);
  }
  return n;
}
function fn(t) {
  return t == null ? !0 : !t.element || !t.on;
}
function hn() {
  let t = Date.now();
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (e) => {
    const n = (t + Math.random() * 16) % 16 | 0;
    return t = Math.floor(t / 16), (e == "x" ? n : n & 3 | 8).toString(16);
  });
}
const Le = Math.min, xe = Math.max, et = Math.round, Ge = Math.floor, de = (t) => ({
  x: t,
  y: t
}), ro = {
  left: "right",
  right: "left",
  bottom: "top",
  top: "bottom"
}, io = {
  start: "end",
  end: "start"
};
function mt(t, e, n) {
  return xe(t, Le(e, n));
}
function Pe(t, e) {
  return typeof t == "function" ? t(e) : t;
}
function we(t) {
  return t.split("-")[0];
}
function rt(t) {
  return t.split("-")[1];
}
function Ot(t) {
  return t === "x" ? "y" : "x";
}
function Et(t) {
  return t === "y" ? "height" : "width";
}
function Fe(t) {
  return ["top", "bottom"].includes(we(t)) ? "y" : "x";
}
function At(t) {
  return Ot(Fe(t));
}
function ao(t, e, n) {
  n === void 0 && (n = !1);
  const o = rt(t), s = At(t), r = Et(s);
  let i = s === "x" ? o === (n ? "end" : "start") ? "right" : "left" : o === "start" ? "bottom" : "top";
  return e.reference[r] > e.floating[r] && (i = tt(i)), [i, tt(i)];
}
function lo(t) {
  const e = tt(t);
  return [yt(t), e, yt(e)];
}
function yt(t) {
  return t.replace(/start|end/g, (e) => io[e]);
}
function co(t, e, n) {
  const o = ["left", "right"], s = ["right", "left"], r = ["top", "bottom"], i = ["bottom", "top"];
  switch (t) {
    case "top":
    case "bottom":
      return n ? e ? s : o : e ? o : s;
    case "left":
    case "right":
      return e ? r : i;
    default:
      return [];
  }
}
function uo(t, e, n, o) {
  const s = rt(t);
  let r = co(we(t), n === "start", o);
  return s && (r = r.map((i) => i + "-" + s), e && (r = r.concat(r.map(yt)))), r;
}
function tt(t) {
  return t.replace(/left|right|bottom|top/g, (e) => ro[e]);
}
function fo(t) {
  return B({
    top: 0,
    right: 0,
    bottom: 0,
    left: 0
  }, t);
}
function pn(t) {
  return typeof t != "number" ? fo(t) : {
    top: t,
    right: t,
    bottom: t,
    left: t
  };
}
function nt(t) {
  const {
    x: e,
    y: n,
    width: o,
    height: s
  } = t;
  return {
    width: o,
    height: s,
    top: n,
    left: e,
    right: e + o,
    bottom: n + s,
    x: e,
    y: n
  };
}
const ho = ["mainAxis", "crossAxis", "fallbackPlacements", "fallbackStrategy", "fallbackAxisSideDirection", "flipAlignment"], po = ["mainAxis", "crossAxis", "limiter"];
function Nt(t, e, n) {
  let {
    reference: o,
    floating: s
  } = t;
  const r = Fe(e), i = At(e), a = Et(i), l = we(e), c = r === "y", f = o.x + o.width / 2 - s.width / 2, p = o.y + o.height / 2 - s.height / 2, d = o[a] / 2 - s[a] / 2;
  let g;
  switch (l) {
    case "top":
      g = {
        x: f,
        y: o.y - s.height
      };
      break;
    case "bottom":
      g = {
        x: f,
        y: o.y + o.height
      };
      break;
    case "right":
      g = {
        x: o.x + o.width,
        y: p
      };
      break;
    case "left":
      g = {
        x: o.x - s.width,
        y: p
      };
      break;
    default:
      g = {
        x: o.x,
        y: o.y
      };
  }
  switch (rt(e)) {
    case "start":
      g[i] -= d * (n && c ? -1 : 1);
      break;
    case "end":
      g[i] += d * (n && c ? -1 : 1);
      break;
  }
  return g;
}
const go = async (t, e, n) => {
  const {
    placement: o = "bottom",
    strategy: s = "absolute",
    middleware: r = [],
    platform: i
  } = n, a = r.filter(Boolean), l = await (i.isRTL == null ? void 0 : i.isRTL(e));
  let c = await i.getElementRects({
    reference: t,
    floating: e,
    strategy: s
  }), {
    x: f,
    y: p
  } = Nt(c, o, l), d = o, g = {}, b = 0;
  for (let S = 0; S < a.length; S++) {
    const {
      name: k,
      fn: y
    } = a[S], {
      x,
      y: O,
      data: _,
      reset: m
    } = await y({
      x: f,
      y: p,
      initialPlacement: o,
      placement: d,
      strategy: s,
      middlewareData: g,
      rects: c,
      platform: i,
      elements: {
        reference: t,
        floating: e
      }
    });
    f = x ?? f, p = O ?? p, g = B({}, g, {
      [k]: B({}, g[k], _)
    }), m && b <= 50 && (b++, typeof m == "object" && (m.placement && (d = m.placement), m.rects && (c = m.rects === !0 ? await i.getElementRects({
      reference: t,
      floating: e,
      strategy: s
    }) : m.rects), {
      x: f,
      y: p
    } = Nt(c, d, l)), S = -1);
  }
  return {
    x: f,
    y: p,
    placement: d,
    strategy: s,
    middlewareData: g
  };
};
async function gn(t, e) {
  var n;
  e === void 0 && (e = {});
  const {
    x: o,
    y: s,
    platform: r,
    rects: i,
    elements: a,
    strategy: l
  } = t, {
    boundary: c = "clippingAncestors",
    rootBoundary: f = "viewport",
    elementContext: p = "floating",
    altBoundary: d = !1,
    padding: g = 0
  } = Pe(e, t), b = pn(g), k = a[d ? p === "floating" ? "reference" : "floating" : p], y = nt(await r.getClippingRect({
    element: (n = await (r.isElement == null ? void 0 : r.isElement(k))) == null || n ? k : k.contextElement || await (r.getDocumentElement == null ? void 0 : r.getDocumentElement(a.floating)),
    boundary: c,
    rootBoundary: f,
    strategy: l
  })), x = p === "floating" ? {
    x: o,
    y: s,
    width: i.floating.width,
    height: i.floating.height
  } : i.reference, O = await (r.getOffsetParent == null ? void 0 : r.getOffsetParent(a.floating)), _ = await (r.isElement == null ? void 0 : r.isElement(O)) ? await (r.getScale == null ? void 0 : r.getScale(O)) || {
    x: 1,
    y: 1
  } : {
    x: 1,
    y: 1
  }, m = nt(r.convertOffsetParentRelativeRectToViewportRelativeRect ? await r.convertOffsetParentRelativeRectToViewportRelativeRect({
    elements: a,
    rect: x,
    offsetParent: O,
    strategy: l
  }) : x);
  return {
    top: (y.top - m.top + b.top) / _.y,
    bottom: (m.bottom - y.bottom + b.bottom) / _.y,
    left: (y.left - m.left + b.left) / _.x,
    right: (m.right - y.right + b.right) / _.x
  };
}
const mo = (t) => ({
  name: "arrow",
  options: t,
  async fn(e) {
    const {
      x: n,
      y: o,
      placement: s,
      rects: r,
      platform: i,
      elements: a,
      middlewareData: l
    } = e, {
      element: c,
      padding: f = 0
    } = Pe(t, e) || {};
    if (c == null)
      return {};
    const p = pn(f), d = {
      x: n,
      y: o
    }, g = At(s), b = Et(g), S = await i.getDimensions(c), k = g === "y", y = k ? "top" : "left", x = k ? "bottom" : "right", O = k ? "clientHeight" : "clientWidth", _ = r.reference[b] + r.reference[g] - d[g] - r.floating[b], m = d[g] - r.reference[g], A = await (i.getOffsetParent == null ? void 0 : i.getOffsetParent(c));
    let F = A ? A[O] : 0;
    (!F || !await (i.isElement == null ? void 0 : i.isElement(A))) && (F = a.floating[O] || r.floating[b]);
    const K = _ / 2 - m / 2, I = F / 2 - S[b] / 2 - 1, C = Le(p[y], I), D = Le(p[x], I), E = C, W = F - S[b] - D, q = F / 2 - S[b] / 2 + K, Oe = mt(E, q, W), X = !l.arrow && rt(s) != null && q !== Oe && r.reference[b] / 2 - (q < E ? C : D) - S[b] / 2 < 0, Ee = X ? q < E ? q - E : q - W : 0;
    return {
      [g]: d[g] + Ee,
      data: B({
        [g]: Oe,
        centerOffset: q - Oe - Ee
      }, X && {
        alignmentOffset: Ee
      }),
      reset: X
    };
  }
}), yo = function(e) {
  return e === void 0 && (e = {}), {
    name: "flip",
    options: e,
    async fn(n) {
      var o, s;
      const {
        placement: r,
        middlewareData: i,
        rects: a,
        initialPlacement: l,
        platform: c,
        elements: f
      } = n, p = Pe(e, n), {
        mainAxis: d = !0,
        crossAxis: g = !0,
        fallbackPlacements: b,
        fallbackStrategy: S = "bestFit",
        fallbackAxisSideDirection: k = "none",
        flipAlignment: y = !0
      } = p, x = an(p, ho);
      if ((o = i.arrow) != null && o.alignmentOffset)
        return {};
      const O = we(r), _ = Fe(l), m = we(l) === l, A = await (c.isRTL == null ? void 0 : c.isRTL(f.floating)), F = b || (m || !y ? [tt(l)] : lo(l)), K = k !== "none";
      !b && K && F.push(...uo(l, y, k, A));
      const I = [l, ...F], C = await gn(n, x), D = [];
      let E = ((s = i.flip) == null ? void 0 : s.overflows) || [];
      if (d && D.push(C[O]), g) {
        const X = ao(r, a, A);
        D.push(C[X[0]], C[X[1]]);
      }
      if (E = [...E, {
        placement: r,
        overflows: D
      }], !D.every((X) => X <= 0)) {
        var W, q;
        const X = (((W = i.flip) == null ? void 0 : W.index) || 0) + 1, Ee = I[X];
        if (Ee)
          return {
            data: {
              index: X,
              overflows: E
            },
            reset: {
              placement: Ee
            }
          };
        let je = (q = E.filter((Ae) => Ae.overflows[0] <= 0).sort((Ae, ae) => Ae.overflows[1] - ae.overflows[1])[0]) == null ? void 0 : q.placement;
        if (!je)
          switch (S) {
            case "bestFit": {
              var Oe;
              const Ae = (Oe = E.filter((ae) => {
                if (K) {
                  const le = Fe(ae.placement);
                  return le === _ || // Create a bias to the `y` side axis due to horizontal
                  // reading directions favoring greater width.
                  le === "y";
                }
                return !0;
              }).map((ae) => [ae.placement, ae.overflows.filter((le) => le > 0).reduce((le, Tn) => le + Tn, 0)]).sort((ae, le) => ae[1] - le[1])[0]) == null ? void 0 : Oe[0];
              Ae && (je = Ae);
              break;
            }
            case "initialPlacement":
              je = l;
              break;
          }
        if (r !== je)
          return {
            reset: {
              placement: je
            }
          };
      }
      return {};
    }
  };
}, bo = function(e) {
  return e === void 0 && (e = {}), {
    name: "shift",
    options: e,
    async fn(n) {
      const {
        x: o,
        y: s,
        placement: r
      } = n, i = Pe(e, n), {
        mainAxis: a = !0,
        crossAxis: l = !1,
        limiter: c = {
          fn: (x) => {
            let {
              x: O,
              y: _
            } = x;
            return {
              x: O,
              y: _
            };
          }
        }
      } = i, f = an(i, po), p = {
        x: o,
        y: s
      }, d = await gn(n, f), g = Fe(we(r)), b = Ot(g);
      let S = p[b], k = p[g];
      if (a) {
        const x = b === "y" ? "top" : "left", O = b === "y" ? "bottom" : "right", _ = S + d[x], m = S - d[O];
        S = mt(_, S, m);
      }
      if (l) {
        const x = g === "y" ? "top" : "left", O = g === "y" ? "bottom" : "right", _ = k + d[x], m = k - d[O];
        k = mt(_, k, m);
      }
      const y = c.fn(B({}, n, {
        [b]: S,
        [g]: k
      }));
      return B({}, y, {
        data: {
          x: y.x - o,
          y: y.y - s
        }
      });
    }
  };
}, xo = function(e) {
  return e === void 0 && (e = {}), {
    options: e,
    fn(n) {
      const {
        x: o,
        y: s,
        placement: r,
        rects: i,
        middlewareData: a
      } = n, {
        offset: l = 0,
        mainAxis: c = !0,
        crossAxis: f = !0
      } = Pe(e, n), p = {
        x: o,
        y: s
      }, d = Fe(r), g = Ot(d);
      let b = p[g], S = p[d];
      const k = Pe(l, n), y = typeof k == "number" ? {
        mainAxis: k,
        crossAxis: 0
      } : B({
        mainAxis: 0,
        crossAxis: 0
      }, k);
      if (c) {
        const _ = g === "y" ? "height" : "width", m = i.reference[g] - i.floating[_] + y.mainAxis, A = i.reference[g] + i.reference[_] - y.mainAxis;
        b < m ? b = m : b > A && (b = A);
      }
      if (f) {
        var x, O;
        const _ = g === "y" ? "width" : "height", m = ["top", "left"].includes(we(r)), A = i.reference[d] - i.floating[_] + (m && ((x = a.offset) == null ? void 0 : x[d]) || 0) + (m ? 0 : y.crossAxis), F = i.reference[d] + i.reference[_] + (m ? 0 : ((O = a.offset) == null ? void 0 : O[d]) || 0) - (m ? y.crossAxis : 0);
        S < A ? S = A : S > F && (S = F);
      }
      return {
        [g]: b,
        [d]: S
      };
    }
  };
};
function Be(t) {
  return mn(t) ? (t.nodeName || "").toLowerCase() : "#document";
}
function U(t) {
  var e;
  return (t == null || (e = t.ownerDocument) == null ? void 0 : e.defaultView) || window;
}
function oe(t) {
  var e;
  return (e = (mn(t) ? t.ownerDocument : t.document) || window.document) == null ? void 0 : e.documentElement;
}
function mn(t) {
  return t instanceof Node || t instanceof U(t).Node;
}
function G(t) {
  return t instanceof Element || t instanceof U(t).Element;
}
function ee(t) {
  return t instanceof HTMLElement || t instanceof U(t).HTMLElement;
}
function Ht(t) {
  return typeof ShadowRoot > "u" ? !1 : t instanceof ShadowRoot || t instanceof U(t).ShadowRoot;
}
function Xe(t) {
  const {
    overflow: e,
    overflowX: n,
    overflowY: o,
    display: s
  } = Z(t);
  return /auto|scroll|overlay|hidden|clip/.test(e + o + n) && !["inline", "contents"].includes(s);
}
function _o(t) {
  return ["table", "td", "th"].includes(Be(t));
}
function it(t) {
  return [":popover-open", ":modal"].some((e) => {
    try {
      return t.matches(e);
    } catch {
      return !1;
    }
  });
}
function Ct(t) {
  const e = Tt(), n = G(t) ? Z(t) : t;
  return n.transform !== "none" || n.perspective !== "none" || (n.containerType ? n.containerType !== "normal" : !1) || !e && (n.backdropFilter ? n.backdropFilter !== "none" : !1) || !e && (n.filter ? n.filter !== "none" : !1) || ["transform", "perspective", "filter"].some((o) => (n.willChange || "").includes(o)) || ["paint", "layout", "strict", "content"].some((o) => (n.contain || "").includes(o));
}
function vo(t) {
  let e = fe(t);
  for (; ee(e) && !De(e); ) {
    if (Ct(e))
      return e;
    if (it(e))
      return null;
    e = fe(e);
  }
  return null;
}
function Tt() {
  return typeof CSS > "u" || !CSS.supports ? !1 : CSS.supports("-webkit-backdrop-filter", "none");
}
function De(t) {
  return ["html", "body", "#document"].includes(Be(t));
}
function Z(t) {
  return U(t).getComputedStyle(t);
}
function at(t) {
  return G(t) ? {
    scrollLeft: t.scrollLeft,
    scrollTop: t.scrollTop
  } : {
    scrollLeft: t.scrollX,
    scrollTop: t.scrollY
  };
}
function fe(t) {
  if (Be(t) === "html")
    return t;
  const e = (
    // Step into the shadow DOM of the parent of a slotted node.
    t.assignedSlot || // DOM Element detected.
    t.parentNode || // ShadowRoot detected.
    Ht(t) && t.host || // Fallback.
    oe(t)
  );
  return Ht(e) ? e.host : e;
}
function yn(t) {
  const e = fe(t);
  return De(e) ? t.ownerDocument ? t.ownerDocument.body : t.body : ee(e) && Xe(e) ? e : yn(e);
}
function qe(t, e, n) {
  var o;
  e === void 0 && (e = []), n === void 0 && (n = !0);
  const s = yn(t), r = s === ((o = t.ownerDocument) == null ? void 0 : o.body), i = U(s);
  return r ? e.concat(i, i.visualViewport || [], Xe(s) ? s : [], i.frameElement && n ? qe(i.frameElement) : []) : e.concat(s, qe(s, [], n));
}
function bn(t) {
  const e = Z(t);
  let n = parseFloat(e.width) || 0, o = parseFloat(e.height) || 0;
  const s = ee(t), r = s ? t.offsetWidth : n, i = s ? t.offsetHeight : o, a = et(n) !== r || et(o) !== i;
  return a && (n = r, o = i), {
    width: n,
    height: o,
    $: a
  };
}
function Rt(t) {
  return G(t) ? t : t.contextElement;
}
function Me(t) {
  const e = Rt(t);
  if (!ee(e))
    return de(1);
  const n = e.getBoundingClientRect(), {
    width: o,
    height: s,
    $: r
  } = bn(e);
  let i = (r ? et(n.width) : n.width) / o, a = (r ? et(n.height) : n.height) / s;
  return (!i || !Number.isFinite(i)) && (i = 1), (!a || !Number.isFinite(a)) && (a = 1), {
    x: i,
    y: a
  };
}
const wo = /* @__PURE__ */ de(0);
function xn(t) {
  const e = U(t);
  return !Tt() || !e.visualViewport ? wo : {
    x: e.visualViewport.offsetLeft,
    y: e.visualViewport.offsetTop
  };
}
function ko(t, e, n) {
  return e === void 0 && (e = !1), !n || e && n !== U(t) ? !1 : e;
}
function ke(t, e, n, o) {
  e === void 0 && (e = !1), n === void 0 && (n = !1);
  const s = t.getBoundingClientRect(), r = Rt(t);
  let i = de(1);
  e && (o ? G(o) && (i = Me(o)) : i = Me(t));
  const a = ko(r, n, o) ? xn(r) : de(0);
  let l = (s.left + a.x) / i.x, c = (s.top + a.y) / i.y, f = s.width / i.x, p = s.height / i.y;
  if (r) {
    const d = U(r), g = o && G(o) ? U(o) : o;
    let b = d, S = b.frameElement;
    for (; S && o && g !== b; ) {
      const k = Me(S), y = S.getBoundingClientRect(), x = Z(S), O = y.left + (S.clientLeft + parseFloat(x.paddingLeft)) * k.x, _ = y.top + (S.clientTop + parseFloat(x.paddingTop)) * k.y;
      l *= k.x, c *= k.y, f *= k.x, p *= k.y, l += O, c += _, b = U(S), S = b.frameElement;
    }
  }
  return nt({
    width: f,
    height: p,
    x: l,
    y: c
  });
}
function So(t) {
  let {
    elements: e,
    rect: n,
    offsetParent: o,
    strategy: s
  } = t;
  const r = s === "fixed", i = oe(o), a = e ? it(e.floating) : !1;
  if (o === i || a && r)
    return n;
  let l = {
    scrollLeft: 0,
    scrollTop: 0
  }, c = de(1);
  const f = de(0), p = ee(o);
  if ((p || !p && !r) && ((Be(o) !== "body" || Xe(i)) && (l = at(o)), ee(o))) {
    const d = ke(o);
    c = Me(o), f.x = d.x + o.clientLeft, f.y = d.y + o.clientTop;
  }
  return {
    width: n.width * c.x,
    height: n.height * c.y,
    x: n.x * c.x - l.scrollLeft * c.x + f.x,
    y: n.y * c.y - l.scrollTop * c.y + f.y
  };
}
function Oo(t) {
  return Array.from(t.getClientRects());
}
function _n(t) {
  return ke(oe(t)).left + at(t).scrollLeft;
}
function Eo(t) {
  const e = oe(t), n = at(t), o = t.ownerDocument.body, s = xe(e.scrollWidth, e.clientWidth, o.scrollWidth, o.clientWidth), r = xe(e.scrollHeight, e.clientHeight, o.scrollHeight, o.clientHeight);
  let i = -n.scrollLeft + _n(t);
  const a = -n.scrollTop;
  return Z(o).direction === "rtl" && (i += xe(e.clientWidth, o.clientWidth) - s), {
    width: s,
    height: r,
    x: i,
    y: a
  };
}
function Ao(t, e) {
  const n = U(t), o = oe(t), s = n.visualViewport;
  let r = o.clientWidth, i = o.clientHeight, a = 0, l = 0;
  if (s) {
    r = s.width, i = s.height;
    const c = Tt();
    (!c || c && e === "fixed") && (a = s.offsetLeft, l = s.offsetTop);
  }
  return {
    width: r,
    height: i,
    x: a,
    y: l
  };
}
function Co(t, e) {
  const n = ke(t, !0, e === "fixed"), o = n.top + t.clientTop, s = n.left + t.clientLeft, r = ee(t) ? Me(t) : de(1), i = t.clientWidth * r.x, a = t.clientHeight * r.y, l = s * r.x, c = o * r.y;
  return {
    width: i,
    height: a,
    x: l,
    y: c
  };
}
function Bt(t, e, n) {
  let o;
  if (e === "viewport")
    o = Ao(t, n);
  else if (e === "document")
    o = Eo(oe(t));
  else if (G(e))
    o = Co(e, n);
  else {
    const s = xn(t);
    o = B({}, e, {
      x: e.x - s.x,
      y: e.y - s.y
    });
  }
  return nt(o);
}
function vn(t, e) {
  const n = fe(t);
  return n === e || !G(n) || De(n) ? !1 : Z(n).position === "fixed" || vn(n, e);
}
function To(t, e) {
  const n = e.get(t);
  if (n)
    return n;
  let o = qe(t, [], !1).filter((a) => G(a) && Be(a) !== "body"), s = null;
  const r = Z(t).position === "fixed";
  let i = r ? fe(t) : t;
  for (; G(i) && !De(i); ) {
    const a = Z(i), l = Ct(i);
    !l && a.position === "fixed" && (s = null), (r ? !l && !s : !l && a.position === "static" && !!s && ["absolute", "fixed"].includes(s.position) || Xe(i) && !l && vn(t, i)) ? o = o.filter((f) => f !== i) : s = a, i = fe(i);
  }
  return e.set(t, o), o;
}
function Ro(t) {
  let {
    element: e,
    boundary: n,
    rootBoundary: o,
    strategy: s
  } = t;
  const i = [...n === "clippingAncestors" ? it(e) ? [] : To(e, this._c) : [].concat(n), o], a = i[0], l = i.reduce((c, f) => {
    const p = Bt(e, f, s);
    return c.top = xe(p.top, c.top), c.right = Le(p.right, c.right), c.bottom = Le(p.bottom, c.bottom), c.left = xe(p.left, c.left), c;
  }, Bt(e, a, s));
  return {
    width: l.right - l.left,
    height: l.bottom - l.top,
    x: l.left,
    y: l.top
  };
}
function Io(t) {
  const {
    width: e,
    height: n
  } = bn(t);
  return {
    width: e,
    height: n
  };
}
function Mo(t, e, n) {
  const o = ee(e), s = oe(e), r = n === "fixed", i = ke(t, !0, r, e);
  let a = {
    scrollLeft: 0,
    scrollTop: 0
  };
  const l = de(0);
  if (o || !o && !r)
    if ((Be(e) !== "body" || Xe(s)) && (a = at(e)), o) {
      const p = ke(e, !0, r, e);
      l.x = p.x + e.clientLeft, l.y = p.y + e.clientTop;
    } else s && (l.x = _n(s));
  const c = i.left + a.scrollLeft - l.x, f = i.top + a.scrollTop - l.y;
  return {
    x: c,
    y: f,
    width: i.width,
    height: i.height
  };
}
function ft(t) {
  return Z(t).position === "static";
}
function jt(t, e) {
  return !ee(t) || Z(t).position === "fixed" ? null : e ? e(t) : t.offsetParent;
}
function wn(t, e) {
  const n = U(t);
  if (it(t))
    return n;
  if (!ee(t)) {
    let s = fe(t);
    for (; s && !De(s); ) {
      if (G(s) && !ft(s))
        return s;
      s = fe(s);
    }
    return n;
  }
  let o = jt(t, e);
  for (; o && _o(o) && ft(o); )
    o = jt(o, e);
  return o && De(o) && ft(o) && !Ct(o) ? n : o || vo(t) || n;
}
const $o = async function(e) {
  const n = this.getOffsetParent || wn, o = this.getDimensions, s = await o(e.floating);
  return {
    reference: Mo(e.reference, await n(e.floating), e.strategy),
    floating: {
      x: 0,
      y: 0,
      width: s.width,
      height: s.height
    }
  };
};
function Lo(t) {
  return Z(t).direction === "rtl";
}
const Po = {
  convertOffsetParentRelativeRectToViewportRelativeRect: So,
  getDocumentElement: oe,
  getClippingRect: Ro,
  getOffsetParent: wn,
  getElementRects: $o,
  getClientRects: Oo,
  getDimensions: Io,
  getScale: Me,
  isElement: G,
  isRTL: Lo
};
function Fo(t, e) {
  let n = null, o;
  const s = oe(t);
  function r() {
    var a;
    clearTimeout(o), (a = n) == null || a.disconnect(), n = null;
  }
  function i(a, l) {
    a === void 0 && (a = !1), l === void 0 && (l = 1), r();
    const {
      left: c,
      top: f,
      width: p,
      height: d
    } = t.getBoundingClientRect();
    if (a || e(), !p || !d)
      return;
    const g = Ge(f), b = Ge(s.clientWidth - (c + p)), S = Ge(s.clientHeight - (f + d)), k = Ge(c), x = {
      rootMargin: -g + "px " + -b + "px " + -S + "px " + -k + "px",
      threshold: xe(0, Le(1, l)) || 1
    };
    let O = !0;
    function _(m) {
      const A = m[0].intersectionRatio;
      if (A !== l) {
        if (!O)
          return i();
        A ? i(!1, A) : o = setTimeout(() => {
          i(!1, 1e-7);
        }, 1e3);
      }
      O = !1;
    }
    try {
      n = new IntersectionObserver(_, B({}, x, {
        // Handle <iframe>s
        root: s.ownerDocument
      }));
    } catch {
      n = new IntersectionObserver(_, x);
    }
    n.observe(t);
  }
  return i(!0), r;
}
function Do(t, e, n, o) {
  o === void 0 && (o = {});
  const {
    ancestorScroll: s = !0,
    ancestorResize: r = !0,
    elementResize: i = typeof ResizeObserver == "function",
    layoutShift: a = typeof IntersectionObserver == "function",
    animationFrame: l = !1
  } = o, c = Rt(t), f = s || r ? [...c ? qe(c) : [], ...qe(e)] : [];
  f.forEach((y) => {
    s && y.addEventListener("scroll", n, {
      passive: !0
    }), r && y.addEventListener("resize", n);
  });
  const p = c && a ? Fo(c, n) : null;
  let d = -1, g = null;
  i && (g = new ResizeObserver((y) => {
    let [x] = y;
    x && x.target === c && g && (g.unobserve(e), cancelAnimationFrame(d), d = requestAnimationFrame(() => {
      var O;
      (O = g) == null || O.observe(e);
    })), n();
  }), c && !l && g.observe(c), g.observe(e));
  let b, S = l ? ke(t) : null;
  l && k();
  function k() {
    const y = ke(t);
    S && (y.x !== S.x || y.y !== S.y || y.width !== S.width || y.height !== S.height) && n(), S = y, b = requestAnimationFrame(k);
  }
  return n(), () => {
    var y;
    f.forEach((x) => {
      s && x.removeEventListener("scroll", n), r && x.removeEventListener("resize", n);
    }), p?.(), (y = g) == null || y.disconnect(), g = null, l && cancelAnimationFrame(b);
  };
}
const No = bo, Ho = yo, Bo = mo, jo = xo, Vo = (t, e, n) => {
  const o = /* @__PURE__ */ new Map(), s = B({
    platform: Po
  }, n), r = B({}, s.platform, {
    _c: o
  });
  return go(t, e, B({}, s, {
    platform: r
  }));
};
function Uo(t) {
  t.cleanup && t.cleanup();
  const e = t._getResolvedAttachToOptions();
  let n = e.element;
  const o = Xo(e, t), s = fn(e);
  return s && (n = document.body, t.shepherdElementComponent.getElement().classList.add("shepherd-centered")), t.cleanup = Do(n, t.el, () => {
    if (!t.el) {
      t.cleanup == null || t.cleanup();
      return;
    }
    qo(n, t, o, s);
  }), t.target = e.element, o;
}
function zo(t, e) {
  return {
    floatingUIOptions: kt(t.floatingUIOptions || {}, e.floatingUIOptions || {})
  };
}
function Wo(t) {
  t.cleanup && t.cleanup(), t.cleanup = null;
}
function qo(t, e, n, o) {
  return Vo(t, e.el, n).then(Yo(e, o)).then((s) => new Promise((r) => {
    setTimeout(() => r(s), 300);
  })).then((s) => {
    s != null && s.el && s.el.focus({
      preventScroll: !0
    });
  });
}
function Yo(t, e) {
  return ({
    x: n,
    y: o,
    placement: s,
    middlewareData: r
  }) => (t.el && (e ? Object.assign(t.el.style, {
    position: "fixed",
    left: "50%",
    top: "50%",
    transform: "translate(-50%, -50%)"
  }) : Object.assign(t.el.style, {
    position: "absolute",
    left: `${n}px`,
    top: `${o}px`
  }), t.el.dataset.popperPlacement = s, Ko(t.el, r)), t);
}
function Ko(t, e) {
  const n = t.querySelector(".shepherd-arrow");
  if (Ke(n) && e.arrow) {
    const {
      x: o,
      y: s
    } = e.arrow;
    Object.assign(n.style, {
      left: o != null ? `${o}px` : "",
      top: s != null ? `${s}px` : ""
    });
  }
}
function Xo(t, e) {
  const n = {
    strategy: "absolute"
  };
  n.middleware = [];
  const o = Jo(e);
  if (!fn(t)) {
    if (n.middleware.push(
      Ho(),
      // Replicate PopperJS default behavior.
      No({
        limiter: jo(),
        crossAxis: !0
      })
    ), o) {
      var r, i;
      const a = (t == null || (r = t.on) == null ? void 0 : r.includes("-start")) || (t == null || (i = t.on) == null ? void 0 : i.includes("-end"));
      n.middleware.push(Bo({
        element: o,
        padding: a ? 4 : 0
      }));
    }
    n.placement = t.on;
  }
  return kt(e.options.floatingUIOptions || {}, n);
}
function Jo(t) {
  return t.options.arrow && t.el ? t.el.querySelector(".shepherd-arrow") : !1;
}
function z() {
}
function Go(t, e) {
  for (const n in e) t[n] = e[n];
  return (
    /** @type {T & S} */
    t
  );
}
function kn(t) {
  return t();
}
function Vt() {
  return /* @__PURE__ */ Object.create(null);
}
function Je(t) {
  t.forEach(kn);
}
function It(t) {
  return typeof t == "function";
}
function se(t, e) {
  return t != t ? e == e : t !== e || t && typeof t == "object" || typeof t == "function";
}
function Zo(t) {
  return Object.keys(t).length === 0;
}
function Ne(t, e) {
  t.appendChild(e);
}
function Q(t, e, n) {
  t.insertBefore(e, n || null);
}
function Y(t) {
  t.parentNode && t.parentNode.removeChild(t);
}
function Qo(t, e) {
  for (let n = 0; n < t.length; n += 1)
    t[n] && t[n].d(e);
}
function te(t) {
  return document.createElement(t);
}
function Ut(t) {
  return document.createElementNS("http://www.w3.org/2000/svg", t);
}
function Sn(t) {
  return document.createTextNode(t);
}
function ot() {
  return Sn(" ");
}
function es() {
  return Sn("");
}
function lt(t, e, n, o) {
  return t.addEventListener(e, n, o), () => t.removeEventListener(e, n, o);
}
function $(t, e, n) {
  n == null ? t.removeAttribute(e) : t.getAttribute(e) !== n && t.setAttribute(e, n);
}
const ts = ["width", "height"];
function zt(t, e) {
  const n = Object.getOwnPropertyDescriptors(t.__proto__);
  for (const o in e)
    e[o] == null ? t.removeAttribute(o) : o === "style" ? t.style.cssText = e[o] : o === "__value" ? t.value = t[o] = e[o] : n[o] && n[o].set && ts.indexOf(o) === -1 ? t[o] = e[o] : $(t, o, e[o]);
}
function ns(t) {
  return Array.from(t.childNodes);
}
function Ce(t, e, n) {
  t.classList.toggle(e, !!n);
}
let Ye;
function Ve(t) {
  Ye = t;
}
function On() {
  if (!Ye) throw new Error("Function called outside component initialization");
  return Ye;
}
function os(t) {
  On().$$.on_mount.push(t);
}
function Mt(t) {
  On().$$.after_update.push(t);
}
const Re = [], He = [];
let $e = [];
const Wt = [], ss = /* @__PURE__ */ Promise.resolve();
let bt = !1;
function rs() {
  bt || (bt = !0, ss.then(En));
}
function xt(t) {
  $e.push(t);
}
const ht = /* @__PURE__ */ new Set();
let Te = 0;
function En() {
  if (Te !== 0)
    return;
  const t = Ye;
  do {
    try {
      for (; Te < Re.length; ) {
        const e = Re[Te];
        Te++, Ve(e), is(e.$$);
      }
    } catch (e) {
      throw Re.length = 0, Te = 0, e;
    }
    for (Ve(null), Re.length = 0, Te = 0; He.length; ) He.pop()();
    for (let e = 0; e < $e.length; e += 1) {
      const n = $e[e];
      ht.has(n) || (ht.add(n), n());
    }
    $e.length = 0;
  } while (Re.length);
  for (; Wt.length; )
    Wt.pop()();
  bt = !1, ht.clear(), Ve(t);
}
function is(t) {
  if (t.fragment !== null) {
    t.update(), Je(t.before_update);
    const e = t.dirty;
    t.dirty = [-1], t.fragment && t.fragment.p(t.ctx, e), t.after_update.forEach(xt);
  }
}
function as(t) {
  const e = [], n = [];
  $e.forEach((o) => t.indexOf(o) === -1 ? e.push(o) : n.push(o)), n.forEach((o) => o()), $e = e;
}
const Qe = /* @__PURE__ */ new Set();
let ye;
function _e() {
  ye = {
    r: 0,
    c: [],
    p: ye
    // parent group
  };
}
function ve() {
  ye.r || Je(ye.c), ye = ye.p;
}
function M(t, e) {
  t && t.i && (Qe.delete(t), t.i(e));
}
function L(t, e, n, o) {
  if (t && t.o) {
    if (Qe.has(t)) return;
    Qe.add(t), ye.c.push(() => {
      Qe.delete(t), o && (n && t.d(1), o());
    }), t.o(e);
  } else o && o();
}
function qt(t) {
  return t?.length !== void 0 ? t : Array.from(t);
}
function ls(t, e) {
  const n = {}, o = {}, s = {
    $$scope: 1
  };
  let r = t.length;
  for (; r--; ) {
    const i = t[r], a = e[r];
    if (a) {
      for (const l in i)
        l in a || (o[l] = 1);
      for (const l in a)
        s[l] || (n[l] = a[l], s[l] = 1);
      t[r] = a;
    } else
      for (const l in i)
        s[l] = 1;
  }
  for (const i in o)
    i in n || (n[i] = void 0);
  return n;
}
function Se(t) {
  t && t.c();
}
function pe(t, e, n) {
  const {
    fragment: o,
    after_update: s
  } = t.$$;
  o && o.m(e, n), xt(() => {
    const r = t.$$.on_mount.map(kn).filter(It);
    t.$$.on_destroy ? t.$$.on_destroy.push(...r) : Je(r), t.$$.on_mount = [];
  }), s.forEach(xt);
}
function ge(t, e) {
  const n = t.$$;
  n.fragment !== null && (as(n.after_update), Je(n.on_destroy), n.fragment && n.fragment.d(e), n.on_destroy = n.fragment = null, n.ctx = []);
}
function cs(t, e) {
  t.$$.dirty[0] === -1 && (Re.push(t), rs(), t.$$.dirty.fill(0)), t.$$.dirty[e / 31 | 0] |= 1 << e % 31;
}
function re(t, e, n, o, s, r, i = null, a = [-1]) {
  const l = Ye;
  Ve(t);
  const c = t.$$ = {
    fragment: null,
    ctx: [],
    // state
    props: r,
    update: z,
    not_equal: s,
    bound: Vt(),
    // lifecycle
    on_mount: [],
    on_destroy: [],
    on_disconnect: [],
    before_update: [],
    after_update: [],
    context: new Map(e.context || (l ? l.$$.context : [])),
    // everything else
    callbacks: Vt(),
    dirty: a,
    skip_bound: !1,
    root: e.target || l.$$.root
  };
  i && i(c.root);
  let f = !1;
  if (c.ctx = n ? n(t, e.props || {}, (p, d, ...g) => {
    const b = g.length ? g[0] : d;
    return c.ctx && s(c.ctx[p], c.ctx[p] = b) && (!c.skip_bound && c.bound[p] && c.bound[p](b), f && cs(t, p)), d;
  }) : [], c.update(), f = !0, Je(c.before_update), c.fragment = o ? o(c.ctx) : !1, e.target) {
    if (e.hydrate) {
      const p = ns(e.target);
      c.fragment && c.fragment.l(p), p.forEach(Y);
    } else
      c.fragment && c.fragment.c();
    e.intro && M(t.$$.fragment), pe(t, e.target, e.anchor), En();
  }
  Ve(l);
}
class ie {
  constructor() {
    this.$$ = void 0, this.$$set = void 0;
  }
  /** @returns {void} */
  $destroy() {
    ge(this, 1), this.$destroy = z;
  }
  /**
   * @template {Extract<keyof Events, string>} K
   * @param {K} type
   * @param {((e: Events[K]) => void) | null | undefined} callback
   * @returns {() => void}
   */
  $on(e, n) {
    if (!It(n))
      return z;
    const o = this.$$.callbacks[e] || (this.$$.callbacks[e] = []);
    return o.push(n), () => {
      const s = o.indexOf(n);
      s !== -1 && o.splice(s, 1);
    };
  }
  /**
   * @param {Partial<Props>} props
   * @returns {void}
   */
  $set(e) {
    this.$$set && !Zo(e) && (this.$$.skip_bound = !0, this.$$set(e), this.$$.skip_bound = !1);
  }
}
const us = "4";
typeof window < "u" && (window.__svelte || (window.__svelte = {
  v: /* @__PURE__ */ new Set()
})).v.add(us);
function ds(t) {
  let e, n, o, s, r;
  return {
    c() {
      e = te("button"), $(e, "aria-label", n = /*label*/
      t[3] ? (
        /*label*/
        t[3]
      ) : null), $(e, "class", o = `${/*classes*/
      t[1] || ""} shepherd-button ${/*secondary*/
      t[4] ? "shepherd-button-secondary" : ""}`), e.disabled = /*disabled*/
      t[2], $(e, "tabindex", "0"), $(e, "type", "button");
    },
    m(i, a) {
      Q(i, e, a), e.innerHTML = /*text*/
      t[5], s || (r = lt(e, "click", function() {
        It(
          /*action*/
          t[0]
        ) && t[0].apply(this, arguments);
      }), s = !0);
    },
    p(i, [a]) {
      t = i, a & /*text*/
      32 && (e.innerHTML = /*text*/
      t[5]), a & /*label*/
      8 && n !== (n = /*label*/
      t[3] ? (
        /*label*/
        t[3]
      ) : null) && $(e, "aria-label", n), a & /*classes, secondary*/
      18 && o !== (o = `${/*classes*/
      t[1] || ""} shepherd-button ${/*secondary*/
      t[4] ? "shepherd-button-secondary" : ""}`) && $(e, "class", o), a & /*disabled*/
      4 && (e.disabled = /*disabled*/
      t[2]);
    },
    i: z,
    o: z,
    d(i) {
      i && Y(e), s = !1, r();
    }
  };
}
function fs(t, e, n) {
  let {
    config: o,
    step: s
  } = e, r, i, a, l, c, f;
  function p(d) {
    return ue(d) ? d = d.call(s) : d;
  }
  return t.$$set = (d) => {
    "config" in d && n(6, o = d.config), "step" in d && n(7, s = d.step);
  }, t.$$.update = () => {
    t.$$.dirty & /*config, step*/
    192 && (n(0, r = o.action ? o.action.bind(s.tour) : null), n(1, i = o.classes), n(2, a = o.disabled ? p(o.disabled) : !1), n(3, l = o.label ? p(o.label) : null), n(4, c = o.secondary), n(5, f = o.text ? p(o.text) : null));
  }, [r, i, a, l, c, f, o, s];
}
class hs extends ie {
  constructor(e) {
    super(), re(this, e, fs, ds, se, {
      config: 6,
      step: 7
    });
  }
}
function Yt(t, e, n) {
  const o = t.slice();
  return o[2] = e[n], o;
}
function Kt(t) {
  let e, n, o = qt(
    /*buttons*/
    t[1]
  ), s = [];
  for (let i = 0; i < o.length; i += 1)
    s[i] = Xt(Yt(t, o, i));
  const r = (i) => L(s[i], 1, 1, () => {
    s[i] = null;
  });
  return {
    c() {
      for (let i = 0; i < s.length; i += 1)
        s[i].c();
      e = es();
    },
    m(i, a) {
      for (let l = 0; l < s.length; l += 1)
        s[l] && s[l].m(i, a);
      Q(i, e, a), n = !0;
    },
    p(i, a) {
      if (a & /*buttons, step*/
      3) {
        o = qt(
          /*buttons*/
          i[1]
        );
        let l;
        for (l = 0; l < o.length; l += 1) {
          const c = Yt(i, o, l);
          s[l] ? (s[l].p(c, a), M(s[l], 1)) : (s[l] = Xt(c), s[l].c(), M(s[l], 1), s[l].m(e.parentNode, e));
        }
        for (_e(), l = o.length; l < s.length; l += 1)
          r(l);
        ve();
      }
    },
    i(i) {
      if (!n) {
        for (let a = 0; a < o.length; a += 1)
          M(s[a]);
        n = !0;
      }
    },
    o(i) {
      s = s.filter(Boolean);
      for (let a = 0; a < s.length; a += 1)
        L(s[a]);
      n = !1;
    },
    d(i) {
      i && Y(e), Qo(s, i);
    }
  };
}
function Xt(t) {
  let e, n;
  return e = new hs({
    props: {
      config: (
        /*config*/
        t[2]
      ),
      step: (
        /*step*/
        t[0]
      )
    }
  }), {
    c() {
      Se(e.$$.fragment);
    },
    m(o, s) {
      pe(e, o, s), n = !0;
    },
    p(o, s) {
      const r = {};
      s & /*buttons*/
      2 && (r.config = /*config*/
      o[2]), s & /*step*/
      1 && (r.step = /*step*/
      o[0]), e.$set(r);
    },
    i(o) {
      n || (M(e.$$.fragment, o), n = !0);
    },
    o(o) {
      L(e.$$.fragment, o), n = !1;
    },
    d(o) {
      ge(e, o);
    }
  };
}
function ps(t) {
  let e, n, o = (
    /*buttons*/
    t[1] && Kt(t)
  );
  return {
    c() {
      e = te("footer"), o && o.c(), $(e, "class", "shepherd-footer");
    },
    m(s, r) {
      Q(s, e, r), o && o.m(e, null), n = !0;
    },
    p(s, [r]) {
      /*buttons*/
      s[1] ? o ? (o.p(s, r), r & /*buttons*/
      2 && M(o, 1)) : (o = Kt(s), o.c(), M(o, 1), o.m(e, null)) : o && (_e(), L(o, 1, 1, () => {
        o = null;
      }), ve());
    },
    i(s) {
      n || (M(o), n = !0);
    },
    o(s) {
      L(o), n = !1;
    },
    d(s) {
      s && Y(e), o && o.d();
    }
  };
}
function gs(t, e, n) {
  let o, {
    step: s
  } = e;
  return t.$$set = (r) => {
    "step" in r && n(0, s = r.step);
  }, t.$$.update = () => {
    t.$$.dirty & /*step*/
    1 && n(1, o = s.options.buttons);
  }, [s, o];
}
class ms extends ie {
  constructor(e) {
    super(), re(this, e, gs, ps, se, {
      step: 0
    });
  }
}
function ys(t) {
  let e, n, o, s, r;
  return {
    c() {
      e = te("button"), n = te("span"), n.textContent = "×", $(n, "aria-hidden", "true"), $(e, "aria-label", o = /*cancelIcon*/
      t[0].label ? (
        /*cancelIcon*/
        t[0].label
      ) : "Close Tour"), $(e, "class", "shepherd-cancel-icon"), $(e, "type", "button");
    },
    m(i, a) {
      Q(i, e, a), Ne(e, n), s || (r = lt(
        e,
        "click",
        /*handleCancelClick*/
        t[1]
      ), s = !0);
    },
    p(i, [a]) {
      a & /*cancelIcon*/
      1 && o !== (o = /*cancelIcon*/
      i[0].label ? (
        /*cancelIcon*/
        i[0].label
      ) : "Close Tour") && $(e, "aria-label", o);
    },
    i: z,
    o: z,
    d(i) {
      i && Y(e), s = !1, r();
    }
  };
}
function bs(t, e, n) {
  let {
    cancelIcon: o,
    step: s
  } = e;
  const r = (i) => {
    i.preventDefault(), s.cancel();
  };
  return t.$$set = (i) => {
    "cancelIcon" in i && n(0, o = i.cancelIcon), "step" in i && n(2, s = i.step);
  }, [o, r, s];
}
class xs extends ie {
  constructor(e) {
    super(), re(this, e, bs, ys, se, {
      cancelIcon: 0,
      step: 2
    });
  }
}
function _s(t) {
  let e;
  return {
    c() {
      e = te("h3"), $(
        e,
        "id",
        /*labelId*/
        t[1]
      ), $(e, "class", "shepherd-title");
    },
    m(n, o) {
      Q(n, e, o), t[3](e);
    },
    p(n, [o]) {
      o & /*labelId*/
      2 && $(
        e,
        "id",
        /*labelId*/
        n[1]
      );
    },
    i: z,
    o: z,
    d(n) {
      n && Y(e), t[3](null);
    }
  };
}
function vs(t, e, n) {
  let {
    labelId: o,
    element: s,
    title: r
  } = e;
  Mt(() => {
    ue(r) && n(2, r = r()), n(0, s.innerHTML = r, s);
  });
  function i(a) {
    He[a ? "unshift" : "push"](() => {
      s = a, n(0, s);
    });
  }
  return t.$$set = (a) => {
    "labelId" in a && n(1, o = a.labelId), "element" in a && n(0, s = a.element), "title" in a && n(2, r = a.title);
  }, [s, o, r, i];
}
class ws extends ie {
  constructor(e) {
    super(), re(this, e, vs, _s, se, {
      labelId: 1,
      element: 0,
      title: 2
    });
  }
}
function Jt(t) {
  let e, n;
  return e = new ws({
    props: {
      labelId: (
        /*labelId*/
        t[0]
      ),
      title: (
        /*title*/
        t[2]
      )
    }
  }), {
    c() {
      Se(e.$$.fragment);
    },
    m(o, s) {
      pe(e, o, s), n = !0;
    },
    p(o, s) {
      const r = {};
      s & /*labelId*/
      1 && (r.labelId = /*labelId*/
      o[0]), s & /*title*/
      4 && (r.title = /*title*/
      o[2]), e.$set(r);
    },
    i(o) {
      n || (M(e.$$.fragment, o), n = !0);
    },
    o(o) {
      L(e.$$.fragment, o), n = !1;
    },
    d(o) {
      ge(e, o);
    }
  };
}
function Gt(t) {
  let e, n;
  return e = new xs({
    props: {
      cancelIcon: (
        /*cancelIcon*/
        t[3]
      ),
      step: (
        /*step*/
        t[1]
      )
    }
  }), {
    c() {
      Se(e.$$.fragment);
    },
    m(o, s) {
      pe(e, o, s), n = !0;
    },
    p(o, s) {
      const r = {};
      s & /*cancelIcon*/
      8 && (r.cancelIcon = /*cancelIcon*/
      o[3]), s & /*step*/
      2 && (r.step = /*step*/
      o[1]), e.$set(r);
    },
    i(o) {
      n || (M(e.$$.fragment, o), n = !0);
    },
    o(o) {
      L(e.$$.fragment, o), n = !1;
    },
    d(o) {
      ge(e, o);
    }
  };
}
function ks(t) {
  let e, n, o, s = (
    /*title*/
    t[2] && Jt(t)
  ), r = (
    /*cancelIcon*/
    t[3] && /*cancelIcon*/
    t[3].enabled && Gt(t)
  );
  return {
    c() {
      e = te("header"), s && s.c(), n = ot(), r && r.c(), $(e, "class", "shepherd-header");
    },
    m(i, a) {
      Q(i, e, a), s && s.m(e, null), Ne(e, n), r && r.m(e, null), o = !0;
    },
    p(i, [a]) {
      /*title*/
      i[2] ? s ? (s.p(i, a), a & /*title*/
      4 && M(s, 1)) : (s = Jt(i), s.c(), M(s, 1), s.m(e, n)) : s && (_e(), L(s, 1, 1, () => {
        s = null;
      }), ve()), /*cancelIcon*/
      i[3] && /*cancelIcon*/
      i[3].enabled ? r ? (r.p(i, a), a & /*cancelIcon*/
      8 && M(r, 1)) : (r = Gt(i), r.c(), M(r, 1), r.m(e, null)) : r && (_e(), L(r, 1, 1, () => {
        r = null;
      }), ve());
    },
    i(i) {
      o || (M(s), M(r), o = !0);
    },
    o(i) {
      L(s), L(r), o = !1;
    },
    d(i) {
      i && Y(e), s && s.d(), r && r.d();
    }
  };
}
function Ss(t, e, n) {
  let {
    labelId: o,
    step: s
  } = e, r, i;
  return t.$$set = (a) => {
    "labelId" in a && n(0, o = a.labelId), "step" in a && n(1, s = a.step);
  }, t.$$.update = () => {
    t.$$.dirty & /*step*/
    2 && (n(2, r = s.options.title), n(3, i = s.options.cancelIcon));
  }, [o, s, r, i];
}
class Os extends ie {
  constructor(e) {
    super(), re(this, e, Ss, ks, se, {
      labelId: 0,
      step: 1
    });
  }
}
function Es(t) {
  let e;
  return {
    c() {
      e = te("div"), $(e, "class", "shepherd-text"), $(
        e,
        "id",
        /*descriptionId*/
        t[1]
      );
    },
    m(n, o) {
      Q(n, e, o), t[3](e);
    },
    p(n, [o]) {
      o & /*descriptionId*/
      2 && $(
        e,
        "id",
        /*descriptionId*/
        n[1]
      );
    },
    i: z,
    o: z,
    d(n) {
      n && Y(e), t[3](null);
    }
  };
}
function As(t, e, n) {
  let {
    descriptionId: o,
    element: s,
    step: r
  } = e;
  Mt(() => {
    let {
      text: a
    } = r.options;
    ue(a) && (a = a.call(r)), Ke(a) ? s.appendChild(a) : n(0, s.innerHTML = a, s);
  });
  function i(a) {
    He[a ? "unshift" : "push"](() => {
      s = a, n(0, s);
    });
  }
  return t.$$set = (a) => {
    "descriptionId" in a && n(1, o = a.descriptionId), "element" in a && n(0, s = a.element), "step" in a && n(2, r = a.step);
  }, [s, o, r, i];
}
class Cs extends ie {
  constructor(e) {
    super(), re(this, e, As, Es, se, {
      descriptionId: 1,
      element: 0,
      step: 2
    });
  }
}
function Zt(t) {
  let e, n;
  return e = new Os({
    props: {
      labelId: (
        /*labelId*/
        t[1]
      ),
      step: (
        /*step*/
        t[2]
      )
    }
  }), {
    c() {
      Se(e.$$.fragment);
    },
    m(o, s) {
      pe(e, o, s), n = !0;
    },
    p(o, s) {
      const r = {};
      s & /*labelId*/
      2 && (r.labelId = /*labelId*/
      o[1]), s & /*step*/
      4 && (r.step = /*step*/
      o[2]), e.$set(r);
    },
    i(o) {
      n || (M(e.$$.fragment, o), n = !0);
    },
    o(o) {
      L(e.$$.fragment, o), n = !1;
    },
    d(o) {
      ge(e, o);
    }
  };
}
function Qt(t) {
  let e, n;
  return e = new Cs({
    props: {
      descriptionId: (
        /*descriptionId*/
        t[0]
      ),
      step: (
        /*step*/
        t[2]
      )
    }
  }), {
    c() {
      Se(e.$$.fragment);
    },
    m(o, s) {
      pe(e, o, s), n = !0;
    },
    p(o, s) {
      const r = {};
      s & /*descriptionId*/
      1 && (r.descriptionId = /*descriptionId*/
      o[0]), s & /*step*/
      4 && (r.step = /*step*/
      o[2]), e.$set(r);
    },
    i(o) {
      n || (M(e.$$.fragment, o), n = !0);
    },
    o(o) {
      L(e.$$.fragment, o), n = !1;
    },
    d(o) {
      ge(e, o);
    }
  };
}
function en(t) {
  let e, n;
  return e = new ms({
    props: {
      step: (
        /*step*/
        t[2]
      )
    }
  }), {
    c() {
      Se(e.$$.fragment);
    },
    m(o, s) {
      pe(e, o, s), n = !0;
    },
    p(o, s) {
      const r = {};
      s & /*step*/
      4 && (r.step = /*step*/
      o[2]), e.$set(r);
    },
    i(o) {
      n || (M(e.$$.fragment, o), n = !0);
    },
    o(o) {
      L(e.$$.fragment, o), n = !1;
    },
    d(o) {
      ge(e, o);
    }
  };
}
function Ts(t) {
  let e, n = !H(
    /*step*/
    t[2].options.title
  ) || /*step*/
  t[2].options.cancelIcon && /*step*/
  t[2].options.cancelIcon.enabled, o, s = !H(
    /*step*/
    t[2].options.text
  ), r, i = Array.isArray(
    /*step*/
    t[2].options.buttons
  ) && /*step*/
  t[2].options.buttons.length, a, l = n && Zt(t), c = s && Qt(t), f = i && en(t);
  return {
    c() {
      e = te("div"), l && l.c(), o = ot(), c && c.c(), r = ot(), f && f.c(), $(e, "class", "shepherd-content");
    },
    m(p, d) {
      Q(p, e, d), l && l.m(e, null), Ne(e, o), c && c.m(e, null), Ne(e, r), f && f.m(e, null), a = !0;
    },
    p(p, [d]) {
      d & /*step*/
      4 && (n = !H(
        /*step*/
        p[2].options.title
      ) || /*step*/
      p[2].options.cancelIcon && /*step*/
      p[2].options.cancelIcon.enabled), n ? l ? (l.p(p, d), d & /*step*/
      4 && M(l, 1)) : (l = Zt(p), l.c(), M(l, 1), l.m(e, o)) : l && (_e(), L(l, 1, 1, () => {
        l = null;
      }), ve()), d & /*step*/
      4 && (s = !H(
        /*step*/
        p[2].options.text
      )), s ? c ? (c.p(p, d), d & /*step*/
      4 && M(c, 1)) : (c = Qt(p), c.c(), M(c, 1), c.m(e, r)) : c && (_e(), L(c, 1, 1, () => {
        c = null;
      }), ve()), d & /*step*/
      4 && (i = Array.isArray(
        /*step*/
        p[2].options.buttons
      ) && /*step*/
      p[2].options.buttons.length), i ? f ? (f.p(p, d), d & /*step*/
      4 && M(f, 1)) : (f = en(p), f.c(), M(f, 1), f.m(e, null)) : f && (_e(), L(f, 1, 1, () => {
        f = null;
      }), ve());
    },
    i(p) {
      a || (M(l), M(c), M(f), a = !0);
    },
    o(p) {
      L(l), L(c), L(f), a = !1;
    },
    d(p) {
      p && Y(e), l && l.d(), c && c.d(), f && f.d();
    }
  };
}
function Rs(t, e, n) {
  let {
    descriptionId: o,
    labelId: s,
    step: r
  } = e;
  return t.$$set = (i) => {
    "descriptionId" in i && n(0, o = i.descriptionId), "labelId" in i && n(1, s = i.labelId), "step" in i && n(2, r = i.step);
  }, [o, s, r];
}
class Is extends ie {
  constructor(e) {
    super(), re(this, e, Rs, Ts, se, {
      descriptionId: 0,
      labelId: 1,
      step: 2
    });
  }
}
function tn(t) {
  let e;
  return {
    c() {
      e = te("div"), $(e, "class", "shepherd-arrow"), $(e, "data-popper-arrow", "");
    },
    m(n, o) {
      Q(n, e, o);
    },
    d(n) {
      n && Y(e);
    }
  };
}
function Ms(t) {
  let e, n, o, s, r, i, a, l, c = (
    /*step*/
    t[4].options.arrow && /*step*/
    t[4].options.attachTo && /*step*/
    t[4].options.attachTo.element && /*step*/
    t[4].options.attachTo.on && tn()
  );
  o = new Is({
    props: {
      descriptionId: (
        /*descriptionId*/
        t[2]
      ),
      labelId: (
        /*labelId*/
        t[3]
      ),
      step: (
        /*step*/
        t[4]
      )
    }
  });
  let f = [
    {
      "aria-describedby": s = H(
        /*step*/
        t[4].options.text
      ) ? null : (
        /*descriptionId*/
        t[2]
      )
    },
    {
      "aria-labelledby": r = /*step*/
      t[4].options.title ? (
        /*labelId*/
        t[3]
      ) : null
    },
    /*dataStepId*/
    t[1],
    {
      role: "dialog"
    },
    {
      tabindex: "0"
    }
  ], p = {};
  for (let d = 0; d < f.length; d += 1)
    p = Go(p, f[d]);
  return {
    c() {
      e = te("div"), c && c.c(), n = ot(), Se(o.$$.fragment), zt(e, p), Ce(
        e,
        "shepherd-has-cancel-icon",
        /*hasCancelIcon*/
        t[5]
      ), Ce(
        e,
        "shepherd-has-title",
        /*hasTitle*/
        t[6]
      ), Ce(e, "shepherd-element", !0);
    },
    m(d, g) {
      Q(d, e, g), c && c.m(e, null), Ne(e, n), pe(o, e, null), t[13](e), i = !0, a || (l = lt(
        e,
        "keydown",
        /*handleKeyDown*/
        t[7]
      ), a = !0);
    },
    p(d, [g]) {
      /*step*/
      d[4].options.arrow && /*step*/
      d[4].options.attachTo && /*step*/
      d[4].options.attachTo.element && /*step*/
      d[4].options.attachTo.on ? c || (c = tn(), c.c(), c.m(e, n)) : c && (c.d(1), c = null);
      const b = {};
      g & /*descriptionId*/
      4 && (b.descriptionId = /*descriptionId*/
      d[2]), g & /*labelId*/
      8 && (b.labelId = /*labelId*/
      d[3]), g & /*step*/
      16 && (b.step = /*step*/
      d[4]), o.$set(b), zt(e, p = ls(f, [(!i || g & /*step, descriptionId*/
      20 && s !== (s = H(
        /*step*/
        d[4].options.text
      ) ? null : (
        /*descriptionId*/
        d[2]
      ))) && {
        "aria-describedby": s
      }, (!i || g & /*step, labelId*/
      24 && r !== (r = /*step*/
      d[4].options.title ? (
        /*labelId*/
        d[3]
      ) : null)) && {
        "aria-labelledby": r
      }, g & /*dataStepId*/
      2 && /*dataStepId*/
      d[1], {
        role: "dialog"
      }, {
        tabindex: "0"
      }])), Ce(
        e,
        "shepherd-has-cancel-icon",
        /*hasCancelIcon*/
        d[5]
      ), Ce(
        e,
        "shepherd-has-title",
        /*hasTitle*/
        d[6]
      ), Ce(e, "shepherd-element", !0);
    },
    i(d) {
      i || (M(o.$$.fragment, d), i = !0);
    },
    o(d) {
      L(o.$$.fragment, d), i = !1;
    },
    d(d) {
      d && Y(e), c && c.d(), ge(o), t[13](null), a = !1, l();
    }
  };
}
const $s = 9, Ls = 27, Ps = 37, Fs = 39;
function nn(t) {
  return t.split(" ").filter((e) => !!e.length);
}
function Ds(t, e, n) {
  let {
    classPrefix: o,
    element: s,
    descriptionId: r,
    firstFocusableElement: i,
    focusableElements: a,
    labelId: l,
    lastFocusableElement: c,
    step: f,
    dataStepId: p
  } = e, d, g, b;
  const S = () => s;
  os(() => {
    n(1, p = {
      [`data-${o}shepherd-step-id`]: f.id
    }), n(9, a = s.querySelectorAll('a[href], area[href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), button:not([disabled]), [tabindex="0"]')), n(8, i = a[0]), n(10, c = a[a.length - 1]);
  }), Mt(() => {
    b !== f.options.classes && k();
  });
  function k() {
    y(b), b = f.options.classes, x(b);
  }
  function y(m) {
    if (We(m)) {
      const A = nn(m);
      A.length && s.classList.remove(...A);
    }
  }
  function x(m) {
    if (We(m)) {
      const A = nn(m);
      A.length && s.classList.add(...A);
    }
  }
  const O = (m) => {
    const {
      tour: A
    } = f;
    switch (m.keyCode) {
      case $s:
        if (a.length === 0) {
          m.preventDefault();
          break;
        }
        m.shiftKey ? (document.activeElement === i || document.activeElement.classList.contains("shepherd-element")) && (m.preventDefault(), c.focus()) : document.activeElement === c && (m.preventDefault(), i.focus());
        break;
      case Ls:
        A.options.exitOnEsc && (m.preventDefault(), m.stopPropagation(), f.cancel());
        break;
      case Ps:
        A.options.keyboardNavigation && (m.preventDefault(), m.stopPropagation(), A.back());
        break;
      case Fs:
        A.options.keyboardNavigation && (m.preventDefault(), m.stopPropagation(), A.next());
        break;
    }
  };
  function _(m) {
    He[m ? "unshift" : "push"](() => {
      s = m, n(0, s);
    });
  }
  return t.$$set = (m) => {
    "classPrefix" in m && n(11, o = m.classPrefix), "element" in m && n(0, s = m.element), "descriptionId" in m && n(2, r = m.descriptionId), "firstFocusableElement" in m && n(8, i = m.firstFocusableElement), "focusableElements" in m && n(9, a = m.focusableElements), "labelId" in m && n(3, l = m.labelId), "lastFocusableElement" in m && n(10, c = m.lastFocusableElement), "step" in m && n(4, f = m.step), "dataStepId" in m && n(1, p = m.dataStepId);
  }, t.$$.update = () => {
    t.$$.dirty & /*step*/
    16 && (n(5, d = f.options && f.options.cancelIcon && f.options.cancelIcon.enabled), n(6, g = f.options && f.options.title));
  }, [s, p, r, l, f, d, g, O, i, a, c, o, S, _];
}
class Ns extends ie {
  constructor(e) {
    super(), re(this, e, Ds, Ms, se, {
      classPrefix: 11,
      element: 0,
      descriptionId: 2,
      firstFocusableElement: 8,
      focusableElements: 9,
      labelId: 3,
      lastFocusableElement: 10,
      step: 4,
      dataStepId: 1,
      getElement: 12
    });
  }
  get getElement() {
    return this.$$.ctx[12];
  }
}
class _t extends wt {
  constructor(e, n = {}) {
    return super(), this._resolvedAttachTo = void 0, this.classPrefix = void 0, this.el = void 0, this.target = void 0, this.tour = void 0, this.tour = e, this.classPrefix = this.tour.options ? dn(this.tour.options.classPrefix) : "", this.styles = e.styles, this._resolvedAttachTo = null, St(this), this._setOptions(n), this;
  }
  /**
   * Cancel the tour
   * Triggers the `cancel` event
   */
  cancel() {
    this.tour.cancel(), this.trigger("cancel");
  }
  /**
   * Complete the tour
   * Triggers the `complete` event
   */
  complete() {
    this.tour.complete(), this.trigger("complete");
  }
  /**
   * Remove the step, delete the step's element, and destroy the FloatingUI instance for the step.
   * Triggers `destroy` event
   */
  destroy() {
    Wo(this), Ke(this.el) && (this.el.remove(), this.el = null), this._updateStepTargetOnHide(), this.trigger("destroy");
  }
  /**
   * Returns the tour for the step
   * @return The tour instance
   */
  getTour() {
    return this.tour;
  }
  /**
   * Hide the step
   */
  hide() {
    var e;
    (e = this.tour.modal) == null || e.hide(), this.trigger("before-hide"), this.el && (this.el.hidden = !0), this._updateStepTargetOnHide(), this.trigger("hide");
  }
  /**
   * Resolves attachTo options.
   * @returns {{}|{element, on}}
   */
  _resolveAttachToOptions() {
    return this._resolvedAttachTo = so(this), this._resolvedAttachTo;
  }
  /**
   * A selector for resolved attachTo options.
   * @returns {{}|{element, on}}
   * @private
   */
  _getResolvedAttachToOptions() {
    return this._resolvedAttachTo === null ? this._resolveAttachToOptions() : this._resolvedAttachTo;
  }
  /**
   * Check if the step is open and visible
   * @return True if the step is open and visible
   */
  isOpen() {
    return !!(this.el && !this.el.hidden);
  }
  /**
   * Wraps `_show` and ensures `beforeShowPromise` resolves before calling show
   */
  show() {
    return ue(this.options.beforeShowPromise) ? Promise.resolve(this.options.beforeShowPromise()).then(() => this._show()) : Promise.resolve(this._show());
  }
  /**
   * Updates the options of the step.
   *
   * @param {StepOptions} options The options for the step
   */
  updateStepOptions(e) {
    Object.assign(this.options, e), this.shepherdElementComponent && this.shepherdElementComponent.$set({
      step: this
    });
  }
  /**
   * Returns the element for the step
   * @return {HTMLElement|null|undefined} The element instance. undefined if it has never been shown, null if it has been destroyed
   */
  getElement() {
    return this.el;
  }
  /**
   * Returns the target for the step
   * @return {HTMLElement|null|undefined} The element instance. undefined if it has never been shown, null if query string has not been found
   */
  getTarget() {
    return this.target;
  }
  /**
   * Creates Shepherd element for step based on options
   *
   * @return {HTMLElement} The DOM element for the step tooltip
   * @private
   */
  _createTooltipContent() {
    const e = `${this.id}-description`, n = `${this.id}-label`;
    return this.shepherdElementComponent = new Ns({
      target: this.tour.options.stepsContainer || document.body,
      props: {
        classPrefix: this.classPrefix,
        descriptionId: e,
        labelId: n,
        step: this,
        // @ts-expect-error TODO: investigate where styles comes from
        styles: this.styles
      }
    }), this.shepherdElementComponent.getElement();
  }
  /**
   * If a custom scrollToHandler is defined, call that, otherwise do the generic
   * scrollIntoView call.
   *
   * @param {boolean | ScrollIntoViewOptions} scrollToOptions - If true, uses the default `scrollIntoView`,
   * if an object, passes that object as the params to `scrollIntoView` i.e. `{ behavior: 'smooth', block: 'center' }`
   * @private
   */
  _scrollTo(e) {
    const {
      element: n
    } = this._getResolvedAttachToOptions();
    ue(this.options.scrollToHandler) ? this.options.scrollToHandler(n) : Hn(n) && typeof n.scrollIntoView == "function" && n.scrollIntoView(e);
  }
  /**
   * _getClassOptions gets all possible classes for the step
   * @param {StepOptions} stepOptions The step specific options
   * @returns {string} unique string from array of classes
   */
  _getClassOptions(e) {
    const n = this.tour && this.tour.options && this.tour.options.defaultStepOptions, o = e.classes ? e.classes : "", s = n && n.classes ? n.classes : "", r = [...o.split(" "), ...s.split(" ")], i = new Set(r);
    return Array.from(i).join(" ").trim();
  }
  /**
   * Sets the options for the step, maps `when` to events, sets up buttons
   * @param options - The options for the step
   */
  _setOptions(e = {}) {
    let n = this.tour && this.tour.options && this.tour.options.defaultStepOptions;
    n = kt({}, n || {}), this.options = Object.assign({
      arrow: !0
    }, n, e, zo(n, e));
    const {
      when: o
    } = this.options;
    this.options.classes = this._getClassOptions(e), this.destroy(), this.id = this.options.id || `step-${hn()}`, o && Object.keys(o).forEach((s) => {
      this.on(s, o[s], this);
    });
  }
  /**
   * Create the element and set up the FloatingUI instance
   * @private
   */
  _setupElements() {
    H(this.el) || this.destroy(), this.el = this._createTooltipContent(), this.options.advanceOn && to(this), Uo(this);
  }
  /**
   * Triggers `before-show`, generates the tooltip DOM content,
   * sets up a FloatingUI instance for the tooltip, then triggers `show`.
   * @private
   */
  _show() {
    var e;
    this.trigger("before-show"), this._resolveAttachToOptions(), this._setupElements(), this.tour.modal || this.tour.setupModal(), (e = this.tour.modal) == null || e.setupForStep(this), this._styleTargetElementForStep(this), this.el && (this.el.hidden = !1), this.options.scrollTo && setTimeout(() => {
      this._scrollTo(this.options.scrollTo);
    }), this.el && (this.el.hidden = !1);
    const n = this.shepherdElementComponent.getElement(), o = this.target || document.body;
    o.classList.add(`${this.classPrefix}shepherd-enabled`), o.classList.add(`${this.classPrefix}shepherd-target`), n.classList.add("shepherd-enabled"), this.trigger("show");
  }
  /**
   * Modulates the styles of the passed step's target element, based on the step's options and
   * the tour's `modal` option, to visually emphasize the element
   *
   * @param {Step} step The step object that attaches to the element
   * @private
   */
  _styleTargetElementForStep(e) {
    const n = e.target;
    n && (e.options.highlightClass && n.classList.add(e.options.highlightClass), n.classList.remove("shepherd-target-click-disabled"), e.options.canClickTarget === !1 && n.classList.add("shepherd-target-click-disabled"));
  }
  /**
   * When a step is hidden, remove the highlightClass and 'shepherd-enabled'
   * and 'shepherd-target' classes
   * @private
   */
  _updateStepTargetOnHide() {
    const e = this.target || document.body;
    this.options.highlightClass && e.classList.remove(this.options.highlightClass), e.classList.remove("shepherd-target-click-disabled", `${this.classPrefix}shepherd-enabled`, `${this.classPrefix}shepherd-target`);
  }
}
function Hs(t) {
  if (t) {
    const {
      steps: e
    } = t;
    e.forEach((n) => {
      n.options && n.options.canClickTarget === !1 && n.options.attachTo && Ke(n.target) && n.target.classList.remove("shepherd-target-click-disabled");
    });
  }
}
function Bs({
  width: t,
  height: e,
  x: n = 0,
  y: o = 0,
  r: s = 0
}) {
  const {
    innerWidth: r,
    innerHeight: i
  } = window, {
    topLeft: a = 0,
    topRight: l = 0,
    bottomRight: c = 0,
    bottomLeft: f = 0
  } = typeof s == "number" ? {
    topLeft: s,
    topRight: s,
    bottomRight: s,
    bottomLeft: s
  } : s;
  return `M${r},${i}H0V0H${r}V${i}ZM${n + a},${o}a${a},${a},0,0,0-${a},${a}V${e + o - f}a${f},${f},0,0,0,${f},${f}H${t + n - c}a${c},${c},0,0,0,${c}-${c}V${o + l}a${l},${l},0,0,0-${l}-${l}Z`;
}
function js(t) {
  let e, n, o, s, r;
  return {
    c() {
      e = Ut("svg"), n = Ut("path"), $(
        n,
        "d",
        /*pathDefinition*/
        t[2]
      ), $(e, "class", o = `${/*modalIsVisible*/
      t[1] ? "shepherd-modal-is-visible" : ""} shepherd-modal-overlay-container`);
    },
    m(i, a) {
      Q(i, e, a), Ne(e, n), t[11](e), s || (r = lt(
        e,
        "touchmove",
        /*_preventModalOverlayTouch*/
        t[3]
      ), s = !0);
    },
    p(i, [a]) {
      a & /*pathDefinition*/
      4 && $(
        n,
        "d",
        /*pathDefinition*/
        i[2]
      ), a & /*modalIsVisible*/
      2 && o !== (o = `${/*modalIsVisible*/
      i[1] ? "shepherd-modal-is-visible" : ""} shepherd-modal-overlay-container`) && $(e, "class", o);
    },
    i: z,
    o: z,
    d(i) {
      i && Y(e), t[11](null), s = !1, r();
    }
  };
}
function An(t) {
  if (!t)
    return null;
  const n = t instanceof HTMLElement && window.getComputedStyle(t).overflowY;
  return n !== "hidden" && n !== "visible" && t.scrollHeight >= t.clientHeight ? t : An(t.parentElement);
}
function Vs(t) {
  let e = {
    top: 0,
    left: 0
  };
  if (!t)
    return e;
  let n = t.ownerDocument.defaultView;
  for (; n !== window.top; ) {
    var o;
    const i = (o = n) == null ? void 0 : o.frameElement;
    if (i) {
      var s, r;
      const a = i.getBoundingClientRect();
      e.top += a.top + ((s = a.scrollTop) != null ? s : 0), e.left += a.left + ((r = a.scrollLeft) != null ? r : 0);
    }
    n = n.parent;
  }
  return e;
}
function Us(t, e) {
  const n = t.getBoundingClientRect();
  let o = n.y || n.top, s = n.bottom || o + n.height;
  if (e) {
    const i = e.getBoundingClientRect(), a = i.y || i.top, l = i.bottom || a + i.height;
    o = Math.max(o, a), s = Math.min(s, l);
  }
  const r = Math.max(s - o, 0);
  return {
    y: o,
    height: r
  };
}
function zs(t, e, n) {
  let {
    element: o,
    openingProperties: s
  } = e, r = !1, i, a;
  c();
  const l = () => o;
  function c() {
    n(4, s = {
      width: 0,
      height: 0,
      x: 0,
      y: 0,
      r: 0
    });
  }
  function f() {
    n(1, r = !1), y();
  }
  function p(_ = 0, m = 0, A = 0, F = 0, K, I) {
    if (I) {
      const {
        y: C,
        height: D
      } = Us(I, K), {
        x: E,
        width: W,
        left: q
      } = I.getBoundingClientRect();
      n(4, s = {
        width: W + _ * 2,
        height: D + _ * 2,
        x: (E || q) + A - _,
        y: C + F - _,
        r: m
      });
    } else
      c();
  }
  function d(_) {
    y(), _.tour.options.useModalOverlay ? (x(_), g()) : f();
  }
  function g() {
    n(1, r = !0);
  }
  const b = (_) => {
    _.preventDefault();
  }, S = (_) => {
    _.stopPropagation();
  };
  function k() {
    window.addEventListener("touchmove", b, {
      passive: !1
    });
  }
  function y() {
    i && (cancelAnimationFrame(i), i = void 0), window.removeEventListener("touchmove", b, {
      passive: !1
    });
  }
  function x(_) {
    const {
      modalOverlayOpeningPadding: m,
      modalOverlayOpeningRadius: A,
      modalOverlayOpeningXOffset: F = 0,
      modalOverlayOpeningYOffset: K = 0
    } = _.options, I = Vs(_.target), C = An(_.target), D = () => {
      i = void 0, p(m, A, F + I.left, K + I.top, C, _.target), i = requestAnimationFrame(D);
    };
    D(), k();
  }
  function O(_) {
    He[_ ? "unshift" : "push"](() => {
      o = _, n(0, o);
    });
  }
  return t.$$set = (_) => {
    "element" in _ && n(0, o = _.element), "openingProperties" in _ && n(4, s = _.openingProperties);
  }, t.$$.update = () => {
    t.$$.dirty & /*openingProperties*/
    16 && n(2, a = Bs(s));
  }, [o, r, a, S, s, l, c, f, p, d, g, O];
}
class Ws extends ie {
  constructor(e) {
    super(), re(this, e, zs, js, se, {
      element: 0,
      openingProperties: 4,
      getElement: 5,
      closeModalOpening: 6,
      hide: 7,
      positionModal: 8,
      setupForStep: 9,
      show: 10
    });
  }
  get getElement() {
    return this.$$.ctx[5];
  }
  get closeModalOpening() {
    return this.$$.ctx[6];
  }
  get hide() {
    return this.$$.ctx[7];
  }
  get positionModal() {
    return this.$$.ctx[8];
  }
  get setupForStep() {
    return this.$$.ctx[9];
  }
  get show() {
    return this.$$.ctx[10];
  }
}
class qs extends wt {
  constructor() {
    super(), this.activeTour = void 0, St(this);
  }
}
class Ys extends wt {
  constructor(e = {}) {
    super(), this.trackedEvents = ["active", "cancel", "complete", "show"], this.classPrefix = void 0, this.currentStep = void 0, this.focusedElBeforeOpen = void 0, this.id = void 0, this.modal = void 0, this.options = void 0, this.steps = void 0, St(this);
    const n = {
      exitOnEsc: !0,
      keyboardNavigation: !0
    };
    return this.options = Object.assign({}, n, e), this.classPrefix = dn(this.options.classPrefix), this.steps = [], this.addSteps(this.options.steps), ["active", "cancel", "complete", "inactive", "show", "start"].map((s) => {
      ((r) => {
        this.on(r, (i) => {
          i = i || {}, i.tour = this, be.trigger(r, i);
        });
      })(s);
    }), this._setTourID(e.id), this;
  }
  /**
   * Adds a new step to the tour
   * @param {StepOptions} options - An object containing step options or a Step instance
   * @param {number | undefined} index - The optional index to insert the step at. If undefined, the step
   * is added to the end of the array.
   * @return The newly added step
   */
  addStep(e, n) {
    let o = e;
    return o instanceof _t ? o.tour = this : o = new _t(this, o), H(n) ? this.steps.push(o) : this.steps.splice(n, 0, o), o;
  }
  /**
   * Add multiple steps to the tour
   * @param {Array<StepOptions> | Array<Step> | undefined} steps - The steps to add to the tour
   */
  addSteps(e) {
    return Array.isArray(e) && e.forEach((n) => {
      this.addStep(n);
    }), this;
  }
  /**
   * Go to the previous step in the tour
   */
  back() {
    const e = this.steps.indexOf(this.currentStep);
    this.show(e - 1, !1);
  }
  /**
   * Calls _done() triggering the 'cancel' event
   * If `confirmCancel` is true, will show a window.confirm before cancelling
   * If `confirmCancel` is a function, will call it and wait for the return value,
   * and only cancel when the value returned is true
   */
  async cancel() {
    if (this.options.confirmCancel) {
      const e = this.options.confirmCancelMessage || "Are you sure you want to stop the tour?";
      let n;
      ue(this.options.confirmCancel) ? n = await this.options.confirmCancel() : n = window.confirm(e), n && this._done("cancel");
    } else
      this._done("cancel");
  }
  /**
   * Calls _done() triggering the `complete` event
   */
  complete() {
    this._done("complete");
  }
  /**
   * Gets the step from a given id
   * @param {number | string} id - The id of the step to retrieve
   * @return The step corresponding to the `id`
   */
  getById(e) {
    return this.steps.find((n) => n.id === e);
  }
  /**
   * Gets the current step
   */
  getCurrentStep() {
    return this.currentStep;
  }
  /**
   * Hide the current step
   */
  hide() {
    const e = this.getCurrentStep();
    if (e)
      return e.hide();
  }
  /**
   * Check if the tour is active
   */
  isActive() {
    return be.activeTour === this;
  }
  /**
   * Go to the next step in the tour
   * If we are at the end, call `complete`
   */
  next() {
    const e = this.steps.indexOf(this.currentStep);
    e === this.steps.length - 1 ? this.complete() : this.show(e + 1, !0);
  }
  /**
   * Removes the step from the tour
   * @param {string} name - The id for the step to remove
   */
  removeStep(e) {
    const n = this.getCurrentStep();
    this.steps.some((o, s) => {
      if (o.id === e)
        return o.isOpen() && o.hide(), o.destroy(), this.steps.splice(s, 1), !0;
    }), n && n.id === e && (this.currentStep = void 0, this.steps.length ? this.show(0) : this.cancel());
  }
  /**
   * Show a specific step in the tour
   * @param {number | string} key - The key to look up the step by
   * @param {boolean} forward - True if we are going forward, false if backward
   */
  show(e = 0, n = !0) {
    const o = We(e) ? this.getById(e) : this.steps[e];
    o && (this._updateStateBeforeShow(), ue(o.options.showOn) && !o.options.showOn() ? this._skipStep(o, n) : (this.trigger("show", {
      step: o,
      previous: this.currentStep
    }), this.currentStep = o, o.show()));
  }
  /**
   * Start the tour
   */
  async start() {
    this.trigger("start"), this.focusedElBeforeOpen = document.activeElement, this.currentStep = null, this.setupModal(), this._setupActiveTour(), this.next();
  }
  /**
   * Called whenever the tour is cancelled or completed, basically anytime we exit the tour
   * @param {string} event - The event name to trigger
   * @private
   */
  _done(e) {
    const n = this.steps.indexOf(this.currentStep);
    if (Array.isArray(this.steps) && this.steps.forEach((o) => o.destroy()), Hs(this), this.trigger(e, {
      index: n
    }), be.activeTour = null, this.trigger("inactive", {
      tour: this
    }), this.modal && this.modal.hide(), (e === "cancel" || e === "complete") && this.modal) {
      const o = document.querySelector(".shepherd-modal-overlay-container");
      o && (o.remove(), this.modal = null);
    }
    Ke(this.focusedElBeforeOpen) && this.focusedElBeforeOpen.focus();
  }
  /**
   * Make this tour "active"
   */
  _setupActiveTour() {
    this.trigger("active", {
      tour: this
    }), be.activeTour = this;
  }
  /**
   * setupModal create the modal container and instance
   */
  setupModal() {
    this.modal = new Ws({
      target: this.options.modalContainer || document.body,
      props: {
        // @ts-expect-error TODO: investigate where styles comes from
        styles: this.styles
      }
    });
  }
  /**
   * Called when `showOn` evaluates to false, to skip the step or complete the tour if it's the last step
   * @param {Step} step - The step to skip
   * @param {boolean} forward - True if we are going forward, false if backward
   * @private
   */
  _skipStep(e, n) {
    const o = this.steps.indexOf(e);
    if (o === this.steps.length - 1)
      this.complete();
    else {
      const s = n ? o + 1 : o - 1;
      this.show(s, n);
    }
  }
  /**
   * Before showing, hide the current step and if the tour is not
   * already active, call `this._setupActiveTour`.
   * @private
   */
  _updateStateBeforeShow() {
    this.currentStep && this.currentStep.hide(), this.isActive() || this._setupActiveTour();
  }
  /**
   * Sets this.id to a provided tourName and id or `${tourName}--${uuid}`
   * @param {string} optionsId - True if we are going forward, false if backward
   * @private
   */
  _setTourID(e) {
    const n = this.options.tourName || "tour", o = e || hn();
    this.id = `${n}--${o}`;
  }
}
const be = new qs(), Cn = typeof window > "u";
be.Step = Cn ? no : _t;
be.Tour = Cn ? oo : Ys;
const Ue = P(!1), ze = P(!1);
let Ze = null;
function ce(t, e) {
  const n = Math.round(t / e * 100);
  return `
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
      <span style="font-size:12px;color:#6b7280;">${u("Step")} ${t} ${u("of")} ${e}</span>
      <div style="flex:1;height:4px;background:#e5e7eb;border-radius:2px;overflow:hidden;">
        <div style="width:${n}%;height:100%;background:#f59e0b;border-radius:2px;transition:width 0.3s;"></div>
      </div>
    </div>
  `;
}
function Ks() {
  return [
    // Step 1 — Welcome (modal)
    {
      id: "welcome",
      text: `
        <div style="text-align:center;padding:8px 0;">
          <h2 style="font-size:20px;font-weight:600;margin-bottom:8px;">${u("Welcome to Home")}</h2>
          <p style="color:#6b7280;">${u("Let's set up your first property in a few steps.")}<br>${u("You can skip this at any time and come back later.")}</p>
        </div>
      `,
      buttons: [
        {
          text: u("Skip tour"),
          action: function() {
            st(), this.complete();
          },
          classes: "shepherd-button-secondary"
        },
        {
          text: u("Let's go") + " →",
          action: function() {
            this.next();
          },
          classes: "shepherd-button-primary"
        }
      ],
      modalOverlayOpeningPadding: 0
    },
    // Step 2 — Add property
    {
      id: "add-property",
      text: ce(1, 6) + `
        <h3 style="font-size:16px;font-weight:600;margin-bottom:4px;">${u("Start here")}</h3>
        <p style="color:#6b7280;font-size:14px;">${u("Add your property — address, type, and when you moved in.")}</p>
      `,
      attachTo: { element: '[data-tour="add-property"]', on: "bottom" },
      buttons: [
        { text: u("Skip"), action: function() {
          this.next();
        }, classes: "shepherd-button-secondary" },
        { text: "→ " + u("Next"), action: function() {
          this.next();
        }, classes: "shepherd-button-primary" }
      ]
    },
    // Step 3 — Add rooms
    {
      id: "add-rooms",
      text: ce(2, 6) + `
        <h3 style="font-size:16px;font-weight:600;margin-bottom:4px;">${u("Add your rooms")}</h3>
        <p style="color:#6b7280;font-size:14px;">${u("Define the rooms in your property — kitchen, bathroom, bedroom, garage. Rooms help organise appliances and tasks.")}</p>
      `,
      attachTo: { element: '[data-tour="add-room"]', on: "bottom" },
      buttons: [
        { text: "← " + u("Back"), action: function() {
          this.back();
        }, classes: "shepherd-button-secondary" },
        { text: u("Skip"), action: function() {
          this.next();
        }, classes: "shepherd-button-secondary" },
        { text: "→ " + u("Next"), action: function() {
          this.next();
        }, classes: "shepherd-button-primary" }
      ]
    },
    // Step 4 — Register item
    {
      id: "add-item",
      text: ce(3, 6) + `
        <h3 style="font-size:16px;font-weight:600;margin-bottom:4px;">${u("Register your items")}</h3>
        <p style="color:#6b7280;font-size:14px;">${u("Add the appliances and possessions in your home — boiler, washing machine, fridge, furniture.")}<br>${u("Tap the camera icon to scan the barcode or rating plate and auto-fill the details.")}</p>
      `,
      attachTo: { element: '[data-tour="add-item"]', on: "bottom" },
      buttons: [
        { text: "← " + u("Back"), action: function() {
          this.back();
        }, classes: "shepherd-button-secondary" },
        { text: u("Skip"), action: function() {
          this.next();
        }, classes: "shepherd-button-secondary" },
        { text: "→ " + u("Next"), action: function() {
          this.next();
        }, classes: "shepherd-button-primary" }
      ]
    },
    // Step 5 — Set maintenance reminder
    {
      id: "create-task",
      text: ce(4, 6) + `
        <h3 style="font-size:16px;font-weight:600;margin-bottom:4px;">${u("Set your first reminder")}</h3>
        <p style="color:#6b7280;font-size:14px;">${u("Create your first task — boiler service, gutter cleaning, smoke alarm check. Manage tasks in Orga.")}</p>
      `,
      attachTo: { element: '[data-tour="create-task"]', on: "bottom" },
      buttons: [
        { text: "← " + u("Back"), action: function() {
          this.back();
        }, classes: "shepherd-button-secondary" },
        { text: u("Skip"), action: function() {
          this.next();
        }, classes: "shepherd-button-secondary" },
        { text: "→ " + u("Next"), action: function() {
          this.next();
        }, classes: "shepherd-button-primary" }
      ]
    },
    // Step 6 — Tour the dashboard
    {
      id: "dashboard",
      text: ce(5, 6) + `
        <h3 style="font-size:16px;font-weight:600;margin-bottom:4px;">${u("Your property dashboard")}</h3>
        <p style="color:#6b7280;font-size:14px;">${u("This is your at-a-glance view — item count, upcoming tasks, health score, and cost forecast.")}</p>
      `,
      attachTo: { element: '[data-tour="dashboard"]', on: "bottom" },
      buttons: [
        { text: "← " + u("Back"), action: function() {
          this.back();
        }, classes: "shepherd-button-secondary" },
        { text: "→ " + u("Next"), action: function() {
          this.next();
        }, classes: "shepherd-button-primary" }
      ]
    },
    // Step 7 — Done (modal)
    {
      id: "done",
      text: `
        <div style="text-align:center;padding:8px 0;">
          ${ce(6, 6)}
          <h2 style="font-size:20px;font-weight:600;margin-bottom:8px;">${u("You're all set")} &#10003;</h2>
          <p style="color:#6b7280;">${u("Home will remind you when warranties are expiring and keep everything about your property in one place.")}</p>
          <p style="color:#9ca3af;font-size:13px;margin-top:8px;">${u("You can restart this tour anytime from Settings.")}</p>
        </div>
      `,
      buttons: [
        {
          text: u("Go to dashboard") + " →",
          action: function() {
            st(), this.complete();
          },
          classes: "shepherd-button-primary"
        }
      ]
    }
  ];
}
function Xs(t) {
  return [
    // Step 1 — Welcome
    {
      id: "welcome",
      text: `
        <div style="text-align:center;padding:8px 0;">
          <h2 style="font-size:20px;font-weight:600;margin-bottom:8px;">${u("Welcome to Home")}</h2>
          <p style="color:#6b7280;">${t} ${u("has added you to their household. Here's what you can see.")}</p>
        </div>
      `,
      buttons: [
        { text: u("Skip"), action: function() {
          st(), this.complete();
        }, classes: "shepherd-button-secondary" },
        { text: u("Show me") + " →", action: function() {
          this.next();
        }, classes: "shepherd-button-primary" }
      ]
    },
    // Step 2 — What you can see
    {
      id: "property-card",
      text: `
        ${ce(1, 2)}
        <h3 style="font-size:16px;font-weight:600;margin-bottom:4px;">${u("Your household property")}</h3>
        <p style="color:#6b7280;font-size:14px;">${u("You can view the property details, items, task history, and emergency contacts.")}</p>
      `,
      attachTo: { element: '[data-tour="dashboard"]', on: "bottom" },
      buttons: [
        { text: "← " + u("Back"), action: function() {
          this.back();
        }, classes: "shepherd-button-secondary" },
        { text: "→ " + u("Next"), action: function() {
          this.next();
        }, classes: "shepherd-button-primary" }
      ]
    },
    // Step 3 — Done
    {
      id: "done",
      text: `
        <div style="text-align:center;padding:8px 0;">
          ${ce(2, 2)}
          <h2 style="font-size:20px;font-weight:600;margin-bottom:8px;">${u("That's it!")}</h2>
          <p style="color:#6b7280;">${u("If you have any questions, ask the household owner.")}</p>
        </div>
      `,
      buttons: [
        {
          text: u("Got it"),
          action: function() {
            st(), this.complete();
          },
          classes: "shepherd-button-primary"
        }
      ]
    }
  ];
}
let Ie = null;
async function st() {
  if (Ie)
    try {
      await V({
        url: "/api/method/home.api.onboarding.complete_onboarding",
        params: { household: Ie }
      });
    } catch {
    }
}
function on(t) {
  const e = new be.Tour({
    useModalOverlay: !0,
    defaultStepOptions: {
      cancelIcon: { enabled: !1 },
      scrollTo: { behavior: "smooth", block: "center" },
      modalOverlayOpeningPadding: 8,
      modalOverlayOpeningRadius: 8,
      // When anchor not found, show as floating modal
      floatingUIOptions: {
        middleware: []
      }
    },
    keyboardNavigation: !0
  });
  t.forEach((o) => e.addStep(o));
  function n(o) {
    e.isActive() && (o.key === "ArrowRight" || o.key === "Enter" ? (o.preventDefault(), e.next()) : (o.key === "ArrowLeft" || o.key === "Backspace") && (o.preventDefault(), e.back()));
  }
  return e.on("start", () => {
    document.addEventListener("keydown", n);
  }), e.on("cancel", () => {
    Ue.value = !1, ze.value = !0, document.removeEventListener("keydown", n);
  }), e.on("complete", () => {
    Ue.value = !1, ze.value = !0, document.removeEventListener("keydown", n);
  }), e;
}
function Js() {
  async function t() {
    if (!(ze.value || Ue.value))
      try {
        const o = (await V({
          url: "/api/method/home.api.permission.get_my_role"
        }))?.household;
        if (!o) return;
        Ie = o;
        const r = await V({
          url: "/api/method/home.api.onboarding.get_onboarding_status",
          params: { household: o }
        });
        if (!r || r.tour_completed) return;
        const i = r.variant;
        if (i === "owner_setup" && !r.household_has_properties)
          Ze = on(Ks());
        else if (i === "invited_member" || i === "owner_setup" && r.household_has_properties) {
          const a = r.owner_display_name || "";
          Ze = on(Xs(a));
        } else
          return;
        setTimeout(() => {
          Ze && !ze.value && (Ue.value = !0, Ze.start());
        }, 800);
      } catch {
      }
  }
  async function e() {
    if (!Ie)
      try {
        Ie = (await V({
          url: "/api/method/home.api.permission.get_my_role"
        }))?.household || null;
      } catch {
        return;
      }
    if (Ie)
      try {
        await V({
          url: "/api/method/home.api.onboarding.reset_tour",
          params: {}
        }), ze.value = !1, await t();
      } catch {
      }
  }
  return { tourActive: Ue, initTour: t, restartTour: e };
}
const Gs = {
  key: 0,
  class: "text-gray-500 dark:text-gray-400 text-sm"
}, Zs = {
  key: 1,
  class: "text-red-600 dark:text-red-400 text-sm"
}, Qs = {
  key: 0,
  class: "mb-8 p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
}, er = { class: "text-h3 text-gray-800 dark:text-gray-200 mb-4" }, tr = { class: "mb-4" }, nr = { class: "text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2" }, or = { class: "grid grid-cols-1 sm:grid-cols-2 gap-3" }, sr = { class: "text-caption text-gray-500 dark:text-gray-400 block mb-1" }, rr = { class: "flex items-center gap-2" }, ir = { class: "text-sm text-gray-500 dark:text-gray-400" }, ar = { class: "text-caption text-gray-500 dark:text-gray-400 block mb-1" }, lr = { class: "flex items-center gap-2" }, cr = { class: "text-sm text-gray-500 dark:text-gray-400" }, ur = { class: "mb-4" }, dr = { class: "text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2" }, fr = { class: "grid grid-cols-1 sm:grid-cols-3 gap-3" }, hr = { class: "text-caption text-gray-500 dark:text-gray-400 block mb-1" }, pr = { class: "flex items-center gap-2" }, gr = { class: "text-sm text-gray-500 dark:text-gray-400" }, mr = { class: "text-caption text-gray-500 dark:text-gray-400 block mb-1" }, yr = { class: "flex items-center gap-2" }, br = { class: "text-sm text-gray-500 dark:text-gray-400" }, xr = { class: "text-caption text-gray-500 dark:text-gray-400 block mb-1" }, _r = { class: "flex items-center gap-2" }, vr = { class: "text-sm text-gray-500 dark:text-gray-400" }, wr = { class: "grid grid-cols-1 sm:grid-cols-2 gap-3" }, kr = { class: "text-caption text-gray-500 dark:text-gray-400 block mb-1" }, Sr = { class: "flex items-center gap-2" }, Or = { class: "text-sm text-gray-500 dark:text-gray-400" }, Er = {
  key: 1,
  class: "mb-8 p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
}, Ar = { class: "text-h3 text-gray-800 dark:text-gray-200 mb-4" }, Cr = { class: "text-sm text-gray-500 dark:text-gray-400 mb-3" }, Tr = { class: "overflow-x-auto" }, Rr = { class: "w-full text-sm" }, Ir = { class: "text-left text-caption text-gray-500 dark:text-gray-400 border-b border-gray-200 dark:border-gray-700" }, Mr = { class: "py-2 pr-4" }, $r = { class: "py-2 pr-4 w-28" }, Lr = { class: "py-2 w-36" }, Pr = { class: "py-2 pr-4 text-gray-700 dark:text-gray-300" }, Fr = { class: "py-2 pr-4" }, Dr = ["onUpdate:modelValue"], Nr = { class: "py-2" }, Hr = { class: "relative" }, Br = ["onUpdate:modelValue"], jr = {
  key: 2,
  class: "mb-8 p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
}, Vr = { class: "text-h3 text-gray-800 dark:text-gray-200 mb-4" }, Ur = { class: "grid grid-cols-1 sm:grid-cols-2 gap-4" }, zr = { class: "text-caption text-gray-500 dark:text-gray-400 block mb-1" }, Wr = { class: "text-caption text-gray-500 dark:text-gray-400 block mb-1" }, qr = ["value"], Yr = { class: "text-xs text-gray-400 dark:text-gray-500 mt-1" }, Kr = {
  key: 3,
  class: "mb-8 p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
}, Xr = { class: "text-h3 text-gray-800 dark:text-gray-200 mb-2" }, Jr = { class: "text-sm text-gray-500 dark:text-gray-400 mb-3" }, Gr = ["disabled"], Zr = { class: "flex items-center gap-3" }, Qr = ["disabled"], ei = {
  key: 0,
  class: "text-sm text-green-600 dark:text-green-400"
}, ti = {
  key: 1,
  class: "text-sm text-red-600 dark:text-red-400"
}, ni = /* @__PURE__ */ vt({
  __name: "HomeSettingsPanel",
  props: {
    household: {},
    section: {}
  },
  setup(t) {
    const e = t, n = ne(() => !e.section || e.section === "alerts"), o = ne(() => !e.section || e.section === "lifespans"), s = ne(() => !e.section || e.section === "preferences"), r = P(null), i = P(!0), a = P(""), l = P(!1), c = P(!1), { restartTour: f } = Js(), p = P(!1), d = [
      { value: "Owner and Adult", label: u("Owner and Adult") },
      { value: "Owner only", label: u("Owner only") }
    ];
    async function g() {
      i.value = !0, a.value = "";
      try {
        const k = await V({
          url: "/api/method/home.api.settings.get_settings"
        });
        r.value = k;
      } catch (k) {
        a.value = k.message || u("Failed to load settings");
      } finally {
        i.value = !1;
      }
    }
    async function b() {
      if (r.value) {
        l.value = !0, c.value = !1, a.value = "";
        try {
          const k = await V({
            url: "/api/method/home.api.settings.save_settings",
            params: {
              data: JSON.stringify({
                name: r.value.name,
                warranty_alert_days_first: r.value.warranty_alert_days_first,
                warranty_alert_days_second: r.value.warranty_alert_days_second,
                legal_warranty_months: r.value.legal_warranty_months,
                burden_of_proof_months: r.value.burden_of_proof_months,
                burden_of_proof_alert_days: r.value.burden_of_proof_alert_days,
                refund_alert_days: r.value.refund_alert_days,
                tenancy_expiry_alert_days: r.value.tenancy_expiry_alert_days,
                default_currency: r.value.default_currency,
                financial_visibility: r.value.financial_visibility,
                category_lifespans: r.value.category_lifespans
              })
            }
          });
          r.value = k, c.value = !0, setTimeout(() => {
            c.value = !1;
          }, 3e3);
        } catch (k) {
          a.value = k.message || u("Failed to save settings");
        } finally {
          l.value = !1;
        }
      }
    }
    async function S() {
      p.value = !0, await f(), p.value = !1;
    }
    return sn(g), (k, y) => i.value ? (T(), R("div", Gs, v(w(u)("Loading settings…")), 1)) : a.value && !r.value ? (T(), R("div", Zs, v(a.value), 1)) : r.value ? (T(), R(me, { key: 2 }, [
      n.value ? (T(), R("section", Qs, [
        h("h2", er, v(w(u)("Alerts")), 1),
        h("div", tr, [
          h("h3", nr, v(w(u)("Warranty expiry alerts")), 1),
          h("div", or, [
            h("div", null, [
              h("label", sr, v(w(u)("First alert")), 1),
              h("div", rr, [
                j(h("input", {
                  "onUpdate:modelValue": y[0] || (y[0] = (x) => r.value.warranty_alert_days_first = x),
                  type: "number",
                  min: "1",
                  max: "365",
                  class: "w-20 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                }, null, 512), [
                  [
                    J,
                    r.value.warranty_alert_days_first,
                    void 0,
                    { number: !0 }
                  ]
                ]),
                h("span", ir, v(w(u)("days before")), 1)
              ])
            ]),
            h("div", null, [
              h("label", ar, v(w(u)("Second alert")), 1),
              h("div", lr, [
                j(h("input", {
                  "onUpdate:modelValue": y[1] || (y[1] = (x) => r.value.warranty_alert_days_second = x),
                  type: "number",
                  min: "1",
                  max: "365",
                  class: "w-20 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                }, null, 512), [
                  [
                    J,
                    r.value.warranty_alert_days_second,
                    void 0,
                    { number: !0 }
                  ]
                ]),
                h("span", cr, v(w(u)("days before")), 1)
              ])
            ])
          ])
        ]),
        h("div", ur, [
          h("h3", dr, v(w(u)("Legal warranty (Gewährleistung)")), 1),
          h("div", fr, [
            h("div", null, [
              h("label", hr, v(w(u)("Warranty duration")), 1),
              h("div", pr, [
                j(h("input", {
                  "onUpdate:modelValue": y[2] || (y[2] = (x) => r.value.legal_warranty_months = x),
                  type: "number",
                  min: "1",
                  max: "120",
                  class: "w-20 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                }, null, 512), [
                  [
                    J,
                    r.value.legal_warranty_months,
                    void 0,
                    { number: !0 }
                  ]
                ]),
                h("span", gr, v(w(u)("months")), 1)
              ])
            ]),
            h("div", null, [
              h("label", mr, v(w(u)("Burden of proof period")), 1),
              h("div", yr, [
                j(h("input", {
                  "onUpdate:modelValue": y[3] || (y[3] = (x) => r.value.burden_of_proof_months = x),
                  type: "number",
                  min: "1",
                  max: "120",
                  class: "w-20 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                }, null, 512), [
                  [
                    J,
                    r.value.burden_of_proof_months,
                    void 0,
                    { number: !0 }
                  ]
                ]),
                h("span", br, v(w(u)("months")), 1)
              ])
            ]),
            h("div", null, [
              h("label", xr, v(w(u)("Alert before proof shift")), 1),
              h("div", _r, [
                j(h("input", {
                  "onUpdate:modelValue": y[4] || (y[4] = (x) => r.value.burden_of_proof_alert_days = x),
                  type: "number",
                  min: "1",
                  max: "365",
                  class: "w-20 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                }, null, 512), [
                  [
                    J,
                    r.value.burden_of_proof_alert_days,
                    void 0,
                    { number: !0 }
                  ]
                ]),
                h("span", vr, v(w(u)("days")), 1)
              ])
            ])
          ])
        ]),
        h("div", wr, [
          h("div", null, [
            h("label", kr, v(w(u)("Overdue refund re-alert")), 1),
            h("div", Sr, [
              j(h("input", {
                "onUpdate:modelValue": y[5] || (y[5] = (x) => r.value.refund_alert_days = x),
                type: "number",
                min: "1",
                max: "90",
                class: "w-20 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              }, null, 512), [
                [
                  J,
                  r.value.refund_alert_days,
                  void 0,
                  { number: !0 }
                ]
              ]),
              h("span", Or, v(w(u)("days after return")), 1)
            ])
          ])
        ])
      ])) : N("", !0),
      o.value ? (T(), R("section", Er, [
        h("h2", Ar, v(w(u)("Item Lifespans")), 1),
        h("p", Cr, v(w(u)("Default lifespan and average replacement cost per item category. Used for health forecasts and replacement planning.")), 1),
        h("div", Tr, [
          h("table", Rr, [
            h("thead", null, [
              h("tr", Ir, [
                h("th", Mr, v(w(u)("Category")), 1),
                h("th", $r, v(w(u)("Lifespan (yr)")), 1),
                h("th", Lr, v(w(u)("Avg replacement cost")), 1)
              ])
            ]),
            h("tbody", null, [
              (T(!0), R(me, null, gt(r.value.category_lifespans, (x, O) => (T(), R("tr", {
                key: O,
                class: "border-b border-gray-100 dark:border-gray-700/50"
              }, [
                h("td", Pr, v(w(u)(x.category)), 1),
                h("td", Fr, [
                  j(h("input", {
                    "onUpdate:modelValue": (_) => x.lifespan_years = _,
                    type: "number",
                    min: "1",
                    max: "100",
                    class: "w-20 border border-gray-300 dark:border-gray-600 rounded px-2 py-1 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  }, null, 8, Dr), [
                    [
                      J,
                      x.lifespan_years,
                      void 0,
                      { number: !0 }
                    ]
                  ])
                ]),
                h("td", Nr, [
                  h("div", Hr, [
                    y[8] || (y[8] = h("span", { class: "absolute left-2 top-1/2 -translate-y-1/2 text-xs text-gray-400" }, "€", -1)),
                    j(h("input", {
                      "onUpdate:modelValue": (_) => x.avg_replacement_cost = _,
                      type: "number",
                      min: "0",
                      step: "50",
                      class: "w-28 border border-gray-300 dark:border-gray-600 rounded px-2 py-1 pl-6 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                    }, null, 8, Br), [
                      [
                        J,
                        x.avg_replacement_cost,
                        void 0,
                        { number: !0 }
                      ]
                    ])
                  ])
                ])
              ]))), 128))
            ])
          ])
        ])
      ])) : N("", !0),
      s.value ? (T(), R("section", jr, [
        h("h2", Vr, v(w(u)("Preferences")), 1),
        h("div", Ur, [
          h("div", null, [
            h("label", zr, v(w(u)("Default currency")), 1),
            j(h("input", {
              "onUpdate:modelValue": y[6] || (y[6] = (x) => r.value.default_currency = x),
              type: "text",
              maxlength: "3",
              class: "w-24 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 uppercase"
            }, null, 512), [
              [J, r.value.default_currency]
            ])
          ]),
          h("div", null, [
            h("label", Wr, v(w(u)("Cost data visible to")), 1),
            j(h("select", {
              "onUpdate:modelValue": y[7] || (y[7] = (x) => r.value.financial_visibility = x),
              class: "w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            }, [
              (T(), R(me, null, gt(d, (x) => h("option", {
                key: x.value,
                value: x.value
              }, v(x.label), 9, qr)), 64))
            ], 512), [
              [rn, r.value.financial_visibility]
            ]),
            h("p", Yr, v(w(u)("Controls who can see purchase prices and budget data. Children never see financial data.")), 1)
          ])
        ])
      ])) : N("", !0),
      s.value ? (T(), R("section", Kr, [
        h("h2", Xr, v(w(u)("Account")), 1),
        h("p", Jr, v(w(u)("Restart the guided onboarding tour to walk through the main features.")), 1),
        h("button", {
          class: "rounded-lg border border-gray-300 dark:border-gray-600 px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors disabled:opacity-50",
          disabled: p.value,
          onClick: S
        }, v(p.value ? w(u)("Restarting…") : w(u)("Reset onboarding tour")), 9, Gr)
      ])) : N("", !0),
      h("div", Zr, [
        h("button", {
          class: "rounded-lg bg-accent-600 dark:bg-accent-400 px-4 py-2 text-sm font-medium text-white dark:text-gray-900 hover:bg-accent-700 dark:hover:bg-accent-300 transition-colors disabled:opacity-50",
          disabled: l.value,
          onClick: b
        }, v(l.value ? w(u)("Saving…") : w(u)("Save settings")), 9, Qr),
        c.value ? (T(), R("span", ei, v(w(u)("Saved")), 1)) : N("", !0),
        a.value ? (T(), R("span", ti, v(a.value), 1)) : N("", !0)
      ])
    ], 64)) : N("", !0);
  }
}), oi = {
  key: 0,
  class: "text-gray-500"
}, si = {
  key: 1,
  class: "text-center py-16"
}, ri = { class: "text-h3 text-gray-800 dark:text-gray-200 mb-2" }, ii = { class: "text-body text-gray-500 dark:text-gray-400 mb-6" }, ai = { class: "max-w-sm mx-auto flex flex-col gap-3" }, li = ["placeholder"], ci = {
  key: 0,
  class: "text-sm text-red-600 dark:text-red-400"
}, ui = {
  key: 2,
  class: "text-red-600 dark:text-red-400"
}, di = { class: "mb-8" }, fi = { class: "text-h3 text-gray-800 dark:text-gray-200 mb-4" }, hi = { class: "space-y-3" }, pi = { class: "flex-1 min-w-0" }, gi = { class: "flex items-center gap-2" }, mi = { class: "font-medium text-gray-900 dark:text-gray-100 truncate" }, yi = {
  key: 0,
  class: "text-xs px-2 py-0.5 rounded-full bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300"
}, bi = {
  key: 1,
  class: "text-xs text-gray-400"
}, xi = { class: "text-caption text-gray-500 dark:text-gray-400" }, _i = { class: "flex items-center gap-2" }, vi = ["value", "onChange"], wi = ["onClick"], ki = { class: "flex items-center gap-1" }, Si = ["onClick", "title"], Oi = {
  key: 0,
  class: "p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
}, Ei = { class: "text-h4 text-gray-800 dark:text-gray-200 mb-3" }, Ai = { class: "flex gap-3 items-end flex-wrap" }, Ci = { class: "flex-1 min-w-[200px]" }, Ti = { class: "text-caption text-gray-500 dark:text-gray-400 block mb-1" }, Ri = ["placeholder"], Ii = { class: "text-caption text-gray-500 dark:text-gray-400 block mb-1" }, Mi = { value: "Adult" }, $i = { value: "Child" }, Li = {
  key: 0,
  class: "mt-2 text-sm text-gray-600 dark:text-gray-400"
}, Pi = {
  key: 2,
  class: "text-center py-12"
}, Fi = { class: "text-sm text-gray-500 dark:text-gray-400" }, Ni = /* @__PURE__ */ vt({
  __name: "HomeSettings",
  props: {
    section: {}
  },
  setup(t) {
    const e = t, n = window.frappe?.session?.user || "", o = P(""), s = P([]), r = P(!0), i = P(""), a = P(!1), l = P(""), c = P(!1), f = P(""), p = P("Adult"), d = P(!1), g = P(""), b = P(null), S = ne(
      () => s.value.find((I) => I.user === n)
    ), k = ne(() => S.value?.role === "Owner"), y = ne(() => e.section || "household");
    async function x() {
      r.value = !0, i.value = "";
      try {
        const C = await V({
          url: "/api/method/home.api.permission.get_user_households"
        }) || [];
        if (!C.length) {
          a.value = !0, r.value = !1;
          return;
        }
        o.value = C[0], await O();
      } catch (I) {
        i.value = I.message || u("Failed to load household");
      } finally {
        r.value = !1;
      }
    }
    async function O() {
      const I = await V({
        url: "/api/method/home.api.household.get_members",
        params: { household: o.value }
      });
      s.value = I || [];
    }
    async function _() {
      if (f.value.trim()) {
        d.value = !0, g.value = "";
        try {
          const C = await V({
            url: "/api/method/home.api.household.invite_member",
            params: {
              household: o.value,
              email: f.value.trim(),
              role: p.value
            }
          });
          g.value = C.user_exists ? u("Member added successfully") : u("Invitation sent — they will appear once they register"), f.value = "", await O();
        } catch (I) {
          g.value = I.message || u("Failed to invite member");
        } finally {
          d.value = !1;
        }
      }
    }
    async function m(I) {
      try {
        await V({
          url: "/api/method/home.api.household.remove_member",
          params: { household: o.value, member_name: I }
        }), await O();
      } catch (C) {
        alert(C.message || u("Failed to remove member"));
      }
    }
    async function A(I, C) {
      try {
        await V({
          url: "/api/method/home.api.household.change_member_role",
          params: { household: o.value, member_name: I, new_role: C }
        }), b.value = null, await O();
      } catch (D) {
        alert(D.message || u("Failed to change role"));
      }
    }
    function F(I) {
      switch (I) {
        case "Owner":
          return "bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200";
        case "Adult":
          return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200";
        case "Child":
          return "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200";
        default:
          return "bg-gray-100 text-gray-800";
      }
    }
    async function K() {
      c.value = !0, i.value = "";
      try {
        await V({
          url: "/api/method/home.api.household.create_household",
          params: { household_name: l.value.trim() }
        }), a.value = !1, l.value = "", await x();
      } catch (I) {
        i.value = I.message || u("Failed to create household");
      } finally {
        c.value = !1;
      }
    }
    return sn(x), (I, C) => {
      const D = Rn("Button");
      return T(), R("div", null, [
        r.value ? (T(), R("div", oi, v(w(u)("Loading…")), 1)) : a.value ? (T(), R("div", si, [
          C[4] || (C[4] = h("div", { class: "text-6xl mb-4" }, "🏠", -1)),
          h("h2", ri, v(w(u)("Welcome to Home")), 1),
          h("p", ii, v(w(u)("Create your household to get started.")), 1),
          h("div", ai, [
            j(h("input", {
              "onUpdate:modelValue": C[0] || (C[0] = (E) => l.value = E),
              type: "text",
              placeholder: w(u)("My Home"),
              class: "w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100",
              onKeyup: $t(K, ["enter"])
            }, null, 40, li), [
              [J, l.value]
            ]),
            ct(D, {
              variant: "solid",
              loading: c.value,
              onClick: K
            }, {
              default: Lt(() => [
                Pt(v(w(u)("Create Household")), 1)
              ]),
              _: 1
            }, 8, ["loading"]),
            i.value ? (T(), R("p", ci, v(i.value), 1)) : N("", !0)
          ])
        ])) : i.value ? (T(), R("div", ui, v(i.value), 1)) : (T(), R(me, { key: 3 }, [
          y.value === "household" ? (T(), R(me, { key: 0 }, [
            h("section", di, [
              h("h2", fi, v(w(u)("Members")), 1),
              h("div", hi, [
                (T(!0), R(me, null, gt(s.value, (E) => (T(), R("div", {
                  key: E.name,
                  class: "flex items-center gap-3 p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
                }, [
                  ct(Nn, {
                    "display-name": E.display_name,
                    avatar: E.avatar,
                    size: "md"
                  }, null, 8, ["display-name", "avatar"]),
                  h("div", pi, [
                    h("div", gi, [
                      h("span", mi, v(E.display_name), 1),
                      E.pending ? (T(), R("span", yi, v(w(u)("Pending")), 1)) : N("", !0),
                      E.user === w(n) ? (T(), R("span", bi, v(w(u)("(you)")), 1)) : N("", !0)
                    ]),
                    h("div", xi, v(E.email || E.user || w(u)("No account")), 1)
                  ]),
                  h("div", _i, [
                    k.value && b.value === E.name ? (T(), R(me, { key: 0 }, [
                      h("select", {
                        value: E.role,
                        onChange: (W) => A(E.name, W.target.value),
                        class: "text-sm border border-gray-300 dark:border-gray-600 rounded px-2 py-1 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                      }, [...C[5] || (C[5] = [
                        h("option", { value: "Owner" }, "Owner", -1),
                        h("option", { value: "Adult" }, "Adult", -1),
                        h("option", { value: "Child" }, "Child", -1)
                      ])], 40, vi),
                      h("button", {
                        onClick: C[1] || (C[1] = (W) => b.value = null),
                        class: "text-xs text-gray-400 hover:text-gray-600"
                      }, v(w(u)("Cancel")), 1)
                    ], 64)) : (T(), R("span", {
                      key: 1,
                      class: pt(["text-xs px-2 py-0.5 rounded-full font-medium", F(E.role)]),
                      onClick: (W) => k.value && E.user !== w(n) ? b.value = E.name : null,
                      style: In(k.value && E.user !== w(n) ? "cursor: pointer" : "")
                    }, v(E.role), 15, wi))
                  ]),
                  h("div", ki, [
                    k.value && E.user !== w(n) ? (T(), R("button", {
                      key: 0,
                      onClick: (W) => m(E.name),
                      class: "text-xs text-red-400 hover:text-red-600 px-2 py-1",
                      title: w(u)("Remove member")
                    }, v(w(u)("Remove")), 9, Si)) : N("", !0)
                  ])
                ]))), 128))
              ])
            ]),
            k.value ? (T(), R("section", Oi, [
              h("h3", Ei, v(w(u)("Invite Member")), 1),
              h("div", Ai, [
                h("div", Ci, [
                  h("label", Ti, v(w(u)("Email")), 1),
                  j(h("input", {
                    "onUpdate:modelValue": C[2] || (C[2] = (E) => f.value = E),
                    type: "email",
                    placeholder: w(u)("person@example.com"),
                    class: "w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100",
                    onKeyup: $t(_, ["enter"])
                  }, null, 40, Ri), [
                    [J, f.value]
                  ])
                ]),
                h("div", null, [
                  h("label", Ii, v(w(u)("Role")), 1),
                  j(h("select", {
                    "onUpdate:modelValue": C[3] || (C[3] = (E) => p.value = E),
                    class: "border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  }, [
                    h("option", Mi, v(w(u)("Adult")), 1),
                    h("option", $i, v(w(u)("Child")), 1)
                  ], 512), [
                    [rn, p.value]
                  ])
                ]),
                ct(D, {
                  onClick: _,
                  variant: "solid",
                  loading: d.value
                }, {
                  default: Lt(() => [
                    Pt(v(w(u)("Send Invite")), 1)
                  ]),
                  _: 1
                }, 8, ["loading"])
              ]),
              g.value ? (T(), R("p", Li, v(g.value), 1)) : N("", !0)
            ])) : N("", !0)
          ], 64)) : N("", !0),
          k.value && (y.value === "alerts" || y.value === "lifespans" || y.value === "preferences") ? (T(), Mn(ni, {
            key: 1,
            household: o.value,
            section: y.value
          }, null, 8, ["household", "section"])) : N("", !0),
          !k.value && y.value !== "household" ? (T(), R("div", Pi, [
            h("p", Fi, v(w(u)("Only the household owner can manage these settings.")), 1)
          ])) : N("", !0)
        ], 64))
      ]);
    };
  }
});
export {
  Ni as HomeSettings
};
