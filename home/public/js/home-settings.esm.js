import { defineComponent as kt, computed as ne, openBlock as T, createElementBlock as R, normalizeClass as mt, toDisplayString as v, ref as P, onMounted as sn, resolveComponent as rn, unref as w, Fragment as me, createElementVNode as d, withDirectives as j, vModelText as Y, createCommentVNode as N, renderList as yt, vModelSelect as an, createVNode as Ve, withCtx as tt, createTextVNode as nt, withKeys as Pt, normalizeStyle as In, createBlock as Mn } from "/assets/dock/js/vendor/vue.esm.js";
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
const Fn = ["src", "alt"], Dn = ["title"], Nn = /* @__PURE__ */ kt({
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
      class: mt([n.value, "rounded-full object-cover"])
    }, null, 10, Fn)) : (T(), R("div", {
      key: 1,
      class: mt([n.value, s.value, "rounded-full flex items-center justify-center text-white font-medium select-none"]),
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
function Xe(t) {
  return t instanceof HTMLElement;
}
function ue(t) {
  return typeof t == "function";
}
function qe(t) {
  return typeof t == "string";
}
function H(t) {
  return t === void 0;
}
class St {
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
          var h;
          (h = this.bindings[e]) == null || h.splice(r, 1);
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
function ln(t, e) {
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
function cn(t) {
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
    }), a = dn(r, e, i);
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
  return new Set(cn(t));
}
function Yn(t) {
  return new Map(cn(t));
}
function un(t) {
  return t.at(-1);
}
var ft = /* @__PURE__ */ Object.freeze({
  __proto__: null,
  mergeArrays: Wn,
  mergeMaps: Yn,
  mergeOthers: un,
  mergeRecords: zn,
  mergeSets: qn
});
function Ot(...t) {
  return Kn({})(...t);
}
function Kn(t, e) {
  const n = Xn(t, o);
  function o(...s) {
    return dn(s, n, e);
  }
  return o;
}
function Xn(t, e) {
  var n, o;
  return {
    defaultMergeFunctions: ft,
    mergeFunctions: B({}, ft, Object.fromEntries(Object.entries(t).filter(([s, r]) => Object.hasOwn(ft, s)).map(([s, r]) => r === !1 ? [s, un] : [s, r]))),
    metaDataUpdater: (n = t.metaDataUpdater) != null ? n : Bn,
    deepmerge: e,
    useImplicitDefaultMerging: (o = t.enableImplicitDefaultMerging) != null ? o : !1,
    actions: he
  };
}
function dn(t, e, n) {
  if (t.length === 0)
    return;
  if (t.length === 1)
    return ht(t, e, n);
  const o = Ft(t[0]);
  if (o !== 0 && o !== 5) {
    for (let s = 1; s < t.length; s++)
      if (Ft(t[s]) !== o)
        return ht(t, e, n);
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
      return ht(t, e, n);
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
function ht(t, e, n) {
  const o = e.mergeFunctions.mergeOthers(t, e, n);
  return o === he.defaultMerge || e.useImplicitDefaultMerging && o === void 0 && e.mergeFunctions.mergeOthers !== e.defaultMergeFunctions.mergeOthers ? e.defaultMergeFunctions.mergeOthers(t) : o;
}
function Et(t) {
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
function fn(t) {
  return !qe(t) || t === "" ? "" : t.charAt(t.length - 1) !== "-" ? `${t}-` : t;
}
function so(t) {
  const e = t.options.attachTo || {}, n = Object.assign({}, e);
  if (ue(n.element) && (n.element = n.element.call(t)), qe(n.element)) {
    try {
      n.element = document.querySelector(n.element);
    } catch {
    }
    n.element || console.error(`The element for this Shepherd step was not found ${e.element}`);
  }
  return n;
}
function hn(t) {
  return t == null ? !0 : !t.element || !t.on;
}
function pn() {
  let t = Date.now();
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (e) => {
    const n = (t + Math.random() * 16) % 16 | 0;
    return t = Math.floor(t / 16), (e == "x" ? n : n & 3 | 8).toString(16);
  });
}
const Le = Math.min, _e = Math.max, ot = Math.round, Ze = Math.floor, de = (t) => ({
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
function bt(t, e, n) {
  return _e(t, Le(e, n));
}
function Pe(t, e) {
  return typeof t == "function" ? t(e) : t;
}
function we(t) {
  return t.split("-")[0];
}
function lt(t) {
  return t.split("-")[1];
}
function At(t) {
  return t === "x" ? "y" : "x";
}
function Ct(t) {
  return t === "y" ? "height" : "width";
}
function Fe(t) {
  return ["top", "bottom"].includes(we(t)) ? "y" : "x";
}
function Tt(t) {
  return At(Fe(t));
}
function ao(t, e, n) {
  n === void 0 && (n = !1);
  const o = lt(t), s = Tt(t), r = Ct(s);
  let i = s === "x" ? o === (n ? "end" : "start") ? "right" : "left" : o === "start" ? "bottom" : "top";
  return e.reference[r] > e.floating[r] && (i = st(i)), [i, st(i)];
}
function lo(t) {
  const e = st(t);
  return [_t(t), e, _t(e)];
}
function _t(t) {
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
  const s = lt(t);
  let r = co(we(t), n === "start", o);
  return s && (r = r.map((i) => i + "-" + s), e && (r = r.concat(r.map(_t)))), r;
}
function st(t) {
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
function gn(t) {
  return typeof t != "number" ? fo(t) : {
    top: t,
    right: t,
    bottom: t,
    left: t
  };
}
function rt(t) {
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
  const r = Fe(e), i = Tt(e), a = Ct(i), l = we(e), c = r === "y", h = o.x + o.width / 2 - s.width / 2, p = o.y + o.height / 2 - s.height / 2, f = o[a] / 2 - s[a] / 2;
  let m;
  switch (l) {
    case "top":
      m = {
        x: h,
        y: o.y - s.height
      };
      break;
    case "bottom":
      m = {
        x: h,
        y: o.y + o.height
      };
      break;
    case "right":
      m = {
        x: o.x + o.width,
        y: p
      };
      break;
    case "left":
      m = {
        x: o.x - s.width,
        y: p
      };
      break;
    default:
      m = {
        x: o.x,
        y: o.y
      };
  }
  switch (lt(e)) {
    case "start":
      m[i] -= f * (n && c ? -1 : 1);
      break;
    case "end":
      m[i] += f * (n && c ? -1 : 1);
      break;
  }
  return m;
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
    x: h,
    y: p
  } = Nt(c, o, l), f = o, m = {}, _ = 0;
  for (let S = 0; S < a.length; S++) {
    const {
      name: k,
      fn: y
    } = a[S], {
      x: O,
      y: b,
      data: x,
      reset: g
    } = await y({
      x: h,
      y: p,
      initialPlacement: o,
      placement: f,
      strategy: s,
      middlewareData: m,
      rects: c,
      platform: i,
      elements: {
        reference: t,
        floating: e
      }
    });
    h = O ?? h, p = b ?? p, m = B({}, m, {
      [k]: B({}, m[k], x)
    }), g && _ <= 50 && (_++, typeof g == "object" && (g.placement && (f = g.placement), g.rects && (c = g.rects === !0 ? await i.getElementRects({
      reference: t,
      floating: e,
      strategy: s
    }) : g.rects), {
      x: h,
      y: p
    } = Nt(c, f, l)), S = -1);
  }
  return {
    x: h,
    y: p,
    placement: f,
    strategy: s,
    middlewareData: m
  };
};
async function mn(t, e) {
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
    rootBoundary: h = "viewport",
    elementContext: p = "floating",
    altBoundary: f = !1,
    padding: m = 0
  } = Pe(e, t), _ = gn(m), k = a[f ? p === "floating" ? "reference" : "floating" : p], y = rt(await r.getClippingRect({
    element: (n = await (r.isElement == null ? void 0 : r.isElement(k))) == null || n ? k : k.contextElement || await (r.getDocumentElement == null ? void 0 : r.getDocumentElement(a.floating)),
    boundary: c,
    rootBoundary: h,
    strategy: l
  })), O = p === "floating" ? {
    x: o,
    y: s,
    width: i.floating.width,
    height: i.floating.height
  } : i.reference, b = await (r.getOffsetParent == null ? void 0 : r.getOffsetParent(a.floating)), x = await (r.isElement == null ? void 0 : r.isElement(b)) ? await (r.getScale == null ? void 0 : r.getScale(b)) || {
    x: 1,
    y: 1
  } : {
    x: 1,
    y: 1
  }, g = rt(r.convertOffsetParentRelativeRectToViewportRelativeRect ? await r.convertOffsetParentRelativeRectToViewportRelativeRect({
    elements: a,
    rect: O,
    offsetParent: b,
    strategy: l
  }) : O);
  return {
    top: (y.top - g.top + _.top) / x.y,
    bottom: (g.bottom - y.bottom + _.bottom) / x.y,
    left: (y.left - g.left + _.left) / x.x,
    right: (g.right - y.right + _.right) / x.x
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
      padding: h = 0
    } = Pe(t, e) || {};
    if (c == null)
      return {};
    const p = gn(h), f = {
      x: n,
      y: o
    }, m = Tt(s), _ = Ct(m), S = await i.getDimensions(c), k = m === "y", y = k ? "top" : "left", O = k ? "bottom" : "right", b = k ? "clientHeight" : "clientWidth", x = r.reference[_] + r.reference[m] - f[m] - r.floating[_], g = f[m] - r.reference[m], A = await (i.getOffsetParent == null ? void 0 : i.getOffsetParent(c));
    let F = A ? A[b] : 0;
    (!F || !await (i.isElement == null ? void 0 : i.isElement(A))) && (F = a.floating[b] || r.floating[_]);
    const X = x / 2 - g / 2, I = F / 2 - S[_] / 2 - 1, C = Le(p[y], I), D = Le(p[O], I), E = C, W = F - S[_] - D, q = F / 2 - S[_] / 2 + X, Oe = bt(E, q, W), J = !l.arrow && lt(s) != null && q !== Oe && r.reference[_] / 2 - (q < E ? C : D) - S[_] / 2 < 0, Ee = J ? q < E ? q - E : q - W : 0;
    return {
      [m]: f[m] + Ee,
      data: B({
        [m]: Oe,
        centerOffset: q - Oe - Ee
      }, J && {
        alignmentOffset: Ee
      }),
      reset: J
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
        elements: h
      } = n, p = Pe(e, n), {
        mainAxis: f = !0,
        crossAxis: m = !0,
        fallbackPlacements: _,
        fallbackStrategy: S = "bestFit",
        fallbackAxisSideDirection: k = "none",
        flipAlignment: y = !0
      } = p, O = ln(p, ho);
      if ((o = i.arrow) != null && o.alignmentOffset)
        return {};
      const b = we(r), x = Fe(l), g = we(l) === l, A = await (c.isRTL == null ? void 0 : c.isRTL(h.floating)), F = _ || (g || !y ? [st(l)] : lo(l)), X = k !== "none";
      !_ && X && F.push(...uo(l, y, k, A));
      const I = [l, ...F], C = await mn(n, O), D = [];
      let E = ((s = i.flip) == null ? void 0 : s.overflows) || [];
      if (f && D.push(C[b]), m) {
        const J = ao(r, a, A);
        D.push(C[J[0]], C[J[1]]);
      }
      if (E = [...E, {
        placement: r,
        overflows: D
      }], !D.every((J) => J <= 0)) {
        var W, q;
        const J = (((W = i.flip) == null ? void 0 : W.index) || 0) + 1, Ee = I[J];
        if (Ee)
          return {
            data: {
              index: J,
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
                if (X) {
                  const le = Fe(ae.placement);
                  return le === x || // Create a bias to the `y` side axis due to horizontal
                  // reading directions favoring greater width.
                  le === "y";
                }
                return !0;
              }).map((ae) => [ae.placement, ae.overflows.filter((le) => le > 0).reduce((le, Rn) => le + Rn, 0)]).sort((ae, le) => ae[1] - le[1])[0]) == null ? void 0 : Oe[0];
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
          fn: (O) => {
            let {
              x: b,
              y: x
            } = O;
            return {
              x: b,
              y: x
            };
          }
        }
      } = i, h = ln(i, po), p = {
        x: o,
        y: s
      }, f = await mn(n, h), m = Fe(we(r)), _ = At(m);
      let S = p[_], k = p[m];
      if (a) {
        const O = _ === "y" ? "top" : "left", b = _ === "y" ? "bottom" : "right", x = S + f[O], g = S - f[b];
        S = bt(x, S, g);
      }
      if (l) {
        const O = m === "y" ? "top" : "left", b = m === "y" ? "bottom" : "right", x = k + f[O], g = k - f[b];
        k = bt(x, k, g);
      }
      const y = c.fn(B({}, n, {
        [_]: S,
        [m]: k
      }));
      return B({}, y, {
        data: {
          x: y.x - o,
          y: y.y - s
        }
      });
    }
  };
}, _o = function(e) {
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
        crossAxis: h = !0
      } = Pe(e, n), p = {
        x: o,
        y: s
      }, f = Fe(r), m = At(f);
      let _ = p[m], S = p[f];
      const k = Pe(l, n), y = typeof k == "number" ? {
        mainAxis: k,
        crossAxis: 0
      } : B({
        mainAxis: 0,
        crossAxis: 0
      }, k);
      if (c) {
        const x = m === "y" ? "height" : "width", g = i.reference[m] - i.floating[x] + y.mainAxis, A = i.reference[m] + i.reference[x] - y.mainAxis;
        _ < g ? _ = g : _ > A && (_ = A);
      }
      if (h) {
        var O, b;
        const x = m === "y" ? "width" : "height", g = ["top", "left"].includes(we(r)), A = i.reference[f] - i.floating[x] + (g && ((O = a.offset) == null ? void 0 : O[f]) || 0) + (g ? 0 : y.crossAxis), F = i.reference[f] + i.reference[x] + (g ? 0 : ((b = a.offset) == null ? void 0 : b[f]) || 0) - (g ? y.crossAxis : 0);
        S < A ? S = A : S > F && (S = F);
      }
      return {
        [m]: _,
        [f]: S
      };
    }
  };
};
function Be(t) {
  return yn(t) ? (t.nodeName || "").toLowerCase() : "#document";
}
function U(t) {
  var e;
  return (t == null || (e = t.ownerDocument) == null ? void 0 : e.defaultView) || window;
}
function oe(t) {
  var e;
  return (e = (yn(t) ? t.ownerDocument : t.document) || window.document) == null ? void 0 : e.documentElement;
}
function yn(t) {
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
function Je(t) {
  const {
    overflow: e,
    overflowX: n,
    overflowY: o,
    display: s
  } = Z(t);
  return /auto|scroll|overlay|hidden|clip/.test(e + o + n) && !["inline", "contents"].includes(s);
}
function xo(t) {
  return ["table", "td", "th"].includes(Be(t));
}
function ct(t) {
  return [":popover-open", ":modal"].some((e) => {
    try {
      return t.matches(e);
    } catch {
      return !1;
    }
  });
}
function Rt(t) {
  const e = It(), n = G(t) ? Z(t) : t;
  return n.transform !== "none" || n.perspective !== "none" || (n.containerType ? n.containerType !== "normal" : !1) || !e && (n.backdropFilter ? n.backdropFilter !== "none" : !1) || !e && (n.filter ? n.filter !== "none" : !1) || ["transform", "perspective", "filter"].some((o) => (n.willChange || "").includes(o)) || ["paint", "layout", "strict", "content"].some((o) => (n.contain || "").includes(o));
}
function vo(t) {
  let e = fe(t);
  for (; ee(e) && !De(e); ) {
    if (Rt(e))
      return e;
    if (ct(e))
      return null;
    e = fe(e);
  }
  return null;
}
function It() {
  return typeof CSS > "u" || !CSS.supports ? !1 : CSS.supports("-webkit-backdrop-filter", "none");
}
function De(t) {
  return ["html", "body", "#document"].includes(Be(t));
}
function Z(t) {
  return U(t).getComputedStyle(t);
}
function ut(t) {
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
function bn(t) {
  const e = fe(t);
  return De(e) ? t.ownerDocument ? t.ownerDocument.body : t.body : ee(e) && Je(e) ? e : bn(e);
}
function Ye(t, e, n) {
  var o;
  e === void 0 && (e = []), n === void 0 && (n = !0);
  const s = bn(t), r = s === ((o = t.ownerDocument) == null ? void 0 : o.body), i = U(s);
  return r ? e.concat(i, i.visualViewport || [], Je(s) ? s : [], i.frameElement && n ? Ye(i.frameElement) : []) : e.concat(s, Ye(s, [], n));
}
function _n(t) {
  const e = Z(t);
  let n = parseFloat(e.width) || 0, o = parseFloat(e.height) || 0;
  const s = ee(t), r = s ? t.offsetWidth : n, i = s ? t.offsetHeight : o, a = ot(n) !== r || ot(o) !== i;
  return a && (n = r, o = i), {
    width: n,
    height: o,
    $: a
  };
}
function Mt(t) {
  return G(t) ? t : t.contextElement;
}
function Me(t) {
  const e = Mt(t);
  if (!ee(e))
    return de(1);
  const n = e.getBoundingClientRect(), {
    width: o,
    height: s,
    $: r
  } = _n(e);
  let i = (r ? ot(n.width) : n.width) / o, a = (r ? ot(n.height) : n.height) / s;
  return (!i || !Number.isFinite(i)) && (i = 1), (!a || !Number.isFinite(a)) && (a = 1), {
    x: i,
    y: a
  };
}
const wo = /* @__PURE__ */ de(0);
function xn(t) {
  const e = U(t);
  return !It() || !e.visualViewport ? wo : {
    x: e.visualViewport.offsetLeft,
    y: e.visualViewport.offsetTop
  };
}
function ko(t, e, n) {
  return e === void 0 && (e = !1), !n || e && n !== U(t) ? !1 : e;
}
function ke(t, e, n, o) {
  e === void 0 && (e = !1), n === void 0 && (n = !1);
  const s = t.getBoundingClientRect(), r = Mt(t);
  let i = de(1);
  e && (o ? G(o) && (i = Me(o)) : i = Me(t));
  const a = ko(r, n, o) ? xn(r) : de(0);
  let l = (s.left + a.x) / i.x, c = (s.top + a.y) / i.y, h = s.width / i.x, p = s.height / i.y;
  if (r) {
    const f = U(r), m = o && G(o) ? U(o) : o;
    let _ = f, S = _.frameElement;
    for (; S && o && m !== _; ) {
      const k = Me(S), y = S.getBoundingClientRect(), O = Z(S), b = y.left + (S.clientLeft + parseFloat(O.paddingLeft)) * k.x, x = y.top + (S.clientTop + parseFloat(O.paddingTop)) * k.y;
      l *= k.x, c *= k.y, h *= k.x, p *= k.y, l += b, c += x, _ = U(S), S = _.frameElement;
    }
  }
  return rt({
    width: h,
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
  const r = s === "fixed", i = oe(o), a = e ? ct(e.floating) : !1;
  if (o === i || a && r)
    return n;
  let l = {
    scrollLeft: 0,
    scrollTop: 0
  }, c = de(1);
  const h = de(0), p = ee(o);
  if ((p || !p && !r) && ((Be(o) !== "body" || Je(i)) && (l = ut(o)), ee(o))) {
    const f = ke(o);
    c = Me(o), h.x = f.x + o.clientLeft, h.y = f.y + o.clientTop;
  }
  return {
    width: n.width * c.x,
    height: n.height * c.y,
    x: n.x * c.x - l.scrollLeft * c.x + h.x,
    y: n.y * c.y - l.scrollTop * c.y + h.y
  };
}
function Oo(t) {
  return Array.from(t.getClientRects());
}
function vn(t) {
  return ke(oe(t)).left + ut(t).scrollLeft;
}
function Eo(t) {
  const e = oe(t), n = ut(t), o = t.ownerDocument.body, s = _e(e.scrollWidth, e.clientWidth, o.scrollWidth, o.clientWidth), r = _e(e.scrollHeight, e.clientHeight, o.scrollHeight, o.clientHeight);
  let i = -n.scrollLeft + vn(t);
  const a = -n.scrollTop;
  return Z(o).direction === "rtl" && (i += _e(e.clientWidth, o.clientWidth) - s), {
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
    const c = It();
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
  return rt(o);
}
function wn(t, e) {
  const n = fe(t);
  return n === e || !G(n) || De(n) ? !1 : Z(n).position === "fixed" || wn(n, e);
}
function To(t, e) {
  const n = e.get(t);
  if (n)
    return n;
  let o = Ye(t, [], !1).filter((a) => G(a) && Be(a) !== "body"), s = null;
  const r = Z(t).position === "fixed";
  let i = r ? fe(t) : t;
  for (; G(i) && !De(i); ) {
    const a = Z(i), l = Rt(i);
    !l && a.position === "fixed" && (s = null), (r ? !l && !s : !l && a.position === "static" && !!s && ["absolute", "fixed"].includes(s.position) || Je(i) && !l && wn(t, i)) ? o = o.filter((h) => h !== i) : s = a, i = fe(i);
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
  const i = [...n === "clippingAncestors" ? ct(e) ? [] : To(e, this._c) : [].concat(n), o], a = i[0], l = i.reduce((c, h) => {
    const p = Bt(e, h, s);
    return c.top = _e(p.top, c.top), c.right = Le(p.right, c.right), c.bottom = Le(p.bottom, c.bottom), c.left = _e(p.left, c.left), c;
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
  } = _n(t);
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
    if ((Be(e) !== "body" || Je(s)) && (a = ut(e)), o) {
      const p = ke(e, !0, r, e);
      l.x = p.x + e.clientLeft, l.y = p.y + e.clientTop;
    } else s && (l.x = vn(s));
  const c = i.left + a.scrollLeft - l.x, h = i.top + a.scrollTop - l.y;
  return {
    x: c,
    y: h,
    width: i.width,
    height: i.height
  };
}
function pt(t) {
  return Z(t).position === "static";
}
function jt(t, e) {
  return !ee(t) || Z(t).position === "fixed" ? null : e ? e(t) : t.offsetParent;
}
function kn(t, e) {
  const n = U(t);
  if (ct(t))
    return n;
  if (!ee(t)) {
    let s = fe(t);
    for (; s && !De(s); ) {
      if (G(s) && !pt(s))
        return s;
      s = fe(s);
    }
    return n;
  }
  let o = jt(t, e);
  for (; o && xo(o) && pt(o); )
    o = jt(o, e);
  return o && De(o) && pt(o) && !Rt(o) ? n : o || vo(t) || n;
}
const $o = async function(e) {
  const n = this.getOffsetParent || kn, o = this.getDimensions, s = await o(e.floating);
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
  getOffsetParent: kn,
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
      top: h,
      width: p,
      height: f
    } = t.getBoundingClientRect();
    if (a || e(), !p || !f)
      return;
    const m = Ze(h), _ = Ze(s.clientWidth - (c + p)), S = Ze(s.clientHeight - (h + f)), k = Ze(c), O = {
      rootMargin: -m + "px " + -_ + "px " + -S + "px " + -k + "px",
      threshold: _e(0, Le(1, l)) || 1
    };
    let b = !0;
    function x(g) {
      const A = g[0].intersectionRatio;
      if (A !== l) {
        if (!b)
          return i();
        A ? i(!1, A) : o = setTimeout(() => {
          i(!1, 1e-7);
        }, 1e3);
      }
      b = !1;
    }
    try {
      n = new IntersectionObserver(x, B({}, O, {
        // Handle <iframe>s
        root: s.ownerDocument
      }));
    } catch {
      n = new IntersectionObserver(x, O);
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
  } = o, c = Mt(t), h = s || r ? [...c ? Ye(c) : [], ...Ye(e)] : [];
  h.forEach((y) => {
    s && y.addEventListener("scroll", n, {
      passive: !0
    }), r && y.addEventListener("resize", n);
  });
  const p = c && a ? Fo(c, n) : null;
  let f = -1, m = null;
  i && (m = new ResizeObserver((y) => {
    let [O] = y;
    O && O.target === c && m && (m.unobserve(e), cancelAnimationFrame(f), f = requestAnimationFrame(() => {
      var b;
      (b = m) == null || b.observe(e);
    })), n();
  }), c && !l && m.observe(c), m.observe(e));
  let _, S = l ? ke(t) : null;
  l && k();
  function k() {
    const y = ke(t);
    S && (y.x !== S.x || y.y !== S.y || y.width !== S.width || y.height !== S.height) && n(), S = y, _ = requestAnimationFrame(k);
  }
  return n(), () => {
    var y;
    h.forEach((O) => {
      s && O.removeEventListener("scroll", n), r && O.removeEventListener("resize", n);
    }), p?.(), (y = m) == null || y.disconnect(), m = null, l && cancelAnimationFrame(_);
  };
}
const No = bo, Ho = yo, Bo = mo, jo = _o, Vo = (t, e, n) => {
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
  const o = Xo(e, t), s = hn(e);
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
    floatingUIOptions: Ot(t.floatingUIOptions || {}, e.floatingUIOptions || {})
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
  if (Xe(n) && e.arrow) {
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
  if (!hn(t)) {
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
  return Ot(e.options.floatingUIOptions || {}, n);
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
function Sn(t) {
  return t();
}
function Vt() {
  return /* @__PURE__ */ Object.create(null);
}
function Ge(t) {
  t.forEach(Sn);
}
function $t(t) {
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
function K(t) {
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
function On(t) {
  return document.createTextNode(t);
}
function it() {
  return On(" ");
}
function es() {
  return On("");
}
function dt(t, e, n, o) {
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
let Ke;
function Ue(t) {
  Ke = t;
}
function En() {
  if (!Ke) throw new Error("Function called outside component initialization");
  return Ke;
}
function os(t) {
  En().$$.on_mount.push(t);
}
function Lt(t) {
  En().$$.after_update.push(t);
}
const Re = [], He = [];
let $e = [];
const Wt = [], ss = /* @__PURE__ */ Promise.resolve();
let xt = !1;
function rs() {
  xt || (xt = !0, ss.then(An));
}
function vt(t) {
  $e.push(t);
}
const gt = /* @__PURE__ */ new Set();
let Te = 0;
function An() {
  if (Te !== 0)
    return;
  const t = Ke;
  do {
    try {
      for (; Te < Re.length; ) {
        const e = Re[Te];
        Te++, Ue(e), is(e.$$);
      }
    } catch (e) {
      throw Re.length = 0, Te = 0, e;
    }
    for (Ue(null), Re.length = 0, Te = 0; He.length; ) He.pop()();
    for (let e = 0; e < $e.length; e += 1) {
      const n = $e[e];
      gt.has(n) || (gt.add(n), n());
    }
    $e.length = 0;
  } while (Re.length);
  for (; Wt.length; )
    Wt.pop()();
  xt = !1, gt.clear(), Ue(t);
}
function is(t) {
  if (t.fragment !== null) {
    t.update(), Ge(t.before_update);
    const e = t.dirty;
    t.dirty = [-1], t.fragment && t.fragment.p(t.ctx, e), t.after_update.forEach(vt);
  }
}
function as(t) {
  const e = [], n = [];
  $e.forEach((o) => t.indexOf(o) === -1 ? e.push(o) : n.push(o)), n.forEach((o) => o()), $e = e;
}
const et = /* @__PURE__ */ new Set();
let ye;
function xe() {
  ye = {
    r: 0,
    c: [],
    p: ye
    // parent group
  };
}
function ve() {
  ye.r || Ge(ye.c), ye = ye.p;
}
function M(t, e) {
  t && t.i && (et.delete(t), t.i(e));
}
function L(t, e, n, o) {
  if (t && t.o) {
    if (et.has(t)) return;
    et.add(t), ye.c.push(() => {
      et.delete(t), o && (n && t.d(1), o());
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
  o && o.m(e, n), vt(() => {
    const r = t.$$.on_mount.map(Sn).filter($t);
    t.$$.on_destroy ? t.$$.on_destroy.push(...r) : Ge(r), t.$$.on_mount = [];
  }), s.forEach(vt);
}
function ge(t, e) {
  const n = t.$$;
  n.fragment !== null && (as(n.after_update), Ge(n.on_destroy), n.fragment && n.fragment.d(e), n.on_destroy = n.fragment = null, n.ctx = []);
}
function cs(t, e) {
  t.$$.dirty[0] === -1 && (Re.push(t), rs(), t.$$.dirty.fill(0)), t.$$.dirty[e / 31 | 0] |= 1 << e % 31;
}
function re(t, e, n, o, s, r, i = null, a = [-1]) {
  const l = Ke;
  Ue(t);
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
  let h = !1;
  if (c.ctx = n ? n(t, e.props || {}, (p, f, ...m) => {
    const _ = m.length ? m[0] : f;
    return c.ctx && s(c.ctx[p], c.ctx[p] = _) && (!c.skip_bound && c.bound[p] && c.bound[p](_), h && cs(t, p)), f;
  }) : [], c.update(), h = !0, Ge(c.before_update), c.fragment = o ? o(c.ctx) : !1, e.target) {
    if (e.hydrate) {
      const p = ns(e.target);
      c.fragment && c.fragment.l(p), p.forEach(K);
    } else
      c.fragment && c.fragment.c();
    e.intro && M(t.$$.fragment), pe(t, e.target, e.anchor), An();
  }
  Ue(l);
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
    if (!$t(n))
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
      t[5], s || (r = dt(e, "click", function() {
        $t(
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
      i && K(e), s = !1, r();
    }
  };
}
function fs(t, e, n) {
  let {
    config: o,
    step: s
  } = e, r, i, a, l, c, h;
  function p(f) {
    return ue(f) ? f = f.call(s) : f;
  }
  return t.$$set = (f) => {
    "config" in f && n(6, o = f.config), "step" in f && n(7, s = f.step);
  }, t.$$.update = () => {
    t.$$.dirty & /*config, step*/
    192 && (n(0, r = o.action ? o.action.bind(s.tour) : null), n(1, i = o.classes), n(2, a = o.disabled ? p(o.disabled) : !1), n(3, l = o.label ? p(o.label) : null), n(4, c = o.secondary), n(5, h = o.text ? p(o.text) : null));
  }, [r, i, a, l, c, h, o, s];
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
        for (xe(), l = o.length; l < s.length; l += 1)
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
      i && K(e), Qo(s, i);
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
      2 && M(o, 1)) : (o = Kt(s), o.c(), M(o, 1), o.m(e, null)) : o && (xe(), L(o, 1, 1, () => {
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
      s && K(e), o && o.d();
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
      Q(i, e, a), Ne(e, n), s || (r = dt(
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
      i && K(e), s = !1, r();
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
class _s extends ie {
  constructor(e) {
    super(), re(this, e, bs, ys, se, {
      cancelIcon: 0,
      step: 2
    });
  }
}
function xs(t) {
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
      n && K(e), t[3](null);
    }
  };
}
function vs(t, e, n) {
  let {
    labelId: o,
    element: s,
    title: r
  } = e;
  Lt(() => {
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
    super(), re(this, e, vs, xs, se, {
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
  return e = new _s({
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
      e = te("header"), s && s.c(), n = it(), r && r.c(), $(e, "class", "shepherd-header");
    },
    m(i, a) {
      Q(i, e, a), s && s.m(e, null), Ne(e, n), r && r.m(e, null), o = !0;
    },
    p(i, [a]) {
      /*title*/
      i[2] ? s ? (s.p(i, a), a & /*title*/
      4 && M(s, 1)) : (s = Jt(i), s.c(), M(s, 1), s.m(e, n)) : s && (xe(), L(s, 1, 1, () => {
        s = null;
      }), ve()), /*cancelIcon*/
      i[3] && /*cancelIcon*/
      i[3].enabled ? r ? (r.p(i, a), a & /*cancelIcon*/
      8 && M(r, 1)) : (r = Gt(i), r.c(), M(r, 1), r.m(e, null)) : r && (xe(), L(r, 1, 1, () => {
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
      i && K(e), s && s.d(), r && r.d();
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
      n && K(e), t[3](null);
    }
  };
}
function As(t, e, n) {
  let {
    descriptionId: o,
    element: s,
    step: r
  } = e;
  Lt(() => {
    let {
      text: a
    } = r.options;
    ue(a) && (a = a.call(r)), Xe(a) ? s.appendChild(a) : n(0, s.innerHTML = a, s);
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
  t[2].options.buttons.length, a, l = n && Zt(t), c = s && Qt(t), h = i && en(t);
  return {
    c() {
      e = te("div"), l && l.c(), o = it(), c && c.c(), r = it(), h && h.c(), $(e, "class", "shepherd-content");
    },
    m(p, f) {
      Q(p, e, f), l && l.m(e, null), Ne(e, o), c && c.m(e, null), Ne(e, r), h && h.m(e, null), a = !0;
    },
    p(p, [f]) {
      f & /*step*/
      4 && (n = !H(
        /*step*/
        p[2].options.title
      ) || /*step*/
      p[2].options.cancelIcon && /*step*/
      p[2].options.cancelIcon.enabled), n ? l ? (l.p(p, f), f & /*step*/
      4 && M(l, 1)) : (l = Zt(p), l.c(), M(l, 1), l.m(e, o)) : l && (xe(), L(l, 1, 1, () => {
        l = null;
      }), ve()), f & /*step*/
      4 && (s = !H(
        /*step*/
        p[2].options.text
      )), s ? c ? (c.p(p, f), f & /*step*/
      4 && M(c, 1)) : (c = Qt(p), c.c(), M(c, 1), c.m(e, r)) : c && (xe(), L(c, 1, 1, () => {
        c = null;
      }), ve()), f & /*step*/
      4 && (i = Array.isArray(
        /*step*/
        p[2].options.buttons
      ) && /*step*/
      p[2].options.buttons.length), i ? h ? (h.p(p, f), f & /*step*/
      4 && M(h, 1)) : (h = en(p), h.c(), M(h, 1), h.m(e, null)) : h && (xe(), L(h, 1, 1, () => {
        h = null;
      }), ve());
    },
    i(p) {
      a || (M(l), M(c), M(h), a = !0);
    },
    o(p) {
      L(l), L(c), L(h), a = !1;
    },
    d(p) {
      p && K(e), l && l.d(), c && c.d(), h && h.d();
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
      n && K(e);
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
  let h = [
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
  for (let f = 0; f < h.length; f += 1)
    p = Go(p, h[f]);
  return {
    c() {
      e = te("div"), c && c.c(), n = it(), Se(o.$$.fragment), zt(e, p), Ce(
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
    m(f, m) {
      Q(f, e, m), c && c.m(e, null), Ne(e, n), pe(o, e, null), t[13](e), i = !0, a || (l = dt(
        e,
        "keydown",
        /*handleKeyDown*/
        t[7]
      ), a = !0);
    },
    p(f, [m]) {
      /*step*/
      f[4].options.arrow && /*step*/
      f[4].options.attachTo && /*step*/
      f[4].options.attachTo.element && /*step*/
      f[4].options.attachTo.on ? c || (c = tn(), c.c(), c.m(e, n)) : c && (c.d(1), c = null);
      const _ = {};
      m & /*descriptionId*/
      4 && (_.descriptionId = /*descriptionId*/
      f[2]), m & /*labelId*/
      8 && (_.labelId = /*labelId*/
      f[3]), m & /*step*/
      16 && (_.step = /*step*/
      f[4]), o.$set(_), zt(e, p = ls(h, [(!i || m & /*step, descriptionId*/
      20 && s !== (s = H(
        /*step*/
        f[4].options.text
      ) ? null : (
        /*descriptionId*/
        f[2]
      ))) && {
        "aria-describedby": s
      }, (!i || m & /*step, labelId*/
      24 && r !== (r = /*step*/
      f[4].options.title ? (
        /*labelId*/
        f[3]
      ) : null)) && {
        "aria-labelledby": r
      }, m & /*dataStepId*/
      2 && /*dataStepId*/
      f[1], {
        role: "dialog"
      }, {
        tabindex: "0"
      }])), Ce(
        e,
        "shepherd-has-cancel-icon",
        /*hasCancelIcon*/
        f[5]
      ), Ce(
        e,
        "shepherd-has-title",
        /*hasTitle*/
        f[6]
      ), Ce(e, "shepherd-element", !0);
    },
    i(f) {
      i || (M(o.$$.fragment, f), i = !0);
    },
    o(f) {
      L(o.$$.fragment, f), i = !1;
    },
    d(f) {
      f && K(e), c && c.d(), ge(o), t[13](null), a = !1, l();
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
    step: h,
    dataStepId: p
  } = e, f, m, _;
  const S = () => s;
  os(() => {
    n(1, p = {
      [`data-${o}shepherd-step-id`]: h.id
    }), n(9, a = s.querySelectorAll('a[href], area[href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), button:not([disabled]), [tabindex="0"]')), n(8, i = a[0]), n(10, c = a[a.length - 1]);
  }), Lt(() => {
    _ !== h.options.classes && k();
  });
  function k() {
    y(_), _ = h.options.classes, O(_);
  }
  function y(g) {
    if (qe(g)) {
      const A = nn(g);
      A.length && s.classList.remove(...A);
    }
  }
  function O(g) {
    if (qe(g)) {
      const A = nn(g);
      A.length && s.classList.add(...A);
    }
  }
  const b = (g) => {
    const {
      tour: A
    } = h;
    switch (g.keyCode) {
      case $s:
        if (a.length === 0) {
          g.preventDefault();
          break;
        }
        g.shiftKey ? (document.activeElement === i || document.activeElement.classList.contains("shepherd-element")) && (g.preventDefault(), c.focus()) : document.activeElement === c && (g.preventDefault(), i.focus());
        break;
      case Ls:
        A.options.exitOnEsc && (g.preventDefault(), g.stopPropagation(), h.cancel());
        break;
      case Ps:
        A.options.keyboardNavigation && (g.preventDefault(), g.stopPropagation(), A.back());
        break;
      case Fs:
        A.options.keyboardNavigation && (g.preventDefault(), g.stopPropagation(), A.next());
        break;
    }
  };
  function x(g) {
    He[g ? "unshift" : "push"](() => {
      s = g, n(0, s);
    });
  }
  return t.$$set = (g) => {
    "classPrefix" in g && n(11, o = g.classPrefix), "element" in g && n(0, s = g.element), "descriptionId" in g && n(2, r = g.descriptionId), "firstFocusableElement" in g && n(8, i = g.firstFocusableElement), "focusableElements" in g && n(9, a = g.focusableElements), "labelId" in g && n(3, l = g.labelId), "lastFocusableElement" in g && n(10, c = g.lastFocusableElement), "step" in g && n(4, h = g.step), "dataStepId" in g && n(1, p = g.dataStepId);
  }, t.$$.update = () => {
    t.$$.dirty & /*step*/
    16 && (n(5, f = h.options && h.options.cancelIcon && h.options.cancelIcon.enabled), n(6, m = h.options && h.options.title));
  }, [s, p, r, l, h, f, m, b, i, a, c, o, S, x];
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
class wt extends St {
  constructor(e, n = {}) {
    return super(), this._resolvedAttachTo = void 0, this.classPrefix = void 0, this.el = void 0, this.target = void 0, this.tour = void 0, this.tour = e, this.classPrefix = this.tour.options ? fn(this.tour.options.classPrefix) : "", this.styles = e.styles, this._resolvedAttachTo = null, Et(this), this._setOptions(n), this;
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
    Wo(this), Xe(this.el) && (this.el.remove(), this.el = null), this._updateStepTargetOnHide(), this.trigger("destroy");
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
    n = Ot({}, n || {}), this.options = Object.assign({
      arrow: !0
    }, n, e, zo(n, e));
    const {
      when: o
    } = this.options;
    this.options.classes = this._getClassOptions(e), this.destroy(), this.id = this.options.id || `step-${pn()}`, o && Object.keys(o).forEach((s) => {
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
      n.options && n.options.canClickTarget === !1 && n.options.attachTo && Xe(n.target) && n.target.classList.remove("shepherd-target-click-disabled");
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
    bottomLeft: h = 0
  } = typeof s == "number" ? {
    topLeft: s,
    topRight: s,
    bottomRight: s,
    bottomLeft: s
  } : s;
  return `M${r},${i}H0V0H${r}V${i}ZM${n + a},${o}a${a},${a},0,0,0-${a},${a}V${e + o - h}a${h},${h},0,0,0,${h},${h}H${t + n - c}a${c},${c},0,0,0,${c}-${c}V${o + l}a${l},${l},0,0,0-${l}-${l}Z`;
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
      Q(i, e, a), Ne(e, n), t[11](e), s || (r = dt(
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
      i && K(e), t[11](null), s = !1, r();
    }
  };
}
function Cn(t) {
  if (!t)
    return null;
  const n = t instanceof HTMLElement && window.getComputedStyle(t).overflowY;
  return n !== "hidden" && n !== "visible" && t.scrollHeight >= t.clientHeight ? t : Cn(t.parentElement);
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
  function h() {
    n(1, r = !1), y();
  }
  function p(x = 0, g = 0, A = 0, F = 0, X, I) {
    if (I) {
      const {
        y: C,
        height: D
      } = Us(I, X), {
        x: E,
        width: W,
        left: q
      } = I.getBoundingClientRect();
      n(4, s = {
        width: W + x * 2,
        height: D + x * 2,
        x: (E || q) + A - x,
        y: C + F - x,
        r: g
      });
    } else
      c();
  }
  function f(x) {
    y(), x.tour.options.useModalOverlay ? (O(x), m()) : h();
  }
  function m() {
    n(1, r = !0);
  }
  const _ = (x) => {
    x.preventDefault();
  }, S = (x) => {
    x.stopPropagation();
  };
  function k() {
    window.addEventListener("touchmove", _, {
      passive: !1
    });
  }
  function y() {
    i && (cancelAnimationFrame(i), i = void 0), window.removeEventListener("touchmove", _, {
      passive: !1
    });
  }
  function O(x) {
    const {
      modalOverlayOpeningPadding: g,
      modalOverlayOpeningRadius: A,
      modalOverlayOpeningXOffset: F = 0,
      modalOverlayOpeningYOffset: X = 0
    } = x.options, I = Vs(x.target), C = Cn(x.target), D = () => {
      i = void 0, p(g, A, F + I.left, X + I.top, C, x.target), i = requestAnimationFrame(D);
    };
    D(), k();
  }
  function b(x) {
    He[x ? "unshift" : "push"](() => {
      o = x, n(0, o);
    });
  }
  return t.$$set = (x) => {
    "element" in x && n(0, o = x.element), "openingProperties" in x && n(4, s = x.openingProperties);
  }, t.$$.update = () => {
    t.$$.dirty & /*openingProperties*/
    16 && n(2, a = Bs(s));
  }, [o, r, a, S, s, l, c, h, p, f, m, b];
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
class qs extends St {
  constructor() {
    super(), this.activeTour = void 0, Et(this);
  }
}
class Ys extends St {
  constructor(e = {}) {
    super(), this.trackedEvents = ["active", "cancel", "complete", "show"], this.classPrefix = void 0, this.currentStep = void 0, this.focusedElBeforeOpen = void 0, this.id = void 0, this.modal = void 0, this.options = void 0, this.steps = void 0, Et(this);
    const n = {
      exitOnEsc: !0,
      keyboardNavigation: !0
    };
    return this.options = Object.assign({}, n, e), this.classPrefix = fn(this.options.classPrefix), this.steps = [], this.addSteps(this.options.steps), ["active", "cancel", "complete", "inactive", "show", "start"].map((s) => {
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
    return o instanceof wt ? o.tour = this : o = new wt(this, o), H(n) ? this.steps.push(o) : this.steps.splice(n, 0, o), o;
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
    const o = qe(e) ? this.getById(e) : this.steps[e];
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
    Xe(this.focusedElBeforeOpen) && this.focusedElBeforeOpen.focus();
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
    const n = this.options.tourName || "tour", o = e || pn();
    this.id = `${n}--${o}`;
  }
}
const be = new qs(), Tn = typeof window > "u";
be.Step = Tn ? no : wt;
be.Tour = Tn ? oo : Ys;
const ze = P(!1), We = P(!1);
let Qe = null;
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
            at(), this.complete();
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
        <p style="color:#6b7280;font-size:14px;">${u("Define the rooms in your property — kitchen, bathroom, bedroom, garage. Rooms help organise appliances and maintenance records.")}</p>
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
      id: "add-maintenance",
      text: ce(4, 6) + `
        <h3 style="font-size:16px;font-weight:600;margin-bottom:4px;">${u("Set your first reminder")}</h3>
        <p style="color:#6b7280;font-size:14px;">${u("Add a maintenance task — boiler service, gutter cleaning, smoke alarm check. Home will remind you when it's due.")}</p>
      `,
      attachTo: { element: '[data-tour="add-maintenance"]', on: "bottom" },
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
          <p style="color:#6b7280;">${u("Home will remind you when maintenance is due, when warranties are expiring, and keep everything about your property in one place.")}</p>
          <p style="color:#9ca3af;font-size:13px;margin-top:8px;">${u("You can restart this tour anytime from Settings.")}</p>
        </div>
      `,
      buttons: [
        {
          text: u("Go to dashboard") + " →",
          action: function() {
            at(), this.complete();
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
          at(), this.complete();
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
        <p style="color:#6b7280;font-size:14px;">${u("You can view the property details, items, maintenance history, and emergency contacts.")}</p>
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
            at(), this.complete();
          },
          classes: "shepherd-button-primary"
        }
      ]
    }
  ];
}
let Ie = null;
async function at() {
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
    ze.value = !1, We.value = !0, document.removeEventListener("keydown", n);
  }), e.on("complete", () => {
    ze.value = !1, We.value = !0, document.removeEventListener("keydown", n);
  }), e;
}
function Js() {
  async function t() {
    if (!(We.value || ze.value))
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
          Qe = on(Ks());
        else if (i === "invited_member" || i === "owner_setup" && r.household_has_properties) {
          const a = r.owner_display_name || "";
          Qe = on(Xs(a));
        } else
          return;
        setTimeout(() => {
          Qe && !We.value && (ze.value = !0, Qe.start());
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
        }), We.value = !1, await t();
      } catch {
      }
  }
  return { tourActive: ze, initTour: t, restartTour: e };
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
}, er = { class: "text-h3 text-gray-800 dark:text-gray-200 mb-4" }, tr = { class: "mb-4" }, nr = { class: "text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2" }, or = { class: "grid grid-cols-1 sm:grid-cols-2 gap-3" }, sr = { class: "text-caption text-gray-500 dark:text-gray-400 block mb-1" }, rr = { class: "flex items-center gap-2" }, ir = { class: "text-sm text-gray-500 dark:text-gray-400" }, ar = { class: "text-caption text-gray-500 dark:text-gray-400 block mb-1" }, lr = { class: "flex items-center gap-2" }, cr = { class: "text-sm text-gray-500 dark:text-gray-400" }, ur = { class: "mb-4" }, dr = { class: "text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2" }, fr = { class: "grid grid-cols-1 sm:grid-cols-3 gap-3" }, hr = { class: "text-caption text-gray-500 dark:text-gray-400 block mb-1" }, pr = { class: "flex items-center gap-2" }, gr = { class: "text-sm text-gray-500 dark:text-gray-400" }, mr = { class: "text-caption text-gray-500 dark:text-gray-400 block mb-1" }, yr = { class: "flex items-center gap-2" }, br = { class: "text-sm text-gray-500 dark:text-gray-400" }, _r = { class: "text-caption text-gray-500 dark:text-gray-400 block mb-1" }, xr = { class: "flex items-center gap-2" }, vr = { class: "text-sm text-gray-500 dark:text-gray-400" }, wr = { class: "grid grid-cols-1 sm:grid-cols-2 gap-3" }, kr = { class: "text-caption text-gray-500 dark:text-gray-400 block mb-1" }, Sr = { class: "flex items-center gap-2" }, Or = { class: "text-sm text-gray-500 dark:text-gray-400" }, Er = { class: "text-caption text-gray-500 dark:text-gray-400 block mb-1" }, Ar = { class: "flex items-center gap-2" }, Cr = { class: "text-sm text-gray-500 dark:text-gray-400" }, Tr = {
  key: 1,
  class: "mb-8 p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
}, Rr = { class: "text-h3 text-gray-800 dark:text-gray-200 mb-4" }, Ir = { class: "text-sm text-gray-500 dark:text-gray-400 mb-3" }, Mr = { class: "overflow-x-auto" }, $r = { class: "w-full text-sm" }, Lr = { class: "text-left text-caption text-gray-500 dark:text-gray-400 border-b border-gray-200 dark:border-gray-700" }, Pr = { class: "py-2 pr-4" }, Fr = { class: "py-2 pr-4 w-28" }, Dr = { class: "py-2 w-36" }, Nr = { class: "py-2 pr-4 text-gray-700 dark:text-gray-300" }, Hr = { class: "py-2 pr-4" }, Br = ["onUpdate:modelValue"], jr = { class: "py-2" }, Vr = { class: "relative" }, Ur = ["onUpdate:modelValue"], zr = {
  key: 2,
  class: "mb-8 p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
}, Wr = { class: "text-h3 text-gray-800 dark:text-gray-200 mb-4" }, qr = { class: "grid grid-cols-1 sm:grid-cols-2 gap-4" }, Yr = { class: "text-caption text-gray-500 dark:text-gray-400 block mb-1" }, Kr = { class: "text-caption text-gray-500 dark:text-gray-400 block mb-1" }, Xr = ["value"], Jr = { class: "text-xs text-gray-400 dark:text-gray-500 mt-1" }, Gr = {
  key: 3,
  class: "mb-8 p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
}, Zr = { class: "text-h3 text-gray-800 dark:text-gray-200 mb-2" }, Qr = { class: "text-sm text-gray-500 dark:text-gray-400 mb-3" }, ei = { class: "flex items-center gap-3" }, ti = {
  key: 0,
  class: "text-sm text-green-600 dark:text-green-400"
}, ni = {
  key: 1,
  class: "text-sm text-red-600 dark:text-red-400"
}, oi = /* @__PURE__ */ kt({
  __name: "HomeSettingsPanel",
  props: {
    household: {},
    section: {}
  },
  setup(t) {
    const e = t, n = ne(() => !e.section || e.section === "alerts"), o = ne(() => !e.section || e.section === "lifespans"), s = ne(() => !e.section || e.section === "preferences"), r = P(null), i = P(!0), a = P(""), l = P(!1), c = P(!1), { restartTour: h } = Js(), p = P(!1), f = [
      { value: "Owner and Adult", label: u("Owner and Adult") },
      { value: "Owner only", label: u("Owner only") }
    ];
    async function m() {
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
    async function _() {
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
                maintenance_reminder_days: r.value.maintenance_reminder_days,
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
      p.value = !0, await h(), p.value = !1;
    }
    return sn(m), (k, y) => {
      const O = rn("Button");
      return i.value ? (T(), R("div", Gs, v(w(u)("Loading settings…")), 1)) : a.value && !r.value ? (T(), R("div", Zs, v(a.value), 1)) : r.value ? (T(), R(me, { key: 2 }, [
        n.value ? (T(), R("section", Qs, [
          d("h2", er, v(w(u)("Alerts")), 1),
          d("div", tr, [
            d("h3", nr, v(w(u)("Warranty expiry alerts")), 1),
            d("div", or, [
              d("div", null, [
                d("label", sr, v(w(u)("First alert")), 1),
                d("div", rr, [
                  j(d("input", {
                    "onUpdate:modelValue": y[0] || (y[0] = (b) => r.value.warranty_alert_days_first = b),
                    type: "number",
                    min: "1",
                    max: "365",
                    class: "w-20 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  }, null, 512), [
                    [
                      Y,
                      r.value.warranty_alert_days_first,
                      void 0,
                      { number: !0 }
                    ]
                  ]),
                  d("span", ir, v(w(u)("days before")), 1)
                ])
              ]),
              d("div", null, [
                d("label", ar, v(w(u)("Second alert")), 1),
                d("div", lr, [
                  j(d("input", {
                    "onUpdate:modelValue": y[1] || (y[1] = (b) => r.value.warranty_alert_days_second = b),
                    type: "number",
                    min: "1",
                    max: "365",
                    class: "w-20 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  }, null, 512), [
                    [
                      Y,
                      r.value.warranty_alert_days_second,
                      void 0,
                      { number: !0 }
                    ]
                  ]),
                  d("span", cr, v(w(u)("days before")), 1)
                ])
              ])
            ])
          ]),
          d("div", ur, [
            d("h3", dr, v(w(u)("Legal warranty (Gewährleistung)")), 1),
            d("div", fr, [
              d("div", null, [
                d("label", hr, v(w(u)("Warranty duration")), 1),
                d("div", pr, [
                  j(d("input", {
                    "onUpdate:modelValue": y[2] || (y[2] = (b) => r.value.legal_warranty_months = b),
                    type: "number",
                    min: "1",
                    max: "120",
                    class: "w-20 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  }, null, 512), [
                    [
                      Y,
                      r.value.legal_warranty_months,
                      void 0,
                      { number: !0 }
                    ]
                  ]),
                  d("span", gr, v(w(u)("months")), 1)
                ])
              ]),
              d("div", null, [
                d("label", mr, v(w(u)("Burden of proof period")), 1),
                d("div", yr, [
                  j(d("input", {
                    "onUpdate:modelValue": y[3] || (y[3] = (b) => r.value.burden_of_proof_months = b),
                    type: "number",
                    min: "1",
                    max: "120",
                    class: "w-20 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  }, null, 512), [
                    [
                      Y,
                      r.value.burden_of_proof_months,
                      void 0,
                      { number: !0 }
                    ]
                  ]),
                  d("span", br, v(w(u)("months")), 1)
                ])
              ]),
              d("div", null, [
                d("label", _r, v(w(u)("Alert before proof shift")), 1),
                d("div", xr, [
                  j(d("input", {
                    "onUpdate:modelValue": y[4] || (y[4] = (b) => r.value.burden_of_proof_alert_days = b),
                    type: "number",
                    min: "1",
                    max: "365",
                    class: "w-20 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  }, null, 512), [
                    [
                      Y,
                      r.value.burden_of_proof_alert_days,
                      void 0,
                      { number: !0 }
                    ]
                  ]),
                  d("span", vr, v(w(u)("days")), 1)
                ])
              ])
            ])
          ]),
          d("div", wr, [
            d("div", null, [
              d("label", kr, v(w(u)("Maintenance reminder")), 1),
              d("div", Sr, [
                j(d("input", {
                  "onUpdate:modelValue": y[5] || (y[5] = (b) => r.value.maintenance_reminder_days = b),
                  type: "number",
                  min: "1",
                  max: "30",
                  class: "w-20 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                }, null, 512), [
                  [
                    Y,
                    r.value.maintenance_reminder_days,
                    void 0,
                    { number: !0 }
                  ]
                ]),
                d("span", Or, v(w(u)("days before due date")), 1)
              ])
            ]),
            d("div", null, [
              d("label", Er, v(w(u)("Overdue refund re-alert")), 1),
              d("div", Ar, [
                j(d("input", {
                  "onUpdate:modelValue": y[6] || (y[6] = (b) => r.value.refund_alert_days = b),
                  type: "number",
                  min: "1",
                  max: "90",
                  class: "w-20 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                }, null, 512), [
                  [
                    Y,
                    r.value.refund_alert_days,
                    void 0,
                    { number: !0 }
                  ]
                ]),
                d("span", Cr, v(w(u)("days after return")), 1)
              ])
            ])
          ])
        ])) : N("", !0),
        o.value ? (T(), R("section", Tr, [
          d("h2", Rr, v(w(u)("Item Lifespans")), 1),
          d("p", Ir, v(w(u)("Default lifespan and average replacement cost per item category. Used for health forecasts and replacement planning.")), 1),
          d("div", Mr, [
            d("table", $r, [
              d("thead", null, [
                d("tr", Lr, [
                  d("th", Pr, v(w(u)("Category")), 1),
                  d("th", Fr, v(w(u)("Lifespan (yr)")), 1),
                  d("th", Dr, v(w(u)("Avg replacement cost")), 1)
                ])
              ]),
              d("tbody", null, [
                (T(!0), R(me, null, yt(r.value.category_lifespans, (b, x) => (T(), R("tr", {
                  key: x,
                  class: "border-b border-gray-100 dark:border-gray-700/50"
                }, [
                  d("td", Nr, v(w(u)(b.category)), 1),
                  d("td", Hr, [
                    j(d("input", {
                      "onUpdate:modelValue": (g) => b.lifespan_years = g,
                      type: "number",
                      min: "1",
                      max: "100",
                      class: "w-20 border border-gray-300 dark:border-gray-600 rounded px-2 py-1 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                    }, null, 8, Br), [
                      [
                        Y,
                        b.lifespan_years,
                        void 0,
                        { number: !0 }
                      ]
                    ])
                  ]),
                  d("td", jr, [
                    d("div", Vr, [
                      y[9] || (y[9] = d("span", { class: "absolute left-2 top-1/2 -translate-y-1/2 text-xs text-gray-400" }, "€", -1)),
                      j(d("input", {
                        "onUpdate:modelValue": (g) => b.avg_replacement_cost = g,
                        type: "number",
                        min: "0",
                        step: "50",
                        class: "w-28 border border-gray-300 dark:border-gray-600 rounded px-2 py-1 pl-6 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                      }, null, 8, Ur), [
                        [
                          Y,
                          b.avg_replacement_cost,
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
        s.value ? (T(), R("section", zr, [
          d("h2", Wr, v(w(u)("Preferences")), 1),
          d("div", qr, [
            d("div", null, [
              d("label", Yr, v(w(u)("Default currency")), 1),
              j(d("input", {
                "onUpdate:modelValue": y[7] || (y[7] = (b) => r.value.default_currency = b),
                type: "text",
                maxlength: "3",
                class: "w-24 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 uppercase"
              }, null, 512), [
                [Y, r.value.default_currency]
              ])
            ]),
            d("div", null, [
              d("label", Kr, v(w(u)("Cost data visible to")), 1),
              j(d("select", {
                "onUpdate:modelValue": y[8] || (y[8] = (b) => r.value.financial_visibility = b),
                class: "w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              }, [
                (T(), R(me, null, yt(f, (b) => d("option", {
                  key: b.value,
                  value: b.value
                }, v(b.label), 9, Xr)), 64))
              ], 512), [
                [an, r.value.financial_visibility]
              ]),
              d("p", Jr, v(w(u)("Controls who can see purchase prices, maintenance costs, and budget data. Children never see financial data.")), 1)
            ])
          ])
        ])) : N("", !0),
        s.value ? (T(), R("section", Gr, [
          d("h2", Zr, v(w(u)("Account")), 1),
          d("p", Qr, v(w(u)("Restart the guided onboarding tour to walk through the main features.")), 1),
          Ve(O, {
            variant: "outline",
            loading: p.value,
            onClick: S
          }, {
            default: tt(() => [
              nt(v(w(u)("Reset onboarding tour")), 1)
            ]),
            _: 1
          }, 8, ["loading"])
        ])) : N("", !0),
        d("div", ei, [
          Ve(O, {
            variant: "solid",
            loading: l.value,
            onClick: _
          }, {
            default: tt(() => [
              nt(v(w(u)("Save settings")), 1)
            ]),
            _: 1
          }, 8, ["loading"]),
          c.value ? (T(), R("span", ti, v(w(u)("Saved")), 1)) : N("", !0),
          a.value ? (T(), R("span", ni, v(a.value), 1)) : N("", !0)
        ])
      ], 64)) : N("", !0);
    };
  }
}), si = {
  key: 0,
  class: "text-gray-500"
}, ri = {
  key: 1,
  class: "text-center py-16"
}, ii = { class: "text-h3 text-gray-800 dark:text-gray-200 mb-2" }, ai = { class: "text-body text-gray-500 dark:text-gray-400 mb-6" }, li = { class: "max-w-sm mx-auto flex flex-col gap-3" }, ci = ["placeholder"], ui = {
  key: 0,
  class: "text-sm text-red-600 dark:text-red-400"
}, di = {
  key: 2,
  class: "text-red-600 dark:text-red-400"
}, fi = { class: "mb-8" }, hi = { class: "text-h3 text-gray-800 dark:text-gray-200 mb-4" }, pi = { class: "space-y-3" }, gi = { class: "flex-1 min-w-0" }, mi = { class: "flex items-center gap-2" }, yi = { class: "font-medium text-gray-900 dark:text-gray-100 truncate" }, bi = {
  key: 0,
  class: "text-xs px-2 py-0.5 rounded-full bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300"
}, _i = {
  key: 1,
  class: "text-xs text-gray-400"
}, xi = { class: "text-caption text-gray-500 dark:text-gray-400" }, vi = { class: "flex items-center gap-2" }, wi = ["value", "onChange"], ki = ["onClick"], Si = { class: "flex items-center gap-1" }, Oi = ["onClick", "title"], Ei = {
  key: 0,
  class: "p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
}, Ai = { class: "text-h4 text-gray-800 dark:text-gray-200 mb-3" }, Ci = { class: "flex gap-3 items-end flex-wrap" }, Ti = { class: "flex-1 min-w-[200px]" }, Ri = { class: "text-caption text-gray-500 dark:text-gray-400 block mb-1" }, Ii = ["placeholder"], Mi = { class: "text-caption text-gray-500 dark:text-gray-400 block mb-1" }, $i = { value: "Adult" }, Li = { value: "Child" }, Pi = {
  key: 0,
  class: "mt-2 text-sm text-gray-600 dark:text-gray-400"
}, Fi = {
  key: 2,
  class: "text-center py-12"
}, Di = { class: "text-sm text-gray-500 dark:text-gray-400" }, Hi = /* @__PURE__ */ kt({
  __name: "HomeSettings",
  props: {
    section: {}
  },
  setup(t) {
    const e = t, n = window.frappe?.session?.user || "", o = P(""), s = P([]), r = P(!0), i = P(""), a = P(!1), l = P(""), c = P(!1), h = P(""), p = P("Adult"), f = P(!1), m = P(""), _ = P(null), S = ne(
      () => s.value.find((I) => I.user === n)
    ), k = ne(() => S.value?.role === "Owner"), y = ne(() => e.section || "household");
    async function O() {
      r.value = !0, i.value = "";
      try {
        const C = await V({
          url: "/api/method/home.api.permission.get_user_households"
        }) || [];
        if (!C.length) {
          a.value = !0, r.value = !1;
          return;
        }
        o.value = C[0], await b();
      } catch (I) {
        i.value = I.message || u("Failed to load household");
      } finally {
        r.value = !1;
      }
    }
    async function b() {
      const I = await V({
        url: "/api/method/home.api.household.get_members",
        params: { household: o.value }
      });
      s.value = I || [];
    }
    async function x() {
      if (h.value.trim()) {
        f.value = !0, m.value = "";
        try {
          const C = await V({
            url: "/api/method/home.api.household.invite_member",
            params: {
              household: o.value,
              email: h.value.trim(),
              role: p.value
            }
          });
          m.value = C.user_exists ? u("Member added successfully") : u("Invitation sent — they will appear once they register"), h.value = "", await b();
        } catch (I) {
          m.value = I.message || u("Failed to invite member");
        } finally {
          f.value = !1;
        }
      }
    }
    async function g(I) {
      try {
        await V({
          url: "/api/method/home.api.household.remove_member",
          params: { household: o.value, member_name: I }
        }), await b();
      } catch (C) {
        alert(C.message || u("Failed to remove member"));
      }
    }
    async function A(I, C) {
      try {
        await V({
          url: "/api/method/home.api.household.change_member_role",
          params: { household: o.value, member_name: I, new_role: C }
        }), _.value = null, await b();
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
    async function X() {
      c.value = !0, i.value = "";
      try {
        await V({
          url: "/api/method/home.api.household.create_household",
          params: { household_name: l.value.trim() }
        }), a.value = !1, l.value = "", await O();
      } catch (I) {
        i.value = I.message || u("Failed to create household");
      } finally {
        c.value = !1;
      }
    }
    return sn(O), (I, C) => {
      const D = rn("Button");
      return T(), R("div", null, [
        r.value ? (T(), R("div", si, v(w(u)("Loading…")), 1)) : a.value ? (T(), R("div", ri, [
          C[4] || (C[4] = d("div", { class: "text-6xl mb-4" }, "🏠", -1)),
          d("h2", ii, v(w(u)("Welcome to Home")), 1),
          d("p", ai, v(w(u)("Create your household to get started.")), 1),
          d("div", li, [
            j(d("input", {
              "onUpdate:modelValue": C[0] || (C[0] = (E) => l.value = E),
              type: "text",
              placeholder: w(u)("My Home"),
              class: "w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100",
              onKeyup: Pt(X, ["enter"])
            }, null, 40, ci), [
              [Y, l.value]
            ]),
            Ve(D, {
              variant: "solid",
              loading: c.value,
              onClick: X
            }, {
              default: tt(() => [
                nt(v(w(u)("Create Household")), 1)
              ]),
              _: 1
            }, 8, ["loading"]),
            i.value ? (T(), R("p", ui, v(i.value), 1)) : N("", !0)
          ])
        ])) : i.value ? (T(), R("div", di, v(i.value), 1)) : (T(), R(me, { key: 3 }, [
          y.value === "household" ? (T(), R(me, { key: 0 }, [
            d("section", fi, [
              d("h2", hi, v(w(u)("Members")), 1),
              d("div", pi, [
                (T(!0), R(me, null, yt(s.value, (E) => (T(), R("div", {
                  key: E.name,
                  class: "flex items-center gap-3 p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
                }, [
                  Ve(Nn, {
                    "display-name": E.display_name,
                    avatar: E.avatar,
                    size: "md"
                  }, null, 8, ["display-name", "avatar"]),
                  d("div", gi, [
                    d("div", mi, [
                      d("span", yi, v(E.display_name), 1),
                      E.pending ? (T(), R("span", bi, v(w(u)("Pending")), 1)) : N("", !0),
                      E.user === w(n) ? (T(), R("span", _i, v(w(u)("(you)")), 1)) : N("", !0)
                    ]),
                    d("div", xi, v(E.email || E.user || w(u)("No account")), 1)
                  ]),
                  d("div", vi, [
                    k.value && _.value === E.name ? (T(), R(me, { key: 0 }, [
                      d("select", {
                        value: E.role,
                        onChange: (W) => A(E.name, W.target.value),
                        class: "text-sm border border-gray-300 dark:border-gray-600 rounded px-2 py-1 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                      }, [...C[5] || (C[5] = [
                        d("option", { value: "Owner" }, "Owner", -1),
                        d("option", { value: "Adult" }, "Adult", -1),
                        d("option", { value: "Child" }, "Child", -1)
                      ])], 40, wi),
                      d("button", {
                        onClick: C[1] || (C[1] = (W) => _.value = null),
                        class: "text-xs text-gray-400 hover:text-gray-600"
                      }, v(w(u)("Cancel")), 1)
                    ], 64)) : (T(), R("span", {
                      key: 1,
                      class: mt(["text-xs px-2 py-0.5 rounded-full font-medium", F(E.role)]),
                      onClick: (W) => k.value && E.user !== w(n) ? _.value = E.name : null,
                      style: In(k.value && E.user !== w(n) ? "cursor: pointer" : "")
                    }, v(E.role), 15, ki))
                  ]),
                  d("div", Si, [
                    k.value && E.user !== w(n) ? (T(), R("button", {
                      key: 0,
                      onClick: (W) => g(E.name),
                      class: "text-xs text-red-400 hover:text-red-600 px-2 py-1",
                      title: w(u)("Remove member")
                    }, v(w(u)("Remove")), 9, Oi)) : N("", !0)
                  ])
                ]))), 128))
              ])
            ]),
            k.value ? (T(), R("section", Ei, [
              d("h3", Ai, v(w(u)("Invite Member")), 1),
              d("div", Ci, [
                d("div", Ti, [
                  d("label", Ri, v(w(u)("Email")), 1),
                  j(d("input", {
                    "onUpdate:modelValue": C[2] || (C[2] = (E) => h.value = E),
                    type: "email",
                    placeholder: w(u)("person@example.com"),
                    class: "w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100",
                    onKeyup: Pt(x, ["enter"])
                  }, null, 40, Ii), [
                    [Y, h.value]
                  ])
                ]),
                d("div", null, [
                  d("label", Mi, v(w(u)("Role")), 1),
                  j(d("select", {
                    "onUpdate:modelValue": C[3] || (C[3] = (E) => p.value = E),
                    class: "border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  }, [
                    d("option", $i, v(w(u)("Adult")), 1),
                    d("option", Li, v(w(u)("Child")), 1)
                  ], 512), [
                    [an, p.value]
                  ])
                ]),
                Ve(D, {
                  onClick: x,
                  variant: "solid",
                  loading: f.value
                }, {
                  default: tt(() => [
                    nt(v(w(u)("Send Invite")), 1)
                  ]),
                  _: 1
                }, 8, ["loading"])
              ]),
              m.value ? (T(), R("p", Pi, v(m.value), 1)) : N("", !0)
            ])) : N("", !0)
          ], 64)) : N("", !0),
          k.value && (y.value === "alerts" || y.value === "lifespans" || y.value === "preferences") ? (T(), Mn(oi, {
            key: 1,
            household: o.value,
            section: y.value
          }, null, 8, ["household", "section"])) : N("", !0),
          !k.value && y.value !== "household" ? (T(), R("div", Fi, [
            d("p", Di, v(w(u)("Only the household owner can manage these settings.")), 1)
          ])) : N("", !0)
        ], 64))
      ]);
    };
  }
});
export {
  Hi as HomeSettings
};
