import { useEffect, useRef, useState } from "react";

// The backend sends no progress updates so this estimates progress from elapsed time
const TARGET_DURATION_S = 75;
const STALL_THRESHOLD_S = 90;

// When each stage starts as a share of the total time
const STAGE_1_AT = 0.15;
const STAGE_2_AT = 0.25;
const STAGE_3_AT = 0.85;

export interface SimulatedProgress {
  pct: number;
  stage: 0 | 1 | 2 | 3;
  elapsed: number;
  stalled: boolean;
}

// Runs while the loading screen is showing so no separate on or off flag is needed
export function useSimulatedProgress(): SimulatedProgress {
  const [elapsed, setElapsed] = useState(0);
  const startRef = useRef<number | null>(null);

  useEffect(() => {
    startRef.current = Date.now();
    const interval = setInterval(() => {
      setElapsed(Math.floor((Date.now() - startRef.current!) / 1000));
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const fraction = Math.min(elapsed / TARGET_DURATION_S, 1);
  const pct = Math.min(Math.round(fraction * 100), 95);

  let stage: 0 | 1 | 2 | 3 = 0;
  if (fraction >= STAGE_3_AT) stage = 3;
  else if (fraction >= STAGE_2_AT) stage = 2;
  else if (fraction >= STAGE_1_AT) stage = 1;

  return { pct, stage, elapsed, stalled: elapsed >= STALL_THRESHOLD_S };
}
