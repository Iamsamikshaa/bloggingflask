document.addEventListener("DOMContentLoaded", () => {
  // Auto-dismiss non-error flash alerts smoothly after 5 seconds
  const alerts = document.querySelectorAll(".fp-flash-auto");
  alerts.forEach((alertEl) => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alertEl);
      bsAlert.close();
    }, 5000);
  });

  // Inline comment edit toggles
  document.querySelectorAll("[data-edit-comment-toggle]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const id = btn.getAttribute("data-edit-comment-toggle");
      const formWrapper = document.getElementById(`comment-edit-${id}`);
      const bodyEl = document.getElementById(`comment-body-${id}`);
      if (!formWrapper || !bodyEl) return;

      const isHidden = formWrapper.classList.contains("d-none");
      formWrapper.classList.toggle("d-none", !isHidden);
      bodyEl.classList.toggle("d-none", isHidden);
    });
  });

  document.querySelectorAll("[data-cancel-comment-edit]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const id = btn.getAttribute("data-cancel-comment-edit");
      const formWrapper = document.getElementById(`comment-edit-${id}`);
      const bodyEl = document.getElementById(`comment-body-${id}`);
      if (!formWrapper || !bodyEl) return;

      formWrapper.classList.add("d-none");
      bodyEl.classList.remove("d-none");
    });
  });

  // Live preview for featured image upload
  const fileInput = document.getElementById("featured_image");
  const previewContainer = document.getElementById("image-preview-container");
  const previewImg = document.getElementById("image-preview-el");

  if (fileInput && previewContainer && previewImg) {
    fileInput.addEventListener("change", (event) => {
      const file = event.target.files?.[0];
      if (!file) {
        return;
      }
      const reader = new FileReader();
      reader.onload = (e) => {
        if (e.target?.result) {
          previewImg.src = e.target.result;
          previewContainer.classList.remove("d-none");
        }
      };
      reader.readAsDataURL(file);
    });
  }
});
