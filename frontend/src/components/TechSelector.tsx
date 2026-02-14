interface Props {
  techs: string[];
  selected: string | null;
  onSelect: (tech: string) => void;
}

export default function TechSelector({ techs, selected, onSelect }: Props) {
  // once a tech is chosen → lock the selector
  const locked = selected !== null;

  return (
    <div>
      <style>
        {`
          @keyframes floatUp {
            from {
              opacity: 0;
              transform: translateY(12px);
            }
            to {
              opacity: 1;
              transform: translateY(0);
            }
          }
        `}
      </style>

      {techs.map((tech, index) => {
        const isSelected = selected === tech;

        return (
          <button
            key={tech}
            disabled={locked}
            onClick={() => onSelect(tech)}
            style={{
              margin: 5,
              padding: "10px 14px",
              background: isSelected ? "#16a34a" : "#4f46e5",
              color: "white",
              border: "none",
              borderRadius: 8,
              fontWeight: 600,

              // animation
              opacity: 0,
              animation: `floatUp 0.4s ease forwards`,
              animationDelay: `${index * 0.08}s`,

              // disabled UX
              cursor: locked ? "not-allowed" : "pointer",

              // fade others after selection
              filter: locked && !isSelected ? "brightness(0.8)" : "none",
            }}
          >
            {tech}
          </button>
        );
      })}
    </div>
  );
}
