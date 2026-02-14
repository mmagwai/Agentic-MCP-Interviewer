export const analyzeCV = async (file: File) => {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch("http://127.0.0.1:8000/analyze-cv", {
    method: "POST",
    body: formData,
  });

  if (!res.ok) throw new Error(await res.text());
  return res.json();
};

export const startInterviewApi = async (file: File, tech: string) => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("selected_tech", tech);

  const res = await fetch("http://127.0.0.1:8000/questions", {
    method: "POST",
    body: formData,
  });

  if (!res.ok) throw new Error(await res.text());
  return res.json();
};

export const evaluateAnswerApi = async (
  question: string,
  answer: string
) => {
  const form = new FormData();
  form.append("question", question);
  form.append("answer", answer);

  const res = await fetch("http://localhost:8000/evaluate-answer", {
    method: "POST",
    body: form,
  });

  if (!res.ok) throw new Error("Evaluation failed");

  return res.json();
};

export const getCodingChallengeApi = async (
  tech: string,
  level: string,
  file: File
) => {
  const form = new FormData();
  form.append("selected_tech", tech);
  form.append("experience_level", level);
  form.append("file", file);

  const res = await fetch("http://localhost:8000/coding-challenge", {
    method: "POST",
    body: form,
  });

  if (!res.ok) throw new Error("Failed to generate challenge");
  return res.json();
};



export const gradeCodeApi = async (
  problem: string,
  code: string,
  output: string
) => {
  const form = new FormData();
  form.append("problem", problem);
  form.append("code", code);
  form.append("output", output);

  const res = await fetch("http://localhost:8000/grade-code", {
    method: "POST",
    body: form,
  });

  return res.json();
};
