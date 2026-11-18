import { useEffect, useLayoutEffect } from "react";

const hasWindow =
  typeof (globalThis).window !==
  "undefined";

export const useIsomorphicLayoutEffect = hasWindow
  ? useLayoutEffect
  : useEffect;
