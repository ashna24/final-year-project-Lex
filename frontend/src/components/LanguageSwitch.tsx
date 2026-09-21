import type { Language } from "../types";

interface LanguageSwitchProps {
  value: Language;
  onChange: (value: Language) => void;
}

const OPTIONS: { value: Language; label: string; urdu?: boolean }[] = [
  { value: "en", label: "English" },
  { value: "both", label: "Both" },
  { value: "ur", label: "اردو", urdu: true },
];

export function LanguageSwitch({ value, onChange }: LanguageSwitchProps) {
  return (
    <div className="lang-switch" role="radiogroup" aria-label="Explanation language">
      {OPTIONS.map((option) => (
        <button
          key={option.value}
          type="button"
          role="radio"
          aria-checked={value === option.value}
          className={`lang-switch__option${value === option.value ? " lang-switch__option--active" : ""}${option.urdu ? " lang-switch__option--urdu" : ""}`}
          onClick={() => onChange(option.value)}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}
