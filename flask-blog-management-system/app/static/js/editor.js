document.addEventListener("DOMContentLoaded", () => {
  const editorContainer = document.getElementById("quill-editor");
  const hiddenTextarea = document.getElementById("content");
  const postForm = document.getElementById("post-editor-form");

  if (!editorContainer || !hiddenTextarea || !postForm || typeof Quill === "undefined") {
    return;
  }

  const quill = new Quill("#quill-editor", {
    theme: "snow",
    placeholder: "Begin writing your article...",
    modules: {
      toolbar: [
        [{ header: [2, 3, false] }],
        ["bold", "italic", "underline", "strike"],
        ["blockquote", "code-block"],
        [{ list: "ordered" }, { list: "bullet" }],
        ["link"],
        ["clean"],
      ],
    },
  });

  // Hydrate initial HTML when editing an existing post or re-rendering after validation error
  const initialHtml = hiddenTextarea.value.trim();
  if (initialHtml) {
    quill.clipboard.dangerouslyPasteHTML(initialHtml);
  }

  const syncContent = () => {
    const html = quill.root.innerHTML;
    const plain = quill.getText().trim();
    hiddenTextarea.value = plain.length > 0 ? html : "";
  };

  quill.on("text-change", syncContent);
  postForm.addEventListener("submit", syncContent);
});
