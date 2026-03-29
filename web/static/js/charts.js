/**
 * Chart.js dashboards: FRA comparison, difference, single curve, confidence gauge.
 * Optional: chartjs-plugin-zoom, chartjs-plugin-annotation (fault bands).
 */
(function () {
  "use strict";

  var F = window.__FRA;
  if (!F || !F.frequencies || !F.frequencies.length) return;

  function tryRegisterPlugins() {
    if (typeof Chart === "undefined") return { zoom: false, annotation: false };
    var zoomOk = false;
    var annOk = false;
    if (!Chart.registry.getPlugin("zoom")) {
      var zc = [window.ChartZoom, window.zoomPlugin, window["chartjs-plugin-zoom"]];
      for (var i = 0; i < zc.length; i++) {
        var z = zc[i];
        if (!z || !Chart.register) continue;
        try {
          Chart.register(z.default != null ? z.default : z);
          zoomOk = !!Chart.registry.getPlugin("zoom");
          if (zoomOk) break;
        } catch (e) {}
      }
    } else {
      zoomOk = true;
    }
    if (!Chart.registry.getPlugin("annotation")) {
      var ac = [window.annotationPlugin, window["chartjs-plugin-annotation"]];
      for (var j = 0; j < ac.length; j++) {
        var a = ac[j];
        if (!a || !Chart.register) continue;
        try {
          Chart.register(a.default != null ? a.default : a);
          annOk = !!Chart.registry.getPlugin("annotation");
          if (annOk) break;
        } catch (e2) {}
      }
    } else {
      annOk = true;
    }
    return { zoom: zoomOk, annotation: annOk };
  }

  function xySeries(freqs, mags) {
    var out = [];
    if (!freqs || !mags) return out;
    for (var i = 0; i < freqs.length && i < mags.length; i++) {
      out.push({ x: freqs[i], y: mags[i] });
    }
    return out;
  }

  function computeFaultBands(freqs, diffs, thresholdDb) {
    var th = thresholdDb == null ? 3 : thresholdDb;
    var bands = [];
    if (!freqs || !diffs || freqs.length !== diffs.length) return bands;
    var start = -1;
    for (var i = 0; i < diffs.length; i++) {
      var over = Math.abs(diffs[i]) >= th;
      if (over && start < 0) start = i;
      if (!over && start >= 0) {
        bands.push({ xMin: freqs[start], xMax: freqs[i - 1] });
        start = -1;
      }
    }
    if (start >= 0) bands.push({ xMin: freqs[start], xMax: freqs[freqs.length - 1] });
    return bands;
  }

  function buildAnnotations(bands) {
    var ann = {};
    for (var b = 0; b < bands.length; b++) {
      ann["fault" + b] = {
        type: "box",
        xMin: bands[b].xMin,
        xMax: bands[b].xMax,
        yMin: "min",
        yMax: "max",
        backgroundColor: "rgba(239, 68, 68, 0.12)",
        borderWidth: 0,
      };
    }
    return ann;
  }

  var plugins = tryRegisterPlugins();

  var commonScaleX = {
    type: "logarithmic",
    grid: { color: "rgba(148, 163, 184, 0.08)" },
    ticks: {
      color: "#64748b",
      maxTicksLimit: 8,
      callback: function (value) {
        if (value === 0) return "0";
        var v = Number(value);
        if (v >= 1e6) return (v / 1e6).toFixed(1) + "M";
        if (v >= 1e3) return (v / 1e3).toFixed(0) + "k";
        return v.toFixed(0);
      },
    },
    title: { display: true, text: "Frequency (Hz)", color: "#94a3b8", font: { size: 11 } },
  };

  var commonScaleY = {
    grid: { color: "rgba(148, 163, 184, 0.08)" },
    ticks: { color: "#64748b" },
    title: { display: true, text: "Magnitude (dB)", color: "#94a3b8", font: { size: 11 } },
  };

  var zoomOpts =
    plugins.zoom && typeof Hammer !== "undefined"
      ? {
          zoom: {
            wheel: { enabled: true },
            pinch: { enabled: true },
            mode: "xy",
          },
          pan: {
            enabled: true,
            mode: "xy",
          },
        }
      : undefined;

  var bands = computeFaultBands(F.frequencies, F.chartDiff || [], F.faultThresholdDb);
  var annotationCfg =
    plugins.annotation && bands.length
      ? { annotations: buildAnnotations(bands) }
      : undefined;

  var compareCanvas = document.getElementById("chart-compare");
  if (compareCanvas) {
    var dsRef = {
      label: "Before — Reference (healthy)",
      data: xySeries(F.frequencies, F.healthy),
      borderColor: "rgba(56, 189, 248, 0.65)",
      borderDash: [6, 4],
      borderWidth: 2,
      pointRadius: 0,
      tension: 0.35,
      fill: false,
    };
    var dsTest = {
      label: "After — Test (uploaded)",
      data: xySeries(F.frequencies, F.faulty),
      borderColor: "#f59e0b",
      borderWidth: 2.5,
      pointRadius: 0,
      tension: 0.35,
      fill: false,
    };

    var cmp = new Chart(compareCanvas.getContext("2d"), {
      type: "line",
      data: {
        datasets: [dsRef, dsTest],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: "index", intersect: false },
        scales: {
          x: commonScaleX,
          y: commonScaleY,
        },
        plugins: {
          legend: {
            position: "top",
            labels: { color: "#e2e8f0", usePointStyle: true, padding: 14 },
          },
          tooltip: {
            callbacks: {
              title: function (items) {
                if (!items.length) return "";
                var raw = items[0].raw;
                var hz = raw && raw.x != null ? raw.x : F.frequencies[items[0].dataIndex];
                return "f = " + Number(hz).toExponential(2) + " Hz";
              },
              afterBody: function (items) {
                if (!items.length || !F.chartDiff) return "";
                var idx = items[0].dataIndex;
                var d = F.chartDiff[idx];
                if (d == null) return "";
                return ["Δ (test − ref): " + d.toFixed(2) + " dB"];
              },
            },
          },
          ...(annotationCfg ? { annotation: annotationCfg } : {}),
          ...(zoomOpts ? { zoom: zoomOpts } : {}),
        },
      },
    });

    window.setFraTimelineMode = function (mode) {
      var showRef = mode === "before" || mode === "both";
      var showTest = mode === "after" || mode === "both";
      cmp.data.datasets[0].hidden = !showRef;
      cmp.data.datasets[1].hidden = !showTest;
      cmp.update();
    };
  }

  var diffCanvas = document.getElementById("chart-diff");
  if (diffCanvas && F.chartDiff && F.chartDiff.length) {
    new Chart(diffCanvas.getContext("2d"), {
      type: "line",
      data: {
        datasets: [
          {
            label: "Difference (test − reference) dB",
            data: xySeries(F.frequencies, F.chartDiff),
            borderColor: "#a78bfa",
            backgroundColor: "rgba(167, 139, 250, 0.08)",
            borderWidth: 2,
            pointRadius: 0,
            tension: 0.35,
            fill: true,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: "index", intersect: false },
        scales: {
          x: commonScaleX,
          y: {
            ...commonScaleY,
            title: { display: true, text: "Δ Magnitude (dB)", color: "#94a3b8", font: { size: 11 } },
            grid: { color: "rgba(148, 163, 184, 0.08)" },
            ticks: { color: "#64748b" },
          },
        },
        plugins: {
          legend: { labels: { color: "#e2e8f0" } },
          tooltip: {
            callbacks: {
              footer: function () {
                return "|Δ| ≥ " + (F.faultThresholdDb || 3) + " dB → shaded on comparison chart";
              },
            },
          },
          ...(zoomOpts ? { zoom: zoomOpts } : {}),
        },
      },
    });
  }

  var singleCanvas = document.getElementById("chart-single");
  if (singleCanvas) {
    new Chart(singleCanvas.getContext("2d"), {
      type: "line",
      data: {
        datasets: [
          {
            label: "Test FRA magnitude",
            data: xySeries(F.frequencies, F.faulty),
            borderColor: "#38bdf8",
            borderWidth: 2,
            pointRadius: 0,
            tension: 0.35,
            fill: false,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: commonScaleX,
          y: commonScaleY,
        },
        plugins: {
          legend: { labels: { color: "#e2e8f0" } },
          tooltip: { mode: "index", intersect: false },
          ...(zoomOpts ? { zoom: zoomOpts } : {}),
        },
      },
    });
  }

  var gaugeEl = document.getElementById("health-gauge");
  if (gaugeEl && F.confidence != null) {
    var score = Math.min(100, Math.max(0, Number(F.confidence)));
    var col = score >= 75 ? "#22c55e" : score >= 45 ? "#f59e0b" : "#ef4444";
    new Chart(gaugeEl.getContext("2d"), {
      type: "doughnut",
      data: {
        datasets: [
          {
            data: [score, Math.max(0, 100 - score)],
            backgroundColor: [col, "#1e293b"],
            borderWidth: 0,
            circumference: 180,
            rotation: 270,
          },
        ],
      },
      options: {
        cutout: "78%",
        aspectRatio: 2,
        plugins: { tooltip: { enabled: false }, legend: { display: false } },
      },
    });
  }
})();
