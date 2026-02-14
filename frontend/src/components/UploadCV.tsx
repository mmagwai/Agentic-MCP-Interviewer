import "../App.css";

interface Props {
  loading: boolean;
  onFileChange: (file: File) => void;
  onUpload: () => void;
}

export default function UploadCV({ loading, onFileChange, onUpload }: Props) {
return (
  <div className="section">
    <h2>Upload your CV</h2>

    <p className="muted">
      Supported formats: PDF, DOC, DOCX, TXT
    </p>

    <div className="inlineRow">
      <input
        type="file"
        accept=".pdf,.doc,.docx,.txt"
        onChange={(e) =>
          e.target.files && onFileChange(e.target.files[0])
        }
      />

      <button
        onClick={onUpload}
        disabled={loading}
        className="primaryButton"
      >
        {loading ? "Analyzing..." : "Upload CV"}
      </button>
    </div>
  </div>
);

}
