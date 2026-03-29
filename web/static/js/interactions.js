/**
 * Drag-and-drop upload, file preview, loading overlay, timeline UI hooks.
 */
(function () {
  "use strict";

  function initUploadZone() {
    var zone = document.getElementById("upload-zone");
    var input = document.getElementById("file-input");
    var form = document.getElementById("fra-upload-form");
    var preview = document.getElementById("file-preview");
    var previewName = document.getElementById("file-preview-name");
    var previewMeta = document.getElementById("file-preview-meta");
    var overlay = document.getElementById("loading-overlay");

    if (!zone || !input || !form) return;

    function showPreview(file) {
      if (!preview || !previewName || !previewMeta) return;
      previewName.textContent = file.name;
      var kb = (file.size / 1024).toFixed(1);
      previewMeta.textContent = kb > 1024 ? (file.size / (1024 * 1024)).toFixed(2) + " MB" : kb + " KB";
      preview.classList.add("visible");
    }

    function clearPreview() {
      if (preview) preview.classList.remove("visible");
    }

    ["dragenter", "dragover"].forEach(function (ev) {
      zone.addEventListener(ev, function (e) {
        e.preventDefault();
        e.stopPropagation();
        zone.classList.add("dragover");
      });
    });

    ["dragleave", "drop"].forEach(function (ev) {
      zone.addEventListener(ev, function (e) {
        e.preventDefault();
        e.stopPropagation();
        zone.classList.remove("dragover");
      });
    });

    zone.addEventListener("drop", function (e) {
      var dt = e.dataTransfer;
      if (!dt || !dt.files || !dt.files.length) return;
      var f = dt.files[0];
      input.files = dt.files;
      showPreview(f);
    });

    input.addEventListener("change", function () {
      if (input.files && input.files[0]) showPreview(input.files[0]);
      else clearPreview();
    });

    form.addEventListener("submit", function () {
      if (overlay) overlay.classList.add("visible");
    });
  }

  function initTimelineToggles() {
    var root = document.getElementById("timeline-toggle");
    if (!root) return;

    var buttons = root.querySelectorAll("[data-timeline]");
    buttons.forEach(function (btn) {
      btn.addEventListener("click", function () {
        buttons.forEach(function (b) {
          b.classList.remove("active");
        });
        btn.classList.add("active");
        var mode = btn.getAttribute("data-timeline") || "both";
        if (typeof window.setFraTimelineMode === "function") {
          window.setFraTimelineMode(mode);
        }
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      initUploadZone();
      initTimelineToggles();
    });
  } else {
    initUploadZone();
    initTimelineToggles();
  }
})();
