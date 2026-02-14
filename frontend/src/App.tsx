import { useEffect, useRef, useState } from "react";
import type { Candidate } from "./types/candidate";
import { analyzeCV, startInterviewApi, getCodingChallengeApi } from "./services/api";

import UploadCV from "./components/UploadCV";
import TechSelector from "./components/TechSelector";
import Questions from "./components/Questions";
import CodingChallenge from "./components/CodingChallenge";
import icon1 from "./assets/images/icon1.png";

function App() {
  const [step, setStep] = useState(1);

  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [candidate, setCandidate] = useState<Candidate | null>(null);
  const [selectedTech, setSelectedTech] = useState<string | null>(null);
  const [questions, setQuestions] = useState<string[]>([]);
  const [challenge, setChallenge] = useState("");

  const contentRef = useRef<HTMLDivElement>(null);

  // auto scroll when step changes
  useEffect(() => {
    contentRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [step]);

  // ================= STEP 1
  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    try {
      const data = await analyzeCV(file);
      setCandidate(data);
      setStep(2);
    } catch (err: any) {
      alert(err.message);
    }
    setLoading(false);
  };

  // ================= STEP 2
  const startInterview = async (tech: string) => {
    if (!file) return;

    setSelectedTech(tech);
    setQuestions([]);

    try {
      const data = await startInterviewApi(file, tech);
      setQuestions(data.questions || []);
      setStep(3);
    } catch {
      alert("Failed to start interview");
    }
  };

  // ================= STEP 3
  const handleInterviewFinish = async () => {
    if (!selectedTech || !candidate || !file) return;

    try {
      const challengeData = await getCodingChallengeApi(
        selectedTech,
        candidate.experience_level,
        file
      );

      setChallenge(challengeData.challenge || "");
      setStep(4);
    } catch {
      alert("Failed to load coding challenge");
    }
  };

  return (
    <div className="app">
      {/* ================= HEADER ================= */}
      <div className="header">
        <div className="headerInner">
          <img src={icon1} className="logoSmall" />
          <div className="brand">AI Technical Interviewer</div>
        </div>
      </div>

      <div className="container" ref={contentRef}>
        {/* ================= STEPPER ================= */}
        <Stepper step={step} />

        {/* ================= CONTENT ================= */}
        <div className="fadeIn">
          {step === 1 && (
            <UploadCV
              loading={loading}
              onFileChange={setFile}
              onUpload={handleUpload}
            />
          )}

          {step === 2 && candidate && (
            <div className="section">
              <h2>{candidate.candidate_name}</h2>
              <p className="muted">Level: {candidate.experience_level}</p>

              <TechSelector
                techs={candidate.tech_stack}
                selected={selectedTech}
                onSelect={startInterview}
              />
            </div>
          )}

          {step === 3 && (
            <Questions
              questions={questions}
              onFinish={handleInterviewFinish}
            />
          )}

          {step === 4 && selectedTech && (
            <CodingChallenge challenge={challenge} language={selectedTech} />
          )}
        </div>
      </div>
    </div>
  );
}

export default App;

/* ================= STEPPER ================= */

function Stepper({ step }: { step: number }) {
  const steps = ["Upload CV", "Select Tech", "Interview", "Coding"];

  return (
    <div className="stepper">
      {steps.map((s, i) => {
        const index = i + 1;
        return (
          <div
            key={s}
            className={`step ${step >= index ? "active" : ""}`}
          >
            <div className="circle">{index}</div>
            <span>{s}</span>
          </div>
        );
      })}
    </div>
  );
}
