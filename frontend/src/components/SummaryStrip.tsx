interface SummaryStripProps {
  high: number;
  medium: number;
  low: number;
  notAnalysed: number;
}

export function SummaryStrip({ high, medium, low, notAnalysed }: SummaryStripProps) {
  const cells: { count: number; label: string }[] = [
    { count: high, label: "High risk" },
    { count: medium, label: "Medium" },
    { count: low, label: "Low risk" },
    { count: notAnalysed, label: "Not analysed" },
  ];

  return (
    <div className="summary-strip">
      {cells.map((cell) => (
        <div key={cell.label} className="summary-strip__cell">
          <p className="summary-strip__count">{cell.count}</p>
          <p className="summary-strip__label">{cell.label}</p>
        </div>
      ))}
    </div>
  );
}
