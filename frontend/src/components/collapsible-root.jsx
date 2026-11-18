"use client";

import { Collapsible } from "@base-ui/react/collapsible";
import { forwardRef } from "react";

export const CollapsibleRoot = forwardRef(function CollapsibleRoot(props, ref) {
  return <Collapsible.Root ref={ref} data-slot="collapsible" {...props} />;
});

export function CollapsibleTrigger({
  ...props
}) {
  return <Collapsible.Trigger data-slot="collapsible-trigger" {...props} />;
}

export function CollapsibleContent({
  ...props
}) {
  return <Collapsible.Panel data-slot="collapsible-content" {...props} />;
}
