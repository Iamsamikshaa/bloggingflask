export default function App() {
  return (
    <div className="min-h-screen bg-[#fbf9f5] text-[#1c1917] flex items-center justify-center p-6">
      <div className="max-w-xl w-full bg-white border border-[#e6e0d6] rounded-lg p-8 text-center">
        <h1 className="text-2xl font-semibold mb-3">FolioPress — Flask Blog Management System</h1>
        <p className="text-sm text-[#57534e] mb-6">
          Start the full-stack server with <code>npm run dev</code> to run the live Python Flask application and export the downloadable ZIP archive.
        </p>
        <a
          href="/download/flask-blog-management-system.zip"
          className="inline-block px-4 py-2 bg-[#14532d] text-white text-sm font-medium rounded-md"
        >
          Download Project ZIP
        </a>
      </div>
    </div>
  );
}
