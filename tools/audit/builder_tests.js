// Clinical-logic tests for the interactive builders in src/app.js.
// No Node on this machine: build (python3 build.py), open dist/index.html in a
// browser, and paste this file into the console. Returns { tests, failures }.
// Expected values come from the cited staging/risk sources, not from app.js.
(() => {
  const fails = []; let n = 0;
  const eq = (name, got, exp) => { n++; if (got !== exp) fails.push(`${name}: got ${got}, expected ${exp}`); };

  // Lung: IASLC/AJCC 9th edition stage groups (Rami-Porta, J Thorac Oncol 2024; PMID 38447919)
  const exp9 = {
    N0: { T1a: "IA1", T1b: "IA2", T1c: "IA3", T2a: "IB", T2b: "IIA", T3: "IIB", T4: "IIIA" },
    N1: { T1: "IIA", T2: "IIB", T3: "IIIA", T4: "IIIA" },
    N2a: { T1: "IIB", T2: "IIIA", T3: "IIIA", T4: "IIIB" },
    N2b: { T1: "IIIA", T2: "IIIB", T3: "IIIB", T4: "IIIB" },
    N3: { T1: "IIIB", T2: "IIIB", T3: "IIIC", T4: "IIIC" },
  };
  for (const t of ["T1mi", "T1a", "T1b", "T1c", "T2a", "T2b", "T3", "T4"]) for (const nn of ["N0", "N1", "N2a", "N2b", "N3"]) {
    const tg = t.startsWith("T1") ? "T1" : t.startsWith("T2") ? "T2" : t;
    eq(`lung ${t}${nn}M0`, lungStageGroup(t, nn, "M0"), nn === "N0" ? (t === "T1mi" ? "IA1" : exp9.N0[t]) : exp9[nn][tg]);
    for (const m of ["M1a", "M1b"]) eq(`lung ${t}${nn}${m}`, lungStageGroup(t, nn, m), "IVA");
    for (const m of ["M1c1", "M1c2"]) eq(`lung ${t}${nn}${m}`, lungStageGroup(t, nn, m), "IVB");
  }

  // Lung N-stage drill (IASLC map, Rusch 2009; PMID 19357537)
  eq("N station 7", nStageFor("L", { st: "7", side: "mid", kind: "med" }).n, "N2");
  eq("N station 5, right tumor", nStageFor("R", { st: "5", side: "L", kind: "med" }).n, "N3");
  eq("N station 10, same side", nStageFor("R", { st: "10R", side: "R", kind: "hilar" }).n, "N1");
  eq("N station 1", nStageFor("R", { st: "1L", side: "L", kind: "scv" }).n, "N3");

  // Gleason -> ISUP Grade Group
  [[3,3,1],[3,4,2],[4,3,3],[4,4,4],[3,5,4],[5,3,4],[4,5,5],[5,4,5],[5,5,5]].forEach(([p, s, g]) => eq(`GG ${p}+${s}`, gleasonGG(p, s), g));

  // NCCN prostate risk groups
  const base = { t: "T1c", gg: 1, psa: "<10", cores50: false, psad: false, primary5: false, cores4: false };
  const R = (o) => prostateRisk({ ...base, ...o });
  eq("very low", R({ psad: true }), "Very low"); eq("low T2a", R({ t: "T2a" }), "Low");
  eq("FIR GG2", R({ gg: 2 }), "Favorable intermediate"); eq("UIR GG2 >=50% cores", R({ gg: 2, cores50: true }), "Unfavorable intermediate");
  eq("UIR GG3", R({ gg: 3 }), "Unfavorable intermediate"); eq("UIR two IRFs", R({ gg: 2, psa: "10-20" }), "Unfavorable intermediate");
  eq("high T3a", R({ t: "T3a" }), "High"); eq("high GG4", R({ gg: 4 }), "High"); eq("high PSA>20", R({ psa: ">20" }), "High");
  eq("VH T3b", R({ t: "T3b" }), "Very high"); eq("VH two HR features", R({ gg: 4, psa: ">20" }), "Very high");
  eq("VH >4 cores GG4-5", R({ gg: 4, cores4: true }), "Very high"); eq("VH primary 5", R({ gg: 5, primary5: true }), "Very high");

  // AJCC 8th edition prostate stage groups
  const A = (o) => prostateAJCC({ ...base, ...o });
  eq("AJCC I", A({}), "I"); eq("AJCC IIA PSA", A({ psa: "10-20" }), "IIA"); eq("AJCC IIA T2b", A({ t: "T2b" }), "IIA");
  eq("AJCC IIB", A({ gg: 2 }), "IIB"); eq("AJCC IIC", A({ gg: 4 }), "IIC"); eq("AJCC IIIA", A({ psa: ">20" }), "IIIA");
  eq("AJCC IIIB", A({ t: "T3a", gg: 4 }), "IIIB"); eq("AJCC IIIC", A({ gg: 5 }), "IIIC");

  // Cervix after radical hysterectomy: Sedlis (GOG 92) / Peters (GOG 109)
  const C = (o) => cervixPostop({ nodes: false, margin: false, param: false, lvsi: true, depth: "middle", size: 2, ...o });
  eq("Peters node", C({ nodes: true }), "peters"); eq("LVSI+ deep any size", C({ depth: "deep", size: 1 }), "sedlis");
  eq("LVSI+ middle >=2", C({}), "sedlis"); eq("LVSI+ middle <2", C({ size: 1 }), "none");
  eq("LVSI+ superficial >=5", C({ depth: "superficial", size: 5 }), "sedlis"); eq("LVSI+ superficial 4", C({ depth: "superficial", size: 4 }), "none");
  eq("LVSI- middle >=4", C({ lvsi: false, size: 4 }), "sedlis"); eq("LVSI- deep 2", C({ lvsi: false, depth: "deep", size: 2 }), "none");

  // WHO CNS5 (2021) adult diffuse glioma
  const G = (o) => classifyGlioma({ idh: false, codel: false, necmvp: false, anaplasia: false, cdkn: false, molgbm: false, ...o });
  eq("GBM histologic", G({ necmvp: true }).grade, 4); eq("GBM molecular", G({ molgbm: true }).dx, "Glioblastoma, IDH-wildtype");
  eq("oligo g2", G({ idh: true, codel: true }).grade, 2); eq("oligo g3", G({ idh: true, codel: true, anaplasia: true }).grade, 3);
  eq("astro g2", G({ idh: true }).grade, 2); eq("astro g3", G({ idh: true, anaplasia: true }).grade, 3);
  eq("astro g4 CDKN2A/B", G({ idh: true, cdkn: true }).grade, 4);

  return { tests: n, failures: fails };
})();
